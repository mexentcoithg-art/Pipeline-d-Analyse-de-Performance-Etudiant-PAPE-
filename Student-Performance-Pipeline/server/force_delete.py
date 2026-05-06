import psycopg2

def force_delete():
    filename = "Students_Grading_Dataset_Biased.csv"
    try:
        conn = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="laure1282",
            dbname="student_db",
            port="5432"
        )
        cur = conn.cursor()
        
        # Find id_import
        cur.execute("SELECT id_import FROM Imports WHERE filename = %s", (filename,))
        row = cur.fetchone()
        if not row:
            print(f"Error: Import with filename '{filename}' not found.")
            # Let's see what's in the table
            cur.execute("SELECT id_import, filename FROM Imports")
            print(f"Current imports: {cur.fetchall()}")
            return
            
        id_import = row[0]
        print(f"Found id_import: {id_import} for {filename}")
        
        # Identify students
        cur.execute("SELECT id_etudiant FROM Etudiant WHERE id_import = %s", (id_import,))
        student_ids = [s[0] for s in cur.fetchall()]
        print(f"Found {len(student_ids)} students to delete.")
        
        if student_ids:
            # Delete related data in order to respect FKs if any
            tables = ["Predictions", "Note", "Absences", "Participations", "Interventions", "Alerts"]
            for table in tables:
                try:
                    print(f"Deleting from {table}...")
                    if table == "Alerts":
                        # We might need to match by massar_code or similar if no direct id_etudiant
                        pass 
                    else:
                        cur.execute(f"DELETE FROM {table} WHERE id_etudiant = ANY(%s)", (student_ids,))
                except Exception as ex:
                    print(f"Warning: Failed to delete from {table}: {ex}")
            
            # Delete students
            print("Deleting from Etudiant...")
            cur.execute("DELETE FROM Etudiant WHERE id_import = %s", (id_import,))
            
        # Delete import record
        print("Deleting from Imports...")
        cur.execute("DELETE FROM Imports WHERE id_import = %s", (id_import,))
        
        conn.commit()
        print("Deletion successful!")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error during force delete: {e}")

if __name__ == "__main__":
    force_delete()
