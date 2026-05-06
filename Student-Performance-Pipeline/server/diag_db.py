import psycopg2
from psycopg2.extras import RealDictCursor
import os

def check():
    print("--- Diagnostic Start ---")
    try:
        conn = psycopg2.connect(host='localhost', user='postgres', password='laure1282', dbname='student_db')
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check Etudiant count
        cur.execute("SELECT COUNT(*) FROM Etudiant")
        print(f"Total Etudiants: {cur.fetchone()['count']}")
        
        # Check column names in Etudiant
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'etudiant'")
        cols = [r['column_name'] for r in cur.fetchall()]
        print(f"Etudiant cols: {cols}")

        # Check Note matiere distribution
        cur.execute("SELECT matiere, COUNT(*) FROM Note GROUP BY matiere")
        matieres = cur.fetchall()
        print(f"Matiere counts: {matieres}")
        
        # Check specific JOIN for class comparison
        # Using the column name from the list above if it differs
        col_name = 'class_name' if 'class_name' in cols else 'school'
        query = f"SELECT e.{col_name}, AVG(n.grade_final) as avg_grade FROM Etudiant e JOIN Note n ON e.id_etudiant = n.id_etudiant WHERE n.matiere = 'General' GROUP BY 1"
        try:
            cur.execute(query)
            rows = cur.fetchall()
            print(f"Class comp count: {len(rows)}")
            if rows:
                print(f"Class comp sample: {rows[:3]}")
            else:
                print("Class comp query returned empty! Checking why...")
                cur.execute("SELECT COUNT(*) FROM Note WHERE matiere = 'General' AND grade_final IS NOT NULL")
                print(f"Notes with General & non-null grade: {cur.fetchone()['count']}")
        except Exception as e:
            print(f"Query Error ({query}): {e}")
        
        conn.close()
    except Exception as e:
        print(f"DB Error: {e}")
    print("--- Diagnostic End ---")

if __name__ == '__main__':
    check()

if __name__ == '__main__':
    check()
