import psycopg2

conn = psycopg2.connect(host='localhost', user='postgres', password='laure1282', port='5432', dbname='student_db')
cur = conn.cursor()

# Check for patterns in massar_codes - original data has codes like E1XXXXXXXX
# Test uploads may have codes like UPLOAD_XX or other patterns
cur.execute("SELECT massar_code FROM Etudiant WHERE massar_code LIKE 'UPLOAD_%' ORDER BY massar_code LIMIT 20")
upload_codes = cur.fetchall()
print('Codes UPLOAD_:', len(upload_codes))
for c in upload_codes[:5]:
    print('  ', c[0])

# Check massar_code patterns
cur.execute("""
    SELECT 
        CASE 
            WHEN massar_code LIKE 'E%' THEN 'E-prefix (Massar)'
            WHEN massar_code LIKE 'UPLOAD_%' THEN 'UPLOAD_ (test)'
            ELSE 'Other: ' || LEFT(massar_code, 10)
        END as pattern,
        COUNT(*) 
    FROM Etudiant 
    GROUP BY 1 
    ORDER BY 2 DESC
""")
patterns = cur.fetchall()
print('\nPatterns de codes Massar:')
for p in patterns:
    print(f'  {p[0]}: {p[1]} etudiants')

# Check the range of id_etudiant - the original 1738 should be the first ones
cur.execute("SELECT MIN(id_etudiant), MAX(id_etudiant) FROM Etudiant")
r = cur.fetchone()
print(f'\nRange id_etudiant: {r[0]} -> {r[1]}')

# Show the last 10 recent students (likely test data)
cur.execute("SELECT id_etudiant, massar_code, class_name FROM Etudiant ORDER BY id_etudiant DESC LIMIT 10")
recent = cur.fetchall()
print('\n10 derniers etudiants (potentiellement parasites):')
for r in recent:
    print(f'  id={r[0]}, massar={r[1]}, classe={r[2]}')

conn.close()
