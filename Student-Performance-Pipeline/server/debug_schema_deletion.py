import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

def check():
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            dbname=os.getenv('DB_NAME'),
            port=os.getenv('DB_PORT')
        )
        cur = conn.cursor()
        
        print("--- Checking Tables ---")
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = [t[0] for t in cur.fetchall()]
        print(f"Tables: {tables}")
        
        print("\n--- Checking Imports Columns ---")
        if 'imports' in [t.lower() for t in tables]:
            cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'imports'")
            print(cur.fetchall())
        else:
            print("Imports table NOT found!")
            
        print("\n--- Checking Etudiant Columns ---")
        cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'etudiant'")
        print(cur.fetchall())
        
        cur.execute("SELECT count(*) FROM Imports")
        print(f"\nImport count: {cur.fetchone()[0]}")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check()
