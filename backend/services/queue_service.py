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

def process_generation_pipeline(app, job_id, image_urls, tipo_ensaio, custom_prompt=None):
    """
    Background thread that processes the AI generation.
    """
    with app.app_context():
        try:
            job = GenerationJob.query.get(job_id)
            if not job: return

            # 1. Prepare Prompts
            prompt = custom_prompt if custom_prompt else generate_prompt(tipo_ensaio)
            negative_prompt = generate_negative_prompt()

            # 2. Process input images and pick the best one
            local_input_path = None
            if image_urls:
                job.status = "validating"
                job.progress = 10
                job.message = "Analisando ângulos e qualidade das fotos..."
                db.session.commit()

                local_paths = []
                for url in image_urls:
                    filename = os.path.basename(url)
                    p = os.path.join(Config.UPLOAD_FOLDER, filename)
                    if os.path.exists(p):
                        local_paths.append(p)
                
                if not local_paths:
                    raise FileNotFoundError("Nenhuma das imagens de referência foi encontrada no servidor.")

                # Use face_service to rank images and pick the best face
                ranked_faces = face_service.get_face_quality_rank(local_paths)
                
                if ranked_faces:
                    # Pick the best one
                    best_face = ranked_faces[0]
                    local_input_path = best_face["face_crop_path"]
                    logger.info(f"Melhor rosto selecionado para geração: {local_input_path} (Score: {best_face['quality_score']})")
                else:
                    # Fallback to the first image if no face detected in any
                    local_input_path = local_paths[0]
                    logger.warning("Nenhum rosto claro detectado. Usando a primeira imagem como fallback.")

            # 3. Call Replicate (Real AI)
            job.status = "generating"
            job.progress = 50
            job.message = "Processando sua obra de arte via FLUX + PuLID..."
            db.session.commit()

            ai_result = generate_with_retry(
                image_path=local_input_path,
                prompt=prompt,
                negative_prompt=negative_prompt,
                id_weight=1.0 if local_input_path else 0.0
            )

            if ai_result["success"] and ai_result["images"]:
                # 4. Download and save images locally
                final_images = []
                for idx, remote_url in enumerate(ai_result["images"]):
                    local_path = download_generated_image(remote_url)
                    if local_path:
                        rel_url = f"/uploads/outputs/{os.path.basename(local_path)}"
                        final_images.append(rel_url)

                if not final_images:
                    raise Exception("Falha ao salvar as imagens geradas localmente.")

                # 5. Mirror to Supabase if available
                from services.supabase_service import supabase_service
                cloud_images = []
                for local_url in final_images:
                    filename = os.path.basename(local_url)
                    local_path = os.path.join(Config.OUTPUTS_FOLDER, filename)
                    cloud_url = supabase_service.upload_image(local_path, bucket="ensaios")
                    cloud_images.append(cloud_url if cloud_url else local_url)

                job.set_images(cloud_images)
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
            job.status = "failed"
            job.error = str(e)
            db.session.commit()

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
