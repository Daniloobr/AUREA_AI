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
    aspect_ratio: str = None,
    output_format: str = "webp",
    safety_filter_level: str = "block_only_high",
    **kwargs
) -> dict:
    """
    Calls the AI generation API to generate images.

    Args:
        image_urls: List of 3 reference image URLs
        prompt: Full generation prompt
        aspect_ratio: Aspect ratio ("1:1", "3:2", "2:3")
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
        token = os.environ.get('AI_PROVIDER_API_TOKEN', '').strip() or os.environ.get('REPLICATE_API_TOKEN', '').strip()
            
        if not token or 'YOUR_' in token:
            raise ValueError("Token da API de IA não configurado ou inválido.")

        logger.info(f"Starting openai/gpt-image-2 Generation...")
        logger.info(f"  prompt: {prompt[:80]}...")
        logger.info(f"  image_urls: {image_urls}")

        start_time = time.time()

        # Normalize aspect ratio — model only accepts "1:1", "3:2", "2:3"
        VALID_RATIOS = ["1:1", "3:2", "2:3"]
        if not aspect_ratio or aspect_ratio not in VALID_RATIOS:
            fallback = "1:1"
            logger.warning(
                f"Aspect ratio '{aspect_ratio}' inválido ou não informado. "
                f"Usando fallback '{fallback}'."
            )
            aspect_ratio = fallback

        model_input = {
            "prompt": prompt,
            "input_images": image_urls,
            "aspect_ratio": aspect_ratio,
            "quality": "medium",
            "output_format": output_format if output_format in ["webp", "jpg", "png"] else "webp",
            "output_compression": 90,
            "number_of_images": 1
        }

        logger.info(f"  aspect_ratio: {aspect_ratio}")

        client = replicate.Client(api_token=token, timeout=120)
        model_id = os.environ.get("AI_MODEL_ID", "openai/gpt-image-2")
        logger.info(f"Calling Replicate model={model_id} with prompt={prompt[:60] if prompt else 'None'}...")
        output = client.run(model_id, input=model_input)

        elapsed = round(time.time() - start_time, 2)
        result["generation_time"] = elapsed

        # ── Log raw output from Replicate ─────────────────────────────────
        logger.info(f"[RAW_REPLICATE] output type={type(output).__name__}, value={str(output)[:300]}")

        # Process output (list of FileOutput objects)
        images = []
        if output:
            if isinstance(output, list):
                logger.info(f"[RAW_REPLICATE] output is list of len={len(output)}")
                for i, item in enumerate(output):
                    logger.info(f"[RAW_REPLICATE]   item[{i}] type={type(item).__name__}, has_url={hasattr(item, 'url')}, value={str(item)[:200]}")
                    images.append(str(item.url) if hasattr(item, 'url') else str(item))
            elif hasattr(output, 'url'):
                logger.info(f"[RAW_REPLICATE] output is single FileOutput, url={output.url}")
                images.append(str(output.url))
            else:
                logger.info(f"[RAW_REPLICATE] output is scalar, converting to str")
                images.append(str(output))
        else:
            logger.warning(f"[RAW_REPLICATE] output is None/empty")

        if images:
            result["success"] = True
            result["images"] = images
            logger.info(f"Generation Complete: {len(images)} images in {elapsed}s")
        else:
            result["error"] = "O gerador de IA retornou vazio. Tente novamente."
            logger.error("No images returned from AI provider")

    except replicate.exceptions.ReplicateError as e:
        error_str = str(e)
        if '422' in error_str or 'Input validation failed' in error_str or 'must be one of' in error_str:
            result["error"] = "VALIDATION_ERROR"
            result["detail"] = error_str
            logger.error(f"Erro de validação no modelo Replicate: {e}")
        elif '429' in error_str or 'throttled' in error_str.lower() or 'rate limit' in error_str.lower():
            result["error"] = "RATE_LIMITED"
            logger.warning("Rate limit hit in openai/gpt-image-2")
        else:
            result["error"] = f"REPLICATE_ERROR: {error_str[:200]}"
            logger.error(f"Replicate error: {e}", exc_info=True)
    except Exception as e:
        error_str = str(e)
        if '429' in error_str or 'throttled' in error_str.lower() or 'rate limit' in error_str.lower():
            result["error"] = "RATE_LIMITED"
            logger.warning("Rate limit hit in openai/gpt-image-2")
        else:
            result["error"] = "Erro na geração da imagem. Nossa equipe foi notificada."
            logger.error(f"AI generation error: {e}", exc_info=True)

    return result


def generate_with_retry(image_urls: list, prompt: str, max_retries: int = 3, **kwargs) -> dict:
    """
    Wraps generation with retry logic.
    - 422 / VALIDATION_ERROR: não retenta, retorna imediatamente.
    - 429 / RATE_LIMITED: backoff exponencial (2^attempt segundos).
    - Outros erros: retry linear com seed aleatório.
    """
    last_result = None

    for attempt in range(max_retries + 1):
        if attempt > 0:
            err_type = last_result.get("error", "") if last_result else ""
            if err_type == "VALIDATION_ERROR":
                logger.error("Erro de validação — retry cancelado.")
                return last_result
            elif err_type == "RATE_LIMITED":
                wait_time = 2 ** attempt
            else:
                wait_time = min(5 * attempt, 30)
                kwargs["seed"] = random.randint(1, 2147483647)
            logger.warning(f"Retry {attempt}/{max_retries}, waiting {wait_time}s...")
            time.sleep(wait_time)

        last_result = generate_images(image_urls=image_urls, prompt=prompt, **kwargs)

        if last_result["success"]:
            return last_result

        if last_result.get("error") == "VALIDATION_ERROR":
            logger.error("Erro de validação — não será repetido.")
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