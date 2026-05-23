from flask import Blueprint, request, jsonify
from models.db_models import db, User, Transaction
from services.syncpay_service import syncpay_service
import logging

webhook_bp = Blueprint('webhook', __name__)
logger = logging.getLogger(__name__)

@webhook_bp.route('/webhooks/syncpay', methods=['POST'])
def syncpay_webhook():
    payload = request.get_json()
    logger.info(f"Webhook recebido: {payload}")

    # O identifier pode vir dentro de 'data.id' (ajuste conforme payload real)
    identifier = payload.get('data', {}).get('id')
    if not identifier:
        return jsonify({'status': 'error', 'reason': 'missing identifier'}), 400

    # Consulta os detalhes da transação
    try:
        transaction = syncpay_service.get_transaction(identifier)
        status = transaction['data']['status']
        description = transaction['data']['description']
        amount = transaction['data']['amount']
    except Exception as e:
        logger.error(f"Erro ao consultar transação {identifier}: {e}")
        return jsonify({'status': 'error'}), 500

    if status == 'completed':
        # Extrai user_id do description (formato "user_<uuid>")
        if description and description.startswith('user_'):
            user_id = description[5:]
            user = User.query.get(user_id)
            if user:
                # Mapeia o valor pago para a quantidade de créditos
                if amount == 25.00:
                    credits = 100
                elif amount == 50.00:
                    credits = 200
                elif amount == 120.00:
                    credits = 400
                else:
                    # fallback: 4 créditos por real (25 reais = 100 créditos)
                    credits = int(amount / 25) * 100

                old_balance = user.credits_balance
                user.credits_balance += credits

                transaction_record = Transaction(
                    user_id=user.id,
                    type='purchase',
                    amount=credits,
                    balance_before=old_balance,
                    balance_after=user.credits_balance,
                    description=f"Compra de {credits} créditos via PIX (SyncPay)",
                    external_id=identifier
                )
                db.session.add(transaction_record)
                db.session.commit()
                logger.info(f"Créditos adicionados para usuário {user.id}: +{credits}")
            else:
                logger.error(f"Usuário {user_id} não encontrado")
        else:
            logger.error(f"Description não contém user_id: {description}")

    return jsonify({'status': 'ok'}), 200