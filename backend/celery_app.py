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
_broker_url = os.getenv('CELERY_BROKER_URL')
_backend_url = os.getenv('CELERY_RESULT_BACKEND')
_eager_mode = not _broker_url

if _eager_mode:
    logger.warning("[CELERY] Broker nao configurado no modulo. Modo EAGER.")
    _broker_url = 'memory://'
    _backend_url = 'cache+memory://'
else:
    logger.info(
        "[CELERY] Configurado via env vars: "
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

    # Read from app config first (allows override of env vars)
    broker = app.config.get('CELERY_BROKER_URL') or os.getenv('CELERY_BROKER_URL')
    backend = app.config.get('CELERY_RESULT_BACKEND') or os.getenv('CELERY_RESULT_BACKEND')

    task_always_eager = not broker
    if task_always_eager:
        logger.warning("[CELERY] Broker nao configurado. Ativando modo EAGER (sincrono).")
        broker = 'memory://'
        backend = 'cache+memory://'
    else:
        logger.info(f"[CELERY] Conectado ao broker: {broker.split('@')[0] if '@' in broker else 'redis://'}...")

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
