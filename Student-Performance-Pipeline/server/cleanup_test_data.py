import psycopg2

conn = psycopg2.connect(host='localhost', user='postgres', password='laure1282', port='5432', dbname='student_db')
cur = conn.cursor()

# 1. Find all test student IDs
cur.execute("SELECT id_etudiant FROM Etudiant WHERE massar_code LIKE 'UPLOAD_%'")
test_ids = [r[0] for r in cur.fetchall()]
print(f"Found {len(test_ids)} test records to delete.")

if test_ids:
    # 2. Delete related data
    cur.execute("DELETE FROM Predictions WHERE id_etudiant = ANY(%s)", (test_ids,))
    print(f"  Predictions deleted: {cur.rowcount}")
    
    cur.execute("DELETE FROM Note WHERE id_etudiant = ANY(%s)", (test_ids,))
    print(f"  Notes deleted: {cur.rowcount}")
    
    cur.execute("DELETE FROM Absences WHERE id_etudiant = ANY(%s)", (test_ids,))
    print(f"  Absences deleted: {cur.rowcount}")
    
    cur.execute("DELETE FROM Participations WHERE id_etudiant = ANY(%s)", (test_ids,))
    print(f"  Participations deleted: {cur.rowcount}")
    
    cur.execute("DELETE FROM Interventions WHERE id_etudiant = ANY(%s)", (test_ids,))
    print(f"  Interventions deleted: {cur.rowcount}")
    
    # 3. Delete test students
    cur.execute("DELETE FROM Etudiant WHERE massar_code LIKE 'UPLOAD_%'")
    print(f"  Etudiants test supprimes: {cur.rowcount}")

# 4. Create an Import record for the original data
cur.execute("""
    INSERT INTO Imports (filename, row_count, status)
    VALUES ('Donnees_Massar_Initial_2024.xlsx', 1738, 'Predicted')
    RETURNING id_import
""")
id_import = cur.fetchone()[0]
print(f"\nImport initial cree avec id={id_import}")

# 5. Associate all remaining students with this import
cur.execute("UPDATE Etudiant SET id_import = %s WHERE id_import IS NULL", (id_import,))
print(f"Etudiants associes a l'import initial: {cur.rowcount}")

conn.commit()

# Verify
cur.execute("SELECT COUNT(*) FROM Etudiant")
print(f"\nTotal etudiants final: {cur.fetchone()[0]}")

conn.close()
print("Nettoyage termine!")
