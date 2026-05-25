import json
import uuid

from models.db_models import User, Transaction


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

    def test_webhook_received_no_external_ref(self, client, db):
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
        assert resp.json["status"] == "ignored"

    def test_webhook_confirmed_adds_credits(self, client, db):
        user_id = str(uuid.uuid4())
        user = User(id=user_id, name="Webhook User", email=f"{user_id}@test.com",
                     credits_balance=0)
        user.set_password("123456")
        db.session.add(user)
        db.session.commit()

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
        assert resp.json["status"] == "success"

        updated = User.query.get(user_id)
        assert updated.credits_balance == 200
        tx = Transaction.query.filter_by(external_id="asaas_pay_789").first()
        assert tx is not None
        assert tx.type == "purchase"
        assert tx.amount == 200

    def test_webhook_idempotent(self, client, db):
        user_id = str(uuid.uuid4())
        user = User(id=user_id, name="Idempotent User", email=f"{user_id}@test.com",
                     credits_balance=100)
        user.set_password("123456")
        db.session.add(user)
        db.session.commit()

        payload = {
            "event": "PAYMENT_RECEIVED",
            "payment": {
                "id": "pay_idemp",
                "status": "RECEIVED",
                "value": 25.0,
                "externalReference": f"{user_id}:100_credits",
            },
        }
        resp1 = client.post("/api/webhooks/asaas", data=json.dumps(payload),
                            content_type="application/json")
        assert resp1.json["status"] == "success"

        resp2 = client.post("/api/webhooks/asaas", data=json.dumps(payload),
                            content_type="application/json")
        assert resp2.json["status"] == "success"

        user = User.query.get(user_id)
        assert user.credits_balance == 200
        count = Transaction.query.filter_by(external_id="asaas_pay_idemp").count()
        assert count == 1
