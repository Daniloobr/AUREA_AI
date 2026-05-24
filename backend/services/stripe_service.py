import stripe
import os

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")


def _get_price_mode(price_id: str) -> str:
    """
    Detecta automaticamente se o price é 'subscription' ou 'payment' (one_time).
    Evita erro: "price mode mismatch" da API do Stripe.
    """
    try:
        stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
        price = stripe.Price.retrieve(price_id)
        recurring = getattr(price, "recurring", None)
        mode = "subscription" if recurring else "payment"
        print(f"[STRIPE] price_id={price_id} → mode={mode} | recurring={recurring}")
        return mode
    except Exception as e:
        print(f"[STRIPE][ERRO] Falha ao detectar mode do price {price_id}: {e}")
        # Fallback seguro: tenta 'payment' (one_time) — menos restritivo
        return "payment"


def create_checkout_session(price_id, user_id, user_email, success_url, cancel_url):
    # Garantir a chave da API do Stripe direto do os.environ no momento da chamada
    stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

    print(f"[STRIPE] Iniciando checkout | user_id={user_id} | price_id={price_id}")

    # Detectar mode automaticamente (subscription vs payment)
    mode = _get_price_mode(price_id)

    try:
        session_params = {
            "payment_method_types": ["card"],
            "mode": mode,
            "line_items": [{
                "price": price_id,
                "quantity": 1,
            }],
            "success_url": success_url,
            "cancel_url": cancel_url,
            "client_reference_id": str(user_id),
            "customer_email": user_email,
            "metadata": {
                "user_id": str(user_id),
                "price_id": price_id,
            },
        }

        session = stripe.checkout.Session.create(**session_params)

        print(f"[STRIPE] Sessão criada: {session.id} | url={session.url}")

        return {
            "sessionId": session.id,
            "url": session.url,
        }

    except stripe.error.InvalidRequestError as e:
        print(f"[STRIPE][ERRO] InvalidRequestError ao criar checkout: {str(e)}")
        raise e
    except stripe.error.AuthenticationError as e:
        print(f"[STRIPE][ERRO] AuthenticationError — verifique STRIPE_SECRET_KEY: {str(e)}")
        raise e
    except stripe.error.StripeError as e:
        print(f"[STRIPE][ERRO] StripeError ao criar checkout: {str(e)}")
        raise e
    except Exception as e:
        print(f"[STRIPE][ERRO] Erro inesperado ao criar checkout: {str(e)}")
        raise e