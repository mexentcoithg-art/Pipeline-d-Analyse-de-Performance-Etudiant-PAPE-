import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "student_db")

def create_powerbi_views():
    commands = [
        """
        DROP VIEW IF EXISTS powerbi_students_master CASCADE;
        """,
        """
        CREATE VIEW powerbi_students_master AS
        SELECT 
            e.id_etudiant,
            e.massar_code,
            e.gender,
            e.level,
            e.class_name,
            e.guardian_type,
            e.schooling_years,
            COALESCE(n.grade_final, 0) as final_average,
            COALESCE(a.nombre_absences, 0) as total_absences,
            COALESCE(p_part.avg_participation, 0) as average_participation,
            pred.predicted_g3 as ai_predicted_score,
            pred.niveau_risque as ai_risk_level,
            pred.facteur_top as ai_top_factor
        FROM Etudiant e
        LEFT JOIN (
            SELECT id_etudiant, grade_final FROM Note WHERE matiere = 'General'
        ) n ON e.id_etudiant = n.id_etudiant
        LEFT JOIN (
            SELECT id_etudiant, SUM(nombre_absences) as nombre_absences 
            FROM Absences GROUP BY id_etudiant
        ) a ON e.id_etudiant = a.id_etudiant
        LEFT JOIN (
            SELECT id_etudiant, AVG(score) as avg_participation 
            FROM Participations GROUP BY id_etudiant
        ) p_part ON e.id_etudiant = p_part.id_etudiant
        LEFT JOIN Predictions pred ON e.id_etudiant = pred.id_etudiant;
        """
    ]
    
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
            dbname=DB_NAME
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        for command in commands:
            cursor.execute(command)
            
        cursor.close()
        conn.close()
        print("[SUCCESS] Power BI Views created successfully in PostgreSQL.")
    except Exception as e:
        print(f"[ERROR] Could not create views: {e}")

if __name__ == "__main__":
    create_powerbi_views()
