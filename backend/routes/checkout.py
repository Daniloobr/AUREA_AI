from flask import Blueprint, request, jsonify, os
from models.db_models import db, User, Transaction
from services.stripe_service import stripe_service
from utils.auth_utils import token_required

checkout_bp = Blueprint('checkout', __name__)

# Mapeamento dos pacotes para os IDs reais do Stripe.
# ATENÇÃO: Substitua os valores "price_..." abaixo pelos IDs reais gerados no seu Stripe Dashboard
STRIPE_PRICES = {
    "100_credits": "price_1TXBt5AXb2fn2YJDXDIF0iKk",
    "200_credits": "price_1TXBtWAXb2fn2YJDZxm1s4Xz",
    "400_credits": "price_1TXBtrAXb2fn2YJDNsCz53jj"
}

# Mapeamento de price_id para quantidade de créditos a adicionar
PRICE_TO_CREDITS = {
    "price_1TXBt5AXb2fn2YJDXDIF0iKk": 100,
    "price_1TXBtWAXb2fn2YJDZxm1s4Xz": 200,
    "price_1TXBtrAXb2fn2YJDNsCz53jj": 400,
}

@checkout_bp.route('/create-checkout-session', methods=['POST'])
@token_required
def create_session(current_user):
    data = request.get_json()
    
    # Suporta receber tanto o nome do pacote (ex: "100_credits") quanto o price_id direto
    package_name = data.get('package_id')
    price_id = data.get('price_id')
    
    if package_name and package_name in STRIPE_PRICES:
        price_id = STRIPE_PRICES[package_name]
        
    if not price_id or price_id not in PRICE_TO_CREDITS:
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

        credits_to_add = PRICE_TO_CREDITS.get(price_id)
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
