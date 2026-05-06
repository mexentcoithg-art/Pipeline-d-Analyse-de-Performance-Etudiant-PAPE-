import psycopg2

def check_db():
    try:
        conn = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="laure1282",
            dbname="student_db",
            port="5432"
        )
        cur = conn.cursor()
        
        print("--- Tables in public schema ---")
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        print([t[0] for t in cur.fetchall()])
        
        print("\n--- Student Counts ---")
        cur.execute("SELECT count(*) FROM Etudiant")
        total = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM Etudiant WHERE id_import IS NULL")
        orphans = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM Etudiant WHERE id_import IS NOT NULL")
        linked = cur.fetchone()[0]
        print(f"Total: {total}, orphans: {orphans}, linked: {linked}")
        
        print("\n--- Imports Table Content ---")
        cur.execute("SELECT * FROM Imports")
        rows = cur.fetchall()
        print(f"Rows: {rows}")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_db()
