<p align="center">
  <img src="https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=white" />
  <img src="https://img.shields.io/badge/Flask-3.x-000000?style=for-the-badge&logo=flask&logoColor=white" />
  <img src="https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/Scikit--Learn-ML-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white" />
  <img src="https://img.shields.io/badge/Vite-6-646CFF?style=for-the-badge&logo=vite&logoColor=white" />
  <img src="https://img.shields.io/badge/TailwindCSS-4-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white" />
</p>

# 🎓 Student Performance Pipeline (PAPE)

> **Pipeline d'Analyse de Performance Étudiante** — Une plateforme intelligente d'aide à la décision pour le suivi et la prédiction de la réussite scolaire, basée sur l'Intelligence Artificielle.

---

## 📋 Table des matières

- [Aperçu](#-aperçu)
- [Fonctionnalités](#-fonctionnalités)
- [Architecture](#-architecture)
- [Pile Technologique](#-pile-technologique)
- [Structure du Projet](#-structure-du-projet)
- [Installation & Démarrage](#-installation--démarrage)
- [Pipeline ML](#-pipeline-ml)
- [Endpoints API](#-endpoints-api)
- [Captures d'écran](#-captures-décran)
- [Auteur](#-auteur)

---

## 🌟 Aperçu

**PAPE** est un projet de fin d'études (PFE) qui propose une solution complète pour analyser la performance académique des élèves du système éducatif marocain (données **Massar**). Le système combine un **tableau de bord interactif**, un **pipeline de Machine Learning** et des **outils d'aide à la décision stratégique** pour permettre aux enseignants et administrateurs de :

- 📊 Visualiser les indicateurs de performance en temps réel
- 🤖 Prédire le risque d'échec grâce à l'IA (Random Forest, Régression Logistique)
- 🎯 Obtenir des recommandations d'orientation scolaire personnalisées
- 📈 Analyser l'impact de l'absentéisme sur les résultats
- 🔔 Recevoir des alertes automatiques pour les élèves en difficulté

---

## ✨ Fonctionnalités

### Dashboard Interactif
- **KPI en temps réel** : total élèves, moyenne générale, taux de réussite, taux à risque
- **Tableaux de données** avec tri, recherche, filtrage et pagination
- **Graphiques dynamiques** : distribution des notes, comparaison par classe, évolution temporelle
- **Export CSV** des données filtrées
- **Mode sombre / clair** avec transitions fluides

### Intelligence Artificielle & Prédictions
- **Prédiction de la réussite** avec Random Forest Classifier (Accuracy + AUC-ROC)
- **Niveaux de risque** automatiques : *Succès* / *À risque*
- **Facteur principal** identifié pour chaque élève (ex: absences élevées, faible participation)
- **Recommandations personnalisées** générées par le modèle

### Stratégie & Orientation
- **Clustering K-Means** : regroupement des élèves en profils homogènes
- **Moteur d'orientation hybride** : Multi-Critères (60%) + K-Means (40%) avec règles de gestion
- **Analyse d'impact de l'absentéisme** : régression linéaire + arbre de décision pour identifier les seuils critiques
- **Poids pédagogiques** configurables par filière (Scientifique, Littéraire, Technologique)

### Pipeline Dynamique
- Upload de fichiers **CSV / XLSX** avec analyse automatique du schéma
- **Mapping flexible** des colonnes (identifiant, cible, features)
- Entraînement et prédiction à la volée sur des jeux de données personnalisés

### Autres
- **Authentification** par login/mot de passe
- **Internationalisation** (Français 🇫🇷 / Anglais 🇬🇧)
- **Notifications & alertes** automatiques pour les cas critiques
- **Rapports PDF** générables par élève
- **Intégration Power BI** via vues SQL dédiées
- **Design responsive** (desktop & mobile)

---

## 🏗 Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│          React 19 + Vite + Tailwind CSS 4                    │
│    Recharts · Framer Motion · i18next · Lucide Icons         │
│                                                              │
│  ┌─────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │Dashboard│ │Prédictions│ │Stratégie │ │ Pipeline Modal   │ │
│  │   Tab   │ │   Tab    │ │   Tab    │ │ (Upload/Train)   │ │
│  └─────────┘ └──────────┘ └──────────┘ └──────────────────┘ │
└──────────────────────┬───────────────────────────────────────┘
                       │ REST API (Axios)
                       ▼
┌──────────────────────────────────────────────────────────────┐
│                        BACKEND                               │
│                  Flask + Flask-CORS                           │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                  ML Pipeline                           │  │
│  │  DataIngestion → ModelTrainer → Predictor → Analytics  │  │
│  │      (Pandas)    (RandomForest)  (Predict)   (KMeans)  │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  48 Endpoints REST : CRUD, Pipeline, Analytics, Alerts       │
└──────────────────────┬───────────────────────────────────────┘
                       │ psycopg2
                       ▼
┌──────────────────────────────────────────────────────────────┐
│                      BASE DE DONNÉES                         │
│                   PostgreSQL (student_db)                     │
│                                                              │
│   Etudiant · Note · Absences · Participations · Predictions  │
└──────────────────────────────────────────────────────────────┘
```

---

## 🛠 Pile Technologique

### Frontend

| Technologie | Version | Rôle |
|:--|:--|:--|
| **React** | 19.2 | Bibliothèque UI (composants fonctionnels, hooks) |
| **Vite** | 6.4 | Build tool & serveur de développement ultra-rapide |
| **Tailwind CSS** | 4.1 | Framework CSS utility-first |
| **Recharts** | 3.7 | Visualisation de données (BarChart, PieChart, LineChart, ScatterChart) |
| **Framer Motion** | 12.x | Animations et transitions fluides |
| **React Router** | 6.30 | Navigation SPA |
| **i18next** | 25.x | Internationalisation (FR / EN) |
| **Axios** | 1.13 | Client HTTP pour les appels API |
| **Lucide React** | 0.575 | Bibliothèque d'icônes modernes |

### Backend

| Technologie | Version | Rôle |
|:--|:--|:--|
| **Python** | 3.x | Langage backend |
| **Flask** | 3.x | Framework web léger (API REST) |
| **Flask-CORS** | — | Gestion des requêtes Cross-Origin |
| **psycopg2** | — | Driver PostgreSQL natif |
| **python-dotenv** | — | Gestion des variables d'environnement |

### Machine Learning & Data Science

| Technologie | Rôle |
|:--|:--|
| **Scikit-Learn** | Random Forest, Logistic Regression, KMeans, PCA, Decision Tree |
| **Pandas** | Manipulation et transformation des données |
| **NumPy** | Calcul numérique |
| **Joblib** | Sérialisation des modèles ML (.pkl / .joblib) |
| **Matplotlib / Seaborn** | Génération de heatmaps et visualisations EDA côté serveur |

### Base de Données & BI

| Technologie | Rôle |
|:--|:--|
| **PostgreSQL** | Base de données relationnelle (5 tables normalisées) |
| **Power BI** | Tableaux de bord BI connectés via vues SQL |

### DevOps & Outillage

| Outil | Rôle |
|:--|:--|
| **ESLint** | Linting du code JavaScript/React |
| **PostCSS + Autoprefixer** | Post-processing CSS |
| **Playwright** | Tests end-to-end du navigateur |
| **Git / GitHub** | Versioning et collaboration |

---

## 📁 Structure du Projet

```
Student-Performance-Pipeline/
│
├── client/                          # 🖥 Frontend React
│   ├── src/
│   │   ├── components/
│   │   │   ├── App.jsx              # Composant racine + navigation par onglets
│   │   │   ├── DashboardTab.jsx     # Tableau de bord principal + KPIs
│   │   │   ├── PredictionsTab.jsx   # Affichage des prédictions IA
│   │   │   ├── StrategyTab.jsx      # Clustering, orientation, impact
│   │   │   ├── EdaTab.jsx           # Analyse exploratoire (heatmap)
│   │   │   ├── PipelineModal.jsx    # Import CSV/XLSX + pipeline dynamique
│   │   │   ├── StudentModal.jsx     # Fiche détaillée d'un élève
│   │   │   ├── Login.jsx            # Page d'authentification
│   │   │   ├── NotificationsPopover.jsx  # Alertes automatiques
│   │   │   └── AboutTab.jsx         # Page À propos
│   │   ├── locales/                 # Traductions FR / EN
│   │   ├── i18n.js                  # Configuration i18next
│   │   └── main.jsx                 # Point d'entrée React
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
│
├── server/                          # ⚙ Backend Flask
│   ├── app.py                       # API REST principale (~48 routes)
│   ├── init_db.py                   # Initialisation DB + import XLSX Massar
│   ├── requirements.txt             # Dépendances Python
│   ├── .env                         # Variables d'environnement (DB)
│   ├── pipeline/                    # 🤖 Pipeline ML
│   │   ├── data_ingestion.py        # Chargement & preprocessing des données
│   │   ├── model_training.py        # Entraînement RandomForest + LogisticRegression
│   │   ├── predict.py               # Génération des prédictions + recommandations
│   │   ├── analytics.py             # KMeans, orientation, impact absentéisme
│   │   ├── dynamic_ingestion.py     # Pipeline flexible (schéma dynamique)
│   │   ├── cluster_model.joblib     # Modèle de clustering sauvegardé
│   │   └── orientation_model.joblib # Modèle d'orientation sauvegardé
│   └── data/                        # Dataset source (XLSX Massar)
│
├── models/                          # 📦 Modèles ML sérialisés
│   └── model_massar.pkl             # RandomForest + encoders
│
├── demarrer_projet.bat              # 🚀 Script de démarrage rapide (Windows)
└── README.md
```

---

## 🚀 Installation & Démarrage

### Prérequis

- **Node.js** ≥ 18
- **Python** ≥ 3.9
- **PostgreSQL** ≥ 14

### 1. Cloner le dépôt

```bash
git clone https://github.com/<votre-username>/Student-Performance-Pipeline.git
cd Student-Performance-Pipeline
```

### 2. Configurer la base de données

Créez un fichier `server/.env` :

```env
DB_HOST=localhost
DB_USER=postgres
DB_PASSWORD=votre_mot_de_passe
DB_PORT=5432
DB_NAME=student_db
```

Initialisez la base et importez les données :

```bash
cd server
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python init_db.py
```

### 3. Lancer le Backend

```bash
cd server
venv\Scripts\activate
python app.py
```

> Le serveur Flask démarre sur `http://localhost:5000`

### 4. Lancer le Frontend

```bash
cd client
npm install
npm run dev
```

> L'application React démarre sur `http://localhost:5173`

### ⚡ Démarrage rapide (Windows)

Double-cliquez sur `demarrer_projet.bat` pour lancer simultanément le backend et le frontend.

---

## 🤖 Pipeline ML

Le pipeline de Machine Learning suit un flux en 4 étapes :

```
 ┌───────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
 │ 1. Ingestion  │────▶│ 2. Training  │────▶│ 3. Predict   │────▶│ 4. Analytics │
 │  (PostgreSQL  │     │ (RandomForest│     │ (Proba +     │     │ (KMeans +    │
 │   → Pandas)   │     │  + LogReg)   │     │  Risque)     │     │ Orientation) │
 └───────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

| Étape | Module | Description |
|:--|:--|:--|
| **Ingestion** | `data_ingestion.py` | Charge les données depuis PostgreSQL, effectue les jointures, pivote les notes par matière, encode les variables catégorielles (LabelEncoder) |
| **Training** | `model_training.py` | Entraîne un **RandomForestClassifier** (n=100) et une **LogisticRegression** (baseline). Évalue via Accuracy et AUC-ROC. Sauvegarde le modèle en `.pkl` |
| **Prediction** | `predict.py` | Génère les probabilités de succès, attribue un niveau de risque (*Succès* / *À risque*), identifie le facteur dominant et produit une recommandation textuelle |
| **Analytics** | `analytics.py` | Clustering KMeans (profils élèves), analyse d'impact de l'absentéisme (régression + arbre de décision), moteur d'orientation hybride (multi-critères + KMeans) |

---

## 📡 Endpoints API

L'API REST expose **~48 endpoints** organisés par domaine :

| Domaine | Endpoints clés | Méthodes |
|:--|:--|:--|
| **Authentification** | `/api/login` | POST |
| **Étudiants (CRUD)** | `/api/students`, `/api/students/<id>` | GET, POST, PUT, DELETE |
| **Pipeline** | `/api/upload-csv`, `/api/train`, `/api/predict` | POST |
| **Pipeline Dynamique** | `/api/dynamic/upload`, `/api/dynamic/ingest`, `/api/dynamic/run/<id>` | POST |
| **Prédictions** | `/api/predictions` | GET |
| **Statistiques** | `/api/stats`, `/api/temporal-stats`, `/api/class-comparison` | GET |
| **EDA** | `/api/eda/heatmap` | GET |
| **Stratégie IA** | `/api/absenteeism-impact`, `/api/clusters`, `/api/orientation/<code>` | GET |
| **Alertes** | `/api/alerts`, `/api/alerts/generate`, `/api/alerts/<id>/read` | GET, POST, PUT |
| **Imports** | `/api/imports`, `/api/imports/<id>` | GET, DELETE |
| **Rapports** | `/api/report/<massar>` | GET (PDF) |

---

## 📸 Captures d'écran

> *Ajoutez ici des captures d'écran de votre application pour illustrer les différentes fonctionnalités.*

<!--
![Dashboard](docs/screenshots/dashboard.png)
![Prédictions](docs/screenshots/predictions.png)
![Stratégie](docs/screenshots/strategy.png)
-->

---

## 👤 Auteur

Projet de Fin d'Études (PFE) — **Pipeline d'Analyse de Performance Étudiante (PAPE)**

---

<p align="center">
  <sub>Built with ❤️ using React, Flask, Scikit-Learn & PostgreSQL</sub>
</p>
