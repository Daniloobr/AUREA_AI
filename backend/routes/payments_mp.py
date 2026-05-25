import logging
import os
import uuid

from flask import Blueprint, jsonify, request

from services.mercadopago_service import create_preference
from utils.auth_utils import token_required
from limiter_instance import limiter

payments_mp_bp = Blueprint("payments_mp", __name__)
logger = logging.getLogger(__name__)

PACKAGES = {
    "100_credits": {"title": "100 Créditos AureaIA", "price": 25.00, "credits": 100},
    "200_credits": {"title": "200 Créditos AureaIA", "price": 50.00, "credits": 200},
    "400_credits": {"title": "400 Créditos AureaIA", "price": 120.00, "credits": 400},
}


@payments_mp_bp.route("/create-checkout-preference", methods=["POST"])
@limiter.limit("20 per hour")
@token_required
def create_checkout_preference(current_user):
    try:
        data = request.get_json() or {}
        package_id = data.get("package_id")

        if not package_id or package_id not in PACKAGES:
            return jsonify({"success": False, "error": "package_id inválido"}), 400

        pkg = PACKAGES[package_id]

        FRONTEND_URL = os.environ.get(
            "FRONTEND_URL", "https://aureaia-saas.vercel.app"
        )
        BACKEND_URL = os.environ.get(
            "BACKEND_URL", "https://aurea-ai-ftqa.onrender.com"
        )

        external_reference = str(uuid.uuid4())

        preference = create_preference(
            amount=pkg["price"],
            title=pkg["title"],
            payer_email=current_user.email,
            external_reference=external_reference,
            success_url=f"{FRONTEND_URL}/credits?success=true&ref={external_reference}",
            failure_url=f"{FRONTEND_URL}/credits?canceled=true",
            pending_url=f"{FRONTEND_URL}/credits?pending=true",
        )

        logger.info(
            f"Preferência MP criada | user={current_user.id} | "
            f"package={package_id} | init_point={preference.get('init_point')}"
        )

        return jsonify({
            "success": True,
            "url": preference.get("init_point"),
            "preference_id": preference.get("id"),
            "external_reference": external_reference,
        }), 200

    except Exception as e:
        logger.error(f"Erro ao criar preferência MP: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Não foi possível iniciar o checkout",
        }), 500
