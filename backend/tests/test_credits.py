import uuid
from models.db_models import User, Transaction, GenerationJob

COST = 25


class TestAdminAddCredits:
    def test_admin_add_credits_success(self, client, db, test_user):
        resp = client.post('/api/auth/admin/credits', json={
            'user_id': test_user.id,
            'amount': 50,
        }, headers={'X-Admin-Key': 'test-admin-key-12345'})
        assert resp.status_code == 200
        assert resp.json['new_balance'] == 150

        user = User.query.get(test_user.id)
        assert user.credits_balance == 150

        txn = Transaction.query.filter_by(user_id=test_user.id, type='admin_credit').first()
        assert txn is not None
        assert txn.amount == 50

    def test_admin_add_credits_wrong_key(self, client, db, test_user):
        resp = client.post('/api/auth/admin/credits', json={
            'user_id': test_user.id,
            'amount': 50,
        }, headers={'X-Admin-Key': 'wrong-key'})
        assert resp.status_code == 403

    def test_admin_add_credits_nonexistent_user(self, client, db):
        resp = client.post('/api/auth/admin/credits', json={
            'user_id': 'nonexistent-id',
            'amount': 50,
        }, headers={'X-Admin-Key': 'test-admin-key-12345'})
        assert resp.status_code == 404


class TestAdminAdjustCredits:
    def test_adjust_credits_positive(self, client, db, admin_headers, test_user):
        resp = client.post(f'/api/admin/users/{test_user.id}/credits', json={
            'amount': 30,
            'reason': 'Bônus promocional',
        }, headers=admin_headers)
        assert resp.status_code == 200
        assert resp.json['new_balance'] == 130

    def test_adjust_credits_negative(self, client, db, admin_headers, test_user):
        resp = client.post(f'/api/admin/users/{test_user.id}/credits', json={
            'amount': -20,
            'reason': 'Ajuste manual',
        }, headers=admin_headers)
        assert resp.status_code == 200
        assert resp.json['new_balance'] == 80

    def test_adjust_credits_non_admin(self, client, db, auth_headers, test_user):
        resp = client.post(f'/api/admin/users/{test_user.id}/credits', json={
            'amount': 30,
        }, headers=auth_headers)
        assert resp.status_code == 403


class TestRefund:
    def test_refund_success(self, client, db, test_user):
        from tasks.generation_tasks import _refund_user, _get_flask_app
        flask_app = _get_flask_app()
        _refund_user(flask_app, test_user.id, 25, "Reembolso de teste")

        db.session.expire(test_user)
        user = User.query.get(test_user.id)
        assert user.credits_balance == 125

        txn = Transaction.query.filter_by(
            user_id=test_user.id, type='credit_refund'
        ).first()
        assert txn is not None
        assert txn.amount == 25
        assert txn.balance_before == 100
        assert txn.balance_after == 125

    def test_refund_idempotency(self, client, db, test_user):
        from tasks.generation_tasks import _refund_user, _get_flask_app
        flask_app = _get_flask_app()

        _refund_user(flask_app, test_user.id, 25, "Reembolso de teste")
        _refund_user(flask_app, test_user.id, 25, "Reembolso de teste")

        db.session.expire(test_user)
        user = User.query.get(test_user.id)
        assert user.credits_balance == 125

        txns = Transaction.query.filter_by(
            user_id=test_user.id, type='credit_refund'
        ).all()
        assert len(txns) == 1

    def test_refund_nonexistent_user(self, client, db):
        from tasks.generation_tasks import _refund_user, _get_flask_app
        flask_app = _get_flask_app()
        _refund_user(flask_app, 'nonexistent-id', 25, "Teste")
        assert True

    def test_refund_zero_amount(self, client, db, test_user):
        from tasks.generation_tasks import _refund_user, _get_flask_app
        flask_app = _get_flask_app()
        _refund_user(flask_app, test_user.id, 0, "Reembolso zero")

        db.session.expire(test_user)
        user = User.query.get(test_user.id)
        assert user.credits_balance == 100


class TestAdminEndpoints:
    def test_admin_stats(self, client, db, admin_headers):
        resp = client.get('/api/admin/stats', headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json['stats']
        assert 'total_users' in data
        assert 'total_jobs' in data

    def test_admin_users(self, client, db, admin_headers, test_user):
        resp = client.get('/api/admin/users', headers=admin_headers)
        assert resp.status_code == 200
        emails = [u['email'] for u in resp.json['users']]
        assert test_user.email in emails

    def test_admin_jobs(self, client, db, admin_headers):
        resp = client.get('/api/admin/jobs', headers=admin_headers)
        assert resp.status_code == 200
        assert 'jobs' in resp.json

    def test_admin_ban_user(self, client, db, admin_headers, test_user):
        resp = client.delete(
            f'/api/admin/users/{test_user.id}',
            headers=admin_headers,
        )
        assert resp.status_code == 200
        user = User.query.get(test_user.id)
        assert user.is_active is False
