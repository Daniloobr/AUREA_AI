from flask import Blueprint, request, jsonify, os
from models.db_models import db, User, Transaction
from services.stripe_service import stripe_service
from utils.auth_utils import token_required

checkout_bp = Blueprint('checkout', __name__)

# Mapeamento de precos do Stripe para créditos
# Atualize essas chaves com os price_ids reais do Stripe Dashboard
STRIPE_PRICES = {
    "price_100_credits": 100,
    "price_250_credits": 250,
    "price_500_credits": 500
}

@checkout_bp.route('/create-checkout-session', methods=['POST'])
@token_required
def create_session(current_user):
    data = request.get_json()
    price_id = data.get('price_id')
    
    if not price_id or price_id not in STRIPE_PRICES:
        return jsonify({"error": "Pacote inválido ou não informado"}), 400
    
    frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
    success_url = f"{frontend_url}/credits?success=true"
    cancel_url = f"{frontend_url}/credits?canceled=true"

    try:
        session_data = stripe_service.create_checkout_session(
            price_id=price_id,
            user_id=current_user.id,
            user_email=current_user.email,
            success_url=success_url,
            cancel_url=cancel_url
        )
        
        if not session_data:
            return jsonify({"error": "Falha ao criar sessão de pagamento no Stripe."}), 500
            
        return jsonify(session_data), 200
        
    except Exception as e:
        print(f"ERROR in create_checkout_session: {str(e)}")
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500

@checkout_bp.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')

    if not webhook_secret:
        print("ERROR: STRIPE_WEBHOOK_SECRET is not configured.")
        return jsonify({"error": "Webhook secret not configured"}), 500

    event = stripe_service.handle_webhook(payload, sig_header, webhook_secret)
    
    if event is None:
        return jsonify({"error": "Invalid payload or signature"}), 400

    # Lida com o evento de pagamento concluído
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        user_id = session.get('client_reference_id')
        metadata = session.get('metadata', {})
        price_id = metadata.get('price_id')
        
        if not user_id or not price_id:
            print(f"ERROR: Webhook missing user_id or price_id. Session ID: {session.get('id')}")
            return jsonify({"status": "ignored", "reason": "missing data"}), 200

        credits_to_add = STRIPE_PRICES.get(price_id)
        if not credits_to_add:
            print(f"ERROR: Unknown price_id in webhook: {price_id}")
            return jsonify({"status": "ignored", "reason": "unknown price"}), 200

        user = User.query.get(user_id)
        if user:
            old_balance = user.credits_balance
            user.credits_balance += credits_to_add
            
            # Registra transação
            new_tx = Transaction(
                user_id=user.id,
                type='stripe_purchase',
                amount=credits_to_add,
                balance_before=old_balance,
                balance_after=user.credits_balance,
                description=f"Compra de {credits_to_add} moedas via Stripe",
                status='completed',
                external_id=session.get('id')
            )
            db.session.add(new_tx)
            db.session.commit()
            print(f"SUCCESS: Added {credits_to_add} credits to user {user.email}")
        else:
            print(f"ERROR: User {user_id} not found for Stripe webhook.")

    return jsonify({"status": "success"}), 200
