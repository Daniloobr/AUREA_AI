"""
AI Image Generator Service
==========================
Handles communication with the AI image generation provider.
Supports 3 reference images and produces ultra-realistic maternity photos.

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
    image_urls: list,
    prompt: str,
    resolution: str = "2K",
    aspect_ratio: str = "16:9",
    output_format: str = "webp",
    safety_filter_level: str = "block_only_high",
    **kwargs
) -> dict:
    """
    Calls the AI generation API to generate images.

    Args:
        image_urls: List of 3 reference image URLs
        prompt: Full generation prompt
        aspect_ratio: Aspect ratio ("1:1", "3:2", "2:3", "16:9", "9:16")
        output_format: Image format ("webp", "jpg", "png")

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
        token = os.environ.get('AI_PROVIDER_API_TOKEN', '').strip()
            
        if not token or 'YOUR_' in token or token.startswith('r8_'):
            raise ValueError("AI Provider API token is missing or invalid.")

        logger.info(f"Starting openai/gpt-image-2 Generation...")
        logger.info(f"  prompt: {prompt[:80]}...")
        logger.info(f"  image_urls: {image_urls}")

        start_time = time.time()

        # Normalize aspect ratio to accepted values (FIXED: added 16:9 and 9:16)
        valid_ratios = ["1:1", "3:2", "2:3", "16:9", "9:16"]
        if aspect_ratio not in valid_ratios:
            logger.warning(f"Aspect ratio '{aspect_ratio}' not supported, using '2:3' (vertical portrait)")
            aspect_ratio = "2:3"

        model_input = {
            "prompt": prompt,
            "input_images": image_urls,
            "aspect_ratio": aspect_ratio,
            "quality": "medium",
            "background": "auto",
            "moderation": "auto",
            "output_format": output_format if output_format in ["webp", "jpg", "png"] else "webp",
            "output_compression": 90,
            "number_of_images": 1
        }

        client = replicate.Client(api_token=token)
        model_id = os.environ.get("AI_MODEL_ID", "openai/gpt-image-2")
        output = client.run(model_id, input=model_input)

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
            logger.info(f"Generation Complete: {len(images)} images in {elapsed}s")
            
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
                        logger.info(f"[AI Generator] Job {job_id} updated to 'completed' with result_url='{images[0]}'")
                    else:
                        logger.warning(f"[AI Generator] Job {job_id} not found in database.")
                except Exception as db_err:
                    logger.error(f"[AI Generator] Error updating job {job_id}: {db_err}")
        else:
            result["error"] = "AI provider returned empty output"
            logger.error("No images returned from AI provider")

    except Exception as e:
        error_str = str(e)
        if '429' in error_str or 'throttled' in error_str.lower() or 'rate limit' in error_str.lower():
            result["error"] = "RATE_LIMITED"
            logger.warning("Rate limit hit in openai/gpt-image-2")
        else:
            result["error"] = f"AI generation error: {error_str}"
            logger.error(f"AI generation error: {e}", exc_info=True)

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