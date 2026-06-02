import os
import logging
from celery import Celery

logger = logging.getLogger(__name__)

# Create Celery instance. Configuration will be set from Flask app or env vars.
celery = Celery(__name__)

# Placeholder for the Flask app reference.
# Populated by init_celery() so that Celery tasks can push a Flask app context
# without having to call create_app() a second time inside the worker.
celery.flask_app = None

# ── Module-level configuration (used by Celery worker process) ────────
# Behaviour governed by two env vars:
#   CELERY_ENABLED     = "true" → use real Redis broker (requires a worker process)
#                        unset or "false" → EAGER mode (tasks run inline, no worker needed)
#   CELERY_BROKER_URL  = redis://...  (only used when CELERY_ENABLED=true)
#
_celery_enabled = os.getenv('CELERY_ENABLED', '').strip().lower() == 'true'
_broker_url = os.getenv('CELERY_BROKER_URL') if _celery_enabled else None
_backend_url = os.getenv('CELERY_RESULT_BACKEND') if _celery_enabled else None
_eager_mode = not _broker_url

if _eager_mode:
    logger.warning("[CELERY] Modo EAGER ativado. Tasks executam inline (síncrono).")
    _broker_url = 'memory://'
    _backend_url = 'cache+memory://'
else:
    logger.info(
        "[CELERY] Assíncrono ativado. Broker: "
        f"{_broker_url.split('@')[0] if '@' in _broker_url else 'redis://'}..."
    )

celery.conf.update(
    broker_url=_broker_url,
    result_backend=_backend_url,
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
    task_always_eager=_eager_mode,
    task_soft_time_limit=180,
    task_time_limit=200,
)


def init_celery(app=None):
    """Initialize Celery with Flask app context.

    If an app instance is provided, use its config to set broker and backend URLs.
    Otherwise, read from environment variables.
    Stores `app` on `celery.flask_app` so tasks can obtain a context cheaply.
    """
    if app is None:
        from app import create_app
        app = create_app()

    celery.flask_app = app

    # Respect CELERY_ENABLED flag; fall back to eager mode unless explicitly enabled
    celery_enabled = str(os.getenv('CELERY_ENABLED', app.config.get('CELERY_ENABLED', ''))).strip().lower() == 'true'
    broker = None
    backend = None

    if celery_enabled:
        broker = os.getenv('CELERY_BROKER_URL') or app.config.get('CELERY_BROKER_URL')
        backend = os.getenv('CELERY_RESULT_BACKEND') or app.config.get('CELERY_RESULT_BACKEND')

    task_always_eager = not broker
    if task_always_eager:
        logger.warning("[CELERY] Modo EAGER ativado. Tasks executam inline (síncrono).")
        broker = 'memory://'
        backend = 'cache+memory://'
    else:
        logger.info(f"[CELERY] Assíncrono ativado. Broker: {broker.split('@')[0] if '@' in broker else 'redis://'}...")

    celery.conf.update(
        broker_url=broker,
        result_backend=backend,
        task_serializer='json',
        result_serializer='json',
        accept_content=['json'],
        timezone='UTC',
        enable_utc=True,
        task_always_eager=task_always_eager,
        task_soft_time_limit=180,
        task_time_limit=200,
    )
    return celery
