from unittest.mock import patch, MagicMock
import uuid


class TestQueueService:

    def test_queue_generation_insufficient_credits(self, db, test_user):
        test_user.credits_balance = 10
        db.session.commit()

        from services.queue_service import queue_generation
        import pytest

        with pytest.raises(ValueError, match="moedas suficientes"):
            queue_generation(test_user.id, image_urls=["url1", "url2", "url3"], tipo_ensaio="classic")

    def test_queue_generation_sufficient_credits(self, db, test_user):
        test_user.credits_balance = 100
        db.session.commit()

        with patch("services.queue_service.threading.Thread") as mock_thread:
            with patch("services.queue_service.generate_image_task.run"):
                from services.queue_service import queue_generation
                job_id = queue_generation(test_user.id, image_urls=["url1", "url2", "url3"], tipo_ensaio="classic")

                assert job_id is not None
                assert isinstance(job_id, str)
                assert len(job_id) == 36
                mock_thread.assert_called_once()

    def test_queue_generation_deducts_credits(self, db, test_user):
        test_user.credits_balance = 100
        db.session.commit()

        with patch("services.queue_service.threading.Thread"):
            with patch("services.queue_service.generate_image_task.run"):
                from services.queue_service import queue_generation
                queue_generation(test_user.id, image_urls=["url1", "url2", "url3"], tipo_ensaio="classic")

        from models.db_models import User
        updated = User.query.get(test_user.id)
        assert updated.credits_balance == 75

    def test_get_job_status_not_found(self, db):
        from services.queue_service import get_job_status
        result = get_job_status(str(uuid.uuid4()))
        assert result is None

    def test_get_job_status_found(self, db, test_user):
        from models.db_models import GenerationJob
        import json

        job = GenerationJob(
            id=str(uuid.uuid4()),
            user_id=test_user.id,
            status="completed",
            progress=100,
            message="Done",
            images_json=json.dumps(["img1.jpg"]),
        )
        db.session.add(job)
        db.session.commit()

        from services.queue_service import get_job_status
        result = get_job_status(job.id)
        assert result is not None
        assert result["status"] == "completed"
        assert result["images"] == ["img1.jpg"]

    def test_recover_stuck_jobs(self, db, test_user):
        from models.db_models import GenerationJob
        from datetime import datetime, timedelta

        stuck_job = GenerationJob(
            id=str(uuid.uuid4()),
            user_id=test_user.id,
            status="queued",
            updated_at=datetime.utcnow() - timedelta(hours=1),
            cost_moedas=25,
        )
        db.session.add(stuck_job)
        db.session.commit()

        from services.queue_service import recover_stuck_jobs

        mock_app = MagicMock()
        mock_app.app_context.return_value.__enter__.return_value = None

        with patch("services.queue_service._get_flask_app", return_value=mock_app):
            with patch("services.queue_service.refund_credits") as mock_refund:
                recover_stuck_jobs(mock_app)

                recovered = GenerationJob.query.get(stuck_job.id)
                assert recovered.status == "failed"
                mock_refund.assert_called_once()

    def test_queue_generation_rejects_inactive_user(self, db):
        from models.db_models import User
        inactive = User(
            id=str(uuid.uuid4()),
            name="Inactive",
            email="inactive@test.com",
            credits_balance=100,
            is_active=False,
        )
        inactive.set_password("123456")
        db.session.add(inactive)
        db.session.commit()

        from services.queue_service import queue_generation
        import pytest

        with pytest.raises(ValueError, match="inativo"):
            queue_generation(inactive.id, image_urls=["url1", "url2", "url3"], tipo_ensaio="classic")
