import stripe
import os

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

# ─── Mapeamento LIVE → TEST ───────────────────────────────────────────────────
# Ativo automaticamente quando STRIPE_SECRET_KEY começa com sk_test_
# Garante que price IDs LIVE enviados pelo frontend sejam remapeados para TEST
_LIVE_TO_TEST_MAP = {
    "price_1TXBt5AXb2fn2YJDXDIF0iKk": "price_1TaSlbAXb2fn2YJD21xOhXPs",  # 100 cr
    "price_1TXBtWAXb2fn2YJDZxm1s4Xz": "price_1TaSlbAXb2fn2YJD21xOhXPs",  # 200 cr
    "price_1TXBtrAXb2fn2YJDNsCz53jj": "price_1TaSlbAXb2fn2YJD21xOhXPs",  # 400 cr
}

_TEST_PRICE_ID = "price_1TaSlbAXb2fn2YJD21xOhXPs"


def _resolve_price_id(price_id: str) -> str:
    """
    Se estiver usando chave de TESTE (sk_test_...) e o frontend enviar um
    price ID de PRODUÇÃO, remapeia automaticamente para o price de teste.
    """
    key = os.environ.get("STRIPE_SECRET_KEY", "")
    if key.startswith("sk_test_"):
        if price_id in _LIVE_TO_TEST_MAP:
            mapped = _LIVE_TO_TEST_MAP[price_id]
            print(f"[STRIPE] TEST MODE — remapeando price: {price_id} → {mapped}")
            return mapped
        # Se já for o price de teste, mantém
        if price_id == _TEST_PRICE_ID:
            return price_id
        # Price desconhecido em modo teste → força o price de teste
        print(f"[STRIPE] TEST MODE — price desconhecido '{price_id}', usando fallback: {_TEST_PRICE_ID}")
        return _TEST_PRICE_ID
    return price_id


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
        print(f"[STRIPE] price_id={price_id} → mode={mode}")
        return mode
    except Exception as e:
        print(f"[STRIPE][ERRO] Falha ao detectar mode do price {price_id}: {e}")
        # Fallback seguro: payment (one_time)
        return "payment"


def create_checkout_session(price_id, user_id, user_email, success_url, cancel_url):
    # Garantir a chave da API do Stripe direto do os.environ no momento da chamada
    stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

    print(f"[STRIPE] Iniciando checkout | user_id={user_id} | price_id original={price_id}")

    # ── Remapear price LIVE → TEST automaticamente se necessário ──
    price_id = _resolve_price_id(price_id)

    print(f"[STRIPE] price_id resolvido={price_id}")

    # Detectar mode automaticamente (subscription vs payment)
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

        print(f"[STRIPE] ✅ Sessão criada: {session.id}")

        return {
            "sessionId": session.id,
            "url": session.url,
        }

    except stripe.error.InvalidRequestError as e:
        print(f"[STRIPE][ERRO] InvalidRequestError: {str(e)}")
        raise e
    except stripe.error.AuthenticationError as e:
        print(f"[STRIPE][ERRO] AuthenticationError — verifique STRIPE_SECRET_KEY: {str(e)}")
        raise e
    except stripe.error.StripeError as e:
        print(f"[STRIPE][ERRO] StripeError: {str(e)}")
        raise e
    except Exception as e:
        print(f"[STRIPE][ERRO] Erro inesperado: {str(e)}")
        raise e