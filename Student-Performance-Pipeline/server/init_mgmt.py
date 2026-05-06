import psycopg2
from werkzeug.security import generate_password_hash
import os

def init_mgmt_db():
    conn = None
    try:
        conn = psycopg2.connect(
            host='localhost',
            user='postgres',
            password='laure1282',
            dbname='student_db'
        )
        cur = conn.cursor()

        # 1. Create Users table
        print("Creating Users table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Users (
                id_user SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(20) NOT NULL CHECK (role IN ('Admin', 'Enseignant', 'Direction')),
                class_assigned VARCHAR(50)
            );
        """)

        # 2. Create Interventions table
        print("Creating Interventions table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Interventions (
                id_intervention SERIAL PRIMARY KEY,
                id_etudiant INT REFERENCES Etudiant(id_etudiant),
                type_action VARCHAR(100) NOT NULL,
                description TEXT,
                date_action TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status_efficacite VARCHAR(50),
                id_user INT REFERENCES Users(id_user)
            );
        """)

        # 3. Create Alerts table
        print("Creating Alerts table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Alerts (
                id_alert SERIAL PRIMARY KEY,
                message TEXT NOT NULL,
                is_read BOOLEAN DEFAULT FALSE,
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 4. Insert initial users
        print("Seeding initial users...")
        users = [
            ('admin', 'admin', 'Admin', None),
            ('teacher1', 'teacher1', 'Enseignant', 'TCR1'),
            ('manager1', 'manager1', 'Direction', None)
        ]

        for username, password, role, cl in users:
            hash_pwd = generate_password_hash(password)
            cur.execute("""
                INSERT INTO Users (username, password_hash, role, class_assigned)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (username) DO NOTHING;
            """, (username, hash_pwd, role, cl))

        conn.commit()
        print("Management database initialized successfully!")
    except Exception as e:
        print(f"Error initializing management database: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    init_mgmt_db()
