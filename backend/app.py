"""
AI Photo Studio — Flask Application
======================================
Production-grade entry point with:
- Structured logging
- Blueprint registration
- CORS configuration
- Health check endpoint
- Static file serving
"""
import os
import logging
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from config import Config

# ══════════════════════════════════════════════════════════════
# Logging Configuration
# ══════════════════════════════════════════════════════════════
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s │ %(levelname)-8s │ %(name)-25s │ %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'premium_ia_gravida_secret_2026')
    app.config['ADMIN_SECRET_KEY'] = os.environ.get('ADMIN_SECRET_KEY', 'master_key_777')
    
    # CORS — Allow frontend on port 3000 (standard) and 4000
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:4000", "http://127.0.0.1:4000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Admin-Key"]
        },
        r"/uploads/*": {"origins": "*"}
    }, supports_credentials=True)
    
    # Initialize config (creates directories, sets env vars)
    Config.init_app(app)
    app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH
    
    # Database Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = Config.DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    from database import db
    db.init_app(app)
    
    with app.app_context():
        from models.db_models import GenerationJob
        db.create_all()
        logger.info("Database initialized and tables created.")

    # ─── Register Blueprints ───
    from routes.upload import upload_bp
    from routes.generate import generate_bp
    from routes.gallery import gallery_bp
    from routes.auth import auth_bp
    from routes.admin import admin_bp

    app.register_blueprint(upload_bp, url_prefix='/api/upload')
    app.register_blueprint(generate_bp, url_prefix='/api/generate')
    app.register_blueprint(gallery_bp, url_prefix='/api/gallery')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    # ─── Serve uploaded/generated files ───
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

    # ─── Health Check ───
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

    # ─── Start Cleanup Scheduler (24h Retention) ───
    from services.cleanup_service import start_cleanup_scheduler
    start_cleanup_scheduler(app)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000, threaded=True)
