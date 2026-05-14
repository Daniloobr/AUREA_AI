import sys
import os

# Adiciona o diretório atual ao path para importar os módulos locais
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from database import db
from models.db_models import User

def create_admin_user(name, email, password, credits=999999):
    app = create_app()
    with app.app_context():
        # Verifica se o usuário já existe
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            print(f"⚠️ Usuário com email {email} já existe. Atualizando para Admin e adicionando moedas...")
            existing_user.is_admin = True
            existing_user.credits_balance = credits
            existing_user.set_password(password)
            db.session.commit()
            print(f"✅ Usuário {email} atualizado com sucesso!")
            return

        # Cria novo usuário admin
        new_admin = User(
            name=name,
            email=email,
            credits_balance=credits,
            is_admin=True
        )
        new_admin.set_password(password)
        
        db.session.add(new_admin)
        db.session.commit()
        print(f"🚀 Admin '{name}' criado com sucesso!")
        print(f"📧 Email: {email}")
        print(f"💰 Moedas: {credits}")

if __name__ == "__main__":
    # Configurações padrão para o teste do usuário
    ADMIN_NAME = "Admin Teste"
    ADMIN_EMAIL = "admin@teste.com"
    ADMIN_PASS = "admin123" # Senha simples para teste
    
    create_admin_user(ADMIN_NAME, ADMIN_EMAIL, ADMIN_PASS)
