import os
import requests
import json
from datetime import datetime

class SyncPayService:
    def __init__(self):
        self.client_id = os.getenv('SYNCPAY_CLIENT_ID')
        self.client_secret = os.getenv('SYNCPAY_CLIENT_SECRET')
        self.api_url = os.getenv('SYNCPAY_API_URL', '').rstrip('/')
        self.frontend_url = os.getenv('FRONTEND_URL', 'https://aureaia.com').rstrip('/')
        self.webhook_url = f"{self.frontend_url}/api/webhooks/syncpay"
        print(f"DEBUG: SyncPayService initialized. ClientID present: {bool(self.client_id)}, Secret present: {bool(self.client_secret)}")
        print(f"DEBUG: SyncPay API URL: {self.api_url}")

    def get_access_token(self):
        """Faz POST em /api/partner/v1/auth-token com client_id e client_secret."""
        url = f"{self.api_url}/api/partner/v1/auth-token"
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('access_token')
        except Exception as e:
            print(f"Error getting SyncPay access token: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response error: {e.response.text}")
            return None

    def create_pix_charge(self, amount, external_reference, description, client_data):
        """Usa o token para POST em /api/partner/v1/cash-in."""
        token = self.get_access_token()
        if not token:
            print("ERROR: Could not get access token for SyncPay")
            return None

        # Endpoint atualizado conforme PDR v1.1.0 (exemplo real)
        url = f"{self.api_url}/api/partner/v1/cash-in"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Payload atualizado conforme PDR v1.1.0
        payload = {
            "amount": float(amount),
            "description": description,
            "webhook_url": self.webhook_url,
            "external_reference": external_reference,
            "client": {
                "name": client_data.get('name'),
                "cpf": client_data.get('cpf', ''), # Opcional/Fictício para testes
                "email": client_data.get('email'),
                "phone": client_data.get('phone', '51999999999')
            }
        }
        
        print(f"DEBUG: Creating PIX charge. URL: {url}")
        print(f"DEBUG: Payload: {json.dumps(payload)}")
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            print(f"DEBUG: SyncPay Response: {json.dumps(data)}")
            
            # Resposta esperada: { "message": "...", "pix_code": "...", "identifier": "..." }
            return {
                "pix_code": data.get('pix_code'),
                "transaction_id": str(data.get('identifier') or data.get('id')),
                "message": data.get('message')
            }
        except Exception as e:
            print(f"Error creating SyncPay PIX charge: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response error: {e.response.text}")
            return None

syncpay_service = SyncPayService()
