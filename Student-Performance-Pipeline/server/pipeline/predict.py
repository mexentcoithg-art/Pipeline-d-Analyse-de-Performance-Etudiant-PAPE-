from joblib import dump, load
import pandas as pd
import numpy as np
import os
from pipeline.data_ingestion import DataIngestion

class Predictor:
    def __init__(self, model_path="models/model_massar.pkl"):
        self.model_path = model_path
        self.artifacts = None
        self.ingestion = DataIngestion()

    def load_model(self):
        if os.path.exists(self.model_path):
            self.artifacts = load(self.model_path)
        else:
            raise Exception("Model not found. Please train the model first.")

    def run_predictions_and_save(self):
        if self.artifacts is None:
            self.load_model()
            
        model = self.artifacts['model_rf']
        feature_names = self.artifacts['feature_names']
        
        # Load and preprocess all current students
        df_raw = self.ingestion.load_data()
        df_processed = self.ingestion.preprocess_data(df_raw)
        
        # Ensure columns match training
        X = df_processed[feature_names]
        
        # Predictions & Probabilties
        predictions = model.predict(X)
        probabilities = model.predict_proba(X)[:, 1] # Prob of class 1 (Success)
        
        # Feature importance for explanations
        importances = model.feature_importances_
        top_feature_idx = np.argmax(importances)
        global_top_feature = feature_names[top_feature_idx]

        conn = self.ingestion.get_connection()
        cursor = conn.cursor()
        
        # Clear old predictions
        cursor.execute("TRUNCATE TABLE Predictions CASCADE")
        
        # Insert new predictions
        for idx, row in df_raw.iterrows():
            id_etudiant = row['id_etudiant']
            success_prob = float(probabilities[idx])
            risk_level = "À risque" if success_prob < 0.5 else "Succès"
            
            # Logic for Factor & Recommendation
            absences = row.get('absences', 0)
            participation_cols = [c for c in row.index if 'participation' in c]
            avg_participation = row[participation_cols].mean() if participation_cols else 10
            
            if success_prob < 0.5:
                # Flag the likely cause
                if absences > 10:
                    facteur_top = "Absences élevées"
                    recommandation = "Avertissement : Profil critique. L'absentéisme est le facteur principal de risque. Une convocation du tuteur est recommandée."
                elif avg_participation < 10:
                    facteur_top = "Faible participation"
                    recommandation = "Avertissement : Le manque d'implication en classe freine la progression. Encouragez l'élève à participer davantage."
                else:
                    facteur_top = global_top_feature
                    recommandation = "Avertissement : Profil académique fragile. Un suivi pédagogique renforcé et des cours de soutien sont conseillés."
            else:
                facteur_top = global_top_feature
                if success_prob > 0.85:
                    recommandation = "Encouragement : Excellent profil. Continuez sur cette lancée pour maintenir ce niveau d'excellence."
                else:
                    recommandation = "Encouragement : Bons résultats globaux. Restez vigilant sur l'assiduité pour sécuriser la fin d'année."

            cursor.execute("""
                INSERT INTO Predictions (id_etudiant, predicted_g3, niveau_risque, facteur_top, probabilite_succes, recommandation)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (id_etudiant, 0.0, risk_level, facteur_top, success_prob, recommandation))
            
        conn.commit()
        cursor.close()
        conn.close()
        
        return len(predictions)

if __name__ == '__main__':
    p = Predictor()
    count = p.run_predictions_and_save()
    print(f"Successfully generated and saved {count} predictions with recommendations.")
