import stripe
import os
from flask import Blueprint, request, jsonify, current_app
from models.db_models import db, User, Transaction

webhook_bp = Blueprint('webhook', __name__)

# Cliente Stripe (obrigatório para parse_event_notification)
stripe_client = stripe.StripeClient(api_key=os.environ.get('STRIPE_SECRET_KEY'))

@webhook_bp.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    # Payload em BYTES (obrigatório)
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')

    current_app.logger.info(f"[WEBHOOK] Recebido. Sig: {bool(sig_header)}, Secret: {bool(webhook_secret)}")

    if not sig_header:
        return jsonify({'error': 'Missing signature'}), 400
    if not webhook_secret:
        return jsonify({'error': 'Webhook secret missing'}), 500

    try:
        # Método correto para Event Destinations
        event = stripe_client.parse_event_notification(
            payload=payload,
            sig_header=sig_header,
            secret=webhook_secret
        )
    except Exception as e:
        current_app.logger.error(f"Erro na verificação: {e}")
        return jsonify({'error': 'Invalid event'}), 400

    current_app.logger.info(f"Evento recebido: {event.type}")

    if event.type == 'checkout.session.completed':
        session = event.data.object
        user_id = session.client_reference_id
        price_id = session.metadata.get('price_id') if session.metadata else None
        session_id = session.id

        current_app.logger.info(f"User: {user_id}, Price: {price_id}, Session: {session_id}")

        # Idempotência
        if Transaction.query.filter_by(external_id=session_id).first():
            current_app.logger.warning("Evento duplicado ignorado")
            return jsonify({'status': 'already_processed'}), 200

        credits_map = {
            'price_1TXBt5AXb2fn2YJDXDIF0iKk': 100,
            'price_1TXBtWAXb2fn2YJDZxm1s4Xz': 200,
            'price_1TXBtrAXb2fn2YJDNsCz53jj': 400,
        }
        credits = credits_map.get(price_id)
        if not credits:
            current_app.logger.error(f"Price não mapeado: {price_id}")
            return jsonify({'error': 'Price not mapped'}), 400

        user = User.query.filter_by(id=user_id).first()
        if not user:
            current_app.logger.error(f"Usuário não encontrado: {user_id}")
            return jsonify({'error': 'User not found'}), 404

        try:
            old_balance = user.credits_balance
            user.credits_balance += credits
            tx = Transaction(
                user_id=user.id,
                type='purchase',
                amount=credits,
                balance_before=old_balance,
                balance_after=user.credits_balance,
                description=f'Compra de {credits} créditos via Stripe',
                external_id=session_id
            )
            db.session.add(tx)
            db.session.commit()
            current_app.logger.info(f"✅ Créditos adicionados! user={user.id}, +{credits}")
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erro no banco: {e}", exc_info=True)
            return jsonify({'error': 'Database error'}), 500

    return jsonify({'status': 'success'}), 200