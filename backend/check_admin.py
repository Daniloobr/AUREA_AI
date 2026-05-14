import sys
import os

# Adiciona o diretório atual ao path para importar os módulos locais
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from database import db
from models.db_models import User

def check_admin():
    app = create_app()
    with app.app_context():
        admin = User.query.filter_by(email="admin@teste.com").first()
        if admin:
            print(f"Admin found: {admin.name}")
            print(f"Credits: {admin.credits_balance}")
            print(f"Is Admin: {admin.is_admin}")
        else:
            print("Admin not found.")

if __name__ == "__main__":
    check_admin()
