import os
import requests
import logging

logger = logging.getLogger(__name__)

ASAAS_API_KEY = os.environ.get('ASAAS_API_KEY')
ASAAS_SANDBOX = os.environ.get('ASAAS_SANDBOX', 'True').lower() == 'true'
SANDBOX_CPF = "12345678909"
ASAAS_WALLET_ID = os.environ.get('ASAAS_WALLET_ID')

ASAAS_API_URL = "https://sandbox.asaas.com/api/v3" if ASAAS_SANDBOX else "https://api.asaas.com/api/v3"

if not ASAAS_API_KEY:
    logger.warning("ASAAS_API_KEY nao configurado")


def _headers():
    return {
        "access_token": ASAAS_API_KEY,
        "Content-Type": "application/json",
    }


def find_or_create_customer(name: str, email: str, cpf_cnpj: str = None) -> str:
    existing = requests.get(
        f"{ASAAS_API_URL}/customers",
        params={"email": email},
        headers=_headers(),
    )
    if existing.status_code == 200:
        data = existing.json()
        if data.get("data") and len(data["data"]) > 0:
            customer_id = data["data"][0]["id"]
            logger.info(f"Asaas customer encontrado: {customer_id} para {email}")
            return customer_id

    payload = {"name": name, "email": email, "cpfCnpj": cpf_cnpj or SANDBOX_CPF}
    resp = requests.post(
        f"{ASAAS_API_URL}/customers",
        json=payload,
        headers=_headers(),
    )
    if resp.status_code not in (200, 201):
        logger.error(f"Erro create_customer: {resp.status_code} {resp.text}")
        resp.raise_for_status()
    customer_id = resp.json()["id"]
    logger.info(f"Asaas customer criado: {customer_id} para {email}")
    return customer_id


def update_customer(customer_id: str, cpf_cnpj: str = None) -> dict:
    payload = {}
    if cpf_cnpj:
        payload["cpfCnpj"] = cpf_cnpj
    if not payload:
        return {"id": customer_id}
    resp = requests.post(
        f"{ASAAS_API_URL}/customers/{customer_id}",
        json=payload,
        headers=_headers(),
    )
    if resp.status_code not in (200, 201):
        logger.error(f"Erro update_customer: {resp.status_code} {resp.text}")
        resp.raise_for_status()
    logger.info(f"Asaas customer atualizado: {customer_id}")
    return resp.json()


def create_payment(customer: str, value: float, description: str, external_reference: str, billing_type: str = 'PIX', credit_card_token: str = None, due_date: str = None) -> dict:
    if not due_date:
        from datetime import datetime, timedelta
        due_date = (datetime.utcnow() + timedelta(days=3)).strftime('%Y-%m-%d')

    payload = {
        "customer": customer,
        "billingType": billing_type,
        "value": value,
        "dueDate": due_date,
        "description": description,
        "externalReference": external_reference,
    }
    if ASAAS_WALLET_ID:
        payload["walletId"] = ASAAS_WALLET_ID
    if billing_type == 'CREDIT_CARD' and credit_card_token:
        payload["creditCardToken"] = credit_card_token

    resp = requests.post(
        f"{ASAAS_API_URL}/payments",
        json=payload,
        headers=_headers(),
    )
    if resp.status_code not in (200, 201):
        logger.error(f"Erro create_payment: {resp.status_code} {resp.text}")
        resp.raise_for_status()
    return resp.json()


def get_payment_status(payment_id: str) -> dict:
    resp = requests.get(
        f"{ASAAS_API_URL}/payments/{payment_id}",
        headers=_headers(),
    )
    if resp.status_code != 200:
        logger.error(f"Erro get_payment_status: {resp.status_code} {resp.text}")
        resp.raise_for_status()
    return resp.json()


def get_pix_qr_code(payment_id: str) -> dict:
    resp = requests.get(
        f"{ASAAS_API_URL}/payments/{payment_id}/pixQrCode",
        headers=_headers(),
    )
    if resp.status_code not in (200, 201):
        logger.error(f"Erro get_pix_qr_code: {resp.status_code} {resp.text}")
        resp.raise_for_status()
    return resp.json()


def create_credit_card_token(card_number: str, expiry_month: str, expiry_year: str, cvv: str, holder_name: str) -> str:
    payload = {
        "cardNumber": card_number,
        "holderName": holder_name,
        "expirationMonth": expiry_month,
        "expirationYear": expiry_year,
        "ccv": cvv,
    }
    resp = requests.post(
        f"{ASAAS_API_URL}/creditCard/token",
        json=payload,
        headers=_headers(),
    )
    if resp.status_code not in (200, 201):
        logger.error(f"Erro create_credit_card_token: {resp.status_code} {resp.text}")
        resp.raise_for_status()
    data = resp.json()
    token = data.get("creditCardToken")
    if not token:
        raise ValueError(f"Token de cartao nao retornado pelo Asaas: {data}")
    return token
