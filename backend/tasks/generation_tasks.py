# ✅ CERTO (baseado no seu runtime atual)
from celery_app import celery
from services.replicate_service import generate_with_retry, download_generated_image
from services.supabase_service import supabase_service
from models.db_models import GenerationJob, User, Transaction, db
logger = logging.getLogger(__name__)

def _refund_user(user_id: str, amount: int, reason: str) -> None:
    """Create a refund transaction and add credits back to the user."""
    try:
        user = User.query.get(user_id)
        if not user:
            logger.error(f"Refund failed – user {user_id} not found.")
            return
        old_balance = user.credits_balance
        user.credits_balance += amount
        txn = Transaction(
            user_id=user_id,
            type="refund",
            amount=amount,
            balance_before=old_balance,
            balance_after=user.credits_balance,
            description=reason,
        )
        db.session.add(txn)
        db.session.commit()
        logger.info(f"Refunded {amount} credits to user {user_id}: {reason}")
    except Exception as e:
        db.session.rollback()
        logger.exception(f"Critical error while refunding user {user_id}: {e}")

@shared_task(bind=True, name="generate_image_task")
def generate_image_task(self, job_id: str, image_urls: list, style_id: str, prompt_text: str, user_id: str) -> None:
    """Celery task that runs the full generation pipeline.

    Steps:
    1️⃣ Mark job as processing.
    2️⃣ Call Replicate via ``generate_with_retry``.
    3️⃣ Download each generated image, upload to Supabase and collect public URLs.
    4️⃣ Persist URLs on the job and set status ``completed``.
    5️⃣ On any exception, mark the job ``failed`` and refund the 25‑credit cost.
    """
    logger.info(f"[Task {self.request.id}] Starting job {job_id}")
    job = GenerationJob.query.get(job_id)
    if not job:
        logger.error(f"Job {job_id} not found in DB.")
        return
    try:
        # 1️⃣ Update status
        job.status = "processing"
        job.progress = 10
        job.message = "Iniciando pipeline de geração..."
        db.session.commit()

        # 2️⃣ Call Replicate
        ai_result = generate_with_retry(image_urls=image_urls, prompt=prompt_text, job_id=job.id)
        if not ai_result.get("success") or not ai_result.get("images"):
            raise RuntimeError(ai_result.get("error", "Erro desconhecido na API de IA"))

        # 3️⃣ Upload results to Supabase
        final_urls = []
        for remote_url in ai_result["images"]:
            local_path = download_generated_image(remote_url)
            if not local_path:
                continue
            filename = remote_url.split('/')[-1]
            cloud_url = supabase_service.upload_image(local_path, filename, bucket="outputs")
            if cloud_url:
                final_urls.append(cloud_url)
            # cleanup temp file
            try:
                import os
                os.remove(local_path)
            except Exception:
                pass
        if not final_urls:
            raise RuntimeError("Falha ao salvar as imagens geradas no Supabase.")

        # 4️⃣ Persist success
        job.set_images(final_urls)
        job.status = "completed"
        job.progress = 100
        job.message = "Sucesso! Seu ensaio premium está pronto."
        db.session.commit()
        logger.info(f"Job {job_id} completed successfully.")

    except Exception as exc:
        logger.exception(f"Error processing job {job_id}: {exc}")
        db.session.rollback()
        job = GenerationJob.query.get(job_id)  # re‑load after rollback
        if job:
            job.status = "failed"
            job.error = str(exc)
            job.message = "Ocorreu um erro técnico. Créditos foram reembolsados."
            db.session.commit()
            # Refund the fixed cost (25 credits) – use the amount stored on the job if available
            refund_amount = getattr(job, "cost_moedas", 25)
            if refund_amount > 0:
                _refund_user(user_id, refund_amount, f"Falha automática da geração (job {job_id})")
