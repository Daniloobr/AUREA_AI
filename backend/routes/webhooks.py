import os

import stripe
from flask import Blueprint, current_app, jsonify, request

from models.db_models import Transaction, User, db

webhook_bp = Blueprint("webhook", __name__)

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")


def _as_plain_dict(obj):
    if obj is None:
        return {}
    if isinstance(obj, dict):
        return obj
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    try:
        return dict(obj)
    except Exception:
        return {}


@webhook_bp.route("/stripe-webhook", methods=["POST"])
def stripe_webhook():
    """
    Webhook Stripe para creditar moedas após pagamento aprovado.

    Pontos críticos:
    - Validar assinatura antes de ler request.json (usar request.get_data()).
    - Idempotência via external_id (evita duplicatas em retentativas do Stripe).
    - Commit/rollback explícito no banco.
    """
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature")
    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")

    current_app.logger.info(
        f"[STRIPE] Evento recebido. Path={request.path}, "
        f"Sig presente: {bool(sig_header)}, "
        f"Secret configurado: {bool(webhook_secret)}"
    )

    if not sig_header:
        current_app.logger.error("[STRIPE][ERRO] Header Stripe-Signature ausente")
        return jsonify({"error": "Missing signature"}), 400

    if not webhook_secret:
        current_app.logger.error("[STRIPE][ERRO] STRIPE_WEBHOOK_SECRET não definido no ambiente")
        return jsonify({"error": "Webhook secret not configured"}), 500

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except ValueError as e:
        current_app.logger.error(f"[STRIPE][ERRO] Payload inválido: {e}")
        return jsonify({"error": "Invalid payload"}), 400
    except stripe.error.SignatureVerificationError as e:
        current_app.logger.error(f"[STRIPE][ERRO] Assinatura inválida: {e}")
        return jsonify({"error": "Invalid signature"}), 400

    event_type = event.get("type")
    current_app.logger.info(f"[STRIPE] Evento verificado: {event_type}")

    if event_type == "checkout.session.completed":
        session = event["data"]["object"]
        session_dict = _as_plain_dict(session)
        metadata = _as_plain_dict(session_dict.get("metadata"))

        session_id = session_dict.get("id")
        user_id = metadata.get("user_id") or session_dict.get("client_reference_id")
        price_id = metadata.get("price_id")
        payment_status = session_dict.get("payment_status")

        current_app.logger.info(
            f"[STRIPE] {event_type} — user_id={user_id}, price_id={price_id}, "
            f"session_id={session_id}, payment_status={payment_status}"
        )

        if session_id and Transaction.query.filter_by(external_id=session_id).first():
            current_app.logger.warning(
                f"[STRIPE] Já processado — session_id={session_id}"
            )
            return jsonify({"status": "already_processed"}), 200

        # Proteção: só creditar quando realmente estiver pago.
        # (Em alguns casos, pode chegar "completed" antes de "paid".)
        if payment_status != "paid":
            current_app.logger.info(
                f"[STRIPE] Ignorado (ainda não pago) — session_id={session_id}, payment_status={payment_status}"
            )
            return jsonify({"status": "ignored_not_paid"}), 200

        if not user_id:
            current_app.logger.error("[STRIPE][ERRO] user_id ausente (metadata.user_id/client_reference_id)")
            return jsonify({"error": "Missing user ID"}), 500

        if not price_id and session_id:
            # Fallback: buscar line_items da sessão para obter o price_id.
            try:
                line_items = stripe.checkout.Session.list_line_items(session_id, limit=1)
                items = _as_plain_dict(line_items).get("data") or []
                first = items[0] if items else None
                if isinstance(first, dict):
                    price = first.get("price") or {}
                    price_id = price.get("id")
                current_app.logger.info(f"[STRIPE] Fallback line_items — price_id={price_id}, session_id={session_id}")
            except Exception as e:
                current_app.logger.error(
                    f"[STRIPE][ERRO] Falha ao recuperar sessão {session_id}: {e}", exc_info=True
                )

        if not price_id:
            current_app.logger.error(f"[STRIPE][ERRO] price_id ausente apÃ³s fallback (session_id={session_id})")
            return jsonify({"error": "Missing price ID"}), 500

        credits_map = {
            "price_1TXBt5AXb2fn2YJDXDIF0iKk": 100,  # R$25 — Essencial
            "price_1TXBtWAXb2fn2YJDZxm1s4Xz": 200,  # R$50 — Ateliê
            "price_1TXBtrAXb2fn2YJDNsCz53jj": 400,  # R$120 — Maison
        }
        credits = credits_map.get(price_id)
        if not credits:
            current_app.logger.error(f"[STRIPE][ERRO] price_id não mapeado: '{price_id}' (session_id={session_id})")
            return jsonify({"error": "Price not mapped"}), 500

        user = User.query.filter_by(id=str(user_id)).first()
        if not user:
            current_app.logger.error(f"[STRIPE][ERRO] Usuário não encontrado: '{user_id}' (session_id={session_id})")
            return jsonify({"error": "User not found"}), 500

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
                f"[STRIPE] Créditos adicionados — user_id={user.id}, +{credits}, "
                f"novo_saldo={user.credits_balance}, session_id={session_id}"
            )
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"[STRIPE][ERRO] Erro ao salvar no banco: {e}", exc_info=True)
            return jsonify({"error": "Database error"}), 500

    return jsonify({"status": "success"}), 200
