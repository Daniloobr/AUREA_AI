import os
import time
import logging
import threading
import json
from datetime import datetime, timedelta
from database import db
from models.db_models import GenerationJob
from config import Config
from services.queue_service import recover_stuck_jobs

logger = logging.getLogger(__name__)

def start_cleanup_scheduler(app):
    """
    Starts a background thread that performs cleanup tasks every hour.
    """
    def cleanup_loop():
        with app.app_context():
            while True:
                try:
                    logger.info("Iniciando rotina de limpeza e recuperação...")
                    perform_cleanup()
                    
                    # Also check for stuck jobs from previous sessions
                    recover_stuck_jobs(app)
                except Exception as e:
                    logger.error(f"Erro na rotina de limpeza/recuperação: {e}")
                
                # Sleep for 1 hour before next check
                time.sleep(3600)

    thread = threading.Thread(target=cleanup_loop, daemon=True)
    thread.start()
    logger.info("Agendador de limpeza iniciado (Ciclo de 1 hora).")

def perform_cleanup():
    """
    Deletes images and records older than 24 hours.
    """
    cutoff_time = datetime.utcnow() - timedelta(hours=24)
    
    # 1. Find jobs older than 24 hours
    expired_jobs = GenerationJob.query.filter(GenerationJob.created_at < cutoff_time, GenerationJob.status != "expired").all()
    
    if not expired_jobs:
        logger.info("Nenhuma imagem expirada para limpar.")
        return

    logger.info(f"Limpando {len(expired_jobs)} jobs expirados...")

    for job in expired_jobs:
        try:
            # A. Delete files
            images = json.loads(job.images_json) if job.images_json else []
            
            # Delete output images
            for img_url in images:
                filename = os.path.basename(img_url.split('?')[0])
                # Delete local if exists (legacy)
                local_path = os.path.join(Config.OUTPUTS_FOLDER, filename)
                if os.path.exists(local_path):
                    os.remove(local_path)
                
                # Supabase cleanup disabled for production to ensure no data loss

            # Delete input images
            if job.input_image_url:
                try:
                    # Check if it's a JSON list
                    input_urls = json.loads(job.input_image_url)
                    if not isinstance(input_urls, list): input_urls = [str(input_urls)]
                except:
                    input_urls = [job.input_image_url]

                for url in input_urls:
                    if not url: continue
                    filename = os.path.basename(url.split('?')[0])
                    # Delete local if exists
                    local_path = os.path.join(Config.UPLOAD_FOLDER, filename)
                    if os.path.exists(local_path):
                        os.remove(local_path)
                    
                    # Supabase cleanup disabled for production to ensure no data loss

            # B. Mark job as expired
            job.status = "expired"
            job.set_images([])
            job.message = "Imagens removidas automaticamente após 24h por segurança."
            
        except Exception as e:
            logger.error(f"Erro ao limpar job {job.id}: {e}")

    db.session.commit()
    logger.info("Limpeza de 24 horas concluída com sucesso.")
