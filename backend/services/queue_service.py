import threading
import uuid
import time
import os
import requests
from flask import current_app
from database import db
from models.db_models import GenerationJob, User, Transaction
from services.replicate_service import generate_with_retry, download_generated_image
from services.prompt_engine import generate_prompt, generate_negative_prompt
from services import face_service
from config import Config
import logging
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def refund_credits(user_id, amount, description="Reembolso por falha na geração"):
    """
    Refunds credits to a user and records the transaction.
    """
    try:
        user = User.query.get(user_id)
        if not user:
            logger.error(f"Cannot refund: User {user_id} not found.")
            return False

        old_balance = user.credits_balance
        user.credits_balance += amount
        
        txn = Transaction(
            user_id=user_id,
            type='credit_refund',
            amount=amount,
            balance_before=old_balance,
            balance_after=user.credits_balance,
            description=description
        )
        db.session.add(txn)
        db.session.commit()
        logger.info(f"Refunded {amount} credits to user {user_id}. Reason: {description}")
        return True
    except Exception as e:
        db.session.rollback()
        logger.error(f"Critical error during refund for user {user_id}: {e}")
        return False

def process_generation_pipeline(app, job_id, image_urls, tipo_ensaio, custom_prompt=None):
    """
    Background thread that processes the AI generation.
    """
    with app.app_context():
        job = None
        try:
            job = GenerationJob.query.get(job_id)
            if not job: return

            # 1. Prepare Prompts
            prompt = generate_prompt(tipo_ensaio, subject_description=custom_prompt or "")
            negative_prompt = generate_negative_prompt()

            # 2. Process input images and pick the best one
            local_input_path = None
            if image_urls:
                job.status = "validating"
                job.progress = 10
                job.message = "Analisando ângulos e qualidade das fotos..."
                db.session.commit()

                local_paths = []
                temp_files = []
                for url in image_urls:
                    if url.startswith('http'):
                        # Download cloud image for local processing (face detection)
                        try:
                            resp = requests.get(url, timeout=30)
                            resp.raise_for_status()
                            filename = f"temp_{uuid.uuid4().hex[:8]}_{os.path.basename(url.split('?')[0])}"
                            temp_path = os.path.join(Config.UPLOAD_FOLDER, filename)
                            with open(temp_path, 'wb') as f:
                                f.write(resp.content)
                            local_paths.append(temp_path)
                            temp_files.append(temp_path)
                        except Exception as e:
                            logger.warning(f"Could not download image from {url}: {e}")
                    else:
                        # Check local path (fallback/migration)
                        filename = os.path.basename(url)
                        p = os.path.join(Config.UPLOAD_FOLDER, filename)
                        if os.path.exists(p):
                            local_paths.append(p)
                
                if not local_paths:
                    raise FileNotFoundError("Nenhuma das imagens de referência pôde ser acessada.")

                # Use face_service to rank images and pick the best face
                ranked_faces = face_service.get_face_quality_rank(local_paths)
                
                best_face_local_path = None
                if ranked_faces:
                    # Pick the best one
                    best_face = ranked_faces[0]
                    best_face_local_path = best_face["face_crop_path"]
                    logger.info(f"Melhor rosto selecionado para geração: {best_face_local_path}")
                else:
                    # Fallback to the first image if no face detected in any
                    best_face_local_path = local_paths[0]
                    logger.warning("Nenhum rosto claro detectado. Usando a primeira imagem como fallback.")

                # 3. Call Replicate (Real AI)
                job.status = "generating"
                job.progress = 50
                job.message = "Processando sua obra de arte via FLUX + PuLID..."
                db.session.commit()

                # IMPORTANT: If we have a face crop, we upload it to Supabase so Replicate can access it
                # because Replicate needs a public URL or a file stream.
                # We'll pass the local path to replicate_service which handles the upload/stream.
                ai_result = generate_with_retry(
                    image_path=best_face_local_path,
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    id_weight=0.8 if best_face_local_path else 0.0,
                    guidance_scale=7.0,
                    num_steps=20,
                    job_id=job.id
                )

                # Cleanup temp input files
                for f in temp_files:
                    if os.path.exists(f): os.remove(f)

            if ai_result["success"] and ai_result["images"]:
                # 4. Process and Save Outputs
                from services.supabase_service import supabase_service
                final_cloud_urls = []
                
                for idx, remote_url in enumerate(ai_result["images"]):
                    # Download to temp
                    local_path = download_generated_image(remote_url)
                    if local_path:
                        # Upload to Supabase
                        filename = os.path.basename(local_path)
                        cloud_url = supabase_service.upload_image(local_path, filename, bucket="outputs")
                        if cloud_url:
                            final_cloud_urls.append(cloud_url)
                        
                        # Cleanup local output
                        if os.path.exists(local_path):
                            os.remove(local_path)

                if not final_cloud_urls:
                    raise Exception("Falha ao salvar as imagens geradas no Supabase.")

                job.set_images(final_cloud_urls)
                job.status = "completed"
                job.progress = 100
                job.message = "Sucesso! Seu ensaio premium está pronto."
                logger.info(f"Job {job_id} completed successfully.")

                # Send Notification Email
                try:
                    from services.email_service import email_service
                    user = User.query.get(job.user_id)
                    if user and user.email:
                        email_service.send_generation_complete(user.email, job.id)
                except Exception as mail_err:
                    logger.warning(f"Failed to send completion email: {mail_err}")
            else:
                error_msg = ai_result.get("error") or "Erro desconhecido na API de IA"
                raise Exception(error_msg)

            db.session.commit()

        except Exception as e:
            logger.error(f"Error in pipeline for job {job_id}: {e}")
            db.session.rollback()
            if job:
                try:
                    job.status = "failed"
                    job.error = str(e)
                    job.message = "Ocorreu um erro técnico. Suas moedas foram reembolsadas."
                    db.session.commit()
                    
                    # Automatic Refund
                    if job.cost_moedas > 0:
                        refund_credits(job.user_id, job.cost_moedas, f"Falha automática: {str(e)[:100]}")
                except Exception as inner_e:
                    logger.error(f"Could not rollback/refund job {job_id}: {inner_e}")

def queue_generation(user_id: str, image_urls: list = None, tipo_ensaio: str = None, prompt: str = None) -> str:
    """
    Creates a new generation job with atomic credit deduction.
    """
    COST_PER_CALL = 25 
    
    user = User.query.filter_by(id=user_id, is_active=True).first()
    if not user:
        raise ValueError("Usuário não encontrado ou inativo.")
    
    if user.credits_balance < COST_PER_CALL:
        raise ValueError(f"Saldo insuficiente. Você precisa de {COST_PER_CALL} moedas.")

    job_id = str(uuid.uuid4())

    # 1. Atomic Credit Deduction
    old_balance = user.credits_balance
    user.credits_balance -= COST_PER_CALL
    
    # 2. Record Transaction
    txn = Transaction(
        user_id=user_id,
        type='generation_cost',
        amount=-COST_PER_CALL,
        balance_before=old_balance,
        balance_after=user.credits_balance,
        description=f"Geração de ensaio: {tipo_ensaio or 'Custom Prompt'}"
    )

    # 3. Create Job
    new_job = GenerationJob(
        id=job_id,
        user_id=user_id,
        status="queued",
        progress=0,
        message="Na fila de processamento...",
        tipo_ensaio=tipo_ensaio,
        input_image_url=json.dumps(image_urls) if image_urls else None,
        cost_moedas=COST_PER_CALL
    )
    
    if prompt:
        new_job.set_metadata({"custom_prompt": prompt})

    try:
        db.session.add(txn)
        db.session.add(new_job)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e

    # Start background process
    app = current_app._get_current_object()
    thread = threading.Thread(
        target=process_generation_pipeline,
        args=(app, job_id, image_urls, tipo_ensaio, prompt),
        daemon=True
    )
    thread.start()

    logger.info(f"Job {job_id} queued for user {user_id}. Cost: {COST_PER_CALL}")
    return job_id

def get_job_status(job_id: str) -> dict:
    job = GenerationJob.query.get(job_id)
    if not job: return None
    return job.to_dict()

def recover_stuck_jobs(app):
    """
    Finds jobs stuck in processing states and refunds them.
    This handles cases where the server crashed or restarted.
    """
    with app.app_context():
        # Any job that is 'generating', 'validating' or 'queued' and is older than 20 minutes
        # is likely stuck because the thread died on server restart.
        from datetime import datetime, timedelta
        timeout_limit = datetime.utcnow() - timedelta(minutes=20)
        
        stuck_jobs = GenerationJob.query.filter(
            GenerationJob.status.in_(['queued', 'validating', 'generating']),
            GenerationJob.updated_at < timeout_limit
        ).all()

        if not stuck_jobs:
            return

        logger.info(f"Detectados {len(stuck_jobs)} jobs travados. Iniciando recuperação/reembolso...")
        
        for job in stuck_jobs:
            try:
                job.status = "failed"
                job.error = "Sistema reiniciado durante o processamento."
                job.message = "O sistema foi reiniciado. Suas moedas foram devolvidas."
                
                # Refund
                if job.cost_moedas > 0:
                    refund_credits(job.user_id, job.cost_moedas, "Reembolso por reinicialização do sistema")
                
                db.session.commit()
                logger.info(f"Job {job.id} recuperado e reembolsado.")
            except Exception as e:
                db.session.rollback()
                logger.error(f"Erro ao recuperar job {job.id}: {e}")
