from flask import Blueprint, jsonify, request
from models.db_models import GenerationJob
from database import db

from utils.auth_utils import token_required

gallery_bp = Blueprint('gallery', __name__)

@gallery_bp.route('', methods=['GET'], strict_slashes=False)
@gallery_bp.route('/', methods=['GET'], strict_slashes=False)
@token_required
def get_gallery(current_user):
    """
    Returns the user's generated photo history from the database.
    """
    try:
        # Fetch all jobs for the current user, so they can see pending ones
        jobs = GenerationJob.query.filter_by(
            user_id=current_user.id
        ).order_by(GenerationJob.created_at.desc()).all()
        
        history = [job.to_dict() for job in jobs]
        
        # Flatten images for a simple gallery view if needed, 
        # or keep the job-grouped structure. Let's keep job-grouped for "Ensaios".
        
        return jsonify({
            "gallery": history,
            "count": len(history)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
