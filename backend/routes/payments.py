from flask import Blueprint, request, jsonify
from utils.auth_utils import token_required
from services.stripe_service import create_checkout_session
import os
import logging

payments_bp = Blueprint('payments', __name__)
logger = logging.getLogger(__name__)

# Permitted Stripe Price IDs mapping to credits
ALLOWED_PRICES = {
    'price_1TXBt5AXb2fn2YJDXDIF0iKk',  # 100 credits
    'price_1TXBtWAXb2fn2YJDZxm1s4Xz',  # 200 credits
    'price_1TXBtrAXb2fn2YJDNsCz53jj'   # 400 credits
}

@payments_bp.route('/create-checkout-session', methods=['POST'])
@token_required
def create_session(current_user):
    """
    Creates a Stripe Checkout Session for the current authenticated user.
    """
    try:
        data = request.get_json() or {}
        price_id = data.get('price_id')
        
        if not price_id:
            return jsonify({'success': False, 'error': 'price_id é obrigatório'}), 400
            
        if price_id not in ALLOWED_PRICES:
            return jsonify({'success': False, 'error': 'price_id inválido'}), 400
            
        success_url = os.environ.get('STRIPE_SUCCESS_URL', 'https://aureaia-saas.vercel.app/credits?success=true')
        cancel_url = os.environ.get('STRIPE_CANCEL_URL', 'https://aureaia-saas.vercel.app/credits?canceled=true')
        
        session_data = create_checkout_session(
            price_id=price_id,
            user_id=current_user.id,
            user_email=current_user.email,
            success_url=success_url,
            cancel_url=cancel_url
        )
        
        return jsonify({'success': True, 'url': session_data['url']}), 200
    except Exception as e:
        logger.error(f"Erro ao criar sessão Stripe Checkout: {str(e)}")
        return jsonify({'success': False, 'error': 'Não foi possível iniciar o checkout'}), 500
