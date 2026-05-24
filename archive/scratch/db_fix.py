import os
from dotenv import load_dotenv
load_dotenv()
import psycopg2

print("Connecting to Supabase PostgreSQL...")
conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
conn.autocommit = True
cur = conn.cursor()

print("Killing active idle queries to release locks...")
try:
    cur.execute("""
        SELECT pg_terminate_backend(pid) 
        FROM pg_stat_activity 
        WHERE pid != pg_backend_pid() 
          AND (state = 'idle' OR state = 'idle in transaction')
    """)
    terminated = cur.fetchall()
    print(f"Terminated {len(terminated)} idle connections.")
except Exception as e:
    print(f"Could not terminate idle queries: {e}")

print("Adding result_url column to generation_jobs table...")
try:
    cur.execute("ALTER TABLE generation_jobs ADD COLUMN IF NOT EXISTS result_url VARCHAR(500)")
    print("Column result_url added successfully!")
except Exception as e:
    print(f"Could not add column: {e}")

cur.close()
conn.close()
