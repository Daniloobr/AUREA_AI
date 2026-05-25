import os
import hashlib
import hmac
import json as _json
import logging

from flask import Blueprint, request, jsonify, current_app
from models.db_models import db, User, Transaction

webhook_bp = Blueprint("webhook", __name__)
logger = logging.getLogger(__name__)

PACKAGES_BY_TITLE = {
    "100 Créditos AureaIA": 100,
    "200 Créditos AureaIA": 200,
    "400 Créditos AureaIA": 400,
}


def _verify_signature(payload, x_signature, x_request_id):
    webhook_secret = os.environ.get("MERCADOPAGO_WEBHOOK_SECRET")
    if not webhook_secret:
        logger.warning("MERCADOPAGO_WEBHOOK_SECRET não configurado — pulando verificação")
        return True
    if not x_signature or not x_request_id:
        logger.warning("Headers de assinatura ausentes")
        return False
    parts = {}
    for part in x_signature.split(","):
        if "=" in part:
            key, value = part.split("=", 1)
            parts[key.strip()] = value.strip()
    ts = parts.get("ts")
    hash_value = parts.get("v1")
    if not ts or not hash_value:
        logger.warning("Formato de assinatura inválido")
        return False
    manifest = (
        f"id:{x_request_id};request-id:{x_request_id};ts:{ts};"
        + _json.dumps(payload, separators=(",", ":"))
    )
    expected = hmac.new(
        webhook_secret.encode(),
        manifest.encode(),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(expected, hash_value):
        logger.warning("Assinatura do webhook MP inválida")
        return False
    return True


@webhook_bp.route("/webhooks/mercadopago", methods=["POST"])
def mercadopago_webhook():
    payload = request.get_json(silent=True) or {}
    x_signature = request.headers.get("x-signature", "")
    x_request_id = request.headers.get("x-request-id", "")

    current_app.logger.info(
        f"[WEBHOOK MP] Recebido | type={payload.get('type')} | "
        f"action={payload.get('action')}"
    )

    if not _verify_signature(payload, x_signature, x_request_id):
        return jsonify({"error": "Assinatura inválida"}), 400

    action = payload.get("action")
    if action not in ("payment.created", "payment.updated"):
        return jsonify({"status": "ignored"}), 200

    data = payload.get("data", {})
    payment_id = data.get("id")

    if not payment_id:
        return jsonify({"status": "ignored", "reason": "no_payment_id"}), 200

    if action == "payment.created":
        return jsonify({"status": "received"}), 200

    from services.mercadopago_service import get_payment_info
    payment_info = get_payment_info(payment_id)

    current_app.logger.info(
        f"[WEBHOOK MP] Payment info | id={payment_id} | "
        f"status={payment_info.get('status')} | "
        f"status_detail={payment_info.get('status_detail')}"
    )

    if payment_info.get("status") != "approved":
        return jsonify({"status": "ignored", "reason": "not_approved"}), 200

    external_reference = payment_info.get("external_reference") or ""
    payer_email = payment_info.get("payer", {}).get("email", "")
    items = payment_info.get("additional_info", {}).get("items", [])
    title = items[0].get("title") if items else ""
    credits = PACKAGES_BY_TITLE.get(title, 0)

    if not credits:
        current_app.logger.error(f"[WEBHOOK MP] Título não mapeado: {title}")
        return jsonify({"status": "ignored", "reason": "title_not_mapped"}), 200

    tx_id_str = f"mp_{payment_id}"

    existing = Transaction.query.filter_by(external_id=tx_id_str).first()
    if existing:
        current_app.logger.warning(f"[WEBHOOK MP] Duplicado: {tx_id_str}")
        return jsonify({"status": "already_processed"}), 200

    user = User.query.filter_by(email=payer_email).first()
    if not user:
        current_app.logger.error(
            f"[WEBHOOK MP] Usuário não encontrado: {payer_email}"
        )
        return jsonify({"status": "ignored", "reason": "user_not_found"}), 200

    try:
        old_balance = user.credits_balance or 0
        user.credits_balance = old_balance + credits
        tx = Transaction(
            user_id=user.id,
            type="purchase",
            amount=credits,
            balance_before=old_balance,
            balance_after=user.credits_balance,
            description=f"Compra de {credits} créditos via Mercado Pago",
            external_id=tx_id_str,
        )
        db.session.add(tx)
        db.session.commit()
        current_app.logger.info(
            f"[WEBHOOK MP] +{credits} créditos para {user.id} "
            f"(agora {user.credits_balance})"
        )
        return jsonify({"status": "success", "added_credits": credits}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(
            f"[WEBHOOK MP] Erro DB: {e}", exc_info=True
        )
        return jsonify({"error": "Erro interno ao processar pagamento"}), 500
