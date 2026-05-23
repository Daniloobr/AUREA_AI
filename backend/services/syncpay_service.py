import os
import requests
import logging

logger = logging.getLogger(__name__)

class SyncPayService:
    def __init__(self):
        self.base_url = os.environ.get('SYNCPAY_API_URL')
        self.client_id = os.environ.get('SYNCPAY_CLIENT_ID')
        self.client_secret = os.environ.get('SYNCPAY_CLIENT_SECRET')
        self._access_token = None

    def _get_access_token(self):
        if self._access_token:
            return self._access_token
        url = f"{self.base_url}/oauth/token"  # confirme este endpoint na documentação
        payload = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        resp = requests.post(url, data=payload, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        self._access_token = data['access_token']
        return self._access_token

    def _headers(self):
        return {
            'Authorization': f"Bearer {self._get_access_token()}",
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def create_cash_in(self, amount: float, client_name: str, client_cpf: str,
                       client_email: str, client_phone: str, description: str, webhook_url: str):
        payload = {
            "amount": amount,
            "description": description,
            "webhook_url": webhook_url,
            "client": {
                "name": client_name,
                "cpf": client_cpf,
                "email": client_email,
                "phone": client_phone
            }
        }
        response = requests.post(
            f"{self.base_url}/api/partner/v1/cash-in",
            json=payload,
            headers=self._headers(),
            timeout=30
        )
        response.raise_for_status()
        return response.json()   # { "pix_code": "...", "identifier": "..." }

    def get_transaction(self, identifier: str):
        response = requests.get(
            f"{self.base_url}/api/partner/v1/transaction/{identifier}",
            headers=self._headers(),
            timeout=30
        )
        response.raise_for_status()
        return response.json()   # { "data": { "status": "...", "description": "...", "amount": ... } }

syncpay_service = SyncPayService()