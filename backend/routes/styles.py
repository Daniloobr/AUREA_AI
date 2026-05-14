from flask import Blueprint, jsonify
from services.prompt_engine import get_available_styles
import logging

logger = logging.getLogger(__name__)
styles_bp = Blueprint('styles', __name__)

@styles_bp.route('', methods=['GET'], strict_slashes=False)
@styles_bp.route('/', methods=['GET'], strict_slashes=False)
def list_styles():
    """
    GET /api/styles
    
    Returns all available photoshoot style presets based on PRD 1.0.0.
    """
    try:
        styles = get_available_styles()
        return jsonify({"styles": styles}), 200
    except Exception as e:
        logger.error(f"Error fetching styles: {e}")
        return jsonify({"error": "Falha ao carregar estilos"}), 500
