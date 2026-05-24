import stripe
import os
from flask import Blueprint, request, jsonify, current_app
from models.db_models import db, User, Transaction

webhook_bp = Blueprint('webhook', __name__)

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

@webhook_bp.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    """
    Webhook tradicional do Stripe para créditar moedas após pagamento aprovado.

    Pontos críticos:
    - payload como BYTES (request.get_data()) — obrigatório para validação HMAC
    - STRIPE_WEBHOOK_SECRET lido do ambiente — nunca hardcoded
    - Idempotência via external_id (evita duplicatas em retentativas do Stripe)
    - Rollback explícito em caso de erro no banco
    """
    # ── CRÍTICO: deve ser bytes, não string ──────────────────────────────────
    # Se usar as_text=True, a assinatura HMAC sempre falhará (SignatureVerificationError)
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')

    current_app.logger.info(
        f"[WEBHOOK] Recebido. "
        f"Sig presente: {bool(sig_header)}, "
        f"Secret configurado: {bool(webhook_secret)}"
    )

    if not sig_header:
        current_app.logger.error("[WEBHOOK] Header Stripe-Signature ausente")
        return jsonify({'error': 'Missing signature'}), 400

    if not webhook_secret:
        current_app.logger.error("[WEBHOOK] STRIPE_WEBHOOK_SECRET não definido no Render!")
        return jsonify({'error': 'Webhook secret not configured'}), 500

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except ValueError as e:
        current_app.logger.error(f"[WEBHOOK] Payload inválido: {e}")
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        current_app.logger.error(f"[WEBHOOK] Assinatura inválida: {e}")
        return jsonify({'error': 'Invalid signature'}), 400

    current_app.logger.info(f"[WEBHOOK] Evento verificado: {event['type']}")

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        session_dict = session.to_dict() if hasattr(session, 'to_dict') else dict(session)

        user_id    = session_dict.get('client_reference_id')
        price_id   = (session_dict.get('metadata') or {}).get('price_id')
        session_id = session_dict.get('id')

        current_app.logger.info(
            f"[WEBHOOK] checkout.session.completed — "
            f"UserID={user_id}, PriceID={price_id}, SessionID={session_id}"
        )

        # ── Idempotência: retorna 200 imediatamente se já processado ─────────
        if session_id and Transaction.query.filter_by(external_id=session_id).first():
            current_app.logger.warning(
                f"[WEBHOOK] Duplicata ignorada. SessionID={session_id} já processado."
            )
            return jsonify({'status': 'already_processed'}), 200

        # ── Validações de entrada ─────────────────────────────────────────────
        if not user_id:
            current_app.logger.error("[WEBHOOK] client_reference_id ausente na sessão")
            return jsonify({'error': 'Missing user ID'}), 400

        credits_map = {
            'price_1TXBt5AXb2fn2YJDXDIF0iKk': 100,   # R$25 — Essencial
            'price_1TXBtWAXb2fn2YJDZxm1s4Xz': 200,   # R$50 — Ateliê
            'price_1TXBtrAXb2fn2YJDNsCz53jj': 400,   # R$120 — Maison
        }
        credits = credits_map.get(price_id)
        if not credits:
            current_app.logger.error(f"[WEBHOOK] Price ID '{price_id}' não mapeado.")
            return jsonify({'error': 'Price not mapped'}), 400

        # ── Busca usuário (filter_by: compatível com UUID string + SQLAlchemy 2.x) ──
        user = User.query.filter_by(id=user_id).first()
        if not user:
            current_app.logger.error(f"[WEBHOOK] Usuário não encontrado: '{user_id}'")
            return jsonify({'error': 'User not found'}), 404

        # ── Credita e persiste ────────────────────────────────────────────────
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
                external_id=session_id,
            )
            db.session.add(tx)
            db.session.commit()

            current_app.logger.info(
                f"[WEBHOOK] ✅ Créditos adicionados! "
                f"user_id={user.id}, +{credits} créditos, novo saldo={user.credits_balance}"
            )
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(
                f"[WEBHOOK] ❌ Erro ao salvar no banco: {e}", exc_info=True
            )
            return jsonify({'error': 'Database error'}), 500

    return jsonify({'status': 'success'}), 200