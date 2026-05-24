import logging
import os

from flask import Blueprint, jsonify, request

from services.stripe_service import create_checkout_session
from utils.auth_utils import token_required

payments_bp = Blueprint("payments", __name__)
logger = logging.getLogger(__name__)


def _get_allowed_prices():
    """
    Allowed Stripe Price IDs (comma-separated) to prevent arbitrary price injection.

    - Default keeps current LIVE price IDs.
    - For TEST mode, set STRIPE_ALLOWED_PRICES with your TEST `price_...` IDs.
    """
    raw = os.environ.get("STRIPE_ALLOWED_PRICES")
    if raw:
        return {p.strip() for p in raw.split(",") if p.strip()}
    return {
        "price_1TXBt5AXb2fn2YJDXDIF0iKk",  # 100 credits (LIVE)
        "price_1TXBtWAXb2fn2YJDZxm1s4Xz",  # 200 credits (LIVE)
        "price_1TXBtrAXb2fn2YJDNsCz53jj",  # 400 credits (LIVE)
    }


def _get_price_id_map():
    """
    Optional mapping for migrating LIVE -> TEST without touching frontend.

    Format: STRIPE_PRICE_ID_MAP="live_price:test_price,live_price2:test_price2"
    """
    raw = os.environ.get("STRIPE_PRICE_ID_MAP")
    if not raw:
        return {}
    mapping = {}
    for pair in raw.split(","):
        pair = pair.strip()
        if not pair or ":" not in pair:
            continue
        live_id, test_id = pair.split(":", 1)
        live_id = live_id.strip()
        test_id = test_id.strip()
        if live_id and test_id:
            mapping[live_id] = test_id
    return mapping


@payments_bp.route("/create-checkout-session", methods=["POST"])
@token_required
def create_session(current_user):
    try:
        data = request.get_json() or {}
        price_id = data.get("price_id")

        if not price_id:
            return jsonify({"success": False, "error": "price_id é obrigatório"}), 400

        price_id_map = _get_price_id_map()
        if price_id in price_id_map:
            mapped = price_id_map[price_id]
            logger.info(f"Stripe price_id mapeado: {price_id} -> {mapped}")
            price_id = mapped

        allowed_prices = _get_allowed_prices()
        if price_id not in allowed_prices:
            return jsonify({"success": False, "error": "price_id inválido"}), 400

        success_url = os.environ.get(
            "STRIPE_SUCCESS_URL",
            "https://aureaia-saas.vercel.app/credits?success=true",
        )
        cancel_url = os.environ.get(
            "STRIPE_CANCEL_URL",
            "https://aureaia-saas.vercel.app/credits?canceled=true",
        )

        session_data = create_checkout_session(
            price_id=price_id,
            user_id=current_user.id,
            user_email=current_user.email,
            success_url=success_url,
            cancel_url=cancel_url,
        )

        return jsonify({"success": True, "url": session_data["url"]}), 200
    except Exception as e:
        logger.error(f"Erro ao criar sessão Stripe Checkout: {str(e)}", exc_info=True)
        return jsonify({"success": False, "error": "Não foi possível iniciar o checkout"}), 500
