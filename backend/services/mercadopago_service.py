import os
import requests
import logging

logger = logging.getLogger(__name__)

MERCADOPAGO_ACCESS_TOKEN = os.environ.get('MERCADOPAGO_ACCESS_TOKEN')
MERCADOPAGO_BASE_URL = "https://api.mercadopago.com/v1"


def create_preference(amount, title, payer_email, external_reference,
                      success_url, failure_url, pending_url):
    headers = {
        "Authorization": f"Bearer {MERCADOPAGO_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "items": [{
            "title": title,
            "quantity": 1,
            "unit_price": float(amount),
        }],
        "payer": {"email": payer_email},
        "back_urls": {
            "success": success_url,
            "failure": failure_url,
            "pending": pending_url,
        },
        "auto_return": "approved",
        "external_reference": external_reference,
        "notification_url": f"{os.environ.get('BACKEND_URL')}/api/webhooks/mercadopago",
    }
    logger.info(
        f"Criando preferência MP | title={title} | amount={amount} | "
        f"payer={payer_email} | ref={external_reference}"
    )
    response = requests.post(
        f"{MERCADOPAGO_BASE_URL}/preferences",
        json=payload,
        headers=headers,
    )
    if response.status_code not in (200, 201):
        logger.error(
            f"Erro MP create_preference: {response.status_code} {response.text}"
        )
        response.raise_for_status()
    data = response.json()
    logger.info(f"Preferência criada | id={data.get('id')}")
    return data


def get_payment_info(payment_id):
    headers = {"Authorization": f"Bearer {MERCADOPAGO_ACCESS_TOKEN}"}
    response = requests.get(
        f"{MERCADOPAGO_BASE_URL}/payments/{payment_id}",
        headers=headers,
    )
    if response.status_code != 200:
        logger.error(
            f"Erro MP get_payment_info: {response.status_code} {response.text}"
        )
        response.raise_for_status()
    return response.json()

