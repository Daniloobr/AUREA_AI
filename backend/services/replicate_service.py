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
    image_urls: list,      # lista com 3 URLs das fotos de referência
    prompt: str,
    resolution: str = "2K",
    aspect_ratio: str = "16:9",
    output_format: str = "jpg",
    safety_filter_level: str = "block_only_high",
    **kwargs
) -> dict:
    """
    Calls Replicate API to generate images using google/nano-banana-pro.
    
    Args:
        image_urls: List of 3 reference image URLs
        prompt: Full generation prompt
        resolution: Resolution ("2K", etc)
        aspect_ratio: Aspect ratio ("1:1", "16:9", "9:16", etc)
        output_format: Image format ("jpg", "png")
        safety_filter_level: Safety filter level
    
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
        import os
        token = os.environ.get('REPLICATE_API_TOKEN', '').strip()
        
        # Limpa caso o usuário tenha copiado 'REPLICATE_API_TOKEN=r8_...' no valor
        if token.startswith('REPLICATE_API_TOKEN='):
            token = token.replace('REPLICATE_API_TOKEN=', '').strip()
            
        if not token or 'YOUR_' in token:
            raise ValueError("Replicate API token is missing.")

        # Garante que a env var também está limpa (sem \n)
        os.environ['REPLICATE_API_TOKEN'] = token

        logger.info(f"Starting Nano Banana Pro Generation...")
        logger.info(f"  prompt: {prompt[:80]}...")
        logger.info(f"  image_urls: {image_urls}")

        start_time = time.time()

        # Build input
        replicate_input = {
            "prompt": prompt,
            "resolution": resolution,
            "image_input": image_urls,
            "aspect_ratio": aspect_ratio,
            "output_format": output_format,
            "safety_filter_level": safety_filter_level
        }

        client = replicate.Client(api_token=token)
        output = client.run(
            Config.REPLICATE_MODEL_SLUG,
            input=replicate_input
        )

        elapsed = round(time.time() - start_time, 2)
        result["generation_time"] = elapsed

        # Process output
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
            logger.info(f"Nano Banana Pro Complete: {len(images)} images in {elapsed}s")
            
            # Atualiza o job no banco de dados se job_id foi fornecido
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
                        logger.info(f"[Replicate Service] Job {job_id} atualizado com status='completed' e result_url='{images[0]}'")
                    else:
                        logger.warning(f"[Replicate Service] Job {job_id} não encontrado no banco.")
                except Exception as db_err:
                    logger.error(f"[Replicate Service] Erro ao atualizar job {job_id} no banco: {db_err}")
        else:
            result["error"] = "Replicate returned empty output"
            logger.error("No images returned from Nano Banana Pro")

    except Exception as e:
        error_str = str(e)
        if '429' in error_str or 'throttled' in error_str.lower() or 'rate limit' in error_str.lower():
            result["error"] = "RATE_LIMITED"
            logger.warning("Rate limit hit in Nano Banana Pro")
        else:
            result["error"] = f"Nano Banana Pro error: {error_str}"
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
