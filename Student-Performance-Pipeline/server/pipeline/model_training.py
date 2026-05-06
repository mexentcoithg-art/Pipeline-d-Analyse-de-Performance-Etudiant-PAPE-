from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score
from joblib import dump, load
import os
from pipeline.data_ingestion import DataIngestion

class ModelTrainer:
    def __init__(self):
        # Using Classifier instead of Regressor
        self.model_rf = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model_lr = LogisticRegression(max_iter=1000, random_state=42)
        self.ingestion = DataIngestion()

    def train_and_evaluate(self):
        df_raw = self.ingestion.load_data()
        df_processed = self.ingestion.preprocess_data(df_raw)
        
        # Use the binary target
        y = df_processed['target_success']
        X = df_processed.drop('target_success', axis=1)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Train Random Forest Classifier
        self.model_rf.fit(X_train, y_train)
        rf_pred = self.model_rf.predict(X_test)
        rf_proba = self.model_rf.predict_proba(X_test)[:, 1]
        
        rf_acc = accuracy_score(y_test, rf_pred)
        rf_auc = roc_auc_score(y_test, rf_proba) if len(set(y_test)) > 1 else 0

        # Train Logistic Regression (Baseline)
        self.model_lr.fit(X_train, y_train)
        lr_pred = self.model_lr.predict(X_test)
        lr_acc = accuracy_score(y_test, lr_pred)

        # Save artifacts (models + encoders)
        if not os.path.exists("models"):
            os.makedirs("models")
            
        artifacts = {
            "model_rf": self.model_rf,
            "model_lr": self.model_lr,
            "feature_names": list(X.columns),
            "label_encoders": self.ingestion.label_encoders,
            "type": "classification"
        }
        
        dump(artifacts, "models/model_massar.pkl")
        
        return dict(
            RandomForest_Accuracy=rf_acc,
            RandomForest_AUC=rf_auc,
            LogisticRegression_Accuracy=lr_acc,
            records=len(df_raw),
            features=len(X.columns)
        )

if __name__ == '__main__':
    trainer = ModelTrainer()
    results = trainer.train_and_evaluate()
    print("Training Complete!")
    print(f"Dataset Size: {results['records']} rows, {results['features']} features")
    print(f"Random Forest Accuracy: {results['RandomForest_Accuracy']:.4f}")
    print(f"Random Forest AUC: {results['RandomForest_AUC']:.4f}")
