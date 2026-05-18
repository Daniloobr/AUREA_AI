"""
Generate Route — Production API
=================================
Handles photo generation requests and job status polling.
"""
from flask import Blueprint, request, jsonify
from services.prompt_engine import get_available_styles
from services.queue_service import queue_generation, get_job_status
from utils.auth_utils import token_required
from limiter_instance import limiter
import logging

logger = logging.getLogger(__name__)

generate_bp = Blueprint('generate', __name__)


@generate_bp.route('', methods=['POST'], strict_slashes=False)
@generate_bp.route('/', methods=['POST'], strict_slashes=False)
@limiter.limit("30 per hour")
@token_required
def generate(current_user):
    """
    POST /api/generate
    """
    data = request.json
    if not data:
        return jsonify({"success": False, "error": "Payload JSON inválido"}), 400

    image_url = data.get('image_url')
    image_urls = data.get('image_urls', [])
    if not image_urls and image_url:
        image_urls = [image_url]
    
    prompt = data.get('prompt')
    tipo_ensaio = data.get('tipo_ensaio') or data.get('style') or "gestante_outdoor"

    # Validation: Need at least a prompt or an image
    if not image_urls and not prompt:
        return jsonify({"success": False, "error": "Ao menos uma imagem de referência ou prompt é necessário."}), 400

    try:
        # Queue the full generation pipeline with user_id
        job_id = queue_generation(current_user.id, image_urls, tipo_ensaio, prompt=prompt)

        return jsonify({
            "success": True,
            "message": "Job criado com sucesso",
            "job_id": job_id,
            "tipo_ensaio": tipo_ensaio,
            "prompt": prompt
        }), 200

    except ValueError as ve:
        return jsonify({"success": False, "error": str(ve)}), 402 # Payment Required
    except Exception as e:
        logger.error(f"Generate endpoint error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@generate_bp.route('/status', methods=['GET'], strict_slashes=False)
@generate_bp.route('/status/<job_id>', methods=['GET'], strict_slashes=False)
@token_required
def check_status(current_user, job_id=None):
    """
    GET /api/generate/status?id=<job_id> or GET /api/generate/status/<job_id>
    """
    if not job_id:
        job_id = request.args.get('id')
        
    if not job_id:
        return jsonify({"success": False, "error": "Parâmetro 'id' é obrigatório"}), 400

    job_data = get_job_status(job_id)
    if not job_data:
        return jsonify({"success": False, "error": "Job não encontrado"}), 404

    # Privacy check
    if job_data.get('user_id') and job_data.get('user_id') != current_user.id:
        return jsonify({"success": False, "error": "Acesso negado"}), 403

    return jsonify(job_data), 200


@generate_bp.route('/<job_id>/result', methods=['GET'], strict_slashes=False)
def check_result(job_id):
    """
    GET /api/generate/<id>/result
    Required architectural endpoint that returns exact format:
    { "success": true, "status": "SUCCEEDED", "images": [...] }
    """
    if not job_id:
        return jsonify({"error": "Parâmetro 'id' é obrigatório"}), 400

    job_data = get_job_status(job_id)
    if not job_data:
        return jsonify({"error": "Job não encontrado"}), 404

    # Map internal statuses to required frontend statuses
    status_map = {
        "completed": "SUCCEEDED",
        "failed": "FAILED",
        "queued": "PENDING",
        "validating": "PROCESSING",
        "generating": "PROCESSING"
    }
    
    current_status = job_data.get("status", "pending")
    mapped_status = status_map.get(current_status, current_status.upper())

    return jsonify({
        "success": mapped_status == "SUCCEEDED",
        "status": mapped_status,
        "images": job_data.get("images", []),
        "result_url": job_data.get("result_url"),
        "progress": job_data.get("progress", 0),
        "message": job_data.get("message", "")
    }), 200



@generate_bp.route('/styles', methods=['GET'], strict_slashes=False)
def list_styles():
    """
    GET /api/generate/styles
    
    Returns all available photoshoot style presets.
    """
    styles = get_available_styles()
    return jsonify({"styles": styles}), 200
