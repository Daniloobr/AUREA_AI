import json
import uuid


def _make_mp_payload(action, payment_id, status="approved", title="100 Créditos AureaIA", payer_email="maria@teste.com"):
    return {
        "action": action,
        "api_version": "v1",
        "data": {"id": payment_id},
        "date_created": "2026-05-24T12:00:00.000-03:00",
        "id": str(uuid.uuid4()),
        "live_mode": False,
        "type": "payment",
        "user_id": "123456",
    }


class TestMercadoPagoWebhook:
    def test_webhook_missing_signature(self, client, db):
        resp = client.post(
            "/api/webhooks/mercadopago",
            data=json.dumps({}),
            content_type="application/json",
        )
        assert resp.status_code == 400
        assert "Assinatura" in resp.json["error"]

    def test_webhook_ignored_action(self, client, db):
        payload = _make_mp_payload("merchant_order.created", "123")
        resp = client.post(
            "/api/webhooks/mercadopago",
            data=json.dumps(payload),
            content_type="application/json",
            headers={
                "x-signature": "ts=123456,v1=fake",
                "x-request-id": "req-123",
            },
        )
        assert resp.status_code == 200
        assert resp.json["status"] == "ignored"

    def test_webhook_payment_created(self, client, db):
        payload = _make_mp_payload("payment.created", "456")
        resp = client.post(
            "/api/webhooks/mercadopago",
            data=json.dumps(payload),
            content_type="application/json",
            headers={
                "x-signature": "ts=123456,v1=fake",
                "x-request-id": "req-456",
            },
        )
        assert resp.status_code == 200
        assert resp.json["status"] == "received"
