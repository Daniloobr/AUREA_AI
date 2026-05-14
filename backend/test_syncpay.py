import requests
import json

token = "53652725|rSEwIeiklJXyUAsIqeSury5vPdltNnlJUI61Qv6xf35497df"
url = "https://api.syncpayments.com.br/api/partner/v1/cash-in"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

payload = {
    "amount": 100,
    "description": "Teste QA AureaIA - 100 créditos",
    "webhook_url": "https://aureaia.com/api/webhooks/syncpay",
    "external_reference": "test-transaction-001",
    "client": {
        "name": "QA Tester",
        "cpf": "12345678909",
        "email": "qa@aureaia.com",
        "phone": "51999999999"
    }
}

print(f"Testing URL: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")

response = requests.post(url, json=payload, headers=headers)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")
