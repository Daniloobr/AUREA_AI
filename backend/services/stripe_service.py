import stripe
import os
import logging

logger = logging.getLogger(__name__)

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

_LIVE_TO_TEST_MAP = {}

def _resolve_price_id(price_id: str) -> str:
    key = os.environ.get("STRIPE_SECRET_KEY", "")
    if key.startswith("sk_test_"):
        if price_id in _LIVE_TO_TEST_MAP:
            mapped = _LIVE_TO_TEST_MAP[price_id]
            logger.info(f"TEST MODE — remapeando price: {price_id} -> {mapped}")
            return mapped
        if price_id == os.environ.get("STRIPE_TEST_PRICE_ID"):
            return price_id
        fallback = os.environ.get("STRIPE_TEST_PRICE_ID")
        if fallback:
            logger.info(f"TEST MODE — price desconhecido '{price_id}', usando fallback: {fallback}")
            return fallback
    return price_id


def _get_price_mode(price_id: str) -> str:
    try:
        stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
        price = stripe.Price.retrieve(price_id)
        recurring = getattr(price, "recurring", None)
        mode = "subscription" if recurring else "payment"
        logger.info(f"price_id={price_id} -> mode={mode}")
        return mode
    except Exception as e:
        logger.error(f"Falha ao detectar mode do price {price_id}: {e}")
        return "payment"


def create_checkout_session(price_id, user_id, user_email, success_url, cancel_url):
    stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

    logger.info(f"Iniciando checkout | user_id={user_id} | price_id original={price_id}")

    price_id = _resolve_price_id(price_id)

    logger.info(f"price_id resolvido={price_id}")

    mode = _get_price_mode(price_id)

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode=mode,
            line_items=[{
                "price": price_id,
                "quantity": 1,
            }],
            success_url=success_url,
            cancel_url=cancel_url,
            client_reference_id=str(user_id),
            customer_email=user_email,
            metadata={
                "user_id": str(user_id),
                "price_id": price_id,
            },
        )

        logger.info(f"SUCCESS Sessao criada: {session.id}")

        return {
            "sessionId": session.id,
            "url": session.url,
        }

    except stripe.error.InvalidRequestError as e:
        logger.error(f"InvalidRequestError: {str(e)}")
        raise e
    except stripe.error.AuthenticationError as e:
        logger.error(f"AuthenticationError — verifique STRIPE_SECRET_KEY: {str(e)}")
        raise e
    except stripe.error.StripeError as e:
        logger.error(f"StripeError: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}")
        raise e
