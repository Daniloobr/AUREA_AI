from flask import Blueprint, request, jsonify, make_response
import os
from models.db_models import User, Transaction
from database import db
from utils.auth_utils import generate_token, token_required
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    if not data: return jsonify({"success": False, "error": "Dados inválidos"}), 400

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({"success": False, "error": "Todos os campos são obrigatórios"}), 400

    # Check if user exists
    user = User.query.filter_by(email=email).first()
    if user: return jsonify({"success": False, "error": "Email já cadastrado"}), 409

    try:
        INITIAL_BONUS = 100
        new_user = User(name=name, email=email, credits_balance=INITIAL_BONUS)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.flush() # Get ID before commit

        # Create bonus transaction
        bonus_txn = Transaction(
            user_id=new_user.id,
            type='bonus_initial',
            amount=INITIAL_BONUS,
            balance_before=0,
            balance_after=INITIAL_BONUS,
            description="Bônus de boas-vindas"
        )
        db.session.add(bonus_txn)
        db.session.commit()

        # Send Welcome Email (Async safe via threading if needed, but for now simple)
        try:
            from services.email_service import email_service
            email_service.send_welcome(new_user.email, new_user.name)
        except Exception as e:
            logger.warning(f"Failed to send welcome email: {e}")

        token = generate_token(new_user.id)
        return jsonify({
            "success": True,
            "message": "Usuário registrado com sucesso",
            "user": new_user.to_dict(),
            "token": token
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro no registro: {str(e)}")
        return jsonify({"success": False, "error": "Erro interno ao criar usuário"}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email, is_active=True).first()

    if user and user.check_password(password):
        token = generate_token(user.id)
        response = make_response(jsonify({
            "success": True,
            "user": user.to_dict(),
            "token": token
        }))
        response.set_cookie('auth_token', token, httponly=True, secure=True, samesite='Lax')
        return response

    return jsonify({"success": False, "error": "Email ou senha incorretos"}), 401

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_me(current_user):
    return jsonify({"success": True, "user": current_user.to_dict()})

@auth_bp.route('/user/balance', methods=['GET'])
@token_required
def get_balance(current_user):
    return jsonify({
        "success": True, 
        "balance": current_user.credits_balance
    })

@auth_bp.route('/user/transactions', methods=['GET'])
@token_required
def get_transactions(current_user):
    txns = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.created_at.desc()).all()
    return jsonify({
        "success": True,
        "transactions": [{
            "id": t.id,
            "type": t.type,
            "amount": t.amount,
            "description": t.description,
            "created_at": t.created_at.isoformat()
        } for t in txns]
    })

@auth_bp.route('/admin/credits', methods=['POST'])
def admin_add_credits():
    # Protection via Env Variable
    admin_secret = os.getenv('ADMIN_SECRET_KEY', 'default_secret_key')
    provided_key = request.headers.get('X-Admin-Key')
    
    if provided_key != admin_secret:
        return jsonify({"success": False, "error": "Não autorizado"}), 403

    data = request.json
    user_id = data.get('user_id')
    amount = data.get('amount', 0)

    user = User.query.get(user_id)
    if not user: return jsonify({"success": False, "error": "Usuário não encontrado"}), 404

    old_balance = user.credits_balance
    user.credits_balance += amount
    
    txn = Transaction(
        user_id=user.id,
        type='admin_credit',
        amount=amount,
        balance_before=old_balance,
        balance_after=user.credits_balance,
        description="Crédito manual via Admin"
    )
    db.session.add(txn)
    db.session.commit()
    
    return jsonify({"success": True, "new_balance": user.credits_balance})

@auth_bp.route('/user/account', methods=['DELETE'])
@token_required
def delete_account(current_user):
    """
    LGPD: Logical deletion and anonymization.
    """
    try:
        current_user.name = "Usuário Excluído"
        current_user.email = f"deleted_{current_user.id}@lumiere.ai"
        current_user.password_hash = "DELETED_" + str(uuid.uuid4())
        current_user.is_active = False
        
        # In a real app, delete physical images from disk/S3 here
        # For now, we mark as inactive to prevent further logins
        
        db.session.commit()
        return jsonify({"success": True, "message": "Conta anonimizada conforme LGPD"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    response = make_response(jsonify({"success": True, "message": "Logout realizado"}))
    response.delete_cookie('auth_token')
    return response
