import os
import uuid
import imghdr
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from config import Config
from services.supabase_service import supabase_service
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
    Returns the Supabase public URL for the uploaded file.
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

    filepath = None
    try:
        # Generate unique filename
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4()}.{ext}"
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)

        # Save file temporarily for validation
        file.save(filepath)

        # Validate actual file content (not just extension)
        actual_type = imghdr.what(filepath)
        if actual_type not in ['jpeg', 'png', 'webp']:
            if os.path.exists(filepath): os.remove(filepath)
            return jsonify({
                "error": "O conteúdo do arquivo não é uma imagem válida"
            }), 400

        # Check file size
        file_size = os.path.getsize(filepath)
        if file_size > Config.MAX_CONTENT_LENGTH:
            if os.path.exists(filepath): os.remove(filepath)
            return jsonify({
                "error": f"Arquivo muito grande. Máximo: {Config.MAX_CONTENT_LENGTH // (1024*1024)}MB"
            }), 400

        # Upload to Supabase
        cloud_url = supabase_service.upload_image(filepath, filename, bucket="inputs")
        
        if not cloud_url:
            raise Exception("Falha ao subir imagem para o armazenamento em nuvem.")

        # Cleanup local file
        if os.path.exists(filepath):
            os.remove(filepath)

        logger.info(f"Upload to Supabase successful: {filename} ({file_size // 1024}KB)")

        return jsonify({
            "message": "Upload realizado com sucesso",
            "filename": filename,
            "url": cloud_url,
            "file_url": cloud_url, # Para compatibilidade com o frontend
            "size_kb": file_size // 1024,
            "type": actual_type,
        }), 200

    except Exception as e:
        logger.error(f"Upload error: {e}")
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({"error": f"Erro no upload: {str(e)}"}), 500
