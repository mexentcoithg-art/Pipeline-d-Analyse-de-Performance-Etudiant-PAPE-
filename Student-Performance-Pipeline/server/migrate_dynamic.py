"""
Migration script: Add dynamic pipeline tables.
Does NOT modify existing tables (Etudiant, Note, Absences, Participations, Predictions).
"""
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    user=os.getenv('DB_USER', 'postgres'),
    password=os.getenv('DB_PASSWORD', 'laure1282'),
    port=os.getenv('DB_PORT', '5432'),
    dbname=os.getenv('DB_NAME', 'student_db')
)
cur = conn.cursor()

# 1. Add new columns to Imports table (safe - uses IF NOT EXISTS pattern)
print("[1/3] Updating Imports table...")
try:
    cur.execute("ALTER TABLE Imports ADD COLUMN IF NOT EXISTS mode VARCHAR(20) DEFAULT 'add'")
    cur.execute("ALTER TABLE Imports ADD COLUMN IF NOT EXISTS target_column VARCHAR(100)")
    cur.execute("ALTER TABLE Imports ADD COLUMN IF NOT EXISTS id_column VARCHAR(100)")
    cur.execute("ALTER TABLE Imports ADD COLUMN IF NOT EXISTS columns_detected TEXT[]")
    cur.execute("ALTER TABLE Imports ADD COLUMN IF NOT EXISTS is_dynamic BOOLEAN DEFAULT FALSE")
    conn.commit()
    print("   OK - Columns added to Imports")
except Exception as e:
    conn.rollback()
    print(f"   SKIP - {e}")

# 2. Create ImportedData table for flexible JSONB storage
print("[2/3] Creating ImportedData table...")
cur.execute("""
    CREATE TABLE IF NOT EXISTS ImportedData (
        id SERIAL PRIMARY KEY,
        id_import INTEGER NOT NULL REFERENCES Imports(id_import) ON DELETE CASCADE,
        row_index INTEGER NOT NULL,
        student_id VARCHAR(100),
        raw_data JSONB NOT NULL,
        predicted_value FLOAT,
        risk_level VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
cur.execute("CREATE INDEX IF NOT EXISTS idx_imported_data_import ON ImportedData(id_import)")
cur.execute("CREATE INDEX IF NOT EXISTS idx_imported_data_raw ON ImportedData USING GIN(raw_data)")
conn.commit()
print("   OK - ImportedData table created")

# 3. Verify
print("[3/3] Verifying...")
cur.execute("""
    SELECT column_name FROM information_schema.columns 
    WHERE table_name = 'imports' ORDER BY ordinal_position
""")
cols = [r[0] for r in cur.fetchall()]
print(f"   Imports columns: {cols}")

cur.execute("""
    SELECT column_name FROM information_schema.columns 
    WHERE table_name = 'importeddata' ORDER BY ordinal_position
""")
cols = [r[0] for r in cur.fetchall()]
print(f"   ImportedData columns: {cols}")

conn.close()
print("\nMigration complete!")
