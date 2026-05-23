from flask import Blueprint, request, jsonify
from models.db_models import db, User, Transaction
import stripe
import os
import logging

webhook_bp = Blueprint('webhook', __name__)
logger = logging.getLogger(__name__)

# Configura Stripe key
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

@webhook_bp.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    """
    New Stripe webhook handler for handling secure payments and credit topups.
    """
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    if not sig_header:
        logger.error("Assinatura do Stripe ausente no cabeçalho")
        return jsonify({'error': 'Assinatura Stripe ausente'}), 400

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        logger.error(f"Payload inválido para o webhook: {e}")
        return jsonify({'error': 'Payload inválido'}), 400
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Assinatura do webhook Stripe inválida: {e}")
        return jsonify({'error': 'Assinatura inválida'}), 400
    except Exception as e:
        logger.error(f"Erro inesperado na verificação de webhook Stripe: {e}")
        return jsonify({'error': str(e)}), 400

    logger.info(f"Stripe Webhook recebido: Tipo de evento = {event['type']}")

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session.get('client_reference_id')
        metadata = session.get('metadata') or {}
        price_id = metadata.get('price_id')
        
        logger.info(f"Sessão de checkout Stripe concluída. UserID={user_id}, PriceID={price_id}")

        credits_map = {
            'price_1TXBt5AXb2fn2YJDXDIF0iKk': 100,
            'price_1TXBtWAXb2fn2YJDZxm1s4Xz': 200,
            'price_1TXBtrAXb2fn2YJDNsCz53jj': 400,
        }
        credits = credits_map.get(price_id)
        
        if not credits:
            logger.error(f"Price ID '{price_id}' não mapeado para créditos")
            return jsonify({'error': 'Price ID não configurado para créditos'}), 400

        if not user_id:
            logger.error("User ID ausente na sessão de checkout (client_reference_id)")
            return jsonify({'error': 'User ID ausente na sessão'}), 400

        user = User.query.get(user_id)
        if not user:
            logger.error(f"Usuário com ID {user_id} não encontrado no banco")
            return jsonify({'error': 'Usuário não encontrado'}), 404

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
                external_id=session.get('id')
            )
            db.session.add(tx)
            db.session.commit()
            logger.info(f"Créditos Stripe creditados com sucesso. Usuário: {user.id}, Créditos: +{credits}, Novo saldo: {user.credits_balance}")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao salvar transação no banco de dados: {e}")
            return jsonify({'error': 'Erro ao processar transação no banco'}), 500
            
    return jsonify({'status': 'success'}), 200
