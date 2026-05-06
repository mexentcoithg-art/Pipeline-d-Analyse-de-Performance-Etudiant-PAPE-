import psycopg2
from psycopg2 import sql
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# We'll use the default postgres database first to create our student_db
DB_HOST = "localhost"
DB_USER = "postgres"
DB_PASSWORD = "postgres"  # New password requested by user
DB_PORT = "5432"
DB_NAME = "student_db"

def create_database():
    try:
        # Connect to template1 to create the new DB and avoid locked file errors
        conn = psycopg2.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
            dbname="template1"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Drop if exists to recreate with correct encoding
        cursor.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(DB_NAME)))
        cursor.execute(sql.SQL("CREATE DATABASE {} ENCODING 'UTF8' TEMPLATE template0").format(sql.Identifier(DB_NAME)))
        print(f"[SUCCESS] Database '{DB_NAME}' created successfully with UTF8 encoding.")
            
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[ERROR] Error creating database: {e}")
        return False
    return True

def create_tables():
    commands = (
        """
        CREATE TABLE IF NOT EXISTS Etudiant (
            id_etudiant SERIAL PRIMARY KEY,
            massar_code VARCHAR(20) UNIQUE,
            gender VARCHAR(10),
            schooling_years INTEGER,
            level VARCHAR(20),
            class_name VARCHAR(20),
            guardian_type VARCHAR(50),
            guardian2_job VARCHAR(100)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS Note (
            id_note SERIAL PRIMARY KEY,
            id_etudiant INTEGER REFERENCES Etudiant(id_etudiant) ON DELETE CASCADE,
            matiere VARCHAR(50) NOT NULL,
            cc1 NUMERIC(5,2),
            cc2 NUMERIC(5,2),
            cc3 NUMERIC(5,2),
            activite NUMERIC(5,2),
            grade_final NUMERIC(5,2)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS Absences (
            id_absence SERIAL PRIMARY KEY,
            id_etudiant INTEGER REFERENCES Etudiant(id_etudiant) ON DELETE CASCADE,
            matiere VARCHAR(50),
            nombre_absences NUMERIC(5,2),
            type_absence BOOLEAN DEFAULT false
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS Participations (
            id_participation SERIAL PRIMARY KEY,
            id_etudiant INTEGER REFERENCES Etudiant(id_etudiant) ON DELETE CASCADE,
            matiere VARCHAR(50),
            score NUMERIC(5,2) CHECK (score >= 0 AND score <= 20),
            observation TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS Predictions (
            id_prediction SERIAL PRIMARY KEY,
            id_etudiant INTEGER REFERENCES Etudiant(id_etudiant) ON DELETE CASCADE,
            predicted_g3 NUMERIC(5,2),
            niveau_risque VARCHAR(20),
            date_prediction TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            facteur_top VARCHAR(100)
        )
        """
    )
    
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
            dbname=DB_NAME
        )
        cursor = conn.cursor()
        
        for command in commands:
            cursor.execute(command)
            
        conn.commit()
        cursor.close()
        conn.close()
        print("[SUCCESS] Tables created successfully.")
        return True
    except Exception as e:
        print(f"[ERROR] Error creating tables: {e}")
        return False

def import_xlsx_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.abspath(os.path.join(base_dir, "data", "ML_Dataset_Massar.xlsx"))
    
    if not os.path.exists(data_path):
        print(f"[ERROR] XLSX file not found at {data_path}")
        return
        
    try:
        conn = psycopg2.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, port=DB_PORT, dbname=DB_NAME)
        conn.set_client_encoding('UTF8')
        cursor = conn.cursor()
        
        # Read the Excel file, handling missing values natively
        df = pd.read_excel(data_path)
        # Clean Pandas NA to None for psycopg2
        df = df.where(pd.notnull(df), None)
        
        count = 0
        
        # Clear existing data slightly for fresh import
        cursor.execute("TRUNCATE TABLE Etudiant CASCADE")
        
        for _, row in df.iterrows():
            id_etudiant_str = str(row['MassarCode'])
            
            # Map Arabic Sexe to French
            raw_gender = str(row.get('Gender', '')).strip()
            if 'أنثى' in raw_gender:
                gender = 'F'
            elif 'ذكر' in raw_gender:
                gender = 'M'
            else:
                gender = 'Inconnu'
                
            # Map Arabic Tuteur to French
            raw_tuteur = str(row.get('GuardianType', '')).strip()
            if 'أب' in raw_tuteur:
                tuteur = 'Père'
            elif 'أم' in raw_tuteur:
                tuteur = 'Mère'
            elif 'أخ' in raw_tuteur or 'أخت' in raw_tuteur:
                tuteur = 'Fratrie'
            elif 'خال' in raw_tuteur or 'عم' in raw_tuteur:
                tuteur = 'Oncle'
            else:
                tuteur = 'Autre'

            # Define levels
            level = '3APIC'
            schooling_years = 3

            # Insert or ignore Etudiant
            cursor.execute("""
                INSERT INTO Etudiant (massar_code, level, class_name, gender, schooling_years, guardian_type)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (massar_code) DO NOTHING
                RETURNING id_etudiant
            """, (id_etudiant_str, level, row.get('Class', '3APIC-01'), gender, schooling_years, tuteur))
            
            # Fetch id_etudiant. If ON CONFLICT DO NOTHING was triggered, fetchone() will return None.
            # In that case, we need to query for the existing id_etudiant.
            id_etudiant_result = cursor.fetchone()
            if id_etudiant_result:
                id_etudiant = id_etudiant_result[0]
            else:
                # If student already exists, retrieve their id_etudiant
                cursor.execute("SELECT id_etudiant FROM Etudiant WHERE massar_code = %s", (id_etudiant_str,))
                id_etudiant = cursor.fetchone()[0]
            
            # 2. Insert Absences
            absences = row.get('TotalAbsences')
            if absences is not None:
                cursor.execute("""
                    INSERT INTO Absences (id_etudiant, matiere, nombre_absences)
                    VALUES (%s, %s, %s)
                """, (id_etudiant, 'General', float(absences)))
                
            # 3. Handle Subjects Dynamic Columns
            subjects_found = set()
            for col in df.columns:
                if '_CC' in col or '_Act' in col or 'Participation_' in col:
                    if col.startswith('Participation_'):
                        subj = col.replace('Participation_', '')
                        subjects_found.add(subj)
                    else:
                        subj = col.split('_')[0]
                        subjects_found.add(subj)
            
            # General Average Insert
            gen_avg = row.get('GeneralAverage')
            if pd.notna(gen_avg) and gen_avg is not None:
                try: gen_avg = float(str(gen_avg).replace(',', '.'))
                except: gen_avg = None
                
                if gen_avg is not None:
                    cursor.execute("""
                        INSERT INTO Note (id_etudiant, matiere, grade_final)
                        VALUES (%s, 'General', %s)
                    """, (id_etudiant, gen_avg))

            def clean_val(v):
                if v is None or pd.isna(v): return None
                try: return float(v)
                except: return None

            # Matieres iterations
            for subj in subjects_found:
                # Notes
                cc1 = clean_val(row.get(f"{subj}_CC1"))
                cc2 = clean_val(row.get(f"{subj}_CC2"))
                cc3 = clean_val(row.get(f"{subj}_CC3"))
                act = clean_val(row.get(f"{subj}_Act"))
                
                if any(x is not None for x in [cc1, cc2, cc3, act]):
                    cursor.execute("""
                        INSERT INTO Note (id_etudiant, matiere, cc1, cc2, cc3, activite)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (id_etudiant, subj, cc1, cc2, cc3, act))
                
                # Particpation
                part = clean_val(row.get(f"Participation_{subj}"))
                if part is not None:
                    cursor.execute("""
                        INSERT INTO Participations (id_etudiant, matiere, score, observation)
                        VALUES (%s, %s, %s, 'Importé depuis XLSX')
                    """, (id_etudiant, subj, part))
                    
            count += 1
            if count % 100 == 0:
                print(f"Imported {count} students...")
                
        conn.commit()
        cursor.close()
        conn.close()
        print(f"[SUCCESS] Successfully imported {count} students into PostgreSQL.")
        
    except Exception as e:
        import traceback
        with open("insert_error.log", "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        print("[ERROR] Error inserting data. Check insert_error.log for details.")

if __name__ == "__main__":
    print("[INFO] Starting Database Setup with new Massar Dataset...")
    if create_database():
        if create_tables():
            import_xlsx_data()
