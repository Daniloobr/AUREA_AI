import os
import requests
import logging
import json

logger = logging.getLogger(__name__)

class PagSeguroService:
    def __init__(self):
        self.email = os.environ.get('PAGSEGURO_EMAIL')
        self.token = os.environ.get('PAGSEGURO_TOKEN_SANDBOX')
        self.is_sandbox = os.environ.get('PAGSEGURO_SANDBOX', 'True').lower() == 'true'
        
        if self.is_sandbox:
            self.base_url = "https://sandbox.api.pagseguro.com"
        else:
            self.base_url = "https://api.pagseguro.com"
            # In production, we might use a different token variable, but instructions say use what I have.
        
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "accept": "application/json"
        }

    def create_pix_order(self, amount_cents, customer_name, customer_email, customer_tax_id, reference_id):
        """
        Cria um pedido PIX no PagSeguro (PagBank) v2.
        amount_cents: valor em centavos (ex: 1000 = R$ 10,00)
        """
        url = f"{self.base_url}/orders"
        
        # PagSeguro v2 PIX Order payload
        payload = {
            "reference_id": reference_id,
            "customer": {
                "name": customer_name,
                "email": customer_email,
                "tax_id": customer_tax_id.replace('.', '').replace('-', '').replace(' ', '')
            },
            "qr_codes": [
                {
                    "amount": {
                        "value": amount_cents
                    }
                }
            ],
            "notification_urls": [
                os.environ.get('PAGSEGURO_NOTIFICATION_URL', '')
            ]
        }

        try:
            logger.info(f"Criando pedido PagSeguro PIX para {customer_email} - Valor: {amount_cents}")
            response = requests.post(url, headers=self.headers, json=payload)
            
            if response.status_code != 201:
                logger.error(f"Erro PagSeguro API ({response.status_code}): {response.text}")
                return None

            data = response.json()
            
            # Extrair QR Code
            qr_code_info = data.get('qr_codes', [{}])[0]
            qr_code_text = qr_code_info.get('text')
            
            # A imagem do QR Code vem em links
            links = qr_code_info.get('links', [])
            qr_code_image = next((link['href'] for link in links if link['rel'] == 'QRCODE.PNG'), None)
            
            return {
                "order_id": data.get('id'),
                "qr_code_text": qr_code_text,
                "qr_code_image": qr_code_image,
                "reference_id": data.get('reference_id')
            }

        except Exception as e:
            logger.error(f"Exceção ao criar pedido PagSeguro: {str(e)}")
            return None

    def get_order(self, order_id):
        """
        Consulta o status de um pedido no PagSeguro.
        """
        url = f"{self.base_url}/orders/{order_id}"
        
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Erro ao consultar pedido {order_id}: {str(e)}")
            return None

# Singleton instance
pagseguro_service = PagSeguroService()
