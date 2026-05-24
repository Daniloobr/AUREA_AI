from flask import Blueprint, request, jsonify, make_response, current_app
import os
import uuid  # ← adicionado (faltava no original)
from models.db_models import User, Transaction
from database import db
from utils.auth_utils import generate_token, token_required
from limiter_instance import limiter
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
@limiter.limit("20 per hour")
def register():
    data = request.json
    if not data: return jsonify({"success": False, "error": "Dados inválidos"}), 400

    name = data.get('name')
    raw_email = data.get('email')
    password = data.get('password')

    if not name or not raw_email or not password:
        return jsonify({"success": False, "error": "Todos os campos são obrigatórios"}), 400

    email = raw_email.lower().strip()

    logger.info(f"Tentativa de registro: {email}")

    # Check if user exists
    user = User.query.filter_by(email=email).first()
    if user: 
        logger.warning(f"Tentativa de registro com email já existente: {email}")
        return jsonify({"success": False, "error": "Email já cadastrado"}), 409

    try:
        new_user = User(name=name, email=email, credits_balance=0)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        # Send Welcome Email (Async to prevent timeout)
        import threading
        def send_async_email(email, name):
            try:
                from services.email_service import email_service
                email_service.send_welcome(email, name)
            except Exception as e:
                logger.warning(f"Failed to send welcome email: {e}")

        threading.Thread(target=send_async_email, args=(new_user.email, new_user.name), daemon=True).start()

        token = generate_token(new_user.id)
        return jsonify({
            "success": True,
            "message": "Usuário registrado com sucesso",
            "user": new_user.to_dict(),
            "token": token
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"CRITICAL: Erro no registro de {email}: {str(e)}", exc_info=True)
        return jsonify({
            "success": False, 
            "error": f"Erro interno no servidor: {str(e)[:50]}" 
        }), 500

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    data = request.json
    email = data.get('email', '').lower().strip()
    password = data.get('password')

    user = User.query.filter_by(email=email, is_active=True).first()

    if user and user.check_password(password):
        token = generate_token(user.id)
        response = make_response(jsonify({
            "success": True,
            "user": user.to_dict(),
            "token": token
        }))
        response.set_cookie('auth_token', token, httponly=True, secure=True, samesite='None')
        return response

    return jsonify({"success": False, "error": "Email ou senha incorretos"}), 401

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_me(current_user):
    response = make_response(jsonify({"success": True, "user": current_user.to_dict()}))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@auth_bp.route('/user/balance', methods=['GET'])
@token_required
def get_balance(current_user):
    return jsonify({
        "success": True, 
        "balance": current_user.credits_balance
    })

# ==================== EXTRATO DE TRANSAÇÕES ====================
@auth_bp.route('/user/transactions', methods=['GET'])
@token_required
def get_transactions(current_user):
    """
    Retorna todas as transações (extrato) do usuário autenticado.
    """
    txns = Transaction.query.filter_by(user_id=current_user.id)\
                            .order_by(Transaction.created_at.desc()).all()
    return jsonify({
        "success": True,
        "transactions": [{
            "id": t.id,
            "type": t.type,
            "amount": t.amount,
            "balance_before": t.balance_before,
            "balance_after": t.balance_after,
            "description": t.description,
            "created_at": t.created_at.isoformat() if t.created_at else None
        } for t in txns]
    })

@auth_bp.route('/admin/credits', methods=['POST'])
def admin_add_credits():
    # Protection via Env Variable
    admin_secret = current_app.config.get('ADMIN_SECRET_KEY')
    provided_key = request.headers.get('X-Admin-Key')
    
    if not admin_secret or provided_key != admin_secret:
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
        current_user.email = f"deleted_{current_user.id}@aureaia.com"
        current_user.password_hash = "DELETED_" + str(uuid.uuid4())
        current_user.is_active = False
        
        # In a real app, delete physical images from disk/S3 here
        # For now, we mark as inactive to prevent further logins
        
        db.session.commit()
        return jsonify({"success": True, "message": "Conta anonimizada conforme LGPD"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@auth_bp.route('/google-login', methods=['POST'])
@limiter.limit("20 per hour")
def google_login():
    data = request.json
    access_token = data.get('access_token') or data.get('id_token')

    if not access_token:
        return jsonify({"success": False, "error": "Token de acesso é obrigatório"}), 400

    try:
        from services.supabase_service import supabase_service
        if not supabase_service.client:
            return jsonify({"success": False, "error": "Serviço de autenticação indisponível"}), 500

        # Validate token and get user from Supabase
        user_response = supabase_service.client.auth.get_user(access_token)
        if not user_response or not user_response.user:
            return jsonify({"success": False, "error": "Token inválido ou expirado"}), 401
            
        supabase_user = user_response.user
        email = supabase_user.email.lower().strip() if supabase_user.email else None
        
        # Try to extract name from user_metadata
        metadata = supabase_user.user_metadata or {}
        name = metadata.get('name') or metadata.get('full_name') or (email.split('@')[0] if email else 'User')
        
    except Exception as e:
        logger.error(f"Erro ao validar token do Supabase: {e}")
        return jsonify({"success": False, "error": "Falha na validação do token"}), 401

    if not email:
        return jsonify({"success": False, "error": "Email não fornecido pelo provedor"}), 400

    user = User.query.filter_by(email=email).first()
    
    is_new_user = False
    if not user:
        # Create new user for Google login
        is_new_user = True
        user = User(
            name=name,
            email=email,
            credits_balance=0,
            is_active=True
        )
        # Dummy password for OAuth users
        user.set_password(os.urandom(24).hex())
        db.session.add(user)

        try:
            from services.email_service import email_service
            email_service.send_welcome(user.email, user.name)
        except: pass

    db.session.commit()

    token = generate_token(user.id)
    response = make_response(jsonify({
        "success": True,
        "user": user.to_dict(),
        "token": token,
        "is_new_user": is_new_user
    }))
    # Manter compatibilidade com JWT atual (set cookie)
    response.set_cookie('auth_token', token, httponly=True, secure=True, samesite='None')
    return response

@auth_bp.route('/forgot-password', methods=['POST'])
@limiter.limit("3 per hour")
def forgot_password():
    data = request.json
    email = data.get('email', '').lower().strip()
    
    user = User.query.filter_by(email=email, is_active=True).first()
    if not user:
        # We return success anyway for security (don't leak if email exists)
        return jsonify({"success": True, "message": "Se o e-mail existir, você receberá um link de recuperação."})

    import secrets
    from datetime import datetime, timedelta
    from models.db_models import PasswordResetToken
    from services.email_service import email_service

    # Generate token
    token = secrets.token_urlsafe(32)
    expires = datetime.utcnow() + timedelta(hours=1)
    
    reset_token = PasswordResetToken(user_id=user.id, token=token, expires_at=expires)
    db.session.add(reset_token)
    db.session.commit()

    # Send Email
    frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:3000')
    reset_link = f"{frontend_url}/reset-password?token={token}"
    email_service.send_password_reset(user.email, reset_link)

    return jsonify({"success": True, "message": "E-mail de recuperação enviado."})

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.json
    token = data.get('token')
    new_password = data.get('password')

    if not token or not new_password:
        return jsonify({"success": False, "error": "Token e nova senha são obrigatórios"}), 400

    from models.db_models import PasswordResetToken
    reset_record = PasswordResetToken.query.filter_by(token=token, used=False).first()

    if not reset_record or reset_record.expires_at < datetime.utcnow():
        return jsonify({"success": False, "error": "Token inválido ou expirado"}), 400

    user = User.query.get(reset_record.user_id)
    if not user:
        return jsonify({"success": False, "error": "Usuário não encontrado"}), 404

    # Change password
    user.set_password(new_password)
    reset_record.used = True
    db.session.commit()

    return jsonify({"success": True, "message": "Senha alterada com sucesso!"})

@auth_bp.route('/logout', methods=['POST'])
def logout():
    response = make_response(jsonify({"success": True, "message": "Logout realizado"}))
    response.delete_cookie('auth_token')
    return response