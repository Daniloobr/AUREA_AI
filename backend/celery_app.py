import os
from celery import Celery

# Create Celery instance. Configuration will be set from Flask app or env vars.
celery = Celery(__name__)

def init_celery(app=None):
    """Initialize Celery with Flask app context.

    If an app instance is provided, use its config to set broker and backend URLs.
    Otherwise, read from environment variables.
    """
    if app is None:
        # Import here to avoid circular imports.
        from backend.app import create_app
        app = create_app()
    # Update Celery configuration from Flask app config or environment.
    broker = os.getenv('CELERY_BROKER_URL') or app.config.get('CELERY_BROKER_URL')
    backend = os.getenv('CELERY_RESULT_BACKEND') or app.config.get('CELERY_RESULT_BACKEND')
    celery.conf.update(
        broker_url=broker,
        result_backend=backend,
        task_serializer='json',
        result_serializer='json',
        accept_content=['json'],
        timezone='UTC',
        enable_utc=True,
    )
    return celery

# Initialize Celery at import time for convenience.
# The Flask app may not be created yet, so we defer config update until the app starts.
