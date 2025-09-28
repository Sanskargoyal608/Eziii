# e:\Eziii\setup_sqlite.py
import sqlite3
import os

DB_FILE = "federated_data.db"

def create_database():
    """Creates the SQLite database and the required tables if they don't exist."""
    if os.path.exists(DB_FILE):
        print(f"Database file '{DB_FILE}' already exists. Skipping creation.")
        return

    # The 'with' statement ensures the connection is automatically closed.
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            print(f"Successfully connected to and created '{DB_FILE}'")

            # --- Create govt_jobs table ---
            print("Creating 'govt_jobs' table...")
            cursor.execute("""
            CREATE TABLE govt_jobs (
                job_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                department TEXT NOT NULL,
                location TEXT,
                posted_date DATE NOT NULL,
                closing_date DATE NOT NULL,
                description TEXT,
                url TEXT
            );
            """)
            print("Table 'govt_jobs' created successfully.")

            # --- Create scholarships table ---
            print("Creating 'scholarships' table...")
            cursor.execute("""
            CREATE TABLE scholarships (
                scholarship_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                provider TEXT NOT NULL,
                eligibility TEXT,
                amount INTEGER,
                deadline DATE NOT NULL,
                description TEXT,
                url TEXT
            );
            """)
            print("Table 'scholarships' created successfully.")

        print("Database setup complete and connection closed.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    create_database()
