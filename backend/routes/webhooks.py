import os
import hashlib
import hmac
import json as _json
import logging

from flask import Blueprint, request, jsonify, current_app
from models.db_models import db, User, Transaction

webhook_bp = Blueprint("webhook", __name__)
logger = logging.getLogger(__name__)

PACKAGES_BY_ID = {
    "100_credits": 100,
    "200_credits": 200,
    "400_credits": 400,
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


def _process_payment(payment_info):
    payment_id = payment_info.get("id")
    status = payment_info.get("status")
    external_ref = payment_info.get("external_reference") or ""
    payer_email = payment_info.get("payer", {}).get("email", "")

    current_app.logger.info(
        f"[WEBHOOK MP] Processando | id={payment_id} | status={status} | "
        f"ref={external_ref} | email={payer_email}"
    )

    if status != "approved":
        current_app.logger.info(f"[WEBHOOK MP] Status não aprovado: {status}")
        return False

    user_id = None
    credits = None

    if ":" in external_ref:
        parts = external_ref.split(":", 1)
        user_id = parts[0]
        package_id = parts[1]
        credits = PACKAGES_BY_ID.get(package_id)
        if credits:
            current_app.logger.info(
                f"[WEBHOOK MP] Parsed ref: user={user_id}, pkg={package_id}, credits={credits}"
            )

    if not user_id or not credits:
        current_app.logger.error(
            f"[WEBHOOK MP] external_reference inválida ou não mapeada: {external_ref}"
        )
        return False

    tx_id_str = f"mp_{payment_id}"

    existing = Transaction.query.filter_by(external_id=tx_id_str).first()
    if existing:
        current_app.logger.warning(f"[WEBHOOK MP] Duplicado: {tx_id_str}")
        return True

    user = User.query.get(user_id)
    if not user:
        current_app.logger.error(
            f"[WEBHOOK MP] Usuário não encontrado: {user_id}"
        )
        return False

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
        return True
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(
            f"[WEBHOOK MP] Erro DB: {e}", exc_info=True
        )
        return False


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
        current_app.logger.warning("[WEBHOOK MP] Assinatura inválida")
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

    from services.mercadopago_service import get_payment_status
    payment_info = get_payment_status(payment_id)

    ok = _process_payment(payment_info)
    if ok:
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "ignored"}), 200
