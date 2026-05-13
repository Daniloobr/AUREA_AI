import os
import time
import logging
import threading
import json
from datetime import datetime, timedelta
from database import db
from models.db_models import GenerationJob
from config import Config
from services.supabase_service import supabase_service

logger = logging.getLogger(__name__)

def start_cleanup_scheduler(app):
    """
    Starts a background thread that performs cleanup tasks every hour.
    """
    def cleanup_loop():
        with app.app_context():
            while True:
                try:
                    logger.info("Iniciando rotina de limpeza de 24 horas...")
                    perform_cleanup()
                except Exception as e:
                    logger.error(f"Erro na rotina de limpeza: {e}")
                
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
    expired_jobs = GenerationJob.query.filter(GenerationJob.created_at < cutoff_time).all()
    
    if not expired_jobs:
        logger.info("Nenhuma imagem expirada para limpar.")
        return

    logger.info(f"Limpando {len(expired_jobs)} jobs expirados...")

    for job in expired_jobs:
        try:
            # A. Delete local files
            images = json.loads(job.images_json) if job.images_json else []
            
            # Delete output images
            for img_url in images:
                if img_url.startswith('/uploads/'):
                    filename = os.path.basename(img_url)
                    local_path = os.path.join(Config.OUTPUTS_FOLDER, filename)
                    if os.path.exists(local_path):
                        os.remove(local_path)
                        logger.debug(f"Removido arquivo local: {local_path}")
                    
                    # Delete from Supabase if it was mirrored
                    supabase_service.client.storage.from_("ensaios").remove([filename])

            # Delete input images
            if job.input_image_url:
                try:
                    input_urls = json.loads(job.input_image_url)
                    for url in input_urls:
                        filename = os.path.basename(url)
                        local_path = os.path.join(Config.UPLOAD_FOLDER, filename)
                        if os.path.exists(local_path):
                            os.remove(local_path)
                        
                        # Delete from Supabase
                        supabase_service.client.storage.from_("ensaios").remove([filename])
                except:
                    # Fallback for single string URL
                    filename = os.path.basename(job.input_image_url)
                    local_path = os.path.join(Config.UPLOAD_FOLDER, filename)
                    if os.path.exists(local_path):
                        os.remove(local_path)
                    supabase_service.client.storage.from_("ensaios").remove([filename])

            # B. Mark job as expired or delete it
            # We'll mark as 'expired' to keep a record of the transaction/credit use, 
            # but clear the images to save space.
            job.status = "expired"
            job.set_images([])
            job.message = "Imagens removidas automaticamente após 24h por segurança."
            
        except Exception as e:
            logger.error(f"Erro ao limpar job {job.id}: {e}")

    db.session.commit()
    logger.info("Limpeza de 24 horas concluída com sucesso.")
