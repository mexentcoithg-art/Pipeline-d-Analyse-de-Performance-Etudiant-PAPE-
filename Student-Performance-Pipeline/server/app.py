from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import os
import io
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from werkzeug.security import check_password_hash
from datetime import datetime
from fpdf import FPDF
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

import pipeline.analytics as analytics

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "super-secret-key-pfe-2024")
CORS(app)  # Enable CORS for React frontend

# Database Configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "laure1282")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "student_db")

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
            dbname=DB_NAME
        )
        return conn
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return None

@app.route('/api/reports/student/<string:massar_code>', methods=['GET'])
def generate_report(massar_code):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Erreur de connexion"}), 500
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        # Fetch student data
        query = """
            SELECT e.*, n.grade_final as G3, a.nombre_absences as absences, 
                   pr.predicted_g3, pr.niveau_risque, pr.facteur_top, pr.probabilite_succes, pr.recommandation
            FROM Etudiant e
            LEFT JOIN Note n ON e.id_etudiant = n.id_etudiant AND n.matiere = 'General'
            LEFT JOIN Absences a ON e.id_etudiant = a.id_etudiant AND a.matiere = 'General'
            LEFT JOIN Predictions pr ON e.id_etudiant = pr.id_etudiant
            WHERE e.massar_code = %s
        """
        cursor.execute(query, (massar_code,))
        student = cursor.fetchone()
        
        if not student:
            return jsonify({"error": "Étudiant non trouvé"}), 404
            
        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 20)
        pdf.set_text_color(63, 81, 181) # Indigo
        pdf.cell(0, 20, "RAPPORT PEDAGOGIQUE INDIVIDUEL", ln=True, align='C')
        pdf.ln(10)
        
        # Student Info Header
        pdf.set_font("Arial", 'B', 14)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 10, f"Code Massar: {student['massar_code']}", ln=True)
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 8, f"Classe: {student['class_name'] or 'N/A'}", ln=True)
        pdf.cell(0, 8, f"Niveau: {student['level'] or 'N/A'}", ln=True)
        pdf.ln(5)
        
        # AI Predictions
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(63, 81, 181) # Indigo
        pdf.cell(0, 10, " ANALYSE PREDICTIVE (IA)", ln=True)
        pdf.ln(2)
        
        prob_val = float(student['probabilite_succes']) if student['probabilite_succes'] is not None else 0
        prob_pct = f"{prob_val * 100:.1f}%"
        risk_level = student['niveau_risque'] or "Stable"
        facteur = student['facteur_top'] or "N/A"
        recommandation = student['recommandation'] or "Aucune recommandation."
        
        pdf.set_font("Arial", '', 11)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(90, 8, f"Probabilite de Reussite: {prob_pct}", ln=False)
        pdf.cell(90, 8, f"Statut: {risk_level}", ln=True)
        pdf.cell(0, 8, f"Facteur d'Influence Principal: {facteur}", ln=True)
        
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 10, "RECOMMANDATIONS PÉDAGOGIQUES", ln=True)
        pdf.set_font("Arial", 'I', 11)
        pdf.multi_cell(0, 8, recommandation)
        
        # Interventions History
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, " HISTORIQUE DES INTERVENTIONS", ln=True)
        pdf.ln(2)
        
        cursor.execute("""
            SELECT i.*, u.username FROM Interventions i 
            JOIN Users u ON i.id_user = u.id_user 
            WHERE id_etudiant = %s ORDER BY date_action DESC
        """, (student['id_etudiant'],))
        interventions = cursor.fetchall()
        
        pdf.set_font("Arial", '', 10)
        if not interventions:
            pdf.cell(0, 8, "Aucune intervention enregistree.", ln=True)
        else:
            for inv in interventions:
                pdf.set_font("Arial", 'B', 10)
                pdf.cell(0, 6, f"{inv['date_action'].strftime('%d/%m/%Y')} - {inv['type_action']} (Par: {inv['username']})", ln=True)
                pdf.set_font("Arial", '', 10)
                pdf.multi_cell(0, 6, f"Description: {inv['description']}")
                pdf.cell(0, 6, f"Statut: {inv['status_efficacite']}", ln=True)
                pdf.ln(2)
        
        # Footer
        pdf.set_y(-20)
        pdf.set_font("Arial", 'I', 8)
        pdf.set_text_color(150, 150, 150)
        pdf.cell(0, 10, f"Genere le {datetime.now().strftime('%d/%m/%Y %H:%M')} par Student Performance Pipeline", align='C')

        # Output to buffer
        pdf_bytes = pdf.output(dest='S')
        output = io.BytesIO(pdf_bytes)
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"Rapport_{massar_code}.pdf"
        )
        
    except Exception as e:
        print(f"[PDF ERROR] {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


@app.route('/')
def home():
    return jsonify({"message": "Student Performance Pipeline API is running", "status": "success"})

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"})

# --- AUTHENTICATION ENDPOINTS ---

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Nom d'utilisateur et mot de passe requis"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Erreur de connexion base de données"}), 500
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM Users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password_hash'], password):
            # return user info (don't send hash!)
            return jsonify({
                "status": "success",
                "user": {
                    "id": user['id_user'],
                    "username": user['username'],
                    "role": user['role'],
                    "class_assigned": user['class_assigned']
                }
            })
        else:
            return jsonify({"error": "Identifiants invalides"}), 401
    except Exception as e:
        print(f"[ERROR] Login: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

# --- INTERVENTIONS ENDPOINTS ---

@app.route('/api/interventions/<string:student_id>', methods=['GET'])
def get_interventions(student_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Erreur de connexion"}), 500
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT i.*, u.username as creator_name 
            FROM Interventions i
            JOIN Users u ON i.id_user = u.id_user
            JOIN Etudiant e ON i.id_etudiant = e.id_etudiant
            WHERE e.massar_code = %s
            ORDER BY i.date_action DESC
        """, (student_id,))
        return jsonify(cursor.fetchall())
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/interventions', methods=['POST'])
def add_intervention():
    data = request.json
    required = ['id_etudiant', 'type_action', 'id_user']
    if not all(k in data for k in required):
        return jsonify({"error": "Champs requis manquants"}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Erreur de connexion"}), 500
    try:
        cursor = conn.cursor()
        
        # Get internal id_etudiant from massar_code
        cursor.execute("SELECT id_etudiant FROM Etudiant WHERE massar_code = %s", (data['id_etudiant'],))
        res = cursor.fetchone()
        if not res:
            return jsonify({"error": "Student not found"}), 404
        internal_id = res[0]

        cursor.execute("""
            INSERT INTO Interventions (id_etudiant, type_action, description, id_user, status_efficacite)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id_intervention
        """, (internal_id, data['type_action'], data.get('description'), 
              data['id_user'], data.get('status_efficacite', 'En cours')))
        new_id = cursor.fetchone()[0]
        conn.commit()
        return jsonify({"status": "success", "id": new_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

# --- TEMPORAL & ANALYTICS ENDPOINTS ---

@app.route('/api/temporal-stats')
def get_temporal_stats():
    conn = get_db_connection()
    if not conn:
        return jsonify([]), 500
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        query = """
            SELECT 
                class_name as name, 
                AVG(grade_final) as value
            FROM Etudiant e
            JOIN Note n ON e.id_etudiant = n.id_etudiant
            WHERE n.matiere = 'General'
            GROUP BY class_name
            ORDER BY class_name
        """
        cursor.execute(query)
        results = cursor.fetchall()
        # Convert Decimal to float for JSON
        for row in results:
            if 'value' in row and row['value'] is not None:
                row['value'] = float(row['value'])
        return jsonify(results)
    except Exception as e:
        print(f"[ERROR] Temporal Stats: {e}")
        return jsonify([])
    finally:
        conn.close()

@app.route('/api/feature-importance')
def get_feature_importance():
    # TEMPORARY: Disabled joblib load as it hangs the dev server
    return jsonify([
        {"name": "Absences", "value": 0.35},
        {"name": "Moyenne G1/G2", "value": 0.25},
        {"name": "Note Maths", "value": 0.15},
        {"name": "Note Français", "value": 0.10},
        {"name": "Participation", "value": 0.08},
        {"name": "Assiduité", "value": 0.07}
    ])

@app.route('/api/class-comparison')
def get_class_comparison():
    conn = get_db_connection()
    if not conn:
        return jsonify([]), 500
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        query = """
            SELECT 
                class_name as class_name, 
                AVG(grade_final) as avg_grade,
                COUNT(*) as student_count
            FROM Etudiant e
            JOIN Note n ON e.id_etudiant = n.id_etudiant
            WHERE n.matiere = 'General'
            GROUP BY class_name
            ORDER BY avg_grade DESC
        """
        cursor.execute(query)
        results = cursor.fetchall()
        for row in results:
            if 'avg_grade' in row and row['avg_grade'] is not None:
                row['avg_grade'] = float(row['avg_grade'])
        return jsonify(results)
    except Exception as e:
        print(f"[ERROR] Class Comparison: {e}")
        return jsonify([]), 500
    finally:
        conn.close()
@app.route('/api/stats')
def get_stats():
    conn = get_db_connection()
    if not conn:
        return jsonify({"averageGrade": 0, "passRate": 0, "absences": 0, "atRisk": 0}), 500
        
    try:
        class_name = request.args.get('class_name')
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # 1. Total Students
        if class_name:
            cursor.execute("SELECT COUNT(*) as count FROM Etudiant WHERE class_name = %s", (class_name,))
        else:
            cursor.execute("SELECT COUNT(*) as count FROM Etudiant")
        count = cursor.fetchone()['count']
        
        if count == 0:
            return jsonify({"averageGrade": 0, "passRate": 0, "absences": 0, "atRisk": 0})
            
        # 2. Average Grade (Using General G3)
        if class_name:
            cursor.execute("""
                SELECT AVG(n.grade_final) as avg_grade 
                FROM Note n 
                JOIN Etudiant e ON n.id_etudiant = e.id_etudiant
                WHERE n.matiere = 'General' AND n.grade_final IS NOT NULL AND e.class_name = %s
            """, (class_name,))
        else:
            cursor.execute("SELECT AVG(grade_final) as avg_grade FROM Note WHERE matiere = 'General' AND grade_final IS NOT NULL")
        avg_grade = cursor.fetchone()['avg_grade']
        
        # 3. Passed / At Risk Count
        if class_name:
            cursor.execute("""
                SELECT COUNT(*) as passed 
                FROM Note n 
                JOIN Etudiant e ON n.id_etudiant = e.id_etudiant
                WHERE n.matiere = 'General' AND n.grade_final >= 10 AND e.class_name = %s
            """, (class_name,))
        else:
            cursor.execute("SELECT COUNT(*) as passed FROM Note WHERE matiere = 'General' AND grade_final >= 10")
        passed = cursor.fetchone()['passed']
        
        if class_name:
            cursor.execute("""
                SELECT COUNT(*) as at_risk 
                FROM Note n 
                JOIN Etudiant e ON n.id_etudiant = e.id_etudiant
                WHERE n.matiere = 'General' AND n.grade_final < 10 AND e.class_name = %s
            """, (class_name,))
        else:
            cursor.execute("SELECT COUNT(*) as at_risk FROM Note WHERE matiere = 'General' AND grade_final < 10")
        at_risk = cursor.fetchone()['at_risk']
        
        # 4. Average Absences
        if class_name:
            cursor.execute("""
                SELECT AVG(a.nombre_absences) as avg_absences 
                FROM Absences a 
                JOIN Etudiant e ON a.id_etudiant = e.id_etudiant
                WHERE e.class_name = %s
            """, (class_name,))
        else:
            cursor.execute("SELECT AVG(nombre_absences) as avg_absences FROM Absences")
        avg_absences = cursor.fetchone()['avg_absences']
        
        pass_rate = (passed / count) * 100 if count > 0 else 0
        
        return jsonify({
            "averageGrade": round(float(avg_grade or 0), 1),
            "passRate": round(pass_rate, 1),
            "absences": round(float(avg_absences or 0), 1),
            "atRisk": at_risk
        })
    except Exception as e:
        print(f"[ERROR] API Stats: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/eda/heatmap')
def eda_heatmap():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Erreur DB"}), 500
    try:
        query = """
            SELECT 
                e.schooling_years,
                COALESCE(a.nombre_absences, 0) as absences,
                COALESCE(p.score, 0) as participation,
                COALESCE(n.grade_final, 0) as "G3"
            FROM Etudiant e
            LEFT JOIN Note n ON e.id_etudiant = n.id_etudiant AND n.matiere = 'General'
            LEFT JOIN Absences a ON e.id_etudiant = a.id_etudiant AND a.matiere = 'General'
            LEFT JOIN (SELECT id_etudiant, AVG(score) as score FROM Participations GROUP BY id_etudiant) p ON e.id_etudiant = p.id_etudiant
        """
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query)
        data = cursor.fetchall()

        if not data:
            # If no data, return a 404
            return jsonify({"error": "Aucune donnée disponible pour l'EDA"}), 404

        df = pd.DataFrame(data)

        # Standardiser les noms pour l'affichage
        df.rename(columns={
            'schooling_years': 'Années Scola.',
            'absences': 'Absences',
            'participation': 'Participation',
            'G3': 'Note Finale (G3)'
        }, inplace=True)
        
        # S'assurer que les données sont numériques
        df = df.apply(pd.to_numeric, errors='coerce').fillna(0)

        # Matrice de corrélation
        corr = df.corr()

        # Création de la figure
        plt.figure(figsize=(10, 8))
        
        # Configuration des styles
        sns.set_theme(style="white")
        cmap = sns.diverging_palette(230, 20, as_cmap=True)

        # Dessiner le heatmap aver Seaborn
        sns.heatmap(
            corr, 
            cmap=cmap, 
            vmax=1, vmin=-1, 
            center=0,
            annot=True, 
            fmt=".2f",
            square=True, 
            linewidths=.5, 
            cbar_kws={"shrink": .75},
            annot_kws={"size": 12, "weight": "bold"}
        )

        plt.title('Matrice de Corrélation - Variables Clés', fontsize=16, pad=20, fontweight='bold')
        plt.tight_layout()

        # Sauvegarde vers un BytesIO
        img = io.BytesIO()
        plt.savefig(img, format='png', dpi=100, bbox_inches='tight')
        img.seek(0)
        plt.close()

        return send_file(img, mimetype='image/png', as_attachment=False)

    except Exception as e:
        print(f"[ERROR] EDA Heatmap: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/students')
def get_students():
    conn = get_db_connection()
    if not conn:
        return jsonify([]), 500
        
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        class_name = request.args.get('class_name')
        
        # Pagination params
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        per_page = min(per_page, 500)  # Cap at 500
        offset = (page - 1) * per_page
        
        where_clause = ""
        params = []
        if class_name:
            where_clause = "WHERE e.class_name = %s"
            params.append(class_name)
            
        # Count total
        cursor.execute(f"SELECT COUNT(*) as total FROM Etudiant e {where_clause}", params)
        total = cursor.fetchone()['total']
        
        # Fetch paginated data
        query = f"""
            SELECT 
                e.massar_code,
                e.massar_code as id,
                e.id_etudiant,
                e.class_name as school, 
                e.gender as sex, 
                e.guardian_type,
                e.level,
                COALESCE(a.nombre_absences, 0) as absences,
                COALESCE(p.score, 0) as participation,
                0 as "G1",
                0 as "G2",
                n.grade_final as "G3"
            FROM Etudiant e
            LEFT JOIN Note n ON e.id_etudiant = n.id_etudiant AND n.matiere = 'General'
            LEFT JOIN Absences a ON e.id_etudiant = a.id_etudiant AND a.matiere = 'General'
            LEFT JOIN (SELECT id_etudiant, AVG(score) as score FROM Participations GROUP BY id_etudiant) p ON e.id_etudiant = p.id_etudiant
            {where_clause}
            ORDER BY e.massar_code ASC
            LIMIT %s OFFSET %s
        """
        cursor.execute(query, params + [per_page, offset])
        students = cursor.fetchall()
        
        # Convert Decimals to Floats for JSON serialization
        for student in students:
            student['G1'] = float(student['G1']) if student['G1'] is not None else 0
            student['G2'] = float(student['G2']) if student['G2'] is not None else 0
            student['G3'] = float(student['G3']) if student['G3'] is not None else 0
            
        return jsonify({
            "students": students,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        })
    except Exception as e:
        import traceback
        err = traceback.format_exc()
        print(f"[ERROR] API Students: {err}")
        return jsonify({"error": str(err)}), 500
    finally:
        conn.close()

@app.route('/api/students/<string:id>', methods=['GET'])
def get_student(id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "DB connection failed"}), 500
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        query = """
            SELECT 
                e.*,
                e.massar_code,
                e.massar_code as id,
                COALESCE(a.nombre_absences, 0) as absences,
                COALESCE(p.score, 0) as participation,
                0 as "G1",
                0 as "G2",
                n.grade_final as "G3"
            FROM Etudiant e
            LEFT JOIN Note n ON e.id_etudiant = n.id_etudiant AND n.matiere = 'General'
            LEFT JOIN Absences a ON e.id_etudiant = a.id_etudiant AND a.matiere = 'General'
            LEFT JOIN (SELECT id_etudiant, AVG(score) as score FROM Participations GROUP BY id_etudiant) p ON e.id_etudiant = p.id_etudiant
            WHERE e.massar_code = %s
        """
        cursor.execute(query, (id,))
        student = cursor.fetchone()
        
        if not student:
            return jsonify({"error": "Student not found"}), 404
            
        student['G1'] = float(student['G1']) if student['G1'] is not None else 0
        student['G2'] = float(student['G2']) if student['G2'] is not None else 0
        student['G3'] = float(student['G3']) if student['G3'] is not None else 0
        
        return jsonify(student)
    except Exception as e:
        print(f"[ERROR] Get Student: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/students/<string:id>', methods=['DELETE'])
def delete_student(id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "DB connection failed"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Etudiant WHERE massar_code = %s RETURNING id_etudiant", (id,))
        deleted = cursor.fetchone()
        if deleted:
            conn.commit()
            return jsonify({"message": f"Student {id} deleted successfully"})
        else:
            return jsonify({"error": "Student not found"}), 404
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/students', methods=['POST'])
def create_student():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "DB connection failed"}), 500
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Invalid data"}), 400
            
        cursor = conn.cursor()
        # Get next available id if not provided
        csv_id = data.get('id')
        if not csv_id:
            cursor.execute("SELECT COALESCE(MAX(id_etudiant), 0) + 1 FROM Etudiant")
            csv_id = f"NEW_{cursor.fetchone()[0]}"

        # Insert basic student info
        cursor.execute("""
            INSERT INTO Etudiant (massar_code, level, class_name, gender, schooling_years, guardian_type)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id_etudiant
        """, (
            csv_id, '1APIC', data.get('school', '1APIC-01'), data.get('sex', 'F'), 
            2, 'أب'
        ))
        id_etudiant = cursor.fetchone()[0]
        
        # Insert Notes
        g3 = data.get('G3', 0)
        cursor.execute("""
            INSERT INTO Note (id_etudiant, matiere, grade_final)
            VALUES (%s, %s, %s)
        """, (id_etudiant, 'General', g3))
        
        # Insert Absences
        cursor.execute("""
            INSERT INTO Absences (id_etudiant, matiere, nombre_absences, type_absence)
            VALUES (%s, %s, %s, %s)
        """, (id_etudiant, 'General', data.get('absences', 0), False))
        
        # Insert Participation
        cursor.execute("""
            INSERT INTO Participations (id_etudiant, matiere, score, observation)
            VALUES (%s, %s, %s, %s)
        """, (id_etudiant, 'General', data.get('participation', 0), 'Added manually'))
        
        conn.commit()
        return jsonify({"message": "Student created successfully", "id": csv_id}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/students/<string:id>', methods=['PUT'])
def update_student(id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "DB connection failed"}), 500
    try:
        data = request.json
        cursor = conn.cursor()
        
        # Find the internal id_etudiant first
        cursor.execute("SELECT id_etudiant FROM Etudiant WHERE massar_code = %s", (id,))
        res = cursor.fetchone()
        if not res:
            return jsonify({"error": "Student not found"}), 404
        id_etudiant = res[0]
        
        # Update Etudiant
        if 'school' in data or 'sex' in data:
            cursor.execute("""
                UPDATE Etudiant SET 
                    class_name = COALESCE(%s, class_name),
                    gender = COALESCE(%s, gender)
                WHERE id_etudiant = %s
            """, (data.get('school'), data.get('sex'), id_etudiant))
            
        # Update Notes
        if 'G3' in data:
            cursor.execute("""
                UPDATE Note SET 
                    grade_final = %s
                WHERE id_etudiant = %s AND matiere = 'General'
            """, (data.get('G3'), id_etudiant))
            
        # Update Absences
        if 'absences' in data:
            cursor.execute("""
                UPDATE Absences SET nombre_absences = %s
                WHERE id_etudiant = %s AND matiere = 'General'
            """, (data.get('absences'), id_etudiant))
            
        # Update Participation
        if 'participation' in data:
            cursor.execute("""
                UPDATE Participations SET score = %s
                WHERE id_etudiant = %s AND matiere = 'General'
            """, (data.get('participation'), id_etudiant))
            
        conn.commit()
        return jsonify({"message": f"Student {id} updated successfully"})
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/students/<string:massar_code>', methods=['DELETE'])
def delete_student_by_massar(massar_code):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Erreur de connexion"}), 500
    try:
        cursor = conn.cursor()
        # Find internal ID
        cursor.execute("SELECT id_etudiant FROM Etudiant WHERE massar_code = %s", (massar_code,))
        res = cursor.fetchone()
        if not res:
            return jsonify({"error": "Student not found"}), 404
        id_etudiant = res[0]
        
        # Deletions must follow FK constraints
        cursor.execute("DELETE FROM Predictions WHERE id_etudiant = %s", (id_etudiant,))
        cursor.execute("DELETE FROM Note WHERE id_etudiant = %s", (id_etudiant,))
        cursor.execute("DELETE FROM Absences WHERE id_etudiant = %s", (id_etudiant,))
        cursor.execute("DELETE FROM Participations WHERE id_etudiant = %s", (id_etudiant,))
        cursor.execute("DELETE FROM Interventions WHERE id_etudiant = %s", (id_etudiant,))
        cursor.execute("DELETE FROM Alerts WHERE message LIKE %s", (f"%{massar_code}%",)) # Approximate alert cleanup
        cursor.execute("DELETE FROM Etudiant WHERE id_etudiant = %s", (id_etudiant,))
        conn.commit()
        return jsonify({"status": "success", "message": f"Étudiant {massar_code} supprimé"})
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/imports', methods=['GET'])
def get_imports():
    conn = get_db_connection()
    if not conn:
        return jsonify([]), 500
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM Imports ORDER BY upload_date DESC")
        return jsonify(cursor.fetchall())
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/imports/<int:id_import>', methods=['DELETE'])
def delete_import(id_import):
    print(f"[DEBUG] Received DELETE request for import ID: {id_import}")
    conn = get_db_connection()
    if not conn:
        print("[DEBUG] DB connection failed")
        return jsonify({"error": "Erreur de connexion"}), 500
    try:
        cursor = conn.cursor()
        
        # 1. Identify all students in this import
        print(f"[DEBUG] Finding students for import {id_import}...")
        cursor.execute("SELECT id_etudiant, massar_code FROM Etudiant WHERE id_import = %s", (id_import,))
        students = cursor.fetchall()
        student_ids = [s[0] for s in students]
        massar_codes = [s[1] for s in students]
        
        if student_ids:
            # 2. Cleanup related data
            cursor.execute("DELETE FROM Predictions WHERE id_etudiant = ANY(%s)", (student_ids,))
            cursor.execute("DELETE FROM Note WHERE id_etudiant = ANY(%s)", (student_ids,))
            cursor.execute("DELETE FROM Absences WHERE id_etudiant = ANY(%s)", (student_ids,))
            cursor.execute("DELETE FROM Participations WHERE id_etudiant = ANY(%s)", (student_ids,))
            cursor.execute("DELETE FROM Interventions WHERE id_etudiant = ANY(%s)", (student_ids,))
            
            # Use massar codes for alerts cleanup
            for code in massar_codes:
                cursor.execute("DELETE FROM Alerts WHERE message LIKE %s", (f"%{code}%",))
                
            cursor.execute("DELETE FROM Etudiant WHERE id_import = %s", (id_import,))
            
        # 3. Delete import record
        cursor.execute("DELETE FROM Imports WHERE id_import = %s", (id_import,))
        
        conn.commit()
        return jsonify({"status": "success", "message": f"Import #{id_import} et ses {len(student_ids)} étudiants supprimés."})
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/pipeline/run/<int:id_import>', methods=['POST'])
def run_pipeline(id_import):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Update status to 'Processing'
        cursor.execute("UPDATE Imports SET status = 'Processing' WHERE id_import = %s", (id_import,))
        conn.commit()
        
        # 2. Re-train models (Clean + Train)
        from pipeline.model_training import ModelTrainer
        trainer = ModelTrainer()
        results = trainer.train_and_evaluate()
        
        cursor.execute("UPDATE Imports SET status = 'Trained' WHERE id_import = %s", (id_import,))
        conn.commit()
        
        # 3. Generate Predictions
        from pipeline.predict import Predictor
        predictor = Predictor()
        pred_count = predictor.run_predictions_and_save()
        
        cursor.execute("UPDATE Imports SET status = 'Predicted' WHERE id_import = %s", (id_import,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "status": "success", 
            "id_import": id_import,
            "training": results,
            "predictions_count": pred_count
        })
    except Exception as e:
        print(f"[ERROR] Pipeline Run: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/pipeline/reset', methods=['POST'])
def reset_all_data():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Erreur de connexion"}), 500
    try:
        cursor = conn.cursor()
        print("[DEBUG] Purging ALL data from system...")
        
        # Truncate tables in order
        cursor.execute("TRUNCATE TABLE Predictions, Note, Absences, Participations, Interventions, Alerts, Etudiant, Imports RESTART IDENTITY CASCADE")
        
        conn.commit()
        return jsonify({"status": "success", "message": "Toutes les données ont été réinitialisées."})
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

# ============================================================
# DYNAMIC PIPELINE ENDPOINTS (Schema-flexible imports)
# ============================================================

@app.route('/api/upload/dynamic', methods=['POST'])
def upload_dynamic():
    """Upload a file for the dynamic pipeline. Returns file analysis + id_import."""
    import io, tempfile, os as _os
    
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    fname = file.filename.lower()
    if not (fname.endswith('.csv') or fname.endswith('.xlsx') or fname.endswith('.xls')):
        return jsonify({"error": "Format non supporté. Utilisez CSV ou Excel."}), 400
    
    mode = request.form.get('mode', 'add')  # 'add' or 'replace'
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        # 1. Save file temporarily
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=_os.path.splitext(file.filename)[1])
        file.save(tmp.name)
        tmp.close()
        
        # 2. Create import record
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Imports (filename, row_count, status, mode, is_dynamic)
            VALUES (%s, 0, 'Analyzing', %s, TRUE)
            RETURNING id_import
        """, (file.filename, mode))
        id_import = cursor.fetchone()[0]
        conn.commit()
        
        # 3. Analyze the file
        from pipeline.dynamic_ingestion import DynamicIngestion
        ingestion = DynamicIngestion()
        analysis = ingestion.analyze_file(tmp.name)
        
        # 4. Store detected columns in import record
        col_names = [c['name'] for c in analysis['columns']]
        cursor.execute("""
            UPDATE Imports SET columns_detected = %s, row_count = %s
            WHERE id_import = %s
        """, (col_names, analysis['total_rows'], id_import))
        conn.commit()
        cursor.close()
        
        return jsonify({
            "status": "success",
            "id_import": id_import,
            "temp_path": tmp.name,
            "analysis": analysis
        })
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Dynamic Upload: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


@app.route('/api/pipeline/ingest-dynamic', methods=['POST'])
def ingest_dynamic():
    """
    Step 2: After user configures columns, ingest data into ImportedData.
    Expects JSON: { id_import, temp_path, id_column, target_column, mode }
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body"}), 400
    
    id_import = data.get('id_import')
    temp_path = data.get('temp_path')
    id_column = data.get('id_column')
    target_column = data.get('target_column')
    mode = data.get('mode', 'add')
    
    if not all([id_import, temp_path, target_column]):
        return jsonify({"error": "Missing required fields: id_import, temp_path, target_column"}), 400
    
    conn = get_db_connection()
    try:
        from pipeline.dynamic_ingestion import DynamicIngestion
        ingestion = DynamicIngestion()
        
        # Ingest data
        row_count = ingestion.ingest_data(temp_path, id_import, id_column, mode)
        
        # Update import metadata
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Imports 
            SET target_column = %s, id_column = %s, mode = %s, status = 'Ingested'
            WHERE id_import = %s
        """, (target_column, id_column, mode, id_import))
        conn.commit()
        cursor.close()
        
        # Clean up temp file
        import os as _os
        try:
            _os.remove(temp_path)
        except:
            pass
        
        return jsonify({
            "status": "success",
            "id_import": id_import,
            "rows_ingested": row_count
        })
    except Exception as e:
        print(f"[ERROR] Dynamic Ingest: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


@app.route('/api/pipeline/run-dynamic/<int:id_import>', methods=['POST'])
def run_dynamic_pipeline(id_import):
    """
    Step 3: Train a model on the dynamic data and generate predictions.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get import info
        cursor.execute("SELECT * FROM Imports WHERE id_import = %s", (id_import,))
        imp = cursor.fetchone()
        if not imp:
            return jsonify({"error": "Import not found"}), 404
        
        target_column = imp['target_column']
        if not target_column:
            return jsonify({"error": "Target column not configured"}), 400
        
        # Update status
        cursor.execute("UPDATE Imports SET status = 'Training' WHERE id_import = %s", (id_import,))
        conn.commit()
        
        # 1. Load data dynamically
        from pipeline.dynamic_ingestion import DynamicIngestion
        ingestion = DynamicIngestion()
        X, y, student_ids, feature_names = ingestion.load_for_training(id_import, target_column)
        
        # 2. Train model
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import r2_score, mean_absolute_error
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        model.fit(X_train, y_train)
        
        y_pred_test = model.predict(X_test)
        r2 = r2_score(y_test, y_pred_test)
        mae = mean_absolute_error(y_test, y_pred_test)
        
        # 3. Predict on ALL data
        all_predictions = model.predict(X)
        
        # 4. Feature importance
        importances = dict(zip(feature_names, [float(x) for x in model.feature_importances_]))
        top_features = sorted(importances.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # 5. Save predictions
        pred_count = ingestion.save_predictions(id_import, student_ids, all_predictions, target_column)
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "status": "success",
            "id_import": id_import,
            "training": {
                "r2_score": round(r2, 4),
                "mae": round(mae, 4),
                "train_size": len(X_train),
                "test_size": len(X_test),
                "total_features": len(feature_names),
                "top_features": [{"name": f[0], "importance": round(f[1], 4)} for f in top_features]
            },
            "predictions_count": pred_count
        })
    except Exception as e:
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE Imports SET status = 'Error' WHERE id_import = %s", (id_import,))
            conn.commit()
        except:
            pass
        print(f"[ERROR] Dynamic Pipeline: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/imports/<int:id_import>/data', methods=['GET'])
def get_import_data(id_import):
    """Get the imported data with predictions for a specific import."""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "DB connection failed"}), 500
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get import info
        cursor.execute("SELECT * FROM Imports WHERE id_import = %s", (id_import,))
        imp = cursor.fetchone()
        if not imp:
            return jsonify({"error": "Import not found"}), 404
        
        # Get data rows
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        offset = (page - 1) * per_page
        
        cursor.execute("""
            SELECT student_id, raw_data, predicted_value, risk_level
            FROM ImportedData 
            WHERE id_import = %s
            ORDER BY row_index
            LIMIT %s OFFSET %s
        """, (id_import, per_page, offset))
        rows = cursor.fetchall()
        
        cursor.execute("SELECT COUNT(*) as total FROM ImportedData WHERE id_import = %s", (id_import,))
        total = cursor.fetchone()['total']
        
        return jsonify({
            "import": imp,
            "data": rows,
            "total": total,
            "page": page,
            "total_pages": (total + per_page - 1) // per_page
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/upload', methods=['POST'])
def upload_csv():
    import pandas as pd
    import io

    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    fname = file.filename.lower()
    if not (fname.endswith('.csv') or fname.endswith('.xlsx') or fname.endswith('.xls')):
        return jsonify({"error": "Le fichier doit être au format CSV ou Excel (.xlsx/.xls)"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        # Read the uploaded file into a DataFrame
        if fname.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(file.read()), encoding='utf-8')
        else:
            df = pd.read_excel(io.BytesIO(file.read()))

        df = df.where(pd.notnull(df), None)
        cursor = conn.cursor()
        
        # 1. Create Import Record
        cursor.execute("""
            INSERT INTO Imports (filename, row_count, status)
            VALUES (%s, %s, 'Uploaded')
            RETURNING id_import
        """, (file.filename, len(df)))
        id_import = cursor.fetchone()[0]
        
        count = 0
        errors = []

        for idx, row in df.iterrows():
            try:
                massar_code = str(row.get('MassarCode', row.get('Code Massar', f'UPLOAD_{idx}_{id_import}')))

                # ── Translate Arabic Gender → French ──
                raw_gender = str(row.get('Gender', row.get('Sexe', ''))).strip()
                if 'أنثى' in raw_gender or raw_gender == 'F':
                    gender = 'F'
                elif 'ذكر' in raw_gender or raw_gender == 'M':
                    gender = 'M'
                else:
                    gender = raw_gender if raw_gender else 'Inconnu'

                # ── Translate Arabic GuardianType → French ──
                raw_tuteur = str(row.get('GuardianType', row.get('Tuteur', ''))).strip()
                if 'أب' in raw_tuteur:
                    tuteur = 'Père'
                elif 'أم' in raw_tuteur:
                    tuteur = 'Mère'
                elif 'أخ' in raw_tuteur or 'أخت' in raw_tuteur:
                    tuteur = 'Fratrie'
                elif 'خال' in raw_tuteur or 'عم' in raw_tuteur:
                    tuteur = 'Oncle'
                else:
                    tuteur = raw_tuteur if raw_tuteur else 'Autre'

                level = str(row.get('Level', '3APIC'))
                class_name = str(row.get('Class', row.get('Classe', '3APIC-01')))
                schooling_years = int(row.get('SchoolingYears', 3))

                # Insert student (or update their id_import if they already exist)
                cursor.execute("""
                    INSERT INTO Etudiant (massar_code, level, class_name, gender, schooling_years, guardian_type, id_import)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (massar_code) DO UPDATE SET id_import = EXCLUDED.id_import
                    RETURNING id_etudiant
                """, (massar_code, level, class_name, gender, schooling_years, tuteur, id_import))

                id_etudiant = cursor.fetchone()[0]

                # Insert absences
                absences = row.get('Absences', row.get('TotalAbsences'))
                if absences is not None:
                    cursor.execute("""
                        INSERT INTO Absences (id_etudiant, matiere, nombre_absences)
                        VALUES (%s, 'General', %s)
                        ON CONFLICT DO NOTHING
                    """, (id_etudiant, float(absences)))

                # Insert subject grades dynamically
                for col in df.columns:
                    if '_CC' in col or '_Act' in col:
                        val = row.get(col)
                        if val is not None:
                            parts = col.split('_')
                            subject = parts[0]
                            # Handle Note table correctly
                            cursor.execute("""
                                INSERT INTO Note (id_etudiant, matiere, grade_final)
                                VALUES (%s, %s, %s)
                                ON CONFLICT DO NOTHING
                            """, (id_etudiant, subject, float(val)))
                    elif 'Participation_' in col:
                        val = row.get(col)
                        if val is not None:
                            subject = col.replace('Participation_', '')
                            cursor.execute("""
                                INSERT INTO Participations (id_etudiant, matiere, score)
                                VALUES (%s, %s, %s)
                                ON CONFLICT DO NOTHING
                            """, (id_etudiant, subject, float(val)))

                count += 1
            except Exception as row_err:
                errors.append(f"Row {idx}: {str(row_err)}")

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "message": f"Importation réussie : {count} étudiants enregistrés.",
            "id_import": id_import,
            "imported": count,
            "total_rows": len(df),
            "errors": errors[:10]
        }), 200

    except Exception as e:
        print(f"[ERROR] API Upload: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return jsonify({"error": str(e)}), 500

@app.route('/api/train', methods=['POST'])
def train_model():
    try:
        from pipeline.model_training import ModelTrainer
        trainer = ModelTrainer()
        results = trainer.train_and_evaluate()
        return jsonify({"message": "Models trained successfully", "results": results})
    except Exception as e:
        import traceback
        err = traceback.format_exc()
        print(f"[ERROR] API Train: {err}")
        return jsonify({"error": str(err)}), 500

@app.route('/api/predict_all', methods=['POST'])
def generate_predictions():
    try:
        from pipeline.predict import Predictor
        predictor = Predictor()
        count = predictor.run_predictions_and_save()
        return jsonify({"message": f"Successfully generated and saved {count} predictions."})
    except Exception as e:
        import traceback
        err = traceback.format_exc()
        print(f"[ERROR] API Predict All: {err}")
        return jsonify({"error": str(err)}), 500
        
@app.route('/api/predictions', methods=['GET'])
def get_predictions():
    conn = get_db_connection()
    if not conn:
        return jsonify([]), 500
    try:
        class_name = request.args.get('class_name')
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        where_clause = ""
        params = []
        if class_name:
            where_clause = "WHERE e.class_name = %s"
            params.append(class_name)
            
        query = f"""
            SELECT 
                p.id_prediction,
                e.massar_code,
                e.gender,
                e.class_name,
                p.predicted_g3,
                p.niveau_risque,
                p.facteur_top,
                p.probabilite_succes,
                p.recommandation,
                TO_CHAR(p.date_prediction, 'YYYY-MM-DD HH24:MI') as date_prediction
            FROM Predictions p
            JOIN Etudiant e ON p.id_etudiant = e.id_etudiant
            {where_clause}
            ORDER BY p.id_prediction DESC
            LIMIT 100
        """
        cursor.execute(query, params)
        preds = cursor.fetchall()
        
        # Convert Decimals
        for p in preds:
            p['predicted_g3'] = float(p['predicted_g3']) if p['predicted_g3'] is not None else 0
            p['probabilite_succes'] = float(p['probabilite_succes']) if p['probabilite_succes'] is not None else 0
            
        return jsonify(preds)
    except Exception as e:
        print(f"[ERROR] API Get Predictions: {e}")
        return jsonify([]), 500
    finally:
        conn.close()

@app.route('/api/eda/heatmap', methods=['GET'])
def get_eda_heatmap():
    try:
        import matplotlib
        matplotlib.use('Agg') # Server-side rendering
        import matplotlib.pyplot as plt
        import seaborn as sns
        from pipeline.data_ingestion import DataIngestion
        import io
        from flask import send_file
        
        ingestion = DataIngestion()
        df = ingestion.load_data()
        df_processed = ingestion.preprocess_data(df)
        
        # Select numeric columns limit to top 15 correlated with target_g3 to avoid huge plots
        correlations = df_processed.corr()['target_g3'].abs().sort_values(ascending=False)
        top_features = correlations.index[:15]
        df_subset = df_processed[top_features]
        corr_matrix = df_subset.corr()
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="coolwarm", cbar=True, square=True)
        plt.title('Correlation Heatmap (Top 15 Features vs Final Grade)', pad=20)
        plt.tight_layout()
        
        # Save to BytesIO buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plt.close()
        
        return jsonify([{"matiere": matiere, "correlation": corr} for matiere, corr in features_cors.items()])
    except Exception as e:
        import traceback
        err = traceback.format_exc()
        print(f"[ERROR] API EDA Heatmap: {err}")
        return jsonify({"error": str(err)}), 500

# --- NOUVEAU VOLET: GESTION & IA STRATÉGIQUE ---

@app.route('/api/analytics/absenteeism-impact')
def get_absenteeism_impact():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Erreur de connexion"}), 500
    try:
        x_col = request.args.get('x_col', 'absences_t1')
        y_col = request.args.get('y_col', 'moyenne_g1')

        query = """
            SELECT e.id_etudiant, 
                   COALESCE(AVG(a.nombre_absences), 0) as absences_t1, 
                   MAX(n1.grade_final) as moyenne_g1, 
                   MAX(n1.grade_final) as moyenne_g2,
                   COALESCE(AVG(p.score), 0) as participation_g1
            FROM Etudiant e
            LEFT JOIN Absences a ON e.id_etudiant = a.id_etudiant
            LEFT JOIN Note n1 ON e.id_etudiant = n1.id_etudiant AND n1.matiere = 'General'
            LEFT JOIN Participations p ON e.id_etudiant = p.id_etudiant AND p.matiere = 'General'
            GROUP BY e.id_etudiant
        """
        import pandas as pd
        df = pd.read_sql_query(query, conn)
        result = analytics.calculate_absenteeism_impact(df, x_col=x_col, y_col=y_col)
        return jsonify(result)
    except Exception as e:
         return jsonify({"error": str(e)}), 500
    finally:
         conn.close()

@app.route('/api/analytics/student-clusters')
def get_student_clusters():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Erreur de connexion"}), 500
    try:
        # Extraire les données nécessaires au clustering global
        query = """
            SELECT e.id_etudiant, 
                   COALESCE(AVG(a.nombre_absences), 0) as absences_t1,
                   MAX(n1.grade_final) as moyenne_g1, 
                   MAX(n1.grade_final) as moyenne_g2,
                   MAX(nm.grade_final) as c_math, 
                   MAX(nf.grade_final) as c_fs
            FROM Etudiant e
            LEFT JOIN Absences a ON e.id_etudiant = a.id_etudiant
            LEFT JOIN Note n1 ON e.id_etudiant = n1.id_etudiant AND n1.matiere = 'General'
            LEFT JOIN Note nm ON e.id_etudiant = nm.id_etudiant AND nm.matiere = 'Mathématiques'
            LEFT JOIN Note nf ON e.id_etudiant = nf.id_etudiant AND nf.matiere = 'Français'
            GROUP BY e.id_etudiant
        """
        import pandas as pd
        df = pd.read_sql_query(query, conn)
        result = analytics.train_clustering_model(df)
        
        # Add orientation distribution using CC-based computed averages
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT n.id_etudiant, e.massar_code, n.matiere,
                   (COALESCE(cc1, 0) * (CASE WHEN cc1 IS NOT NULL THEN 1 ELSE 0 END) +
                    COALESCE(cc2, 0) * (CASE WHEN cc2 IS NOT NULL THEN 1 ELSE 0 END) +
                    COALESCE(cc3, 0) * (CASE WHEN cc3 IS NOT NULL THEN 1 ELSE 0 END) +
                    COALESCE(activite, 0) * (CASE WHEN activite IS NOT NULL THEN 1 ELSE 0 END))
                   / NULLIF(
                       (CASE WHEN cc1 IS NOT NULL THEN 1 ELSE 0 END) +
                       (CASE WHEN cc2 IS NOT NULL THEN 1 ELSE 0 END) +
                       (CASE WHEN cc3 IS NOT NULL THEN 1 ELSE 0 END) +
                       (CASE WHEN activite IS NOT NULL THEN 1 ELSE 0 END), 0)
                   AS computed_avg
            FROM Note n
            JOIN Etudiant e ON n.id_etudiant = e.id_etudiant
            WHERE n.matiere != 'General'
              AND (cc1 IS NOT NULL OR cc2 IS NOT NULL OR cc3 IS NOT NULL OR activite IS NOT NULL)
        """)
        all_notes = cursor.fetchall()
        from collections import defaultdict
        student_notes = defaultdict(dict)
        for r in all_notes:
            if r['computed_avg'] is not None:
                student_notes[r['massar_code']][r['matiere']] = float(r['computed_avg'])
            
        # Prepare DataFrame for Orientation Model Training (PCA + K-Means)
        all_student_data = []
        for massar, notes_dict in student_notes.items():
            row = notes_dict.copy()
            row['massar_code'] = massar
            all_student_data.append(row)
        
        if all_student_data:
            df_orient = pd.DataFrame(all_student_data)
            analytics.train_orientation_model(df_orient)
            
        orientations = []
        for notes in student_notes.values():
            rec = analytics.recommend_orientation(notes)
            if 'recommended_track' in rec:
                orientations.append(rec['recommended_track'])
        from collections import Counter
        result['orientation_distribution'] = dict(Counter(orientations))
        
        return jsonify(result)
    except Exception as e:
         return jsonify({"error": str(e)}), 500
@app.route('/api/analytics/orientation/<string:massar_code>')
def get_orientation_recommendation(massar_code):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Erreur de connexion"}), 500
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        # Fetch all notes for this student to calculate orientation
        cursor.execute("""
            SELECT matiere, grade_final FROM Note n
            JOIN Etudiant e ON n.id_etudiant = e.id_etudiant
            WHERE e.massar_code = %s
        """, (massar_code,))
        notes_rows = cursor.fetchall()
        
        if not notes_rows:
            return jsonify({"error": "Aucune note trouvée pour cet élève"}), 404
            
        notes_dict = {r['matiere']: r['grade_final'] for r in notes_rows}
        result = analytics.recommend_orientation(notes_dict)
        return jsonify(result)
    except Exception as e:
         return jsonify({"error": str(e)}), 500
    finally:
         conn.close()

@app.route('/api/analytics/orientation-students/<string:track>')
def get_orientation_students(track):
    """Return all students whose AI-recommended orientation matches the given track."""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Erreur de connexion"}), 500
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        # Fetch all CC-based subject averages for all students
        cursor.execute("""
            SELECT n.id_etudiant, e.massar_code, e.class_name, e.gender, n.matiere,
                   (COALESCE(cc1, 0) * (CASE WHEN cc1 IS NOT NULL THEN 1 ELSE 0 END) +
                    COALESCE(cc2, 0) * (CASE WHEN cc2 IS NOT NULL THEN 1 ELSE 0 END) +
                    COALESCE(cc3, 0) * (CASE WHEN cc3 IS NOT NULL THEN 1 ELSE 0 END) +
                    COALESCE(activite, 0) * (CASE WHEN activite IS NOT NULL THEN 1 ELSE 0 END))
                   / NULLIF(
                       (CASE WHEN cc1 IS NOT NULL THEN 1 ELSE 0 END) +
                       (CASE WHEN cc2 IS NOT NULL THEN 1 ELSE 0 END) +
                       (CASE WHEN cc3 IS NOT NULL THEN 1 ELSE 0 END) +
                       (CASE WHEN activite IS NOT NULL THEN 1 ELSE 0 END), 0)
                   AS computed_avg
            FROM Note n
            JOIN Etudiant e ON n.id_etudiant = e.id_etudiant
            WHERE n.matiere != 'General'
              AND (cc1 IS NOT NULL OR cc2 IS NOT NULL OR cc3 IS NOT NULL OR activite IS NOT NULL)
        """)
        all_notes = cursor.fetchall()

        from collections import defaultdict
        # Group notes by massar_code
        student_notes = defaultdict(dict)
        student_info = {}
        for r in all_notes:
            mc = r['massar_code']
            if r['computed_avg'] is not None:
                student_notes[mc][r['matiere']] = float(r['computed_avg'])
            if mc not in student_info:
                student_info[mc] = {
                    "massar_code": mc,
                    "classe": r['class_name'] or 'N/A',
                    "sexe": r['gender'] or ''
                }

        # Also fetch general averages
        cursor.execute("""
            SELECT e.massar_code, n.grade_final
            FROM Note n JOIN Etudiant e ON n.id_etudiant = e.id_etudiant
            WHERE n.matiere = 'General'
        """)
        gen_avgs = {r['massar_code']: float(r['grade_final']) if r['grade_final'] else None for r in cursor.fetchall()}

        # Compute orientation for each student and filter by requested track
        import urllib.parse
        decoded_track = urllib.parse.unquote(track)
        result = []
        for mc, notes in student_notes.items():
            # Inject general average into notes for threshold analysis
            if mc in gen_avgs:
                notes['General'] = gen_avgs[mc]
                
            rec = analytics.recommend_orientation(notes)
            if 'recommended_track' in rec and rec['recommended_track'] == decoded_track:
                info = student_info.get(mc, {})
                # Find top 4 strongest subjects for this student
                sorted_subjects = sorted(notes.items(), key=lambda x: x[1], reverse=True)[:4]
                result.append({
                    "massar_code": mc,
                    "classe": info.get("classe", "N/A"),
                    "sexe": info.get("sexe", ""),
                    "moyenne_generale": gen_avgs.get(mc),
                    "matieres_dominantes": [{"matiere": s[0], "note": round(s[1], 2)} for s in sorted_subjects],
                    "confidence": rec.get("confidence", 0.7),
                    "interpretation": rec.get("interpretation", ""),
                    "scores": rec.get("scores", {})
                })

        return jsonify(result)
    except Exception as e:
        import traceback
        print(f"Error fetching orientation students: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/analytics/cluster-students/<int:cluster_id>')
def get_cluster_students(cluster_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Erreur de connexion"}), 500
    try:
        query = """
            SELECT e.id_etudiant, e.massar_code, e.class_name, e.gender,
                   COALESCE(AVG(a.nombre_absences), 0) as absences_t1,
                   MAX(n1.grade_final) as moyenne_g1, 
                   MAX(n1.grade_final) as moyenne_g2,
                   MAX(nm.grade_final) as c_math, 
                   MAX(nf.grade_final) as c_fs
            FROM Etudiant e
            LEFT JOIN Absences a ON e.id_etudiant = a.id_etudiant
            LEFT JOIN Note n1 ON e.id_etudiant = n1.id_etudiant AND n1.matiere = 'General'
            LEFT JOIN Note nm ON e.id_etudiant = nm.id_etudiant AND nm.matiere = 'Mathématiques'
            LEFT JOIN Note nf ON e.id_etudiant = nf.id_etudiant AND nf.matiere = 'Français'
            GROUP BY e.id_etudiant, e.massar_code, e.class_name, e.gender
        """
        import pandas as pd
        df = pd.read_sql_query(query, conn)
        
        import pipeline.analytics as analytics
        import joblib
        import os
        model_path = analytics.CLUSTER_MODEL_PATH
        if not os.path.exists(model_path):
             return jsonify({"error": "Modèle non trouvé"}), 404
             
        data = joblib.load(model_path)
        kmeans = data['model']
        scaler = data['scaler']
        features = data['features']
        
        for f in features:
            if f not in df.columns:
                df[f] = 0
                
        X_input = df[features]
        X_input = X_input.fillna(X_input.median(numeric_only=True)).fillna(0)
        X_scaled = scaler.transform(X_input)
        
        clusters = kmeans.predict(X_scaled)
        df['cluster_id'] = clusters
        
        cluster_df = df[df['cluster_id'] == cluster_id]
        
        student_ids = tuple(cluster_df['id_etudiant'].tolist())
        weak_subjects_dict = {}
        strong_subjects_dict = {}
        if student_ids:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            # Compute subject average from CC components (cc1, cc2, cc3, activite)
            # grade_final is NULL for subject-specific rows; only General has it filled
            q = """
                SELECT id_etudiant, matiere,
                       (COALESCE(cc1, 0) * (CASE WHEN cc1 IS NOT NULL THEN 1 ELSE 0 END) +
                        COALESCE(cc2, 0) * (CASE WHEN cc2 IS NOT NULL THEN 1 ELSE 0 END) +
                        COALESCE(cc3, 0) * (CASE WHEN cc3 IS NOT NULL THEN 1 ELSE 0 END) +
                        COALESCE(activite, 0) * (CASE WHEN activite IS NOT NULL THEN 1 ELSE 0 END)) 
                       / NULLIF(
                           (CASE WHEN cc1 IS NOT NULL THEN 1 ELSE 0 END) +
                           (CASE WHEN cc2 IS NOT NULL THEN 1 ELSE 0 END) +
                           (CASE WHEN cc3 IS NOT NULL THEN 1 ELSE 0 END) +
                           (CASE WHEN activite IS NOT NULL THEN 1 ELSE 0 END), 0)
                       AS computed_avg
                FROM Note 
                WHERE id_etudiant IN %s AND matiere != 'General'
                  AND (cc1 IS NOT NULL OR cc2 IS NOT NULL OR cc3 IS NOT NULL OR activite IS NOT NULL)
            """
            cursor.execute(q, (student_ids,))
            all_notes = cursor.fetchall()
            from collections import defaultdict
            weak_subjects_dict = defaultdict(list)
            strong_subjects_dict = defaultdict(list)
            for n in all_notes:
                grade = float(n['computed_avg']) if n['computed_avg'] is not None else -1
                if grade != -1:
                    if grade < 10:
                        weak_subjects_dict[n['id_etudiant']].append({"matiere": n['matiere'], "note": round(grade, 2)})
                    elif grade >= 14:
                        strong_subjects_dict[n['id_etudiant']].append({"matiere": n['matiere'], "note": round(grade, 2)})
                
        result = []
        for _, row in cluster_df.iterrows():
            sid = row['id_etudiant']
            avg_grade = row['moyenne_g2'] if pd.notna(row['moyenne_g2']) else (row['moyenne_g1'] if pd.notna(row['moyenne_g1']) else None)
            result.append({
                "id_etudiant": sid,
                "nom": "N/A",
                "prenom": "N/A",
                "massar_code": str(row['massar_code']),
                "classe": str(row['class_name'] if pd.notna(row['class_name']) else 'N/A'),
                "sexe": str(row['gender'] if pd.notna(row['gender']) else ''),
                "moyenne_generale": float(avg_grade) if avg_grade is not None else None,
                "matieres_faibles": weak_subjects_dict.get(sid, []),
                "matieres_fortes": strong_subjects_dict.get(sid, [])
            })
            
        return jsonify(result)
    except Exception as e:
        import traceback
        print(f"Error fetching cluster students: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

# --- VOLET NOTIFICATIONS & ALERTES ---

def generate_automatic_alerts():
    """Analyses students and creates alerts for critical cases."""
    conn = get_db_connection()
    if not conn:
        return 0
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        alerts_count = 0
        
        # 1. Alert for students with high risk (predicted grade < 10)
        cursor.execute("""
            SELECT e.massar_code, p.predicted_g3, e.class_name
            FROM Predictions p
            JOIN Etudiant e ON p.id_etudiant = e.id_etudiant
            WHERE p.predicted_g3 < 10
              AND NOT EXISTS (
                  SELECT 1 FROM Alerts 
                  WHERE message LIKE '%%' || e.massar_code || '%%' 
                    AND date_creation > CURRENT_DATE - INTERVAL '7 days'
              )
        """)
        at_risk = cursor.fetchall()
        for s in at_risk:
            msg = f"Alerte Performance: L'étudiant {s['massar_code']} ({s['class_name']}) a une prédiction de {float(s['predicted_g3']):.2f}/20. Intervention recommandée."
            cursor.execute("INSERT INTO Alerts (message) VALUES (%s)", (msg,))
            alerts_count += 1

        # 2. Alert for high absenteeism (> 10 days)
        cursor.execute("""
            SELECT e.massar_code, SUM(a.nombre_absences) as total_abs, e.class_name
            FROM Absences a
            JOIN Etudiant e ON a.id_etudiant = e.id_etudiant
            GROUP BY e.massar_code, e.class_name
            HAVING SUM(a.nombre_absences) > 10
              AND NOT EXISTS (
                  SELECT 1 FROM Alerts 
                  WHERE message LIKE '%%' || e.massar_code || '%%' 
                    AND message LIKE '%%absentéisme%%'
                    AND date_creation > CURRENT_DATE - INTERVAL '15 days'
              )
        """)
        absentees = cursor.fetchall()
        for s in absentees:
            msg = f"Alerte Absentéisme: L'étudiant {s['massar_code']} ({s['class_name']}) cumule {int(s['total_abs'])} absences. Risque de décrochage."
            cursor.execute("INSERT INTO Alerts (message) VALUES (%s)", (msg,))
            alerts_count += 1
            
        conn.commit()
        return alerts_count
    except Exception as e:
        print(f"[ERROR] Alert Generation: {e}")
        return 0
    finally:
        conn.close()

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    conn = get_db_connection()
    if not conn:
        return jsonify([]), 500
    try:
        role = request.args.get('role')
        class_name = request.args.get('class_name')
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Base query
        query = "SELECT * FROM Alerts "
        params = []
        
        # Filtering for teachers
        if role == 'Enseignant' and class_name:
            query += "WHERE message LIKE %s "
            params.append(f"%({class_name})%")
            
        query += "ORDER BY date_creation DESC LIMIT 50"
        
        cursor.execute(query, params)
        alerts = cursor.fetchall()
        return jsonify(alerts)
    except Exception as e:
        print(f"[ERROR] API Get Alerts: {e}")
        return jsonify([]), 500
    finally:
        conn.close()

@app.route('/api/alerts/<int:id>/read', methods=['PUT'])
def mark_alert_read(id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "DB connection failed"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE Alerts SET is_read = TRUE WHERE id_alert = %s", (id,))
        conn.commit()
        return jsonify({"message": "Alert marked as read"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/alerts/generate', methods=['POST'])
def trigger_alerts():
    count = generate_automatic_alerts()
    return jsonify({"message": f"Generated {count} new alerts."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
