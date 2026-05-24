import os
import sys
from dotenv import load_dotenv

# Carregar dotenv da pasta pai
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
load_dotenv()

import stripe
from services.stripe_service import create_checkout_session

print("STRIPE_SECRET_KEY:", os.environ.get("STRIPE_SECRET_KEY"))
print("STRIPE_ALLOWED_PRICES:", os.environ.get("STRIPE_ALLOWED_PRICES"))

try:
    res = create_checkout_session(
        price_id="price_1TaSlbAXb2fn2YJD21xOhXPs",
        user_id="123",
        user_email="test@example.com",
        success_url="https://example.com/success",
        cancel_url="https://example.com/cancel"
    )
    print("Sucesso! URL da sessao:", res["url"])
except Exception as e:
    print("ERRO DETECTADO:", e)
