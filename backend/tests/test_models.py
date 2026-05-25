import uuid
import json
from models.db_models import User, Transaction, GenerationJob


class TestUserModel:
    def test_create_user(self, db):
        user = User(
            name="Ana Teste",
            email="ana@teste.com",
            credits_balance=50,
        )
        user.set_password("Senha123!")
        db.session.add(user)
        db.session.commit()

        saved = User.query.filter_by(email="ana@teste.com").first()
        assert saved is not None
        assert saved.name == "Ana Teste"
        assert saved.credits_balance == 50
        assert saved.is_admin is False
        assert saved.is_active is True
        assert len(saved.id) == 36

    def test_password_hashing(self, db):
        user = User(name="Test", email="test@teste.com")
        user.set_password("MinhaSenha123!")
        assert user.password_hash.startswith('$2b$')
        assert user.check_password("MinhaSenha123!") is True
        assert user.check_password("SenhaErrada") is False

    def test_to_dict_anonymized(self, db):
        user = User(name="Original", email="original@teste.com")
        user.set_password("Senha123!")
        db.session.add(user)
        db.session.commit()

        user.is_active = False
        data = user.to_dict()
        assert data['name'] == "Usuário Excluído"
        assert data['email'] == "anonimo@aureaia.com"

    def test_to_dict_active(self, db):
        user = User(name="Ativa", email="ativa@teste.com", credits_balance=30)
        user.set_password("Senha123!")
        db.session.add(user)
        db.session.commit()

        data = user.to_dict()
        assert data['name'] == "Ativa"
        assert data['email'] == "ativa@teste.com"
        assert data['credits_balance'] == 30


class TestTransactionModel:
    def test_create_transaction(self, db, test_user):
        txn = Transaction(
            user_id=test_user.id,
            type='purchase',
            amount=100,
            balance_before=0,
            balance_after=100,
            description="Compra de 100 créditos",
        )
        db.session.add(txn)
        db.session.commit()

        saved = Transaction.query.get(txn.id)
        assert saved.type == 'purchase'
        assert saved.amount == 100
        assert saved.status == 'completed'

    def test_transaction_external_id_unique(self, db, test_user):
        txn1 = Transaction(
            user_id=test_user.id, type='purchase',
            amount=100, balance_before=0, balance_after=100,
            external_id='mp_payment_123',
        )
        db.session.add(txn1)
        db.session.commit()

        from sqlalchemy.exc import IntegrityError
        import pytest
        txn2 = Transaction(
            user_id=test_user.id, type='purchase',
            amount=200, balance_before=100, balance_after=300,
            external_id='mp_payment_123',
        )
        db.session.add(txn2)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()


class TestGenerationJobModel:
    def test_create_job(self, db, test_user):
        job = GenerationJob(
            id=str(uuid.uuid4()),
            user_id=test_user.id,
            status='queued',
            tipo_ensaio='classic',
            cost_moedas=25,
        )
        db.session.add(job)
        db.session.commit()

        saved = GenerationJob.query.get(job.id)
        assert saved.status == 'queued'
        assert saved.cost_moedas == 25

    def test_result_url_property(self, db, test_user):
        job = GenerationJob(
            id=str(uuid.uuid4()),
            user_id=test_user.id,
            status='completed',
        )
        job.set_images(['https://img1.jpg', 'https://img2.jpg'])
        db.session.add(job)
        db.session.commit()

        assert job.result_url == 'https://img1.jpg'

    def test_result_url_none_when_empty(self, db, test_user):
        job = GenerationJob(
            id=str(uuid.uuid4()),
            user_id=test_user.id,
            status='queued',
        )
        db.session.add(job)
        db.session.commit()

        assert job.result_url is None

    def test_to_dict_format(self, db, test_user):
        job = GenerationJob(
            id=str(uuid.uuid4()),
            user_id=test_user.id,
            status='completed',
            tipo_ensaio='floral',
            cost_moedas=25,
        )
        job.set_images(['https://img1.jpg'])
        db.session.add(job)
        db.session.commit()

        data = job.to_dict()
        assert data['id'] == job.id
        assert data['status'] == 'completed'
        assert data['images'] == ['https://img1.jpg']
        assert data['cost_moedas'] == 25
        assert 'created_at' in data
