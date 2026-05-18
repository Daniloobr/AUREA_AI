import os
from flask import Flask
from database import db
from models.db_models import User, PasswordResetToken, GenerationJob, Transaction
from config import Config
from sqlalchemy import text

app = Flask(__name__)
app.config.from_object(Config)
app.config['SQLALCHEMY_DATABASE_URI'] = Config.DATABASE_URI
db.init_app(app)

def update_schema():
    with app.app_context():
        print("Verificando atualizações de schema no Supabase...")
        
        # 1. Adicionar coluna is_admin se não existir
        try:
            db.session.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE"))
            db.session.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS phone VARCHAR(20)"))
            db.session.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS cpf VARCHAR(14)"))
            db.session.commit()
            print("Colunas is_admin, phone e cpf verificadas/adicionadas.")
        except Exception as e:
            print(f"Erro ao adicionar is_admin: {e}")
            db.session.rollback()

        # 2. Adicionar colunas de pagamento em transactions se não existirem
        try:
            db.session.execute(text("ALTER TABLE transactions ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'completed'"))
            db.session.execute(text("ALTER TABLE transactions ADD COLUMN IF NOT EXISTS external_id VARCHAR(100) UNIQUE"))
            db.session.execute(text("ALTER TABLE transactions ADD COLUMN IF NOT EXISTS paid_amount FLOAT"))
            db.session.commit()
            print("Colunas de pagamento em transactions verificadas/adicionadas.")
        except Exception as e:
            print(f"Erro ao adicionar colunas de pagamento: {e}")
            db.session.rollback()

        # 3. Adicionar coluna result_url em generation_jobs se não existir
        try:
            db.session.execute(text("ALTER TABLE generation_jobs ADD COLUMN IF NOT EXISTS result_url VARCHAR(500)"))
            db.session.commit()
            print("Coluna result_url em generation_jobs verificada/adicionada.")
        except Exception as e:
            print(f"Erro ao adicionar result_url: {e}")
            db.session.rollback()

        # 4. Criar tabela de tokens de reset se não existir
        try:
            db.create_all()
            print("Tabelas (incluindo PasswordResetToken) verificadas/criadas.")
        except Exception as e:
            print(f"Erro ao criar tabelas: {e}")

        print("Schema atualizado com sucesso!")

if __name__ == "__main__":
    update_schema()
