import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app import create_app
from database import db
from models.db_models import User, GenerationJob
from services.queue_service import process_generation_pipeline
from config import Config

def run_test():
    app = create_app()
    with app.app_context():
        # 1. Setup user
        user = User.query.filter_by(email='qa@aureaia.com').first()
        if not user:
            print("Usuário QA não encontrado. Por favor, rode prep_test_db.py")
            return

        # 2. Find a test image
        uploads_dir = Path(Config.UPLOAD_FOLDER)
        test_images = list(uploads_dir.glob("*.jpg")) + list(uploads_dir.glob("*.png"))
        if not test_images:
            print("Nenhuma imagem de teste em uploads/")
            return
        image_path = str(test_images[0])
        print(f"Usando imagem: {image_path}")
        
        # Copiar imagem pro bucket ou usar path local mockado como URL
        # Para testar, vamos passar como se fosse uma URL que já existe
        fake_url = "/uploads/" + os.path.basename(image_path)
        
        # 3. Create Job
        job = GenerationJob(
            id="test-job-999",
            user_id=user.id,
            tipo_ensaio="luxury_studio",
            input_image_url=fake_url,
            status="queued"
        )
        # Limpar jobs antigos de teste
        old_job = GenerationJob.query.get("test-job-999")
        if old_job:
            db.session.delete(old_job)
        db.session.add(job)
        db.session.commit()
        
        print(f"Job {job.id} criado. Status: {job.status}")
        
        # 4. Executar pipeline (vai chamar replicate e atualizar o banco)
        custom_prompt = "No jardim do Eden, flores douradas."
        print(f"Testando pipeline com estilo 'luxury_studio' e prompt customizado: '{custom_prompt}'")
        
        # Process generation pipeline expects image_urls as list
        # We'll just run it synchronously for testing
        process_generation_pipeline(app, job.id, [fake_url], "luxury_studio", custom_prompt=custom_prompt)
        
        # 5. Verificar resultado no banco
        db.session.refresh(job)
        print("="*50)
        print("RESULTADO DO JOB NO BANCO DE DADOS:")
        print(f"Status: {job.status}")
        print(f"Progress: {job.progress}")
        print(f"Message: {job.message}")
        print(f"Result URL: {job.result_url}")
        print(f"Images JSON: {job.images_json}")
        
        job_dict = job.to_dict()
        print(f"To_Dict() output URL: {job_dict.get('result_url')}")
        print("="*50)

if __name__ == "__main__":
    run_test()
