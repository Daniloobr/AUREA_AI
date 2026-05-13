from flask import Blueprint, request, jsonify
from models.db_models import User, GenerationJob, Transaction
from database import db
from utils.auth_utils import admin_required
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/stats', methods=['GET'])
@admin_required
def get_stats(current_user):
    """Overall system statistics."""
    total_users = User.query.filter_by(is_active=True).count()
    total_jobs = GenerationJob.query.count()
    completed_jobs = GenerationJob.query.filter_by(status='completed').count()
    
    # Jobs in the last 24h
    last_24h = datetime.utcnow() - timedelta(hours=24)
    jobs_24h = GenerationJob.query.filter(GenerationJob.created_at >= last_24h).count()
    
    return jsonify({
        "success": True,
        "stats": {
            "total_users": total_users,
            "total_jobs": total_jobs,
            "completed_jobs": completed_jobs,
            "jobs_24h": jobs_24h
        }
    })

@admin_bp.route('/users', methods=['GET'])
@admin_required
def list_users(current_user):
    """List all users with their credit balance."""
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify({
        "success": True,
        "users": [u.to_dict() for u in users]
    })

@admin_bp.route('/jobs', methods=['GET'])
@admin_required
def list_jobs(current_user):
    """Monitor real-time generation queue."""
    jobs = GenerationJob.query.order_by(GenerationJob.created_at.desc()).limit(50).all()
    return jsonify({
        "success": True,
        "jobs": [{
            "id": j.id,
            "user_email": User.query.get(j.user_id).email if User.query.get(j.user_id) else "Unknown",
            "status": j.status,
            "progress": j.progress,
            "tipo_ensaio": j.tipo_ensaio,
            "created_at": j.created_at.isoformat()
        } for j in jobs]
    })

@admin_bp.route('/users/<user_id>/credits', methods=['POST'])
@admin_required
def adjust_credits(current_user, user_id):
    """Adjust user credits manually from the admin panel."""
    data = request.json
    amount = data.get('amount', 0)
    reason = data.get('reason', 'Ajuste administrativo')

    target_user = User.query.get(user_id)
    if not target_user:
        return jsonify({"success": False, "error": "Usuário não encontrado"}), 404

    old_balance = target_user.credits_balance
    target_user.credits_balance += amount
    
    txn = Transaction(
        user_id=target_user.id,
        type='admin_credit',
        amount=amount,
        balance_before=old_balance,
        balance_after=target_user.credits_balance,
        description=reason
    )
    db.session.add(txn)
    db.session.commit()
    
    return jsonify({
        "success": True, 
        "new_balance": target_user.credits_balance,
        "message": f"Créditos de {target_user.name} atualizados."
    })

@admin_bp.route('/users/<user_id>', methods=['DELETE'])
@admin_required
def ban_user(current_user, user_id):
    """Deactivate a user account."""
    target_user = User.query.get(user_id)
    if not target_user:
        return jsonify({"success": False, "error": "Usuário não encontrado"}), 404
    
    target_user.is_active = False
    db.session.commit()
    return jsonify({"success": True, "message": "Usuário desativado com sucesso."})
