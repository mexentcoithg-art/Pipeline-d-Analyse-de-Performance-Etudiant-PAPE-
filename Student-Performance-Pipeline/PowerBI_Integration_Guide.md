# Guide d'Intégration Power BI 📊

Ce guide vous explique comment connecter **Power BI Desktop** à notre base de données PostgreSQL (`student_db`) pour créer les tableaux de bord décisionnels pour l'administration de l'établissement (Sprint 5).

---

## Étape 1 : Prérequis

1. Avoir **Power BI Desktop** installé sur votre machine Windows.
2. S'assurer que le serveur PostgreSQL local est en cours d'exécution.
3. Avoir exécuté le script `server/setup_powerbi_views.py` (déjà fait ✅) qui a créé la vue optimisée `powerbi_students_master`.

## Étape 2 : Connexion de Power BI à PostgreSQL

1. Ouvrez Power BI Desktop.
2. Cliquez sur **Obtenir les données** (Get Data) -> **Plus...**
3. Recherchez **Base de données PostgreSQL** dans la barre de recherche et sélectionnez-la, puis cliquez sur **Se connecter**.
4. Remplissez les informations de connexion :
   - **Serveur** : `localhost`
   - **Base de données** : `student_db`
   - **Mode de connectivité** : Choisissez `DirectQuery` (pour des données toujours à jour en temps réel) ou `Importation` (pour plus de fluidité si le volume est faible).
5. Dans l'écran suivant, entrez vos identifiants PostgreSQL (Utilisateur : `postgres`, Mot de passe : `postgres`).
6. Le Navigateur va s'ouvrir. Déroulez le schéma `public` et **cochez la vue `powerbi_students_master`**.
7. Cliquez sur **Charger** (Load).

---

## Étape 3 : Création des Tableaux de Bord (Suggestions)

Avec la vue `powerbi_students_master` importée, vous disposez maintenant de toutes les colonnes nécessaires (données démographiques, performances réelles, absentéisme, et **prédictions de l'IA**).

### 1. Dashboard : KPI Généraux (Aperçu)
- **Cartes à plusieurs lignes** (Cards) :
  - Nombre total d'étudiants (Count de `massar_code`).
  - Moyenne générale de l'établissement (Moyenne de `final_average`).
  - Taux global d'absentéisme (Somme de `total_absences`).

### 2. Dashboard : Intelligence Artificielle (Prédictions)
- **Graphique en anneau** (Donut Chart) : 
  - *Légende* : `ai_risk_level` (Succès vs À risque).
  - *Valeurs* : Nombre de `id_etudiant`.
- **Graphique à barres groupées** :
  - *Axe X* : `ai_top_factor` (Quels sont les facteurs qui font échouer le plus d'élèves ?).
  - *Axe Y* : Nombre de `id_etudiant`.
  
### 3. Dashboard : Analyse Démographique 
- **Graphique en entonnoir** (Funnel Chart) ou **Matrice** :
  - Analysez la corrélation (moyenne de `final_average`) en fonction du `guardian_type` (Métier du tuteur) ou du `gender` (Sexe).

### 4. Filtres (Slicers)
N'oubliez pas d'ajouter des filtres interactifs pour l'administration sur le côté gauche ou en haut du rapport :
- Filtre par `class_name` (ex: 3APIC-13).
- Filtre par `level` (Niveau d'étude).
- Filtre par statut d'IA : `ai_risk_level`.

---

## Étape 4 : Publication

Une fois les visuels créés, vous pouvez enregistrer le fichier sous `.pbix` et le publier sur le **Power BI Service** (Cloud) ou le transmettre sous ce format à l'administration de l'établissement scolaire.
