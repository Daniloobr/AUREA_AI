import pytest
import os
import uuid


def pytest_configure(config):
    os.environ['FLASK_ENV'] = 'development'
    os.environ['SECRET_KEY'] = 'test-secret-key-12345'
    os.environ['ADMIN_SECRET_KEY'] = 'test-admin-key-12345'
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    os.environ['SUPABASE_URL'] = ''
    os.environ['SUPABASE_KEY'] = ''
    os.environ['SUPABASE_SERVICE_ROLE_KEY'] = ''
    os.environ['SENDGRID_API_KEY'] = ''
    os.environ['ASAAS_API_KEY'] = 'test_asaas_mock_key'
    os.environ['ASAAS_SANDBOX'] = 'True'
    os.environ['BACKEND_URL'] = 'http://localhost:5000'
    os.environ['FRONTEND_URL'] = 'http://localhost:3000'
    os.environ['CELERY_BROKER_URL'] = ''


@pytest.fixture(scope='session')
def app():
    from app import create_app
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['CELERY_TASK_ALWAYS_EAGER'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    from limiter_instance import limiter
    limiter.enabled = False
    return app


@pytest.fixture(scope='function')
def db(app):
    from database import db as _db
    from models.db_models import User, Transaction, GenerationJob
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()


@pytest.fixture(scope='function')
def client(app, db):
    return app.test_client()


@pytest.fixture(scope='function')
def test_user(db):
    from models.db_models import User
    user = User(
        id=str(uuid.uuid4()),
        name="Maria Teste",
        email="maria@teste.com",
        credits_balance=100,
        is_admin=False,
    )
    user.set_password("Teste123!")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture(scope='function')
def admin_user(db):
    from models.db_models import User
    user = User(
        id=str(uuid.uuid4()),
        name="Admin Teste",
        email="admin@teste.com",
        credits_balance=0,
        is_admin=True,
    )
    user.set_password("Admin123!")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture(scope='function')
def auth_headers(client, test_user):
    resp = client.post('/api/auth/login', json={
        'email': 'maria@teste.com',
        'password': 'Teste123!',
    })
    token = resp.json['token']
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture(scope='function')
def admin_headers(client, admin_user):
    resp = client.post('/api/auth/login', json={
        'email': 'admin@teste.com',
        'password': 'Admin123!',
    })
    token = resp.json['token']
    return {'Authorization': f'Bearer {token}'}
