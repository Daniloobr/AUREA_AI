import os
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


def _process_asaas_payment(payment):
    payment_id = payment.get("id")
    status = payment.get("status")
    external_ref = payment.get("externalReference") or ""

    current_app.logger.info(
        f"[WEBHOOK ASAAS] Processando | id={payment_id} | status={status} | ref={external_ref}"
    )

    if status not in ("RECEIVED", "CONFIRMED"):
        current_app.logger.info(f"[WEBHOOK ASAAS] Status nao confirmado: {status}")
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
                f"[WEBHOOK ASAAS] Parsed ref: user={user_id}, pkg={package_id}, credits={credits}"
            )

    if not user_id or not credits:
        current_app.logger.error(
            f"[WEBHOOK ASAAS] external_reference invalida ou nao mapeada: {external_ref}"
        )
        return False

    tx_id_str = f"asaas_{payment_id}"

    existing = Transaction.query.filter_by(external_id=tx_id_str).first()
    if existing:
        current_app.logger.warning(f"[WEBHOOK ASAAS] Duplicado: {tx_id_str}")
        return True

    user = User.query.get(user_id)
    if not user:
        current_app.logger.error(f"[WEBHOOK ASAAS] Usuario nao encontrado: {user_id}")
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
            description=f"Compra de {credits} creditos via Asaas",
            external_id=tx_id_str,
        )
        db.session.add(tx)
        db.session.commit()
        current_app.logger.info(
            f"[WEBHOOK ASAAS] +{credits} creditos para {user.id} "
            f"(agora {user.credits_balance})"
        )
        return True
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[WEBHOOK ASAAS] Erro DB: {e}", exc_info=True)
        return False


@webhook_bp.route("/webhooks/asaas", methods=["POST"])
def asaas_webhook():
    expected_token = os.environ.get("ASAAS_WEBHOOK_TOKEN")
    if expected_token:
        received_token = request.headers.get("asaas-access-token", "")
        if received_token != expected_token:
            current_app.logger.warning(
                f"[WEBHOOK ASAAS] Token invalido: recebido={received_token[:8]}... esperado={expected_token[:8]}..."
            )
            return jsonify({"error": "Token de acesso invalido"}), 401

    payload = request.get_json(silent=True) or {}

    current_app.logger.info(
        f"[WEBHOOK ASAAS] Recebido | event={payload.get('event')}"
    )

    event = payload.get("event")
    if event not in ("PAYMENT_RECEIVED", "PAYMENT_CONFIRMED"):
        return jsonify({"status": "ignored"}), 200

    payment = payload.get("payment", {})
    if not payment.get("id"):
        return jsonify({"status": "ignored", "reason": "no_payment_id"}), 200

    ok = _process_asaas_payment(payment)
    if ok:
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "ignored"}), 200
