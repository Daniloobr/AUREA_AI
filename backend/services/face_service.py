"""
Face Detection & Validation Service
=====================================
Uses OpenCV DNN Face Detector (Caffe model) for:
- Face detection with bounding box
- Blur detection (Laplacian variance)
- Image quality scoring
- Single-face enforcement
- Face crop extraction (padded 1024x1024)

Falls back to OpenCV Haar Cascade if DNN model is unavailable.
"""
import cv2
import numpy as np
from pathlib import Path
from config import Config
import logging
import uuid

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════
# OpenCV Haar Cascade Face Detector (built-in, no downloads)
# ═══════════════════════════════════════════════════════
_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
_face_cascade = cv2.CascadeClassifier(_cascade_path)


def validate_image(image_path: str) -> dict:
    """
    Full validation pipeline for an uploaded reference image.
    Returns a detailed report with pass/fail and diagnostics.
    """
    result = {
        "valid": False,
        "errors": [],
        "warnings": [],
        "face_detected": False,
        "face_count": 0,
        "blur_score": 0.0,
        "resolution": {"width": 0, "height": 0},
        "quality_score": 0.0,
        "face_crop_path": None,
        "face_bbox": None,
    }

    # 1. Load image
    img = cv2.imread(image_path)
    if img is None:
        result["errors"].append("Não foi possível abrir a imagem. Arquivo corrompido ou formato inválido.")
        return result

    h, w = img.shape[:2]
    result["resolution"] = {"width": w, "height": h}

    # 2. Resolution check
    if w < Config.MIN_IMAGE_RESOLUTION or h < Config.MIN_IMAGE_RESOLUTION:
        result["errors"].append(f"Resolução muito baixa ({w}x{h}). Mínimo: {Config.MIN_IMAGE_RESOLUTION}px.")
        return result

    # Downscale very large images for processing speed
    process_img = img.copy()
    if max(w, h) > 2048:
        scale = 2048.0 / max(w, h)
        process_img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)

    proc_h, proc_w = process_img.shape[:2]

    # 3. Blur detection (Laplacian variance)
    gray = cv2.cvtColor(process_img, cv2.COLOR_BGR2GRAY)
    blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
    result["blur_score"] = round(blur_score, 2)

    if blur_score < Config.BLUR_THRESHOLD:
        result["errors"].append(
            f"Imagem muito desfocada (nitidez: {blur_score:.0f}, mínimo: {Config.BLUR_THRESHOLD}). "
            "Envie uma foto mais nítida."
        )
        return result

    # 4. Face detection with OpenCV Haar Cascade
    gray_eq = cv2.equalizeHist(gray)  # Improve detection in varying lighting
    
    faces = _face_cascade.detectMultiScale(
        gray_eq,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(80, 80),
        flags=cv2.CASCADE_SCALE_IMAGE
    )

    face_count = len(faces)
    result["face_count"] = face_count

    if face_count == 0:
        result["errors"].append("Nenhum rosto detectado. Envie uma foto clara com seu rosto visível e de frente.")
        return result

    result["face_detected"] = True

    if face_count > Config.MAX_FACES_ALLOWED:
        result["errors"].append(f"Detectados {face_count} rostos. Envie uma foto com apenas 1 pessoa.")
        return result

    # 5. Get the largest face (most prominent)
    face_x, face_y, face_w, face_h = max(faces, key=lambda f: f[2] * f[3])
    
    # Scale back to original image coordinates
    if max(w, h) > 2048:
        inv_scale = max(w, h) / 2048.0
        face_x = int(face_x * inv_scale)
        face_y = int(face_y * inv_scale)
        face_w = int(face_w * inv_scale)
        face_h = int(face_h * inv_scale)

    result["face_bbox"] = {
        "x": face_x, "y": face_y,
        "width": face_w, "height": face_h
    }

    # 6. Face size validation
    face_area_ratio = (face_w * face_h) / (w * h)
    if face_area_ratio < Config.MIN_FACE_SIZE_RATIO:
        result["errors"].append("Rosto muito pequeno na imagem. Aproxime a câmera do rosto.")
        return result

    # 7. Generate padded face crop (1024x1024)
    face_crop_path = _generate_face_crop(img, face_x, face_y, face_w, face_h, w, h)
    result["face_crop_path"] = face_crop_path

    # 8. Quality score (composite)
    brightness = np.mean(gray)
    contrast = gray.std()

    # Normalize scores to 0-1
    blur_norm = min(blur_score / 500.0, 1.0)
    bright_norm = 1.0 - abs(brightness - 127) / 127.0  # Best around 127
    contrast_norm = min(contrast / 80.0, 1.0)
    face_size_norm = min(face_area_ratio / 0.15, 1.0)  # Bigger face = better

    quality_score = (
        blur_norm * 0.30 +
        bright_norm * 0.20 +
        contrast_norm * 0.20 +
        face_size_norm * 0.30
    )
    result["quality_score"] = round(quality_score, 3)

    if quality_score < 0.3:
        result["warnings"].append("Qualidade da imagem abaixo do ideal. Resultados podem variar.")

    # All checks passed
    result["valid"] = True
    logger.info(
        f"Image validated: blur={blur_score:.1f}, quality={quality_score:.3f}, "
        f"faces={face_count}, face_ratio={face_area_ratio:.3f}"
    )
    return result


def _generate_face_crop(img, face_x, face_y, face_w, face_h, img_w, img_h) -> str:
    """
    Generates a padded square face crop (1024x1024) centered on the detected face.
    Includes hair, jaw, and neck for better identity conditioning.
    """
    # Add generous padding (100% of face size on each side)
    # to include hair, forehead, jaw, and shoulders
    pad_x = int(face_w * 1.0)
    pad_y_top = int(face_h * 0.8)     # Less padding above (forehead)
    pad_y_bottom = int(face_h * 1.2)   # More padding below (neck/shoulders)

    x1 = max(0, face_x - pad_x)
    y1 = max(0, face_y - pad_y_top)
    x2 = min(img_w, face_x + face_w + pad_x)
    y2 = min(img_h, face_y + face_h + pad_y_bottom)

    crop = img[y1:y2, x1:x2]

    # Make it square with padding
    crop_h, crop_w = crop.shape[:2]
    max_dim = max(crop_h, crop_w)

    # Create square canvas (black padding)
    canvas = np.zeros((max_dim, max_dim, 3), dtype=np.uint8)
    offset_x = (max_dim - crop_w) // 2
    offset_y = (max_dim - crop_h) // 2
    canvas[offset_y:offset_y + crop_h, offset_x:offset_x + crop_w] = crop

    # Resize to 1024x1024
    final_crop = cv2.resize(canvas, (1024, 1024), interpolation=cv2.INTER_LANCZOS4)

    # Save
    crop_filename = f"face_crop_{uuid.uuid4().hex[:8]}.jpg"
    crop_path = str(Path(Config.FACE_CROPS_FOLDER) / crop_filename)
    cv2.imwrite(crop_path, final_crop, [cv2.IMWRITE_JPEG_QUALITY, 95])

    logger.info(f"Face crop saved: {crop_path}")
    return crop_path


def get_face_quality_rank(image_paths: list) -> list:
    """
    Ranks multiple images by face quality score.
    Returns list sorted best-to-worst with scores.
    """
    ranked = []
    for path in image_paths:
        report = validate_image(path)
        if report["valid"]:
            ranked.append({
                "path": path,
                "quality_score": report["quality_score"],
                "blur_score": report["blur_score"],
                "face_crop_path": report["face_crop_path"]
            })

    ranked.sort(key=lambda x: x["quality_score"], reverse=True)
    return ranked
