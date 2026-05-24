import uuid
import os
from database import db
from models.db_models import GenerationJob, User, Transaction
from services.replicate_service import generate_with_retry, download_generated_image
from services.prompt_engine import generate_prompt, generate_negative_prompt
import logging
import json
from tasks.generation_tasks import generate_image_task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def refund_credits(user_id, amount, description="Reembolso por falha na geração"):
    """
    Refunds credits to a user and records the transaction.
    """
    try:
        user = User.query.filter_by(id=user_id).first()
        if not user:
            logger.error(f"❌ Refund: User {user_id} not found.")
            return False

        old_balance = user.credits_balance
        user.credits_balance += amount

        txn = Transaction(
            user_id=user.id,  # use user.id para consistência
            type='credit_refund',
            amount=amount,
            balance_before=old_balance,
            balance_after=user.credits_balance,
            description=description
        )
        db.session.add(txn)
        db.session.commit()
        logger.info(f"✅ Refunded {amount} credits to user {user_id}. New balance: {user.credits_balance}")
        return True
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Critical error during refund for user {user_id}: {e}", exc_info=True)
        return False

def process_generation_pipeline(app, job_id, image_urls, tipo_ensaio, custom_prompt=None):
    with app.app_context():
        job = None
        try:
            job = GenerationJob.query.get(job_id)
            if not job:
                return

            prompt = generate_prompt(tipo_ensaio, subject_description=custom_prompt or "", use_identity_text=True)
            generate_negative_prompt()

            if image_urls:
                job.status = "validating"
                job.progress = 10
                job.message = "Verificando parâmetros de geração..."
                db.session.commit()

            job.status = "generating"
            job.progress = 50
            job.message = "Processando sua obra de arte via Google Nano Banana Pro..."
            db.session.commit()

            ai_result = generate_with_retry(
                image_urls=image_urls,
                prompt=prompt,
                job_id=job.id
            )

            if ai_result["success"] and ai_result["images"]:
                from services.supabase_service import supabase_service
                final_cloud_urls = []

                for idx, remote_url in enumerate(ai_result["images"]):
                    local_path = download_generated_image(remote_url)
                    if local_path:
                        filename = os.path.basename(local_path)
                        cloud_url = supabase_service.upload_image(local_path, filename, bucket="outputs")
                        if cloud_url:
                            final_cloud_urls.append(cloud_url)
                        if os.path.exists(local_path):
                            os.remove(local_path)

                if not final_cloud_urls:
                    raise Exception("Falha ao salvar as imagens geradas no Supabase.")

                job.set_images(final_cloud_urls)
                job.status = "completed"
                job.progress = 100
                job.message = "Sucesso! Seu ensaio premium está pronto."
                logger.info(f"Job {job_id} completed successfully.")

                try:
                    from services.email_service import email_service
                    user = User.query.filter_by(id=job.user_id).first()
                    if user and user.email:
                        email_service.send_generation_complete(user.email, job.id)
                except Exception as mail_err:
                    logger.warning(f"Failed to send completion email: {mail_err}")
            else:
                error_msg = ai_result.get("error") or "Erro desconhecido na API de IA"
                raise Exception(error_msg)

            db.session.commit()

        except Exception as e:
            logger.error(f"Error in pipeline for job {job_id}: {e}", exc_info=True)
            db.session.rollback()
            if job:
                try:
                    job.status = "failed"
                    job.error = str(e)
                    job.message = "Ocorreu um erro técnico. Suas moedas foram reembolsadas."
                    db.session.commit()

                    if job.cost_moedas > 0:
                        logger.info(f"Attempting refund for job {job_id}, amount {job.cost_moedas}")
                        refund_credits(job.user_id, job.cost_moedas, f"Falha automática: {str(e)[:100]}")
                    else:
                        logger.warning(f"Job {job_id} has cost_moedas = {job.cost_moedas}, no refund")
                except Exception as inner_e:
                    logger.error(f"Could not rollback/refund job {job_id}: {inner_e}", exc_info=True)

def queue_generation(user_id: str, image_urls: list = None, tipo_ensaio: str = None, prompt: str = None) -> str:
    COST_PER_CALL = 25
    user = User.query.filter_by(id=user_id, is_active=True).first()
    if not user:
        raise ValueError("Usuário não encontrado ou inativo.")
    if user.credits_balance < COST_PER_CALL:
        raise ValueError(f"Saldo insuficiente. Você precisa de {COST_PER_CALL} moedas.")

    job_id = str(uuid.uuid4())
    old_balance = user.credits_balance
    user.credits_balance -= COST_PER_CALL

    txn = Transaction(
        user_id=user.id,
        type='generation_cost',
        amount=-COST_PER_CALL,
        balance_before=old_balance,
        balance_after=user.credits_balance,
        description=f"Geração de ensaio: {tipo_ensaio or 'Custom Prompt'}"
    )

    new_job = GenerationJob(
        id=job_id,
        user_id=user.id,
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

    generate_image_task.delay(job_id, image_urls, tipo_ensaio, prompt, user.id)
    logger.info(f"Job {job_id} queued for user {user.id}. Cost: {COST_PER_CALL}")
    return job_id

def get_job_status(job_id: str) -> dict:
    job = GenerationJob.query.get(job_id)
    if not job:
        return None
    return job.to_dict()

def recover_stuck_jobs(app):
    with app.app_context():
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
                if job.cost_moedas > 0:
                    refund_credits(job.user_id, job.cost_moedas, "Reembolso por reinicialização do sistema")
                db.session.commit()
                logger.info(f"Job {job.id} recuperado e reembolsado.")
            except Exception as e:
                db.session.rollback()
                logger.error(f"Erro ao recuperar job {job.id}: {e}", exc_info=True)