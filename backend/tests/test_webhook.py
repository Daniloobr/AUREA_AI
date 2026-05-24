import json
import uuid


class MockStripeSession:
    def __init__(self, payment_status, user_id, price_id):
        self.id = f'cs_test_{uuid.uuid4().hex}'
        self.payment_status = payment_status
        self.metadata = {'user_id': user_id, 'price_id': price_id}


class MockStripeEvent:
    def __init__(self, event_type, data_object):
        self.type = event_type
        self.data = {'object': data_object}

    def __getitem__(self, key):
        return getattr(self, key)


class TestStripeWebhook:
    def test_webhook_missing_signature(self, client, db):
        resp = client.post('/api/stripe-webhook', data='{}',
                           content_type='application/json')
        assert resp.status_code == 400
        assert 'assinatura' in resp.json['error']

    def test_webhook_invalid_signature(self, client, db):
        resp = client.post('/api/stripe-webhook', data='{}',
                           content_type='application/json',
                           headers={'Stripe-Signature': 'invalid'})
        assert resp.status_code == 400

    def test_webhook_unrelated_event(self, client, db, mocker):
        mocker.patch('stripe.Webhook.construct_event',
                     return_value=MockStripeEvent('ping', {}))
        resp = client.post('/api/stripe-webhook', data='{}',
                           content_type='application/json',
                           headers={'Stripe-Signature': 'fake'})
        assert resp.status_code == 200
        assert resp.json['status'] == 'ignored'

    def test_webhook_unpaid_session(self, client, db, test_user, mocker):
        session = MockStripeSession('unpaid', test_user.id, 'price_1TXBt5AXb2fn2YJDXDIF0iKk')
        event = MockStripeEvent('checkout.session.completed', session)
        mocker.patch('stripe.Webhook.construct_event', return_value=event)

        resp = client.post('/api/stripe-webhook', data='{}',
                           content_type='application/json',
                           headers={'Stripe-Signature': 'fake'})
        assert resp.status_code == 200
        assert resp.json['status'] == 'ignored'
