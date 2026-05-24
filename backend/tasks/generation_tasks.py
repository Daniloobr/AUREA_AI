import logging
import os

from celery import shared_task
from celery_app import celery

from services.replicate_service import generate_with_retry, download_generated_image
from services.supabase_service import supabase_service
from models.db_models import GenerationJob, User, Transaction, db

logger = logging.getLogger(__name__)


def _get_flask_app():
    """
    Returns the Flask application instance.
    Celery workers run in a separate process and do NOT inherit the Flask app
    context automatically. We must obtain the app to push a context before any
    SQLAlchemy / Flask-extension call.
    """
    try:
        # Preferred path: the app was stored on the Celery instance by app.py
        flask_app = celery.flask_app
        if flask_app:
            return flask_app
    except AttributeError:
        pass

    # Fallback: recreate the app (slower but safe)
    from app import create_app
    return create_app()


def _refund_user(flask_app, user_id: str, amount: int, reason: str) -> None:
    """
    Refund credits to a user inside an explicit Flask app context.
    Always receives `flask_app` so it can push its own context – it must NEVER
    depend on an ambient context from the caller (which may have been rolled back).
    """
    with flask_app.app_context():
        try:
            # Use filter_by to avoid cached/stale identity-map objects
            user = User.query.filter_by(id=user_id).first()
            if not user:
                logger.error(f"[REFUND] ❌ User {user_id} not found – refund of {amount} credits aborted.")
                return

            old_balance = user.credits_balance
            user.credits_balance += amount

            txn = Transaction(
                user_id=user_id,
                type="credit_refund",
                amount=amount,
                balance_before=old_balance,
                balance_after=user.credits_balance,
                description=reason,
            )

            db.session.add(txn)
            db.session.commit()

            logger.info(
                f"[REFUND] ✅ +{amount} moedas → user {user_id} "
                f"(antes: {old_balance}, depois: {user.credits_balance}) | motivo: {reason}"
            )

        except Exception as e:
            db.session.rollback()
            logger.exception(f"[REFUND] ❌ Erro crítico ao reembolsar user {user_id}: {e}")


@shared_task(bind=True, name="generate_image_task")
def generate_image_task(self, job_id: str, image_urls: list, style_id: str, prompt_text: str, user_id: str) -> None:
    """
    Celery task: executes the full image-generation pipeline.

    IMPORTANT: all SQLAlchemy operations MUST happen inside `with flask_app.app_context():`
    because the Celery worker process has no ambient Flask context.
    """
    logger.info(f"[Task {self.request.id}] Iniciando job {job_id} para user {user_id}")

    flask_app = _get_flask_app()

    with flask_app.app_context():
        job = GenerationJob.query.filter_by(id=job_id).first()
        if not job:
            logger.error(f"[Task] Job {job_id} não encontrado no banco.")
            return

        # Guardar custo antes de qualquer possível falha
        refund_amount = job.cost_moedas if job.cost_moedas and job.cost_moedas > 0 else 25

        try:
            # 1️⃣ Atualizar status
            job.status = "processing"
            job.progress = 10
            job.message = "Iniciando pipeline de geração..."
            db.session.commit()
            logger.info(f"[Task] Job {job_id} → status=processing")

            # 2️⃣ Chamar API de IA
            ai_result = generate_with_retry(
                image_urls=image_urls,
                prompt=prompt_text,
                job_id=job.id
            )

            if not ai_result.get("success") or not ai_result.get("images"):
                raise RuntimeError(ai_result.get("error", "Erro desconhecido na API de IA"))

            # 3️⃣ Fazer upload das imagens geradas
            final_urls = []

            for remote_url in ai_result["images"]:
                local_path = download_generated_image(remote_url)

                if not local_path:
                    logger.warning(f"[Task] Falha ao baixar imagem: {remote_url}")
                    continue

                filename = os.path.basename(local_path)

                cloud_url = supabase_service.upload_image(
                    local_path,
                    filename,
                    bucket="outputs"
                )

                if cloud_url:
                    final_urls.append(cloud_url)

                # Cleanup seguro
                try:
                    if os.path.exists(local_path):
                        os.remove(local_path)
                except Exception as cleanup_err:
                    logger.warning(f"[Task] Erro ao deletar arquivo temp: {cleanup_err}")

            if not final_urls:
                raise RuntimeError("Falha ao salvar as imagens no Supabase.")

            # 4️⃣ Persistir sucesso
            job.set_images(final_urls)
            job.status = "completed"
            job.progress = 100
            job.message = "Sucesso! Seu ensaio premium está pronto."

            db.session.commit()
            logger.info(f"[Task] ✅ Job {job_id} concluído com {len(final_urls)} imagens.")

        except Exception as exc:
            logger.exception(f"[Task] ❌ Erro no job {job_id}: {exc}")

            # Rollback the failed pipeline transaction
            try:
                db.session.rollback()
            except Exception:
                pass

            # Re-fetch the job in a clean state to mark as failed
            try:
                job = GenerationJob.query.filter_by(id=job_id).first()
                if job:
                    job.status = "failed"
                    job.error = str(exc)
                    job.message = "Erro técnico. Créditos reembolsados."
                    db.session.commit()
                    logger.info(f"[Task] Job {job_id} marcado como failed.")
            except Exception as mark_err:
                logger.error(f"[Task] Não foi possível marcar job como failed: {mark_err}")

    # 5️⃣ Reembolso em contexto SEPARADO para evitar contaminação da sessão anterior
    # _refund_user abre seu próprio app_context internamente
    logger.info(f"[Task] Iniciando reembolso de {refund_amount} moedas para user {user_id} (job {job_id})")
    _refund_user(
        flask_app,
        user_id,
        refund_amount,
        f"Reembolso automático – falha no job {job_id}"
    )