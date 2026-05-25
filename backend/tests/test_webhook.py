import json
import uuid


class TestAsaasWebhook:
    def test_webhook_ignored_event(self, client, db):
        payload = {"event": "PAYMENT_CREATED", "payment": {"id": "pay_123"}}
        resp = client.post(
            "/api/webhooks/asaas",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert resp.status_code == 200
        assert resp.json["status"] == "ignored"

    def test_webhook_payment_received_no_external_ref(self, client, db):
        payload = {
            "event": "PAYMENT_RECEIVED",
            "payment": {
                "id": "pay_456",
                "status": "RECEIVED",
                "value": 25.0,
                "externalReference": "",
            },
        }
        resp = client.post(
            "/api/webhooks/asaas",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert resp.status_code == 200

    def test_webhook_payment_confirmed(self, client, db):
        user_id = str(uuid.uuid4())
        payload = {
            "event": "PAYMENT_CONFIRMED",
            "payment": {
                "id": "pay_789",
                "status": "CONFIRMED",
                "value": 50.0,
                "externalReference": f"{user_id}:200_credits",
            },
        }
        resp = client.post(
            "/api/webhooks/asaas",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert resp.status_code == 200
