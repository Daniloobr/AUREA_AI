"""
Replicate API Service — openai/gpt-image-2
===========================================
Handles communication with Replicate using the openai/gpt-image-2 model.
This model supports 3 reference images and produces ultra-realistic maternity photos.

Features:
- Single image generation per call (rate-limit safe)
- Identity preservation via input_images (3 reference photos)
- Medium quality preset for optimal cost/quality balance
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
    image_urls: list,      # lista com 3 URLs das fotos de referência
    prompt: str,
    resolution: str = "2K",
    aspect_ratio: str = "16:9",
    output_format: str = "webp",
    safety_filter_level: str = "block_only_high",
    **kwargs
) -> dict:
    """
    Calls Replicate API to generate images using openai/gpt-image-2.
    
    Args:
        image_urls: List of 3 reference image URLs
        prompt: Full generation prompt
        resolution: Resolution ("2K", etc) - not directly used by this model
        aspect_ratio: Aspect ratio ("1:1", "3:2", "2:3") - normalized to "2:3" for vertical portraits
        output_format: Image format ("webp", "jpg", "png")
        safety_filter_level: Not used (kept for compatibility)
    
    Returns:
        dict with 'success', 'images' (list of URLs), 'error'
    """
    result = {
        "success": False,
        "images": [],
        "error": None,
        "generation_time": 0,
    }

    try:
        token = os.environ.get('REPLICATE_API_TOKEN', '').strip()
        
        # Clean up if user accidentally pasted 'REPLICATE_API_TOKEN=r8_...'
        if token.startswith('REPLICATE_API_TOKEN='):
            token = token.replace('REPLICATE_API_TOKEN=', '').strip()
            
        if not token or 'YOUR_' in token:
            raise ValueError("Replicate API token is missing.")

        # Ensure environment variable is clean (no newlines)
        os.environ['REPLICATE_API_TOKEN'] = token

        logger.info(f"Starting openai/gpt-image-2 Generation...")
        logger.info(f"  prompt: {prompt[:80]}...")
        logger.info(f"  image_urls: {image_urls}")

        start_time = time.time()

        # Normalize aspect ratio to accepted values
        valid_ratios = ["1:1", "3:2", "2:3"]
        if aspect_ratio not in valid_ratios:
            logger.warning(f"Aspect ratio '{aspect_ratio}' not supported, using '2:3' (vertical portrait)")
            aspect_ratio = "2:3"

        # Build input for openai/gpt-image-2
        replicate_input = {
            "prompt": prompt,
            "input_images": image_urls,
            "aspect_ratio": aspect_ratio,
            "quality": "medium",               # ← fixed to medium for optimal cost/quality
            "background": "auto",
            "moderation": "auto",
            "output_format": output_format if output_format in ["webp", "jpg", "png"] else "webp",
            "output_compression": 90,
            "number_of_images": 1
        }

        client = replicate.Client(api_token=token)
        output = client.run(
            "openai/gpt-image-2",
            input=replicate_input
        )

        elapsed = round(time.time() - start_time, 2)
        result["generation_time"] = elapsed

        # Process output (list of FileOutput objects)
        images = []
        if output:
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
            logger.info(f"openai/gpt-image-2 Complete: {len(images)} images in {elapsed}s")
            
            # Update job in database if job_id provided
            job_id = kwargs.get('job_id')
            if job_id:
                try:
                    from database import db
                    from models.db_models import GenerationJob
                    import json
                    
                    job = GenerationJob.query.get(job_id)
                    if job:
                        job.status = 'completed'
                        job.result_url = images[0]
                        job.images_json = json.dumps(images)
                        job.progress = 100
                        job.message = "Sucesso! Seu ensaio premium está pronto."
                        db.session.commit()
                        logger.info(f"[Replicate Service] Job {job_id} updated to 'completed' with result_url='{images[0]}'")
                    else:
                        logger.warning(f"[Replicate Service] Job {job_id} not found in database.")
                except Exception as db_err:
                    logger.error(f"[Replicate Service] Error updating job {job_id}: {db_err}")
        else:
            result["error"] = "Replicate returned empty output"
            logger.error("No images returned from openai/gpt-image-2")

    except Exception as e:
        error_str = str(e)
        if '429' in error_str or 'throttled' in error_str.lower() or 'rate limit' in error_str.lower():
            result["error"] = "RATE_LIMITED"
            logger.warning("Rate limit hit in openai/gpt-image-2")
        else:
            result["error"] = f"openai/gpt-image-2 error: {error_str}"
            logger.error(f"Replicate error: {e}", exc_info=True)

    return result


def generate_with_retry(image_urls: list, prompt: str, max_retries: int = 3, **kwargs) -> dict:
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

        last_result = generate_images(image_urls=image_urls, prompt=prompt, **kwargs)

        if last_result["success"]:
            return last_result

    return last_result


def download_generated_image(url: str, save_dir: str = None) -> str:
    """
    Downloads generated image and saves locally (for legacy support).
    """
    if save_dir is None:
        save_dir = Config.OUTPUTS_FOLDER

    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()

        ext = 'jpg' if 'jpeg' in response.headers.get('content-type', '') else 'png'
        filename = f"gpt_image_{int(time.time())}_{random.randint(1000, 9999)}.{ext}"
        filepath = str(Path(save_dir) / filename)

        with open(filepath, 'wb') as f:
            f.write(response.content)

        return filepath
    except Exception as e:
        logger.error(f"Download failed: {e}")
        return None