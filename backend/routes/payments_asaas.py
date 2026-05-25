import logging
import re
from flask import Blueprint, jsonify, request
from database import db

from services.asaas_service import (
    find_or_create_customer,
    update_customer,
    create_payment,
    get_payment_status,
    get_pix_qr_code,
    create_credit_card_token,
    ASAAS_API_KEY,
    SANDBOX_CPF,
)
from utils.auth_utils import token_required
from limiter_instance import limiter

payments_asaas_bp = Blueprint("payments_asaas", __name__)
logger = logging.getLogger(__name__)

PACKAGES = {
    "100_credits": {"title": "100 Creditos AureaIA", "price": 25.00, "credits": 100},
    "200_credits": {"title": "200 Creditos AureaIA", "price": 50.00, "credits": 200},
    "400_credits": {"title": "400 Creditos AureaIA", "price": 120.00, "credits": 400},
}


def _get_or_create_customer(current_user):
    cpf = current_user.cpf or SANDBOX_CPF
    if current_user.asaas_customer_id:
        update_customer(current_user.asaas_customer_id, cpf_cnpj=cpf)
        return current_user.asaas_customer_id
    customer_id = find_or_create_customer(
        name=current_user.name,
        email=current_user.email,
        cpf_cnpj=cpf,
    )
    current_user.asaas_customer_id = customer_id
    db.session.commit()
    return customer_id


def _parse_external_ref(external_reference):
    if ":" in external_reference:
        parts = external_reference.split(":", 1)
        return parts[0], parts[1]
    return None, None


def _validate_package(package_id):
    if package_id in PACKAGES:
        return PACKAGES[package_id]
    return None


@payments_asaas_bp.route("/create-pix-payment", methods=["POST"])
@limiter.limit("20 per hour")
@token_required
def create_pix_payment_route(current_user):
    if not ASAAS_API_KEY:
        return jsonify({"success": False, "error": "Pagamento PIX indisponivel no momento"}), 503
    try:
        data = request.get_json() or {}
        external_reference = data.get("external_reference")
        value = data.get("value")
        description = data.get("description")

        if not external_reference:
            return jsonify({"success": False, "error": "external_reference é obrigatório"}), 400

        _, package_id = _parse_external_ref(external_reference)
        pkg = _validate_package(package_id)
        if not pkg:
            return jsonify({"success": False, "error": "package_id inválido na referência"}), 400

        customer_id = _get_or_create_customer(current_user)

        payment = create_payment(
            customer=customer_id,
            value=float(value) if value else pkg["price"],
            description=description or pkg["title"],
            external_reference=external_reference,
            billing_type='PIX',
        )

        payment_id = payment.get("id")
        qr_data = get_pix_qr_code(payment_id)

        logger.info(
            f"PIX payment | user={current_user.id} | "
            f"package={package_id} | asaas_id={payment_id} | "
            f"status={payment.get('status')}"
        )

        return jsonify({
            "success": True,
            "payment_id": payment_id,
            "status": payment.get("status"),
            "qr_code": qr_data.get("payload"),
            "qr_code_base64": qr_data.get("encodedImage"),
        }), 200

    except Exception as e:
        logger.error(f"Erro PIX route: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Nao foi possivel gerar o PIX",
        }), 500


@payments_asaas_bp.route("/create-card-payment", methods=["POST"])
@limiter.limit("20 per hour")
@token_required
def create_card_payment_route(current_user):
    if not ASAAS_API_KEY:
        return jsonify({"success": False, "error": "Pagamento com cartao indisponivel no momento"}), 503
    try:
        data = request.get_json() or {}
        external_reference = data.get("external_reference")
        value = data.get("value")
        description = data.get("description")

        if not external_reference:
            return jsonify({"success": False, "error": "external_reference é obrigatório"}), 400

        _, package_id = _parse_external_ref(external_reference)
        pkg = _validate_package(package_id)
        if not pkg:
            return jsonify({"success": False, "error": "package_id inválido na referência"}), 400

        customer_id = _get_or_create_customer(current_user)

        payment = create_payment(
            customer=customer_id,
            value=float(value) if value else pkg["price"],
            description=description or pkg["title"],
            external_reference=external_reference,
            billing_type='CREDIT_CARD',
        )

        logger.info(
            f"Card payment | user={current_user.id} | "
            f"package={package_id} | asaas_id={payment.get('id')} | "
            f"status={payment.get('status')}"
        )

        return jsonify({
            "success": True,
            "payment_id": payment.get("id"),
            "status": payment.get("status"),
            "checkout_url": payment.get("invoiceUrl"),
        }), 200

    except Exception as e:
        logger.error(f"Erro card payment route: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Nao foi possivel processar o pagamento",
        }), 500


@payments_asaas_bp.route("/payment-status/<payment_id>", methods=["GET"])
@limiter.limit("60 per minute")
@token_required
def payment_status_route(current_user, payment_id):
    try:
        result = get_payment_status(payment_id)
        return jsonify({
            "success": True,
            "payment_id": result.get("id"),
            "status": result.get("status"),
        }), 200
    except Exception as e:
        logger.error(f"Erro payment status: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Erro ao consultar pagamento",
        }), 500
