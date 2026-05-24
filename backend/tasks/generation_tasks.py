import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

from celery.exceptions import SoftTimeLimitExceeded
from celery_app import celery

from services.ai_generator import generate_with_retry, download_generated_image
from services.supabase_service import supabase_service
from models.db_models import GenerationJob, Transaction, db

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
    Refund credits to a user using **direct SQL** to bypass ORM session issues.

    Root cause discovered:
    ----------------------
    The previous implementation used `user.credits_balance += amount` on an ORM
    object. In eager (synchronous) mode, the same SQLAlchemy session is shared
    across nested app contexts. The combination of `db.session.expire_all()`
    followed by ORM mutation + commit could cause the User row update to silently
    not persist, even though the Transaction INSERT succeeded in the same commit
    (because the Transaction was a new object `add()`-ed to the session, while
    the User was a pre-existing tracked object whose dirty flag was affected by
    `expire_all` / rollback in the calling context).

    Fix:
    - Use `UPDATE users SET credits_balance = credits_balance + :amount WHERE id = :uid`
      (atomic, bypasses ORM state entirely).
    - Use `SELECT ... FOR UPDATE` to lock the row against concurrent refunds.
    - Remove `db.session.expire_all()` — no longer needed and was part of the issue.
    - Add idempotency check: skip if a credit_refund for this reason already exists
      within the last 60 seconds (prevents double-refund on retry/recovery).
    - Add post-commit verification + detailed logging.
    """
    with flask_app.app_context():
        try:
            # ── Idempotency check ──────────────────────────────────────────
            # Avoid processing the same refund twice within 60s
            from datetime import datetime, timedelta
            recent = Transaction.query.filter(
                Transaction.user_id == user_id,
                Transaction.type == 'credit_refund',
                Transaction.description == reason,
                Transaction.created_at > datetime.utcnow() - timedelta(seconds=60),
            ).first()
            if recent:
                logger.warning(
                    f"[REFUND] ⚠️ Reembolso duplicado detectado — ignorando. "
                    f"user={user_id}, amount={amount}, reason={reason[:100]}"
                )
                return

            # ── Lock the row and read current balance ──────────────────────
            if db.engine.dialect.name == 'sqlite':
                row = db.session.execute(
                    db.text("SELECT credits_balance FROM users WHERE id = :uid"),
                    {"uid": user_id},
                ).one_or_none()
            else:
                row = db.session.execute(
                    db.text("SELECT credits_balance FROM users WHERE id = :uid FOR UPDATE"),
                    {"uid": user_id},
                ).one_or_none()

            if row is None:
                logger.error(
                    f"[REFUND] ❌ User {user_id} não encontrado — "
                    f"reembolso de {amount} moedas cancelado."
                )
                return

            old_balance = row[0]
            new_balance = old_balance + amount

            logger.info(
                f"[REFUND] ⏳ Iniciando reembolso: user={user_id}, "
                f"amount={amount}, old_balance={old_balance}, "
                f"new_balance={new_balance}, reason={reason[:100]}"
            )

            # ── Atomic UPDATE (direct SQL — bypasses ORM) ──────────────────
            updated = db.session.execute(
                db.text(
                    "UPDATE users SET credits_balance = credits_balance + :amount "
                    "WHERE id = :user_id"
                ),
                {"amount": amount, "user_id": user_id},
            ).rowcount

            if updated == 0:
                logger.error(
                    f"[REFUND] ❌ Nenhuma linha foi atualizada para user {user_id}. "
                    f"Reembolso de {amount} moedas NÃO aplicado."
                )

            # ── Create transaction record ──────────────────────────────────
            txn = Transaction(
                user_id=user_id,
                type="credit_refund",
                amount=amount,
                balance_before=old_balance,
                balance_after=new_balance,
                description=reason,
            )
            db.session.add(txn)
            db.session.commit()

            # ── Post-commit verification ───────────────────────────────────
            verify_balance = db.session.execute(
                db.text("SELECT credits_balance FROM users WHERE id = :uid"),
                {"uid": user_id},
            ).scalar()

            if verify_balance != new_balance:
                logger.error(
                    f"[REFUND] ❌ CRÍTICO: Saldo NÃO foi persistido corretamente! "
                    f"Esperado={new_balance}, Real={verify_balance}, "
                    f"user={user_id}, amount={amount}"
                )
            else:
                logger.info(
                    f"[REFUND] ✅ Reembolso confirmado: user={user_id}, "
                    f"amount={amount}, old={old_balance}, new={verify_balance}, "
                    f"reason={reason[:100]}"
                )

        except Exception as e:
            db.session.rollback()
            logger.exception(
                f"[REFUND] ❌ Erro crítico ao reembolsar user {user_id}: {e}"
            )


# ─── Timeout ────────────────────────────────────────────────────────────
TIMEOUT_SECONDS = 180  # 3 minutos — soft limit (graceful exception)
HARD_TIMEOUT_SECONDS = 200  # 3min20s — hard kill se o soft falhar


@celery.task(
    bind=True,
    name="generate_image_task",
    soft_time_limit=TIMEOUT_SECONDS,
    time_limit=HARD_TIMEOUT_SECONDS,
)
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

        deadline = time.monotonic() + TIMEOUT_SECONDS

        try:
            # 1️⃣ Atualizar status → processing
            job.status = "processing"
            job.progress = 10
            job.message = "Iniciando pipeline de geração..."
            db.session.commit()
            logger.info(f"[Task] Job {job_id} → status=processing")

            # 2️⃣ Chamar API de IA com timeout Python-level
            # (ThreadPoolExecutor garante que o timeout funciona mesmo que
            #  o Replicate client bloqueie em C, onde sinais SIGUSR1 do
            #  Celery podem não ser entregues.)
            with ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(
                    generate_with_retry,
                    image_urls=image_urls,
                    prompt=prompt_text,
                    job_id=job.id,
                )
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise SoftTimeLimitExceeded()
                try:
                    ai_result = future.result(timeout=remaining)
                except FutureTimeoutError:
                    future.cancel()
                    raise SoftTimeLimitExceeded()

            if not ai_result.get("success") or not ai_result.get("images"):
                raise RuntimeError(
                    ai_result.get("error", "Erro desconhecido na API de IA")
                )

            # 3️⃣ Fazer upload das imagens geradas
            final_urls = []

            for remote_url in ai_result["images"]:
                if time.monotonic() >= deadline:
                    raise SoftTimeLimitExceeded()

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

        except SoftTimeLimitExceeded:
            logger.error(f"[Task] ⏰ TIMEOUT job {job_id} — excedeu {TIMEOUT_SECONDS}s")

            try:
                db.session.rollback()
            except Exception:
                pass

            try:
                job = GenerationJob.query.filter_by(id=job_id).first()
                if job:
                    job.status = "failed"
                    job.error = "Tempo limite excedido"
                    job.message = "Tempo limite excedido. Tente novamente mais tarde. Seus créditos foram devolvidos."
                    db.session.commit()
                    logger.info(f"[Task] Job {job_id} marcado como timeout.")

                    # ⚡ Reembolso IMEDIATO dentro do handler
                    from services.queue_service import refund_credits
                    amt = job.cost_moedas if (job.cost_moedas and job.cost_moedas > 0) else 25
                    refund_credits(user_id, amt, f"Timeout na geração – job {job_id}")
                    logger.info(f"[Task] ✅ Reembolso imediato de {amt} moedas para user {user_id} (timeout).")
            except Exception as mark_err:
                logger.error(f"[Task] Não foi possível marcar job como timeout: {mark_err}")

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

    # 5️⃣ Reembolso — SOMENTE para erros não-timeout (timeout já reembolsou acima)
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