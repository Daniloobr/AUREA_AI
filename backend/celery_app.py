import os
from celery import Celery

# Create Celery instance. Configuration will be set from Flask app or env vars.
celery = Celery(__name__)

# Placeholder for the Flask app reference.
# Populated by init_celery() so that Celery tasks can push a Flask app context
# without having to call create_app() a second time inside the worker.
celery.flask_app = None


def init_celery(app=None):
    """Initialize Celery with Flask app context.

    If an app instance is provided, use its config to set broker and backend URLs.
    Otherwise, read from environment variables.
    Stores `app` on `celery.flask_app` so tasks can obtain a context cheaply.
    """
    if app is None:
        # Import here to avoid circular imports.
        from backend.app import create_app
        app = create_app()

    # Store the Flask app so generation_tasks._get_flask_app() can retrieve it.
    celery.flask_app = app

    broker = os.getenv('CELERY_BROKER_URL') or app.config.get('CELERY_BROKER_URL')
    backend = os.getenv('CELERY_RESULT_BACKEND') or app.config.get('CELERY_RESULT_BACKEND')
    
    # Eager mode (synchronous task execution) if broker is not set
    task_always_eager = not broker
    if task_always_eager:
        print("[CELERY] Broker nao configurado. Ativando modo EAGER (sincrono) com broker em memoria.")
        broker = 'memory://'
        backend = 'cache+memory://'

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

# Initialize Celery at import time for convenience.
# The Flask app may not be created yet, so we defer config update until the app starts.
