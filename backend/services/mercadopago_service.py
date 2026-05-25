import os
import requests
import logging

logger = logging.getLogger(__name__)

MERCADOPAGO_ACCESS_TOKEN = os.environ.get('MERCADOPAGO_ACCESS_TOKEN')
MERCADOPAGO_API_URL = "https://api.mercadopago.com"

if not MERCADOPAGO_ACCESS_TOKEN:
    logger.warning("MERCADOPAGO_ACCESS_TOKEN não configurado — pagamentos com cartão e PIX falharão")
elif MERCADOPAGO_ACCESS_TOKEN.startswith("TEST"):
    logger.warning("MERCADOPAGO_ACCESS_TOKEN está em modo TEST — pagamentos reais serão rejeitados")


def _headers():
    return {
        "Authorization": f"Bearer {MERCADOPAGO_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }


def _build_identification(identification=None, payer_email=None):
    """Retorna identification se dados forem fornecidos, senão None."""
    if identification and identification.get("number"):
        return identification
    return None


def create_card_payment(card_token, amount, description, payer_email, external_ref, installments=1, identification=None):
    payer = {"email": payer_email}
    ident = _build_identification(identification)
    if ident:
        payer["identification"] = ident

    payload = {
        "token": card_token,
        "installments": installments,
        "transaction_amount": float(amount),
        "description": description,
        "external_reference": external_ref,
        "notification_url": f"{os.environ.get('BACKEND_URL')}/api/webhooks/mercadopago",
        "statement_descriptor": "AureaIA",
        "payer": payer,
    }
    logger.info(f"Card payment payload: {payload}")
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


def create_pix_payment(amount, description, payer_email, external_ref, identification=None):
    payer = {"email": payer_email}
    ident = _build_identification(identification)
    if ident:
        payer["identification"] = ident

    payload = {
        "transaction_amount": float(amount),
        "description": description,
        "payment_method_id": "pix",
        "external_reference": external_ref,
        "notification_url": f"{os.environ.get('BACKEND_URL')}/api/webhooks/mercadopago",
        "statement_descriptor": "AureaIA",
        "payer": payer,
    }
    logger.info(f"PIX payment payload: {payload}")
    resp = requests.post(
        f"{MERCADOPAGO_API_URL}/v1/payments",
        json=payload,
        headers=_headers(),
    )
    if resp.status_code not in (200, 201):
        details = resp.json() if resp.text else {}
        logger.error(
            f"Erro PIX payment: status={resp.status_code} "
            f"message={details.get('message', resp.text)} "
            f"cause={details.get('cause', [])}"
        )
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
        logger.error(f"Erro get_payment_status: {resp.status_code} {resp.text}")
        resp.raise_for_status()
    return resp.json()
