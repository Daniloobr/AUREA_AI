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
    Stripe webhook handler para créditos pós-pagamento.

    Correções aplicadas:
    - payload como bytes (request.get_data()) para validação correta de assinatura
    - User.query.filter_by() para compatibilidade com UUID string e SQLAlchemy 2.x
    - Idempotência via external_id para evitar créditos duplicados em retentativas
    - Log de diagnóstico detalhado com prefixo [WEBHOOK]
    """
    # CRÍTICO: bytes raw — não decodificar como texto, ou a assinatura Stripe falha
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')

    logger.info(f"[WEBHOOK] Recebido. Sig presente: {bool(sig_header)}, Secret configurado: {bool(webhook_secret)}")

    if not sig_header:
        logger.error("[WEBHOOK] Assinatura do Stripe ausente no cabeçalho")
        return jsonify({'error': 'Assinatura Stripe ausente'}), 400

    if not webhook_secret:
        logger.error("[WEBHOOK] STRIPE_WEBHOOK_SECRET não configurado no ambiente Render!")
        return jsonify({'error': 'Webhook secret não configurado'}), 500

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        logger.error(f"[WEBHOOK] Payload inválido: {e}")
        return jsonify({'error': 'Payload inválido'}), 400
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"[WEBHOOK] Assinatura inválida: {e}")
        return jsonify({'error': 'Assinatura inválida'}), 400
    except Exception as e:
        logger.error(f"[WEBHOOK] Erro inesperado na verificação: {e}", exc_info=True)
        return jsonify({'error': 'Erro interno ao processar webhook'}), 400

    logger.info(f"[WEBHOOK] Evento verificado: {event['type']}")

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        # Converte para dict padrão para compatibilidade com todas as versões do SDK
        session_dict = session.to_dict() if hasattr(session, 'to_dict') else dict(session)

        user_id = session_dict.get('client_reference_id')
        metadata = session_dict.get('metadata') or {}
        price_id = metadata.get('price_id')
        session_stripe_id = session_dict.get('id')

        logger.info(
            f"[WEBHOOK] checkout.session.completed — "
            f"UserID={user_id}, PriceID={price_id}, SessionID={session_stripe_id}"
        )

        # ── Idempotência: evitar créditos duplicados em retentativas do Stripe ──
        if session_stripe_id:
            existing = Transaction.query.filter_by(external_id=session_stripe_id).first()
            if existing:
                logger.warning(
                    f"[WEBHOOK] Evento duplicado ignorado. "
                    f"SessionID={session_stripe_id} já foi processado."
                )
                return jsonify({'status': 'already_processed'}), 200

        credits_map = {
            'price_1TXBt5AXb2fn2YJDXDIF0iKk': 100,   # R$25 — Essencial
            'price_1TXBtWAXb2fn2YJDZxm1s4Xz': 200,   # R$50 — Ateliê
            'price_1TXBtrAXb2fn2YJDNsCz53jj': 400,   # R$120 — Maison
        }
        credits = credits_map.get(price_id)

        if not credits:
            logger.error(f"[WEBHOOK] Price ID '{price_id}' não mapeado. Verifique credits_map.")
            return jsonify({'error': 'Price ID não configurado para créditos'}), 400

        if not user_id:
            logger.error("[WEBHOOK] client_reference_id ausente na sessão de checkout")
            return jsonify({'error': 'User ID ausente na sessão'}), 400

        # CORREÇÃO: filter_by é compatível com UUID string e SQLAlchemy 2.x
        # User.query.get() está deprecated no SQLAlchemy 2.x e pode falhar com strings UUID
        user = User.query.filter_by(id=user_id).first()
        if not user:
            logger.error(f"[WEBHOOK] Usuário não encontrado no banco. ID recebido: '{user_id}'")
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
                external_id=session_stripe_id
            )
            db.session.add(tx)
            db.session.commit()
            logger.info(
                f"[WEBHOOK] ✅ Créditos creditados com sucesso! "
                f"user_id={user.id}, +{credits} créditos, novo saldo={user.credits_balance}"
            )
        except Exception as e:
            db.session.rollback()
            logger.error(f"[WEBHOOK] ❌ Erro ao salvar transação no banco: {e}", exc_info=True)
            return jsonify({'error': 'Erro ao processar transação no banco'}), 500

    return jsonify({'status': 'success'}), 200
