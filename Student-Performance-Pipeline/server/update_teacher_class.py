import psycopg2

conn = psycopg2.connect(
    host='localhost',
    user='postgres',
    password='laure1282',
    dbname='student_db'
)
cur = conn.cursor()

# Update teacher's assigned class to 3APIC-13
cur.execute("UPDATE Users SET class_assigned = '3APIC-13' WHERE username = 'teacher1'")
conn.commit()

# Verify the update
cur.execute("SELECT username, role, class_assigned FROM Users")
rows = cur.fetchall()
for row in rows:
    print(f"User: {row[0]}, Role: {row[1]}, Class: {row[2]}")

conn.close()
print("\nDone! Teacher1 is now assigned to class 3APIC-13")
