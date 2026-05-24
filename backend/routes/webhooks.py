import stripe
import os
from flask import Blueprint, request, jsonify, current_app
from models.db_models import db, User, Transaction

webhook_bp = Blueprint('webhook', __name__)

# ⚠️ Configure sua chave secreta do Stripe (ambiente)
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

# Chave do webhook (hardcoded conforme solicitado)
WEBHOOK_SECRET = "whsec_rNsq1Hprs4ve2K5o0vhFYjsyKBRvDuue"

@webhook_bp.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = WEBHOOK_SECRET

    current_app.logger.info("[WEBHOOK] Recebido. Verificando assinatura...")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        current_app.logger.info(f"✅ Evento verificado: {event['type']}")
    except ValueError as e:
        current_app.logger.error(f"❌ Payload inválido: {e}")
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        current_app.logger.error(f"❌ Assinatura inválida: {e}")
        return jsonify({'error': 'Invalid signature'}), 400

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session.get('client_reference_id')
        price_id = session.get('metadata', {}).get('price_id')
        session_id = session.get('id')

        current_app.logger.info(f"Sessão concluída. UserID={user_id}, PriceID={price_id}, SessionID={session_id}")

        # Idempotência: evita processar o mesmo evento duas vezes
        if Transaction.query.filter_by(external_id=session_id).first():
            current_app.logger.warning(f"Evento duplicado ignorado. SessionID={session_id}")
            return jsonify({'status': 'already_processed'}), 200

        # Mapeamento price_id -> créditos
        credits_map = {
            'price_1TXBt5AXb2fn2YJDXDIF0iKk': 100,
            'price_1TXBtWAXb2fn2YJDZxm1s4Xz': 200,
            'price_1TXBtrAXb2fn2YJDNsCz53jj': 400,
        }
        credits = credits_map.get(price_id)
        if not credits:
            current_app.logger.error(f"Price ID '{price_id}' não mapeado.")
            return jsonify({'error': 'Price not mapped'}), 400

        # Busca o usuário
        user = User.query.filter_by(id=user_id).first()
        if not user:
            current_app.logger.error(f"Usuário não encontrado: {user_id}")
            return jsonify({'error': 'User not found'}), 404

        # Atualiza saldo e cria transação
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

        current_app.logger.info(f"🎉 **CRÉDITO ADICIONADO!** Usuário: {user.id}, +{credits} créditos. Saldo: {user.credits_balance}")

    return jsonify({'status': 'success'}), 200