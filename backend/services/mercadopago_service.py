import os
import requests
import logging

logger = logging.getLogger(__name__)

MERCADOPAGO_ACCESS_TOKEN = os.environ.get('MERCADOPAGO_ACCESS_TOKEN')
MERCADOPAGO_API_URL = "https://api.mercadopago.com"


def _headers():
    return {
        "Authorization": f"Bearer {MERCADOPAGO_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }


def create_card_payment(card_token, amount, description, payer_email, external_ref, installments=1):
    payload = {
        "token": card_token,
        "installments": installments,
        "transaction_amount": float(amount),
        "description": description,
        "external_reference": external_ref,
        "payer": {
            "email": payer_email,
            "identification": {
                "type": "CPF",
                "number": "12345678909",
            },
        },
    }
    logger.info(
        f"Criando pagamento cartão | amount={amount} | "
        f"payer={payer_email} | ref={external_ref}"
    )
    resp = requests.post(
        f"{MERCADOPAGO_API_URL}/v1/payments",
        json=payload,
        headers=_headers(),
    )
    if resp.status_code not in (200, 201):
        logger.error(f"Erro card payment: {resp.status_code} {resp.text}")
        resp.raise_for_status()
    data = resp.json()
    logger.info(f"Pagamento cartão | id={data.get('id')} | status={data.get('status')}")
    return data


def create_pix_payment(amount, description, payer_email, external_ref):
    payload = {
        "transaction_amount": float(amount),
        "description": description,
        "payment_method_id": "pix",
        "external_reference": external_ref,
        "payer": {
            "email": payer_email,
            "identification": {
                "type": "CPF",
                "number": "12345678909",
            },
        },
    }
    logger.info(
        f"Criando pagamento PIX | amount={amount} | "
        f"payer={payer_email} | ref={external_ref}"
    )
    resp = requests.post(
        f"{MERCADOPAGO_API_URL}/v1/payments",
        json=payload,
        headers=_headers(),
    )
    if resp.status_code not in (200, 201):
        logger.error(f"Erro PIX payment: {resp.status_code} {resp.text}")
        resp.raise_for_status()
    data = resp.json()
    logger.info(f"Pagamento PIX | id={data.get('id')} | status={data.get('status')}")
    return data


def get_payment_status(payment_id):
    resp = requests.get(
        f"{MERCADOPAGO_API_URL}/v1/payments/{payment_id}",
        headers=_headers(),
    )
    if resp.status_code != 200:
        logger.error(
            f"Erro get_payment_status: {resp.status_code} {resp.text}"
        )
        resp.raise_for_status()
    return resp.json()
