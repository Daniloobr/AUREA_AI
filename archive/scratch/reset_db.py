
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

with engine.connect() as connection:
    print("Dropping existing tables to fix schema mismatch...")
    # Drop in reverse order of dependencies
    connection.execute(text("DROP TABLE IF EXISTS password_reset_tokens CASCADE"))
    connection.execute(text("DROP TABLE IF EXISTS transactions CASCADE"))
    connection.execute(text("DROP TABLE IF EXISTS generation_jobs CASCADE"))
    connection.execute(text("DROP TABLE IF EXISTS users CASCADE"))
    connection.commit()
    print("Tables dropped successfully.")
