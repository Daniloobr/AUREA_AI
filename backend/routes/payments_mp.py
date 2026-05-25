import logging
import os

from flask import Blueprint, jsonify, request

from services.mercadopago_service import (
    create_card_payment,
    create_pix_payment,
    get_payment_status,
)
from utils.auth_utils import token_required
from limiter_instance import limiter

payments_mp_bp = Blueprint("payments_mp", __name__)
logger = logging.getLogger(__name__)

PACKAGES = {
    "100_credits": {"title": "100 Créditos AureaIA", "price": 25.00, "credits": 100},
    "200_credits": {"title": "200 Créditos AureaIA", "price": 50.00, "credits": 200},
    "400_credits": {"title": "400 Créditos AureaIA", "price": 120.00, "credits": 400},
}


@payments_mp_bp.route("/create-card-payment", methods=["POST"])
@limiter.limit("20 per hour")
@token_required
def create_card_payment_route(current_user):
    if not MERCADOPAGO_ACCESS_TOKEN:
        return jsonify({"success": False, "error": "Pagamento indisponível no momento"}), 503
    try:
        data = request.get_json() or {}
        card_token = data.get("card_token")
        package_id = data.get("package_id")

        if not card_token:
            return jsonify({"success": False, "error": "card_token é obrigatório"}), 400
        if not package_id or package_id not in PACKAGES:
            return jsonify({"success": False, "error": "package_id inválido"}), 400

        pkg = PACKAGES[package_id]
        external_ref = f"{current_user.id}:{package_id}"
        identification = {"type": "CPF", "number": current_user.cpf} if current_user.cpf else None

        result = create_card_payment(
            card_token=card_token,
            amount=pkg["price"],
            description=pkg["title"],
            payer_email=current_user.email,
            external_ref=external_ref,
        )

        logger.info(
            f"Card payment | user={current_user.id} | "
            f"package={package_id} | mp_id={result.get('id')} | "
            f"status={result.get('status')}"
        )

        return jsonify({
            "success": True,
            "payment_id": result.get("id"),
            "status": result.get("status"),
            "status_detail": result.get("status_detail"),
        }), 200

    except Exception as e:
        logger.error(f"Erro card payment route: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Não foi possível processar o pagamento",
        }), 500


@payments_mp_bp.route("/create-pix-payment", methods=["POST"])
@limiter.limit("20 per hour")
@token_required
def create_pix_payment_route(current_user):
    if not MERCADOPAGO_ACCESS_TOKEN:
        return jsonify({"success": False, "error": "Pagamento PIX indisponível no momento"}), 503
    try:
        data = request.get_json() or {}
        package_id = data.get("package_id")

        if not package_id or package_id not in PACKAGES:
            return jsonify({"success": False, "error": "package_id inválido"}), 400

        pkg = PACKAGES[package_id]
        external_ref = f"{current_user.id}:{package_id}"
        identification = {"type": "CPF", "number": current_user.cpf} if current_user.cpf else None

        result = create_pix_payment(
            amount=pkg["price"],
            description=pkg["title"],
            payer_email=current_user.email,
            external_ref=external_ref,
        )

        point_of_interaction = result.get("point_of_interaction", {})
        transaction_data = point_of_interaction.get("transaction_data", {})

        logger.info(
            f"PIX payment | user={current_user.id} | "
            f"package={package_id} | mp_id={result.get('id')} | "
            f"status={result.get('status')}"
        )

        return jsonify({
            "success": True,
            "payment_id": result.get("id"),
            "status": result.get("status"),
            "qr_code": transaction_data.get("qr_code"),
            "qr_code_base64": transaction_data.get("qr_code_base64"),
            "ticket_url": transaction_data.get("ticket_url"),
            "expiration": point_of_interaction.get("business_hours"),
        }), 200

    except Exception as e:
        logger.error(f"Erro PIX route: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Não foi possível gerar o PIX",
        }), 500



@payments_mp_bp.route("/payment-status/<payment_id>", methods=["GET"])@payments_mp_bp.route("/payment-status/<payment_id>", methods=["GET"])
@limiter.limit("60 per minute")
@token_required
def payment_status_route(current_user, payment_id):
    try:
        result = get_payment_status(payment_id)
        return jsonify({
            "success": True,
            "payment_id": result.get("id"),
            "status": result.get("status"),
            "status_detail": result.get("status_detail"),
        }), 200
    except Exception as e:
        logger.error(f"Erro payment status: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Erro ao consultar pagamento",
        }), 500
