"""
Upload Route — Production Grade
==================================
Handles file uploads with comprehensive validation:
- MIME type checking
- File size limits
- Extension whitelist
- Unique filename generation
"""
import os
import uuid
import imghdr
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from config import Config
import logging

logger = logging.getLogger(__name__)

upload_bp = Blueprint('upload', __name__)


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


@upload_bp.route('', methods=['POST'], strict_slashes=False)
@upload_bp.route('/', methods=['POST'], strict_slashes=False)
def upload_file():
    """
    POST /api/upload
    
    Accepts multipart/form-data with 'file' field.
    Validates file type, size, and content.
    Returns the relative URL for the uploaded file.
    """
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Nenhum arquivo selecionado"}), 400

    if not file or not allowed_file(file.filename):
        return jsonify({
            "error": "Tipo de arquivo não permitido. Use: PNG, JPG, JPEG ou WEBP"
        }), 400

    try:
        # Generate unique filename
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4()}.{ext}"
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)

        # Save file
        file.save(filepath)

        # Validate actual file content (not just extension)
        actual_type = imghdr.what(filepath)
        if actual_type not in ['jpeg', 'png', 'webp']:
            os.remove(filepath)
            return jsonify({
                "error": "O conteúdo do arquivo não é uma imagem válida"
            }), 400

        # Check file size
        file_size = os.path.getsize(filepath)
        if file_size > Config.MAX_CONTENT_LENGTH:
            os.remove(filepath)
            return jsonify({
                "error": f"Arquivo muito grande. Máximo: {Config.MAX_CONTENT_LENGTH // (1024*1024)}MB"
            }), 400

        # Return relative URL
        image_url = f"/uploads/{filename}"

        logger.info(f"Upload successful: {filename} ({file_size // 1024}KB, type={actual_type})")

        return jsonify({
            "message": "Upload realizado com sucesso",
            "filename": filename,
            "url": image_url,
            "file_url": image_url, # Para compatibilidade com o novo frontend
            "size_kb": file_size // 1024,
            "type": actual_type,
        }), 200

    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({"error": f"Erro no upload: {str(e)}"}), 500
