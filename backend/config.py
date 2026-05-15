"""
AI Photo Studio — Production Configuration
============================================
Central config for all services, API keys, and system parameters.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


class Config:
    # ──────────────────────────────────────────────
    # Supabase Configuration
    # ──────────────────────────────────────────────
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
    SUPABASE_SERVICE_ROLE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

    # ──────────────────────────────────────────────
    # API Keys
    # ──────────────────────────────────────────────
    REPLICATE_API_TOKEN = os.environ.get('REPLICATE_API_TOKEN')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    ADMIN_SECRET_KEY = os.environ.get('ADMIN_SECRET_KEY')

    # ──────────────────────────────────────────────
    # Security & Production
    # ──────────────────────────────────────────────
    FLASK_ENV = os.environ.get('FLASK_ENV', 'production')
    FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
    
    # CORS: In production, we MUST define ALLOWED_ORIGINS. Never use '*'
    _origins = os.environ.get('ALLOWED_ORIGINS')
    if _origins:
        ALLOWED_ORIGINS = [o.strip() for o in _origins.split(',')]
    else:
        if FLASK_ENV == 'development':
            ALLOWED_ORIGINS = ['http://localhost:3000', 'http://localhost:4000', 'http://127.0.0.1:3000', 'http://127.0.0.1:4000']
        else:
            # Restricted by default in production if not configured
            ALLOWED_ORIGINS = [] 

    # ──────────────────────────────────────────────
    # Storage Paths
    # ──────────────────────────────────────────────
    BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
    UPLOAD_FOLDER = str(BASE_DIR / 'uploads')
    FACE_CROPS_FOLDER = str(BASE_DIR / 'uploads' / 'face_crops')
    OUTPUTS_FOLDER = str(BASE_DIR / 'uploads' / 'outputs')
    THUMBNAILS_FOLDER = str(BASE_DIR / 'uploads' / 'thumbnails')

    # ──────────────────────────────────────────────
    # Upload Constraints
    # ──────────────────────────────────────────────
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
    MIN_IMAGE_RESOLUTION = 512   # px (minimum width or height)
    MAX_IMAGE_RESOLUTION = 8192  # px

    # ──────────────────────────────────────────────
    # Face Detection Thresholds
    # ──────────────────────────────────────────────
    FACE_DETECTION_CONFIDENCE = 0.7   # Minimum confidence to accept a face
    BLUR_THRESHOLD = 80.0             # Laplacian variance below this = blurry
    MIN_FACE_SIZE_RATIO = 0.08        # Face must occupy at least 8% of image area
    MAX_FACES_ALLOWED = 1             # Only 1 face per reference image

    # ──────────────────────────────────────────────
    # Generation & Auto-Reroll Configuration
    # ──────────────────────────────────────────────
    SIMILARITY_THRESHOLD = 0.40       # Reduced from 0.60 to allow FLUX stylization
    MAX_REROLL_ATTEMPTS = 3           # How many times to retry if similarity fails
    NUM_IMAGES_PER_GENERATION = 3     # Reduced from 4 as requested

    # ──────────────────────────────────────────────
    # Replicate AI Models
    # ──────────────────────────────────────────────
    REPLICATE_MODEL = "bytedance/flux-pulid"
    REPLICATE_MODEL_SLUG = "bytedance/flux-pulid:8baa7ef2255075b46f4d91cd238c21d31181b3e6a864463f967960bb0112525b"
    REPLICATE_TIMEOUT = 300  # seconds

    # ──────────────────────────────────────────────
    # Database (placeholder until Prisma/Supabase)
    # ──────────────────────────────────────────────
    DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///photostudio.db')

    # ──────────────────────────────────────────────
    # Credits
    # ──────────────────────────────────────────────
    CREDITS_PER_GENERATION = 25

    @staticmethod
    def init_app(app):
        """Initialize all required directories and environment variables."""
        for folder in [
            Config.UPLOAD_FOLDER,
            Config.FACE_CROPS_FOLDER,
            Config.OUTPUTS_FOLDER,
            Config.THUMBNAILS_FOLDER,
        ]:
            os.makedirs(folder, exist_ok=True)

        if Config.REPLICATE_API_TOKEN:
            os.environ['REPLICATE_API_TOKEN'] = Config.REPLICATE_API_TOKEN
