import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv
from sklearn.preprocessing import LabelEncoder

class DataIngestion:
    def __init__(self):
        load_dotenv()
        self.db_host = os.getenv("DB_HOST", "localhost")
        self.db_user = os.getenv("DB_USER", "postgres")
        self.db_password = os.getenv("DB_PASSWORD", "postgres")
        self.db_port = os.getenv("DB_PORT", "5432")
        self.db_name = os.getenv("DB_NAME", "student_db")

    def get_connection(self):
        return psycopg2.connect(
            host=self.db_host, user=self.db_user, password=self.db_password,
            port=self.db_port, dbname=self.db_name
        )

    def load_data(self):
        """Loads data from PostgreSQL and flattens it for ML."""
        conn = self.get_connection()
        
        # Base student info + absences + target
        # Added guardian_type, guardian2_job as social features
        query_base = """
            SELECT 
                e.id_etudiant, e.gender, e.schooling_years, e.class_name, 
                e.guardian_type, e.guardian2_job,
                COALESCE(a.nombre_absences, 0) as absences,
                n.grade_final as raw_target_g3
            FROM Etudiant e
            LEFT JOIN Note n ON e.id_etudiant = n.id_etudiant AND n.matiere = 'General'
            LEFT JOIN Absences a ON e.id_etudiant = a.id_etudiant AND a.matiere = 'General'
            WHERE n.grade_final IS NOT NULL
        """
        df_base = pd.read_sql_query(query_base, conn)

        # Notes for pivoting
        query_notes = "SELECT id_etudiant, matiere, cc1, cc2, cc3, activite FROM Note WHERE matiere != 'General'"
        df_notes = pd.read_sql_query(query_notes, conn)
        
        # Participations
        query_part = "SELECT id_etudiant, matiere, score as participation FROM Participations"
        df_part = pd.read_sql_query(query_part, conn)
        
        conn.close()

        # Define success target (Binary: 1 if >= 10, else 0)
        df_base['target_success'] = (df_base['raw_target_g3'] >= 10).astype(int)
        # Drop raw target to avoid circular logic during training
        df_base = df_base.drop('raw_target_g3', axis=1)

        # Pivot Notes
        df_notes_melt = df_notes.melt(id_vars=['id_etudiant', 'matiere'], value_vars=['cc1', 'cc2', 'cc3', 'activite'], var_name='note_type', value_name='score')
        df_notes_melt['feature_name'] = df_notes_melt['matiere'] + '_' + df_notes_melt['note_type']
        df_notes_pivot = df_notes_melt.pivot_table(index='id_etudiant', columns='feature_name', values='score', aggfunc='first').reset_index()

        # Pivot Participations
        df_part['feature_name'] = df_part['matiere'] + '_participation'
        df_part_pivot = df_part.pivot_table(index='id_etudiant', columns='feature_name', values='participation', aggfunc='first').reset_index()

        # Merge all together
        df = df_base.merge(df_notes_pivot, on='id_etudiant', how='left')
        df = df.merge(df_part_pivot, on='id_etudiant', how='left')
        
        return df

    def preprocess_data(self, df):
        """Preprocessing features (Handling NaN and Categorical encoding)."""
        df = df.copy()
        
        # 1. Handle Missing Values
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        # Exclude target from numeric features
        feature_cols = [c for c in numeric_cols if c != 'target_success']
        df[feature_cols] = df[feature_cols].fillna(0)
        
        # For categorical, fill with 'Inconnu'
        cat_cols = df.select_dtypes(include=['object']).columns
        df[cat_cols] = df[cat_cols].fillna('Inconnu')
        
        # 2. Encode Categorical Variables
        df_encoded = df.copy()
        
        self.label_encoders = {}
        for col in cat_cols:
            le = LabelEncoder()
            # Convert explicitly to string to avoid mixed types
            df_encoded[col] = le.fit_transform(df_encoded[col].astype(str))
            self.label_encoders[col] = le
            
        # Drop ID as it's not a predictive feature
        if 'id_etudiant' in df_encoded.columns:
            df_encoded = df_encoded.drop('id_etudiant', axis=1)
            
        return df_encoded
