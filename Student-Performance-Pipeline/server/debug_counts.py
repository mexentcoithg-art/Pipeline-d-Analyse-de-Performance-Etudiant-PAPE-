import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

def count_stats():
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            dbname=os.getenv('DB_NAME'),
            port=os.getenv('DB_PORT'),
            connect_timeout=5
        )
        cur = conn.cursor()
        
        print("--- Imports ---")
        cur.execute("SELECT id_import, filename, status, row_count FROM Imports")
        imports = cur.fetchall()
        for imp in imports:
            cur.execute("SELECT count(*) FROM Etudiant WHERE id_import = %s", (imp[0],))
            count = cur.fetchone()[0]
            print(f"ID: {imp[0]}, File: {imp[1]}, Status: {imp[2]}, Declared: {imp[3]}, Actual: {count}")
            
        print("\n--- Students with No Import ID ---")
        cur.execute("SELECT count(*) FROM Etudiant WHERE id_import IS NULL")
        print(f"Count: {cur.fetchone()[0]}")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    count_stats()
