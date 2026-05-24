import os
import sys

# Add the parent directory to the path so we can import app and database
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from database import db
from models.db_models import User

def create_or_update_test_user(email="teste@aureaia.com", password="teste123", coins=99999):
    app = create_app()
    with app.app_context():
        # Check if user already exists
        user = User.query.filter_by(email=email).first()
        if user:
            user.credits_balance = coins
            user.set_password(password)
            user.is_active = True
            db.session.commit()
            print(f"[SUCCESS] Usuario '{email}' ja existia. Saldo atualizado para {coins} moedas e senha redefinida para '{password}'!")
        else:
            # Create new user
            new_user = User(
                name="Testador AureaAI",
                email=email,
                credits_balance=coins,
                is_admin=True,
                is_active=True
            )
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            print(f"[SUCCESS] Novo usuario criado com sucesso!")
            print(f"Email: {email}")
            print(f"Senha: {password}")
            print(f"Saldo: {coins} moedas")

if __name__ == "__main__":
    create_or_update_test_user()
