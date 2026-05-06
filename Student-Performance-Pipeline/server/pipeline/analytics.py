import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from joblib import dump, load
import os

MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
CLUSTER_MODEL_PATH = os.path.join(MODEL_DIR, 'cluster_model.joblib')
ORIENTATION_MODEL_PATH = os.path.join(MODEL_DIR, 'orientation_model.joblib')

def train_clustering_model(df):
    """
    Entraîne un modèle K-Means pour créer des groupes (clusters) d'élèves
    basés sur leurs notes et absences.
    """
    try:
        # Sélection des caractéristiques pertinentes pour le profilage (en minuscules depuis PostgreSQL)
        features = ['c_math', 'c_fs', 'absences_t1', 'absences_t2', 'moyenne_g1', 'moyenne_g2']
        
        # Vérifier que les colonnes existent
        available_features = [f for f in features if f in df.columns]
        if len(available_features) < 3:
            return {"error": "Pas assez de caractéristiques pour le clustering."}

        X = df[available_features].copy()
        
        # Gestion des valeurs manquantes : remplacer par la médiane, puis par 0 si toute la colonne est vide
        X = X.fillna(X.median()).fillna(0)
        
        # Standardisation des données (crucial pour K-Means)
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Entraînement avec 3 clusters (Profils type: Excellent, Moyen, En difficulté)
        # On peut déterminer le K optimal via d'autres méthodes (Elbow) si nécessaire.
        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        kmeans.fit(X_scaled)
        
        # Analyse des centres pour donner des noms aux profils
        centers = scaler.inverse_transform(kmeans.cluster_centers_)
        cluster_profiles = []
        
        for i, center in enumerate(centers):
            profile_summary = {
                "cluster_id": i,
                "notes_moyennes": float(np.mean([center[available_features.index('moyenne_g1')], center[available_features.index('moyenne_g2')]])) if 'moyenne_g1' in available_features else 0,
                "absences_moyennes": float(np.mean([center[available_features.index('absences_T1')], center[available_features.index('absences_T2')]])) if 'absences_T1' in available_features else 0,
            }
            cluster_profiles.append(profile_summary)
            
        # Tri empirique des clusters (0 = Difficulté, 1 = Moyen, 2 = Bon) basé sur la note moyenne
        cluster_profiles.sort(key=lambda x: x['notes_moyennes'])
        
        # Assignation de labels descriptifs
        labels_map = {
            cluster_profiles[0]['cluster_id']: "Priorité Accompagnement (Notes basses)",
            cluster_profiles[1]['cluster_id']: "Profil Intermédiaire",
            cluster_profiles[2]['cluster_id']: "Profil Moteur (Bons résultats)"
        }

        # Sauvegarde du modèle et du scaler
        dump({
            'model': kmeans, 
            'scaler': scaler, 
            'features': available_features,
            'labels_map': labels_map
        }, CLUSTER_MODEL_PATH)

        return {
            "status": "success", 
            "message": "Modèle de clustering entraîné avec succès",
            "profiles_detected": labels_map
        }
        
    except Exception as e:
        return {"error": f"Erreur lors du clustering: {str(e)}"}

def calculate_absenteeism_impact(df, x_col=None, y_col=None):
    """
    Utilise une régression linéaire simple et un arbre de décision pour calculer 
    l'impact d'une variable (X) sur une cible (Y) et trouver le seuil critique.
    """
    try:
        # Variables dynamiques ou fallback
        target = y_col if y_col and y_col in df.columns else ('moyenne_g1' if 'moyenne_g1' in df.columns else 'moyenne_g2')
        feature = x_col if x_col and x_col in df.columns else ('absences_t1' if 'absences_t1' in df.columns else 'absences_t2')

        if target not in df.columns or feature not in df.columns:
            return {"error": f"Colonnes requises ({target}, {feature}) non trouvées dans le dataset."}

        # Nettoyage des données pour la régression (supprimer les NaN)
        data = df[[feature, target]].dropna()
        
        # Filtre anti-aberrations basique (IQ) optionnel, mais ici on garde le brut pour voir l'impact
        if len(data) < 20:
            return {"error": "Pas assez de données valides (min 20) pour la régression."}

        X = data[[feature]]
        y = data[target]

        # 1. Régression Linéaire Stricte
        model = LinearRegression()
        model.fit(X, y)
        coefficient = model.coef_[0]
        r2_score = model.score(X, y)

        # 2. Arbre de Décision (pour trouver la cassure / le seuil d'alerte)
        # On limite max_leaf_nodes=2 pour trouver la séparation "optimale" selon le MSE
        tree = DecisionTreeRegressor(max_leaf_nodes=2, random_state=42)
        tree.fit(X, y)
        threshold = None
        if tree.tree_.feature[0] != -2: # Si une scission a pu être faite
            threshold = float(tree.tree_.threshold[0])

        # 3. Échantillon pour le graphique Scatter (Limité à 150 points pour la perf frontend)
        sample_data = data.sample(min(150, len(data)), random_state=42)
        points = [{"x": float(row[feature]), "y": float(row[target])} for _, row in sample_data.iterrows()]
        
        # Droite de régression (points de la ligne)
        x_min, x_max = float(X[feature].min()), float(X[feature].max())
        y_min_pred = float(model.predict([[x_min]])[0])
        y_max_pred = float(model.predict([[x_max]])[0])
        line = [{"x": x_min, "y": y_min_pred}, {"x": x_max, "y": y_max_pred}]

        # Déterminer la phrase
        var_name_x = feature.split('_')[0].capitalize()
        if coefficient < 0:
             interp = f"Pour chaque bloc de {var_name_x}, la note diminue statistiquement de {abs(coefficient):.2f} points."
        else:
             interp = f"Pour chaque ajout de {var_name_x}, la note augmente statistiquement de {abs(coefficient):.2f} points."

        return {
            "status": "success",
            "x_feature": feature,
            "y_target": target,
            "impact_coefficient": float(coefficient),
            "interpretation": interp,
            "reliability_score": float(r2_score),
            "critical_threshold": float(threshold) if threshold else None,
            "plot_data": {
                "points": points,
                "regression_line": line
            }
        }

    except Exception as e:
        return {"error": f"Erreur lors du calcul dynamique d'impact: {str(e)}"}

def get_student_cluster(student_data):
    """
    Prédit le cluster (profil) d'un étudiant spécifique.
    """
    if not os.path.exists(CLUSTER_MODEL_PATH):
        return {"error": "Modèle de clustering non trouvé."}
        
    try:
        data = load(CLUSTER_MODEL_PATH)
        kmeans = data['model']
        scaler = data['scaler']
        features = data['features']
        labels_map = data['labels_map']

        # Préparation des données d'entrée
        df_student = pd.DataFrame([student_data])
        
        # Vérification des colonnes manquantes
        for f in features:
            if f not in df_student.columns:
                 df_student[f] = 0 # Default fallback
                 
        X_input = df_student[features]
        X_scaled = scaler.transform(X_input)
        
        cluster_id = kmeans.predict(X_scaled)[0]
        
        return {
            "cluster_id": int(cluster_id),
            "profile_label": labels_map.get(cluster_id, "Inconnu")
        }
    except Exception as e:
         return {"error": f"Erreur de prédiction de cluster: {str(e)}"}
# Poids Pédagogiques (Configuration Expertise)
PEDAGOGICAL_WEIGHTS = {
    'Scientifique': {
        'MATHEMATIQUES': 0.30, 'MATHÉMATIQUES': 0.30, 'PHYSIQUECHIMIE': 0.25, 'PHYSIQUE-CHIMIE': 0.25,
        'PHYSIQUE CHIMIE': 0.25, 'SCDELAVIEETDELA': 0.20, 'SCIENCES DE LA VIE ET DE LA': 0.20, 
        'SVT': 0.20, 'INFORMATIQUE': 0.10, 'LANGUEARABE': 0.05, 'ARABE': 0.05,
        'LANGUEANGLAISE': 0.05, 'ANGLAIS': 0.05, 'EDUCATIONPHYSIQUE': 0.05, 'ED. PHYSIQUE': 0.05,
        'FRANÇAIS': 0.05, 'FRANCAIS': 0.05, 'LANGUEFRANCAISE': 0.05
    },
    'Littéraire': {
        'MATHEMATIQUES': 0.05, 'MATHÉMATIQUES': 0.05, 'PHYSIQUECHIMIE': 0.03, 'PHYSIQUE-CHIMIE': 0.03,
        'PHYSIQUE CHIMIE': 0.03, 'SCDELAVIEETDELA': 0.05, 'SVT': 0.05,
        'INFORMATIQUE': 0.02, 'LANGUEARABE': 0.30, 'ARABE': 0.30,
        'LANGUEANGLAISE': 0.25, 'ANGLAIS': 0.25, 'EDUCATIONPHYSIQUE': 0.05, 'ED. PHYSIQUE': 0.05,
        'FRANÇAIS': 0.25, 'FRANCAIS': 0.25, 'LANGUEFRANCAISE': 0.25
    },
    'Formation Professionnelle': {
        'MATHEMATIQUES': 0.10, 'MATHÉMATIQUES': 0.10, 'PHYSIQUECHIMIE': 0.10, 'PHYSIQUE-CHIMIE': 0.10,
        'PHYSIQUE CHIMIE': 0.10, 'SCDELAVIEETDELA': 0.10, 'SVT': 0.10,
        'INFORMATIQUE': 0.30, 'LANGUEARABE': 0.10, 'ARABE': 0.10,
        'LANGUEANGLAISE': 0.15, 'ANGLAIS': 0.15, 'EDUCATIONPHYSIQUE': 0.15, 'ED. PHYSIQUE': 0.15,
        'FRANÇAIS': 0.15, 'FRANCAIS': 0.15, 'LANGUEFRANCAISE': 0.15
    }
}

def normalize_key(key):
    """Normalize subject names: uppercase, no accents, no spaces/hyphens."""
    import unicodedata
    s = key.upper().strip()
    s = "".join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    return s.replace(" ", "").replace("-", "").replace("_", "")

def calculate_orientation_scores(notes_dict, weights_dict):
    """
    Calcule le score pondéré pour chaque série.
    Retourne { 'Scientifique': 15.2, ... }
    """
    results = {}
    normalized_notes = {normalize_key(k): v for k, v in notes_dict.items()}
    
    for track, weights in weights_dict.items():
        total_score = 0
        total_weight = 0
        
        # Match weights accurately with student notes
        for subj_weight_name, weight in weights.items():
            norm_subj = normalize_key(subj_weight_name)
            if norm_subj in normalized_notes:
                total_score += normalized_notes[norm_subj] * weight
                total_weight += weight
        
        # Weighted average (normalized scale 0-20)
        results[track] = total_score / total_weight if total_weight > 0 else 0
        
    return results

def train_orientation_model(df_notes):
    """
    Entraîne le moteur hybride K-Means (40%) + Analyse Multi-Critères (60%).
    """
    try:
        # Nettoyage colonnes
        exclude = ['id_etudiant', 'massar_code', 'classe', 'moyenne_generale', 'moyenne_g1', 'moyenne_g2', 'absences_t1', 'absences_t2', 'c_math', 'c_fs']
        features = [col for col in df_notes.columns if col not in exclude]
        
        if len(features) < 3:
            return {"error": "Données insuffisantes."}

        X = df_notes[features].copy()
        for col in features:
            X[col] = pd.to_numeric(X[col], errors='coerce')
        X = X.fillna(X.median()).fillna(0)
        
        # 1. K-Means
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        kmeans.fit(X_scaled)
        
        # 2. Étiquetage auto des clusters par profil dominant
        cluster_labels = {}
        for i in range(3):
            mask = (kmeans.labels_ == i)
            node_data = X[mask].mean()
            # On utilise notre propre logique multi-critères pour étiqueter le cluster entier
            scores = calculate_orientation_scores(node_data.to_dict(), PEDAGOGICAL_WEIGHTS)
            cluster_labels[i] = max(scores, key=scores.get)

        # Sauvegarde
        dump({
            'kmeans': kmeans,
            'scaler': scaler,
            'features': features,
            'cluster_labels': cluster_labels,
            'pedagogical_weights': PEDAGOGICAL_WEIGHTS
        }, ORIENTATION_MODEL_PATH)

        return {"status": "success", "labels": cluster_labels}
    except Exception as e:
        return {"error": str(e)}

def recommend_orientation(notes):
    """
    Recommandation Hybride Optimisée : Multi-Critères (60%) + K-Means (40%) + Règles de Gestion (Seuils).
    """
    if not os.path.exists(ORIENTATION_MODEL_PATH):
        return {"recommended_track": "Scientifique", "error": "Modèle non prêt"}
        
    try:
        data = load(ORIENTATION_MODEL_PATH)
        kmeans = data['kmeans']
        scaler = data['scaler']
        features = data['features']
        cluster_labels = data['cluster_labels']
        
        # 1. Calcul des scores multi-critères (Métier)
        mc_scores = calculate_orientation_scores(notes, PEDAGOGICAL_WEIGHTS)
        
        # 2. Récupération de la moyenne générale (si disponible)
        # On essaie de normaliser la clé pour trouver la moyenne
        normalized_notes = {normalize_key(k): v for k, v in notes.items()}
        avg_gen = normalized_notes.get('GENERAL', 10.0) # 10 par défaut si non trouvé
        
        # 3. Application des RÈGLES DE GESTION PÉDAGOGIQUES (Guardrails)
        
        # Règle A : Échec Global -> Formation Professionnelle
        # Si la moyenne générale est < 10, l'élève est prioritairement orienté vers le Pro
        if avg_gen < 10:
            final_rec = "Formation Professionnelle"
            interpretation = "Moyenne générale insuffisante pour les filières générales. Session de rattrapage ou orientation professionnelle recommandée."
            confidence = 0.9
        
        # Règle B : Excellence Polyvalente -> Priorité Scientifique
        # Si l'élève est excellent (> 14) et solide en sciences (> 12), on privilégie Sciences
        elif avg_gen >= 14 and mc_scores.get('Scientifique', 0) >= 12:
            final_rec = "Scientifique"
            interpretation = "Profil académique excellent avec de solides bases scientifiques."
            confidence = 0.95
            
        else:
            # Règle C : Choix par Score Pondéré (Métier)
            # On ne considère Littéraire ou Scientifique que si le score est >= 10
            valid_tracks = {k: v for k, v in mc_scores.items() if v >= 9.5} # Tolérance 9.5
            
            if not valid_tracks:
                final_rec = "Formation Professionnelle"
                interpretation = "Profil ne répondant pas aux exigences minimales des séries générales dans les matières clés."
                confidence = 0.8
            else:
                # 4. Arbitrage final avec K-Means
                df_input = pd.DataFrame([{f: float(notes.get(f, 0)) for f in features}])
                X_scaled = scaler.transform(df_input)
                cluster_id = kmeans.predict(X_scaled)[0]
                stat_rec = cluster_labels.get(cluster_id, "Scientifique")
                
                # Le gagnant métier
                mc_rec = max(valid_tracks, key=valid_tracks.get)
                
                # Si l'IA et le métier s'accordent, on confirme
                final_rec = mc_rec
                confidence = 0.7 + (0.2 if stat_rec == mc_rec else 0)
                interpretation = f"Orientation basée sur une excellence relative en {final_rec}."

        return {
            "recommended_track": final_rec,
            "confidence": min(round(confidence, 2), 1.0),
            "scores": {k: round(v, 2) for k, v in mc_scores.items()},
            "method": "Hybride Multi-Critères (Poids métier) + Seuils de réussite",
            "interpretation": interpretation
        }
    except Exception as e:
         return {"error": str(e)}

