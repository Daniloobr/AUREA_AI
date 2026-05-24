import uuid
from models.db_models import User, PasswordResetToken

class TestAuthRegister:
    def test_register_success(self, client, db):
        resp = client.post('/api/auth/register', json={
            'name': 'Joana Teste',
            'email': 'joana@teste.com',
            'password': 'SenhaForte1!',
        })
        assert resp.status_code == 201
        data = resp.json
        assert data['success'] is True
        assert data['user']['email'] == 'joana@teste.com'
        assert data['user']['credits_balance'] == 0
        assert 'token' in data

    def test_register_duplicate_email(self, client, db, test_user):
        resp = client.post('/api/auth/register', json={
            'name': 'Outro',
            'email': 'maria@teste.com',
            'password': 'SenhaForte1!',
        })
        assert resp.status_code == 409
        assert resp.json['error'] == 'Email já cadastrado'

    def test_register_missing_fields(self, client, db):
        resp = client.post('/api/auth/register', json={'name': 'Só Nome'})
        assert resp.status_code == 400

    def test_register_lowercases_email(self, client, db):
        resp = client.post('/api/auth/register', json={
            'name': 'Caixa Alta',
            'email': 'CaixaAlta@TESTE.com',
            'password': 'SenhaForte1!',
        })
        assert resp.status_code == 201
        assert resp.json['user']['email'] == 'caixaalta@teste.com'


class TestAuthLogin:
    def test_login_success(self, client, db, test_user):
        resp = client.post('/api/auth/login', json={
            'email': 'maria@teste.com',
            'password': 'Teste123!',
        })
        assert resp.status_code == 200
        data = resp.json
        assert data['success'] is True
        assert 'token' in data
        assert data['user']['email'] == 'maria@teste.com'

    def test_login_wrong_password(self, client, db, test_user):
        resp = client.post('/api/auth/login', json={
            'email': 'maria@teste.com',
            'password': 'senha_errada',
        })
        assert resp.status_code == 401
        assert 'incorretos' in resp.json['error']

    def test_login_nonexistent_user(self, client, db):
        resp = client.post('/api/auth/login', json={
            'email': 'nao_existe@teste.com',
            'password': 'Teste123!',
        })
        assert resp.status_code == 401


class TestAuthMe:
    def test_get_me_success(self, client, db, auth_headers, test_user):
        resp = client.get('/api/auth/me', headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json['user']['id'] == test_user.id

    def test_get_me_no_token(self, client, db):
        resp = client.get('/api/auth/me')
        assert resp.status_code == 401

    def test_get_me_invalid_token(self, client, db):
        resp = client.get('/api/auth/me', headers={'Authorization': 'Bearer invalid-token'})
        assert resp.status_code == 401


class TestAuthBalance:
    def test_get_balance(self, client, db, auth_headers, test_user):
        resp = client.get('/api/auth/user/balance', headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json['balance'] == 100

    def test_balance_unauthorized(self, client, db):
        resp = client.get('/api/auth/user/balance')
        assert resp.status_code == 401


class TestAuthTransactions:
    def test_empty_transactions(self, client, db, auth_headers):
        resp = client.get('/api/auth/user/transactions', headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json['transactions'] == []


class TestAuthDeleteAccount:
    def test_delete_account(self, client, db, auth_headers, test_user):
        resp = client.delete('/api/auth/user/account', headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json['success'] is True

        user = User.query.get(test_user.id)
        assert user.is_active is False
        assert user.name == "Usuário Excluído"

    def test_deleted_user_cannot_login(self, client, db, test_user):
        user = User.query.get(test_user.id)
        user.is_active = False
        db.session.commit()

        resp = client.post('/api/auth/login', json={
            'email': 'maria@teste.com',
            'password': 'Teste123!',
        })
        assert resp.status_code == 401


class TestAuthLogout:
    def test_logout(self, client, db):
        resp = client.post('/api/auth/logout')
        assert resp.status_code == 200
        assert resp.json['success'] is True


class TestAuthForgotPassword:
    def test_forgot_password_nonexistent_email(self, client, db):
        resp = client.post('/api/auth/forgot-password', json={
            'email': 'naoexiste@teste.com'
        })
        assert resp.status_code == 200
        assert "Se o e-mail existir" in resp.json['message']

    def test_forgot_password_existing_email(self, client, db, test_user):
        resp = client.post('/api/auth/forgot-password', json={
            'email': 'maria@teste.com'
        })
        assert resp.status_code == 200
        token = PasswordResetToken.query.filter_by(user_id=test_user.id).first()
        assert token is not None
        assert token.used is False


class TestAuthResetPassword:
    def test_reset_password_success(self, client, db, test_user):
        from datetime import datetime, timedelta
        import secrets
        token = secrets.token_urlsafe(32)
        reset = PasswordResetToken(
            user_id=test_user.id,
            token=token,
            expires_at=datetime.utcnow() + timedelta(hours=1),
        )
        db.session.add(reset)
        db.session.commit()

        resp = client.post('/api/auth/reset-password', json={
            'token': token,
            'password': 'NovaSenha123!',
        })
        assert resp.status_code == 200
        assert resp.json['success'] is True

        user = User.query.get(test_user.id)
        assert user.check_password('NovaSenha123!') is True
        assert PasswordResetToken.query.get(reset.id).used is True

    def test_reset_password_expired_token(self, client, db, test_user):
        from datetime import datetime, timedelta
        import secrets
        token = secrets.token_urlsafe(32)
        reset = PasswordResetToken(
            user_id=test_user.id,
            token=token,
            expires_at=datetime.utcnow() - timedelta(hours=2),
        )
        db.session.add(reset)
        db.session.commit()

        resp = client.post('/api/auth/reset-password', json={
            'token': token,
            'password': 'NovaSenha123!',
        })
        assert resp.status_code == 400
        assert 'expirado' in resp.json['error']

    def test_reset_password_invalid_token(self, client, db):
        resp = client.post('/api/auth/reset-password', json={
            'token': 'token_invalido',
            'password': 'NovaSenha123!',
        })
        assert resp.status_code == 400
