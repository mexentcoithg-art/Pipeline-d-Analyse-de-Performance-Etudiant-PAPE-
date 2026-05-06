import psycopg2
conn = psycopg2.connect('dbname=student_db user=postgres password=laure1282 host=localhost')
c = conn.cursor()
c.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'absences'")
print("Absences:", c.fetchall())

c.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'note'")
print("Note:", c.fetchall())
conn.close()
