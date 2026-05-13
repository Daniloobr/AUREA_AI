"""
Replicate API Service — FLUX + PuLID (Ultra Premium)
======================================================
Handles communication with Replicate using the FLUX + PuLID model.
This is the gold standard for high-fidelity maternity photos.

Features:
- Single image generation per call (Rate-limit safe)
- Identity preservation via PuLID
- Cinematic quality via FLUX
- Smart retry logic for 429 errors
"""
import os
import time
import random
import replicate
import requests
import logging
from pathlib import Path
from config import Config

logger = logging.getLogger(__name__)


def generate_images(
    image_path: str,
    prompt: str,
    negative_prompt: str = None,
    num_outputs: int = 1,
    seed: int = None,
    id_weight: float = 1.0,
    guidance_scale: float = 3.5,
    num_steps: int = 20,
    **kwargs
) -> dict:
    """
    Calls Replicate API to generate images using FLUX + PuLID.
    
    Args:
        image_path: Local path to the reference face image (main_face)
        prompt: Full generation prompt
        num_outputs: Number of variations (always 1 for rate-limiting)
        seed: Random seed
        id_weight: How strongly to preserve face identity (0.0-1.0)
        guidance_scale: Prompt adherence
        num_steps: Inference steps (20 is ideal for FLUX Schnell/Dev)
    
    Returns:
        dict with 'success', 'images' (list of URLs), 'seed', 'error'
    """
    result = {
        "success": False,
        "images": [],
        "seed": seed or random.randint(1, 2147483647),
        "error": None,
        "generation_time": 0,
    }

    if seed is None:
        seed = result["seed"]

    try:
        token = Config.REPLICATE_API_TOKEN
        if not token or 'YOUR_' in token:
            raise ValueError("Replicate API token is missing.")

        if image_path and not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        logger.info(f"Starting FLUX-PuLID Generation...")
        logger.info(f"  prompt: {prompt[:80]}...")
        logger.info(f"  id_weight: {id_weight}, seed: {seed}")

        start_time = time.time()

        # Build input
        replicate_input = {
            "prompt": prompt,
            "negative_prompt": negative_prompt or "",
            "width": 896,
            "height": 1152,
            "num_steps": num_steps,
            "guidance_scale": guidance_scale,
            "id_weight": id_weight,
            "seed": seed,
            "true_cfg": 1.0, 
        }

        # Add image if provided
        if image_path:
            image_file = open(image_path, "rb")
            replicate_input["main_face_image"] = image_file
        else:
            # If no image, we might need to use a different model or adjust PuLID settings
            # But for now we just try without it, though PuLID usually requires it.
            logger.warning("Generating without main_face_image (PuLID might fail)")

        try:
            output = replicate.run(
                Config.REPLICATE_MODEL_SLUG,
                input=replicate_input
            )
        finally:
            if image_path and 'image_file' in locals():
                image_file.close()

        elapsed = round(time.time() - start_time, 2)
        result["generation_time"] = elapsed

        # Process output
        images = []
        if output:
            # Replicate output for flux-pulid is usually a single URL or list of one
            if isinstance(output, list):
                for item in output:
                    images.append(str(item.url) if hasattr(item, 'url') else str(item))
            elif hasattr(output, 'url'):
                images.append(str(output.url))
            else:
                images.append(str(output))

        if images:
            result["success"] = True
            result["images"] = images
            logger.info(f"FLUX-PuLID Complete: {len(images)} images in {elapsed}s")
        else:
            result["error"] = "Replicate returned empty output"
            logger.error("No images returned from FLUX-PuLID")

    except Exception as e:
        error_str = str(e)
        if '429' in error_str or 'throttled' in error_str.lower() or 'rate limit' in error_str.lower():
            result["error"] = "RATE_LIMITED"
            logger.warning("Rate limit hit in FLUX-PuLID")
        else:
            result["error"] = f"FLUX error: {error_str}"
            logger.error(f"Replicate error: {e}", exc_info=True)

    return result


def generate_with_retry(image_path: str, prompt: str, max_retries: int = 3, **kwargs) -> dict:
    """
    Wraps generation with retry logic and 429 handling.
    """
    last_result = None

    for attempt in range(max_retries + 1):
        if attempt > 0:
            wait_time = 15 if last_result and last_result.get("error") == "RATE_LIMITED" else 5 * attempt
            logger.warning(f"Retry {attempt}/{max_retries}, waiting {wait_time}s...")
            time.sleep(wait_time)
            kwargs["seed"] = random.randint(1, 2147483647)

        last_result = generate_images(image_path=image_path, prompt=prompt, **kwargs)

        if last_result["success"]:
            return last_result

    return last_result


def download_generated_image(url: str, save_dir: str = None) -> str:
    """
    Downloads image and saves locally.
    """
    if save_dir is None:
        save_dir = Config.OUTPUTS_FOLDER

    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()

        ext = 'jpg' if 'jpeg' in response.headers.get('content-type', '') else 'png'
        filename = f"flux_{int(time.time())}_{random.randint(1000, 9999)}.{ext}"
        filepath = str(Path(save_dir) / filename)

        with open(filepath, 'wb') as f:
            f.write(response.content)

        return filepath
    except Exception as e:
        logger.error(f"Download failed: {e}")
        return None
