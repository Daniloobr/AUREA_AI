import os
import stripe
from flask import Blueprint, request, jsonify, current_app

from models.db_models import db, User, Transaction

webhook_bp = Blueprint("webhook", __name__)

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")


@webhook_bp.route("/stripe-webhook", methods=["POST"])
def stripe_webhook():
    stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature")
    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")

    current_app.logger.info("[STRIPE] Evento recebido")

    # Validação básica
    if not sig_header:
        current_app.logger.error("[STRIPE][ERRO] Missing Stripe-Signature")
        return "", 400

    if not webhook_secret:
        current_app.logger.error("[STRIPE][ERRO] Webhook secret não configurado")
        return "", 500

    # Verificar assinatura
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except Exception as e:
        current_app.logger.error(f"[STRIPE][ERRO] Assinatura inválida: {e}")
        return "", 400

    # Apenas evento necessário
    if event["type"] != "checkout.session.completed":
        return "", 200

    session = event["data"]["object"]

    session_id = session.get("id")
    payment_status = session.get("payment_status")

    metadata = session.get("metadata") or {}

    user_id = metadata.get("user_id") or session.get("client_reference_id")
    price_id = metadata.get("price_id")

    current_app.logger.info(
        f"[STRIPE] user_id={user_id} price_id={price_id} session_id={session_id} payment_status={payment_status}"
    )

    # Idempotência (ANTES de tudo)
    if session_id and Transaction.query.filter_by(external_id=session_id).first():
        current_app.logger.warning("[STRIPE] Já processado")
        return "", 200

    # Só processa se pago
    if payment_status != "paid":
        current_app.logger.info("[STRIPE] Ignorado - não pago")
        return "", 200

    # user_id obrigatório
    if not user_id:
        current_app.logger.error("[STRIPE][ERRO] user_id ausente")
        return "", 500

    # Fallback para price_id
    if not price_id:
        try:
            line_items = stripe.checkout.Session.list_line_items(session_id, limit=1)
            if line_items.data:
                price_id = line_items.data[0].price.id
        except Exception as e:
            current_app.logger.error(f"[STRIPE][ERRO] Falha ao buscar line_items: {e}")
            return "", 500

    if not price_id:
        current_app.logger.error("[STRIPE][ERRO] price_id ausente")
        return "", 500

    # Mapeamento de créditos
        credits_map = {
            "price_1TXBt5AXb2fn2YJDXDIF0iKk": 100,
            "price_1TXBtWAXb2fn2YJDZxm1s4Xz": 200,
            "price_1TXBtrAXb2fn2YJDNsCz53jj": 400,
            # TEST (temporário): um único PriceID usado para todos os pacotes
            "price_1TaSlbAXb2fn2YJD21xOhXPs": 100,
        }

    if price_id not in credits_map:
        current_app.logger.error(f"[STRIPE][ERRO] price_id não mapeado: {price_id}")
        return "", 500

    credits = credits_map[price_id]

    # Buscar usuário corretamente
    try:
        user = User.query.get(int(user_id))
    except Exception:
        user = None

    if not user:
        current_app.logger.error(f"[STRIPE][ERRO] Usuário não encontrado: {user_id}")
        return "", 500

    # Atualizar créditos
    try:
        old_balance = user.credits_balance
        user.credits_balance += credits

        tx = Transaction(
            user_id=user.id,
            type="purchase",
            amount=credits,
            balance_before=old_balance,
            balance_after=user.credits_balance,
            description=f"Compra de {credits} créditos via Stripe",
            external_id=session_id,
        )

        db.session.add(tx)
        db.session.commit()

        current_app.logger.info(
            f"[STRIPE] Créditos adicionados user_id={user.id} +{credits}"
        )

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[STRIPE][ERRO] DB error: {e}")
        return "", 500

    return "", 200
