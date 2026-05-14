
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

with engine.connect() as connection:
    result = connection.execute(text("SELECT table_schema, column_name, data_type FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'id'"))
    for row in result:
        print(f"Schema: {row[0]}, Table 'users', Column 'id' type: {row[2]}")
