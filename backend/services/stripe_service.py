import stripe
import os

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")


def create_checkout_session(price_id, user_id, user_email, success_url, cancel_url):
    # Garantir a chave da API do Stripe direto do os.environ no momento da chamada
    stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
    
    # Forçar o uso do Price ID de teste
    price_id = "price_1TaSlbAXb2fn2YJD21xOhXPs"

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="subscription",
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
            }
        )

        return {
            "sessionId": session.id,
            "url": session.url
        }

    except stripe.error.StripeError as e:
        print(f"[STRIPE][ERRO] Erro da API do Stripe ao criar checkout: {str(e)}")
        raise e
    except Exception as e:
        print(f"[STRIPE][ERRO] Erro inesperado ao criar checkout: {str(e)}")
        raise e