from app import create_app
from database import db
from sqlalchemy import text
import sys

app = create_app()
with app.app_context():
    try:
        print("--- Iniciando Sincronização do Banco de Dados ---")
        
        # Check database connection first
        db.session.execute(text("SELECT 1"))
        print("✅ Conexão com o banco de dados estabelecida.")

        print("⚠️ Removendo tabelas antigas para evitar conflitos de tipos...")
        # Drop in order to avoid foreign key issues
        tables = ['password_reset_tokens', 'generation_jobs', 'transactions', 'users']
        for table in tables:
            try:
                db.session.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                print(f"   - Tabela '{table}' removida.")
            except Exception as e:
                print(f"   - Erro ao remover '{table}': {e}")
        
        db.session.commit()
        
        print("🚀 Criando novas tabelas com o esquema atualizado...")
        db.create_all()
        
        print("✅ Banco de dados sincronizado com sucesso!")
        print("\nAgora você pode iniciar o servidor com: python app.py")
        
    except Exception as e:
        print(f"\n❌ Erro crítico ao sincronizar banco de dados: {e}")
        db.session.rollback()
        sys.exit(1)
