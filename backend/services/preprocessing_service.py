"""
Image Preprocessing Service
==============================
Handles all image preprocessing before sending to AI generation:
- Resize & normalize
- Auto-enhance (brightness, contrast, sharpness)
- EXIF orientation fix
- Thumbnail generation
- Format standardization
"""
import numpy as np
from PIL import Image, ImageEnhance, ImageOps
from pathlib import Path
import uuid
import logging
from config import Config

logger = logging.getLogger(__name__)


def preprocess_for_generation(image_path: str) -> dict:
    """
    Full preprocessing pipeline before sending to Replicate.
    Returns dict with paths to processed files.
    """
    result = {
        "processed_path": image_path,  # Fallback to original
        "thumbnail_path": None,
        "original_size": None,
        "processed_size": None,
    }

    try:
        # Open with Pillow for EXIF-aware processing
        pil_img = Image.open(image_path)

        # Fix EXIF rotation (phones often store rotation in metadata)
        pil_img = ImageOps.exif_transpose(pil_img)
        
        result["original_size"] = pil_img.size

        # Convert to RGB if necessary (handles RGBA, P, L modes)
        if pil_img.mode != 'RGB':
            pil_img = pil_img.convert('RGB')

        # Resize if larger than 2048px on any side (saves bandwidth to Replicate)
        max_dim = 2048
        if max(pil_img.size) > max_dim:
            pil_img.thumbnail((max_dim, max_dim), Image.LANCZOS)

        # Light auto-enhancement
        pil_img = _auto_enhance(pil_img)

        result["processed_size"] = pil_img.size

        # Save processed version
        processed_filename = f"processed_{uuid.uuid4().hex[:8]}.jpg"
        processed_path = str(Path(Config.UPLOAD_FOLDER) / processed_filename)
        pil_img.save(processed_path, 'JPEG', quality=95)
        result["processed_path"] = processed_path

        # Generate thumbnail (300x300)
        thumb = pil_img.copy()
        thumb.thumbnail((300, 300), Image.LANCZOS)
        thumb_filename = f"thumb_{uuid.uuid4().hex[:8]}.jpg"
        thumb_path = str(Path(Config.THUMBNAILS_FOLDER) / thumb_filename)
        thumb.save(thumb_path, 'JPEG', quality=85)
        result["thumbnail_path"] = thumb_path

        logger.info(f"Preprocessed: {pil_img.size}, saved to {processed_path}")

    except Exception as e:
        logger.error(f"Preprocessing failed: {e}")
        # Return original path as fallback
        result["processed_path"] = image_path

    return result


def _auto_enhance(img: Image.Image) -> Image.Image:
    """
    Apply subtle auto-enhancement to improve AI generation input quality.
    Very light touch — we don't want to alter the face significantly.
    """
    # Slight brightness correction (target: well-lit photo)
    brightness_enhancer = ImageEnhance.Brightness(img)
    img_array = np.array(img)
    avg_brightness = img_array.mean()

    if avg_brightness < 90:
        # Dark image — brighten slightly
        img = brightness_enhancer.enhance(1.15)
    elif avg_brightness > 200:
        # Overexposed — darken slightly
        img = brightness_enhancer.enhance(0.9)

    # Slight contrast boost
    contrast_enhancer = ImageEnhance.Contrast(img)
    img = contrast_enhancer.enhance(1.05)

    # Slight sharpness boost
    sharpness_enhancer = ImageEnhance.Sharpness(img)
    img = sharpness_enhancer.enhance(1.1)

    return img
