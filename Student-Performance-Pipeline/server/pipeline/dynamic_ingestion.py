"""
Dynamic Data Ingestion Module.
Handles schema-flexible imports: analyzes CSV/XLSX files, stores data as JSONB,
and enables ML training on arbitrary datasets.
"""
import pandas as pd
import numpy as np
import json
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from dotenv import load_dotenv
import os

load_dotenv()

class DynamicIngestion:
    """Handles flexible data loading and analysis for any CSV/XLSX."""
    
    def __init__(self):
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'laure1282'),
            'port': os.getenv('DB_PORT', '5432'),
            'dbname': os.getenv('DB_NAME', 'student_db')
        }

    def get_connection(self):
        return psycopg2.connect(**self.db_config)

    def analyze_file(self, filepath):
        """
        Analyze a CSV/XLSX file and return its structure.
        Returns column names, types, sample data, and suggestions.
        """
        df = self._read_file(filepath)
        
        columns_info = []
        for col in df.columns:
            col_type = str(df[col].dtype)
            is_numeric = pd.api.types.is_numeric_dtype(df[col])
            unique_count = df[col].nunique()
            null_count = int(df[col].isnull().sum())
            
            columns_info.append({
                'name': col,
                'dtype': 'numeric' if is_numeric else 'text',
                'unique_values': unique_count,
                'null_count': null_count,
                'sample_values': [str(v) for v in df[col].dropna().head(3).tolist()],
            })
        
        # Auto-detect potential ID column (high uniqueness, text type)
        suggested_id = None
        for ci in columns_info:
            ratio = ci['unique_values'] / len(df) if len(df) > 0 else 0
            if ratio > 0.9 and ci['dtype'] == 'text':
                suggested_id = ci['name']
                break
        
        # Auto-detect potential target column (last numeric column)
        numeric_cols = [ci['name'] for ci in columns_info if ci['dtype'] == 'numeric']
        suggested_target = numeric_cols[-1] if numeric_cols else None
        
        # Get preview rows
        preview = df.head(5).fillna('').to_dict(orient='records')
        
        return {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'columns': columns_info,
            'suggested_id_column': suggested_id,
            'suggested_target_column': suggested_target,
            'preview': preview
        }

    def ingest_data(self, filepath, id_import, id_column=None, mode='add'):
        """
        Ingest data from a file into the ImportedData table as JSONB rows.
        - id_column: which column identifies each student/row
        - mode: 'add' (append) or 'replace' (delete old, insert new)
        """
        df = self._read_file(filepath)
        conn = self.get_connection()
        cur = conn.cursor()
        
        try:
            if mode == 'replace':
                # Delete all previous dynamic import data
                cur.execute("""
                    DELETE FROM ImportedData WHERE id_import IN (
                        SELECT id_import FROM Imports WHERE is_dynamic = TRUE AND id_import != %s
                    )
                """, (id_import,))
                # Also delete the old import records
                cur.execute("""
                    DELETE FROM Imports WHERE is_dynamic = TRUE AND id_import != %s
                """, (id_import,))
            
            # Insert each row as a JSONB record
            inserted = 0
            for idx, row in df.iterrows():
                row_dict = {}
                for col in df.columns:
                    val = row[col]
                    if pd.isna(val):
                        row_dict[col] = None
                    elif isinstance(val, (np.integer,)):
                        row_dict[col] = int(val)
                    elif isinstance(val, (np.floating,)):
                        row_dict[col] = float(val)
                    else:
                        row_dict[col] = str(val)
                
                student_id = row_dict.get(id_column) if id_column else str(idx)
                
                cur.execute("""
                    INSERT INTO ImportedData (id_import, row_index, student_id, raw_data)
                    VALUES (%s, %s, %s, %s)
                """, (id_import, idx, student_id, Json(row_dict)))
                inserted += 1
            
            # Update import metadata
            cur.execute("""
                UPDATE Imports 
                SET row_count = %s, columns_detected = %s, status = 'Uploaded'
                WHERE id_import = %s
            """, (inserted, list(df.columns), id_import))
            
            conn.commit()
            return inserted
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cur.close()
            conn.close()

    def load_for_training(self, id_import, target_column):
        """
        Load data from ImportedData JSONB, reconstruct a DataFrame,
        and split into features (X) and target (y).
        """
        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT row_index, student_id, raw_data 
            FROM ImportedData 
            WHERE id_import = %s 
            ORDER BY row_index
        """, (id_import,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        if not rows:
            raise ValueError("No data found for this import")
        
        # Reconstruct DataFrame from JSONB
        data = [r['raw_data'] for r in rows]
        student_ids = [r['student_id'] for r in rows]
        df = pd.DataFrame(data)
        df['_student_id'] = student_ids
        
        if target_column not in df.columns:
            raise ValueError(f"Target column '{target_column}' not found in data")
        
        # Separate target
        y = pd.to_numeric(df[target_column], errors='coerce')
        
        # Drop rows where target is NaN
        valid_mask = y.notna()
        df = df[valid_mask].copy()
        y = y[valid_mask].copy()
        
        # Prepare features: drop target and non-feature columns
        feature_cols = [c for c in df.columns if c not in [target_column, '_student_id']]
        X = df[feature_cols].copy()
        
        # Auto-encode: convert text columns to numeric via label encoding
        for col in X.columns:
            if not pd.api.types.is_numeric_dtype(X[col]):
                X[col] = pd.to_numeric(X[col], errors='coerce')
                if X[col].isna().all():
                    # Pure text column -> label encode
                    X[col] = df[col].astype('category').cat.codes
        
        # Fill remaining NaN with median
        X = X.fillna(X.median())
        
        return X, y, df['_student_id'].values, list(X.columns)

    def save_predictions(self, id_import, student_ids, predictions, target_column):
        """Save predictions back to ImportedData rows."""
        conn = self.get_connection()
        cur = conn.cursor()
        
        for sid, pred in zip(student_ids, predictions):
            risk = "À risque" if pred < 10 else "Succès"
            cur.execute("""
                UPDATE ImportedData 
                SET predicted_value = %s, risk_level = %s
                WHERE id_import = %s AND student_id = %s
            """, (float(pred), risk, id_import, sid))
        
        # Update import status
        cur.execute("UPDATE Imports SET status = 'Predicted' WHERE id_import = %s", (id_import,))
        conn.commit()
        cur.close()
        conn.close()
        
        return len(predictions)

    def _read_file(self, filepath):
        """Read CSV or Excel file into a pandas DataFrame."""
        ext = os.path.splitext(filepath)[1].lower()
        if ext == '.csv':
            # Try multiple encodings
            for enc in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    return pd.read_csv(filepath, encoding=enc)
                except (UnicodeDecodeError, pd.errors.ParserError):
                    continue
            raise ValueError("Unable to read CSV file with common encodings")
        elif ext in ['.xlsx', '.xls']:
            return pd.read_excel(filepath)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
