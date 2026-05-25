import logging
from flask import Blueprint, jsonify, request
from database import db

from services.asaas_service import (
    find_or_create_customer,
    create_payment,
    get_payment_status,
    get_pix_qr_code,
    create_credit_card_token,
    ASAAS_API_KEY,
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
    if current_user.asaas_customer_id:
        return current_user.asaas_customer_id
    customer_id = find_or_create_customer(
        name=current_user.name,
        email=current_user.email,
        cpf_cnpj=current_user.cpf,
    )
    current_user.asaas_customer_id = customer_id
    db.session.commit()
    return customer_id


@payments_asaas_bp.route("/create-pix-payment", methods=["POST"])
@limiter.limit("20 per hour")
@token_required
def create_pix_payment_route(current_user):
    if not ASAAS_API_KEY:
        return jsonify({"success": False, "error": "Pagamento PIX indisponivel no momento"}), 503
    try:
        data = request.get_json() or {}
        package_id = data.get("package_id")

        if not package_id or package_id not in PACKAGES:
            return jsonify({"success": False, "error": "package_id invalido"}), 400

        pkg = PACKAGES[package_id]
        external_ref = f"{current_user.id}:{package_id}"

        customer_id = _get_or_create_customer(current_user)

        payment = create_payment(
            customer=customer_id,
            value=pkg["price"],
            description=pkg["title"],
            external_reference=external_ref,
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


@payments_asaas_bp.route("/create-card-payment-direct", methods=["POST"])
@limiter.limit("20 per hour")
@token_required
def create_card_payment_route(current_user):
    if not ASAAS_API_KEY:
        return jsonify({"success": False, "error": "Pagamento com cartao indisponivel no momento"}), 503
    try:
        data = request.get_json() or {}
        package_id = data.get("package_id")
        card_number = data.get("card_number")
        card_expiration_month = data.get("card_expiration_month")
        card_expiration_year = data.get("card_expiration_year")
        card_cvv = data.get("card_cvv")
        card_holder_name = data.get("card_holder_name")

        if not package_id or package_id not in PACKAGES:
            return jsonify({"success": False, "error": "package_id invalido"}), 400
        if not all([card_number, card_expiration_month, card_expiration_year, card_cvv, card_holder_name]):
            return jsonify({"success": False, "error": "Dados do cartao incompletos"}), 400

        pkg = PACKAGES[package_id]
        external_ref = f"{current_user.id}:{package_id}"

        customer_id = _get_or_create_customer(current_user)

        card_token = create_credit_card_token(
            card_number=card_number,
            expiry_month=card_expiration_month,
            expiry_year=card_expiration_year,
            cvv=card_cvv,
            holder_name=card_holder_name,
        )

        payment = create_payment(
            customer=customer_id,
            value=pkg["price"],
            description=pkg["title"],
            external_reference=external_ref,
            billing_type='CREDIT_CARD',
            credit_card_token=card_token,
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
