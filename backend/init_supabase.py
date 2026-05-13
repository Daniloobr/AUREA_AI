from app import create_app
from database import db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    app = create_app()
    with app.app_context():
        try:
            logger.info("Tentando conectar ao Supabase e criar tabelas...")
            db.create_all()
            logger.info("SUCESSO! As tabelas foram criadas no Supabase.")
        except Exception as e:
            logger.error(f"FALHA ao conectar ou criar tabelas: {e}")

if __name__ == "__main__":
    init_db()
