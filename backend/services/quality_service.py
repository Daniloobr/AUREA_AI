"""
Quality Control Service
========================
Post-generation quality assessment:
- Image quality scoring
- Aesthetic scoring
- Face presence verification in output (OpenCV Haar)
- Resolution validation
"""
import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

# Haar cascade for quick face detection in generated outputs
_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
_face_cascade = cv2.CascadeClassifier(_cascade_path)


def assess_output_quality(image_path: str) -> dict:
    """
    Assesses the quality of a generated image.
    Returns a quality report.
    """
    result = {
        "quality_score": 0.0,
        "has_face": False,
        "resolution_ok": True,
        "blur_score": 0.0,
        "brightness_score": 0.0,
        "contrast_score": 0.0,
        "aesthetic_score": 0.0,
        "issues": [],
    }

    try:
        img = cv2.imread(image_path)
        if img is None:
            result["issues"].append("Could not load generated image")
            return result

        h, w = img.shape[:2]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 1. Resolution check
        if w < 512 or h < 512:
            result["resolution_ok"] = False
            result["issues"].append(f"Low resolution: {w}x{h}")

        # 2. Blur score
        blur = cv2.Laplacian(gray, cv2.CV_64F).var()
        result["blur_score"] = round(blur, 2)
        if blur < 50:
            result["issues"].append("Generated image appears blurry")

        # 3. Brightness
        brightness = gray.mean()
        result["brightness_score"] = round(brightness, 2)
        if brightness < 40:
            result["issues"].append("Image too dark")
        elif brightness > 240:
            result["issues"].append("Image overexposed")

        # 4. Contrast
        contrast = gray.std()
        result["contrast_score"] = round(contrast, 2)
        if contrast < 20:
            result["issues"].append("Very low contrast")

        # 5. Face detection in output using Haar Cascade
        gray_eq = cv2.equalizeHist(gray)
        faces = _face_cascade.detectMultiScale(
            gray_eq,
            scaleFactor=1.1,
            minNeighbors=4,
            minSize=(60, 60)
        )
        result["has_face"] = len(faces) > 0
        if not result["has_face"]:
            result["issues"].append("No face detected in generated image")

        # 6. Aesthetic score (composite)
        blur_norm = min(blur / 300.0, 1.0)
        bright_norm = 1.0 - abs(brightness - 140) / 140.0
        contrast_norm = min(contrast / 70.0, 1.0)
        face_bonus = 0.3 if result["has_face"] else 0.0

        aesthetic = (
            blur_norm * 0.25 +
            bright_norm * 0.2 +
            contrast_norm * 0.2 +
            face_bonus +
            (0.05 if result["resolution_ok"] else 0.0)
        )
        result["aesthetic_score"] = round(min(1.0, aesthetic), 3)

        # 7. Overall quality score
        result["quality_score"] = round(
            aesthetic * (1.0 if result["has_face"] else 0.5),
            3
        )

    except Exception as e:
        logger.error(f"Quality assessment failed: {e}")
        result["issues"].append(f"Assessment error: {str(e)}")

    return result
