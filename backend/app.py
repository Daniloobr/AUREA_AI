"""
Estúdio de Fotos IA — Aplicação Flask
======================================
Ponto de entrada de produção com:
- Logs estruturados
- Registro de Blueprints
- Configuração de CORS
- Endpoint de verificação de integridade (Health check)
- Servidor de arquivos estáticos
"""
import os
import logging
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from limiter_instance import limiter
from flask_talisman import Talisman
from config import Config

# ══════════════════════════════════════════════════════════════
# Configuração de Logs
# ══════════════════════════════════════════════════════════════
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s │ %(levelname)-8s │ %(name)-25s │ %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__)
    
    # Configurações de Segurança Críticas (Sem fallbacks inseguros para produção)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['ADMIN_SECRET_KEY'] = os.environ.get('ADMIN_SECRET_KEY')
    
    if not app.config['SECRET_KEY']:
        # Fallback apenas para desenvolvimento local, logando aviso
        if os.environ.get('FLASK_ENV') == 'development':
            app.config['SECRET_KEY'] = 'dev_secret_key_low_security'
            logger.warning("⚠️ SECRET_KEY não definida. Usando chave de desenvolvimento!")
        else:
            print("CRITICAL ERROR: SECRET_KEY is not set in the environment variables! Please add it in the Render dashboard.")
            raise RuntimeError("CRITICAL: SECRET_KEY não configurada no ambiente!")
    
    # CORS — Restricted to ALLOWED_ORIGINS for production security
    CORS(app, resources={
        r"/api/*": {
            "origins": Config.ALLOWED_ORIGINS,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Admin-Key"]
        },
        r"/uploads/*": {"origins": Config.ALLOWED_ORIGINS}
    }, supports_credentials=True)
    
    # ─── Proteção de Headers (CSP, HSTS, XSS Protection) ───
    # force_https=False para permitir desenvolvimento local, em produção deve ser True
    Talisman(app, 
             force_https=False, 
             content_security_policy=None, # Desativado CSP restritivo para permitir imagens externas
             session_cookie_secure=True,
             session_cookie_http_only=True)

    # ─── Rate Limiting Global ───
    limiter.init_app(app)
    app.limiter = limiter # Disponibiliza para as rotas
    
    # Inicializa a configuração (cria diretórios, define variáveis de ambiente)
    Config.init_app(app)
    app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH
    
    # Configuração do Banco de Dados
    app.config['SQLALCHEMY_DATABASE_URI'] = Config.DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    from database import db
    db.init_app(app)
    
    # ─── Registrar Blueprints ───
    from routes.upload import upload_bp
    from routes.generate import generate_bp
    from routes.gallery import gallery_bp
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.styles import styles_bp
    from routes.checkout import checkout_bp

    app.register_blueprint(upload_bp, url_prefix='/api/upload')
    app.register_blueprint(generate_bp, url_prefix='/api/generate')
    app.register_blueprint(gallery_bp, url_prefix='/api/gallery')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(styles_bp, url_prefix='/api/styles')
    app.register_blueprint(checkout_bp, url_prefix='/api/checkout')

    # Rota específica para o Webhook da SyncPay conforme pedido no PDR
    from routes.checkout import webhook_syncpay
    app.add_url_rule('/api/webhooks/syncpay', view_func=webhook_syncpay, methods=['POST'])

    # ─── Servir arquivos carregados/gerados ───
    @app.route('/uploads/<path:filename>')
    def serve_upload(filename):
        return send_from_directory(Config.UPLOAD_FOLDER, filename)

    @app.route('/uploads/outputs/<path:filename>')
    def serve_output(filename):
        return send_from_directory(Config.OUTPUTS_FOLDER, filename)

    @app.route('/uploads/face_crops/<path:filename>')
    def serve_face_crop(filename):
        return send_from_directory(Config.FACE_CROPS_FOLDER, filename)

    @app.route('/uploads/thumbnails/<path:filename>')
    def serve_thumbnail(filename):
        return send_from_directory(Config.THUMBNAILS_FOLDER, filename)

    # ─── Verificação de Integridade (Health Check) ───
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            "status": "healthy",
            "service": "AI Photo Studio API",
            "version": "2.0.0",
            "features": [
                "face_detection",
                "face_validation", 
                "similarity_check",
                "auto_reroll",
                "quality_scoring",
                "async_pipeline"
            ]
        }), 200

    logger.info("═" * 60)
    logger.info("  AI Photo Studio API v2.0 — Production Pipeline")
    logger.info("  Face Detection: MediaPipe")
    logger.info("  Generation: Replicate InstantID")
    logger.info("  Quality: Similarity + Aesthetic Scoring")
    logger.info(f"  Uploads: {Config.UPLOAD_FOLDER}")
    logger.info("═" * 60)

# ─── Iniciar Agendador de Limpeza (Retenção de 24h) ───
    from services.cleanup_service import start_cleanup_scheduler
    start_cleanup_scheduler(app)

    # ─── Recuperar Jobs Travados (Crash Recovery) ───
    from services.queue_service import recover_stuck_jobs
    recover_stuck_jobs(app)

    return app


# Ponto de entrada para Gunicorn em Produção
app = create_app()

if __name__ == '__main__':
    # Inicialização do banco apenas quando executado diretamente
    with app.app_context():
        try:
            from database import db
            from models.db_models import User, GenerationJob, Transaction, PasswordResetToken
            db.create_all()
            logger.info("✅ Banco de dados inicializado e tabelas verificadas.")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar banco de dados: {e}")

    # Usar host 0.0.0.0 para ser acessível em qualquer rede local se necessário
    # Em produção (Render), a variável de ambiente PORT é usada automaticamente pelo Gunicorn ou injetada aqui
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port, threaded=True)

