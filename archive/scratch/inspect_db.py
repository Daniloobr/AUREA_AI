
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

with engine.connect() as connection:
    result = connection.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'id'"))
    for row in result:
        print(f"Table 'users', Column 'id' type: {row[1]}")

    result = connection.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
    tables = [row[0] for row in result]
    print(f"Tables in database: {tables}")
