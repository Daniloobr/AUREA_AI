# backend/routes/webhooks.py
import stripe
import os
from flask import Blueprint, request, jsonify, current_app
from database import db
from models import User, Transaction

webhook_bp = Blueprint('webhook', __name__)

# Inicializa cliente Stripe (para o método parse_event_notification)
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
stripe_client = stripe.StripeClient(api_key=stripe.api_key)

@webhook_bp.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')

    current_app.logger.info(f"[WEBHOOK] Recebido. Sig presente: {bool(sig_header)}, Secret configurado: {bool(webhook_secret)}")

    if not webhook_secret:
        current_app.logger.error("STRIPE_WEBHOOK_SECRET não configurado")
        return jsonify({'error': 'Webhook secret missing'}), 500

    if not sig_header:
        current_app.logger.error("Assinatura Stripe ausente")
        return jsonify({'error': 'Missing signature'}), 400

    try:
        # Método para Event Destinations (thin events)
        event = stripe_client.parse_event_notification(
            payload=payload,
            sig_header=sig_header,
            secret=webhook_secret
        )
    except Exception as e:
        current_app.logger.error(f"Erro ao verificar evento: {e}")
        return jsonify({'error': 'Invalid event'}), 400

    current_app.logger.info(f"Evento verificado: {event.type}")

    if event.type == 'checkout.session.completed':
        session = event.data.object
        user_id = session.client_reference_id
        price_id = session.metadata.get('price_id') if session.metadata else None
        session_id = session.id

        current_app.logger.info(f"UserID={user_id}, PriceID={price_id}, SessionID={session_id}")

        # Idempotência
        existing = Transaction.query.filter_by(external_id=session_id).first()
        if existing:
            current_app.logger.warning(f"Evento duplicado ignorado: {session_id}")
            return jsonify({'status': 'already_processed'}), 200

        # Mapeamento price_id -> créditos (live)
        credits_map = {
            'price_1TXBt5AXb2fn2YJDXDIF0iKk': 100,
            'price_1TXBtWAXb2fn2YJDZxm1s4Xz': 200,
            'price_1TXBtrAXb2fn2YJDNsCz53jj': 400,
        }
        credits = credits_map.get(price_id)
        if not credits:
            current_app.logger.error(f"Price ID '{price_id}' não mapeado")
            return jsonify({'error': 'Price not mapped'}), 400

        if not user_id:
            current_app.logger.error("client_reference_id ausente")
            return jsonify({'error': 'Missing user_id'}), 400

        user = User.query.filter_by(id=user_id).first()
        if not user:
            current_app.logger.error(f"Usuário não encontrado: {user_id}")
            return jsonify({'error': 'User not found'}), 404

        # Atualiza créditos
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
        current_app.logger.info(f"✅ Créditos creditados! user={user.id}, +{credits}, saldo={user.credits_balance}")

    return jsonify({'status': 'success'}), 200