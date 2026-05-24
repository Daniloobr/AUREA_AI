import logging
import os

from celery_app import celery

from services.ai_generator import generate_with_retry, download_generated_image
from services.supabase_service import supabase_service
from models.db_models import GenerationJob, User, Transaction, db

logger = logging.getLogger(__name__)


def _get_flask_app():
    """
    Returns the Flask application instance.

    Celery workers run in a separate process and do NOT inherit the Flask app
    context automatically. We must obtain the app to push a context before any
    SQLAlchemy / Flask-extension call.

    In EAGER mode (no broker, task runs synchronously in the Flask process),
    celery.flask_app is already set by init_celery(app).
    """
    try:
        flask_app = celery.flask_app
        if flask_app:
            return flask_app
    except AttributeError:
        pass

    # Fallback: recreate the app (used by standalone Celery worker processes)
    from app import create_app
    return create_app()


def _refund_user(flask_app, user_id: str, amount: int, reason: str) -> None:
    """
    Refund credits to a user in an **isolated** app context + DB session.

    Must never reuse the calling session (which may be dirty or rolled back).
    Opens its own app_context so it gets a fresh SQLAlchemy session from the
    scoped-session registry.
    """
    with flask_app.app_context():
        # Expire all objects in this new context so we read fresh data from DB
        db.session.expire_all()
        try:
            user = User.query.filter_by(id=user_id).first()
            if not user:
                logger.error(
                    f"[REFUND] ❌ User {user_id} não encontrado — "
                    f"reembolso de {amount} moedas cancelado."
                )
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
                f"(antes: {old_balance}, depois: {user.credits_balance}) | {reason}"
            )

        except Exception as e:
            db.session.rollback()
            logger.exception(f"[REFUND] ❌ Erro crítico ao reembolsar user {user_id}: {e}")


@celery.task(bind=True, name="generate_image_task")
def generate_image_task(
    self,
    job_id: str,
    image_urls: list,
    style_id: str,
    prompt_text: str,
    user_id: str,
) -> None:
    """
    Celery task: executes the full image-generation pipeline.

    Design decisions
    ----------------
    * ALL SQLAlchemy calls happen inside `with flask_app.app_context():`
      (required for worker processes; harmless when running in eager/sync mode).
    * `job_failed` flag controls whether a refund is issued — the refund must
      NOT be called on success.
    * The refund opens a SEPARATE app_context to avoid inheriting a dirty or
      rolled-back session from the pipeline block.
    """
    logger.info(f"[Task {self.request.id}] Iniciando job {job_id} para user {user_id}")

    flask_app = _get_flask_app()
    job_failed = False      # ← flag: only True when an exception occurs
    refund_amount = 25      # default fallback; overwritten from DB below

    with flask_app.app_context():
        # Expire all to avoid stale objects inherited from the caller (eager mode)
        db.session.expire_all()

        job = GenerationJob.query.filter_by(id=job_id).first()
        if not job:
            logger.error(f"[Task] Job {job_id} não encontrado no banco.")
            return

        # Capture cost BEFORE any possible exception
        refund_amount = job.cost_moedas if (job.cost_moedas and job.cost_moedas > 0) else 25

        try:
            # 1️⃣ Atualizar status → processing
            job.status = "processing"
            job.progress = 10
            job.message = "Iniciando pipeline de geração..."
            db.session.commit()
            logger.info(f"[Task] Job {job_id} → status=processing")

            # 2️⃣ Chamar API de IA
            ai_result = generate_with_retry(
                image_urls=image_urls,
                prompt=prompt_text,
                job_id=job.id,
            )

            if not ai_result.get("success") or not ai_result.get("images"):
                raise RuntimeError(
                    ai_result.get("error", "Erro desconhecido na API de IA")
                )

            # 3️⃣ Fazer upload das imagens geradas
            final_urls = []

            for remote_url in ai_result["images"]:
                local_path = download_generated_image(remote_url)

                if not local_path:
                    logger.warning(f"[Task] Falha ao baixar imagem: {remote_url}")
                    continue

                filename = os.path.basename(local_path)
                cloud_url = supabase_service.upload_image(
                    local_path, filename, bucket="outputs"
                )
                if cloud_url:
                    final_urls.append(cloud_url)

                try:
                    if os.path.exists(local_path):
                        os.remove(local_path)
                except Exception as cleanup_err:
                    logger.warning(f"[Task] Erro ao deletar temp: {cleanup_err}")

            if not final_urls:
                raise RuntimeError("Falha ao salvar as imagens no Supabase.")

            # 4️⃣ Persistir sucesso — job_failed permanece False
            job.set_images(final_urls)
            job.status = "completed"
            job.progress = 100
            job.message = "Sucesso! Seu ensaio premium está pronto."
            db.session.commit()
            logger.info(f"[Task] ✅ Job {job_id} concluído com {len(final_urls)} imagens.")

        except Exception as exc:
            logger.exception(f"[Task] ❌ Erro no job {job_id}: {exc}")
            job_failed = True  # ← marca falha para acionar reembolso abaixo

            try:
                db.session.rollback()
            except Exception:
                pass

            # Re-fetch em sessão limpa para marcar como failed
            try:
                job = GenerationJob.query.filter_by(id=job_id).first()
                if job:
                    job.status = "failed"
                    job.error = str(exc)
                    job.message = "Erro técnico. Créditos reembolsados."
                    db.session.commit()
                    logger.info(f"[Task] Job {job_id} marcado como failed.")
            except Exception as mark_err:
                logger.error(
                    f"[Task] Não foi possível marcar job como failed: {mark_err}"
                )

    # 5️⃣ Reembolso em contexto SEPARADO — SOMENTE em caso de falha
    if job_failed:
        logger.info(
            f"[Task] Emitindo reembolso de {refund_amount} moedas "
            f"para user {user_id} (job {job_id})"
        )
        _refund_user(
            flask_app,
            user_id,
            refund_amount,
            f"Reembolso automático – falha no job {job_id}",
        )
    else:
        logger.info(f"[Task] Job {job_id} concluído com sucesso — sem reembolso.")