import sqlite3
import os

DB_FILE = "federated_data.db"

def create_database():
    """Creates the SQLite database and the required tables if they don't exist."""
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"Removed existing database file '{DB_FILE}'.")

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
                job_title TEXT NOT NULL,
                job_description TEXT,
                company_name TEXT,
                location TEXT,
                posted_date TEXT,
                source_url TEXT,
                eligibility_criteria TEXT
            );
            """)
            print("Table 'govt_jobs' created successfully.")

            # --- Create scholarships table ---
            print("Creating 'scholarships' table...")
            cursor.execute("""
            CREATE TABLE scholarships (
                scholarship_id INTEGER PRIMARY KEY AUTOINCREMENT,
                scholarship_name TEXT NOT NULL,
                description TEXT,
                eligibility_criteria TEXT
            );
            """)
            print("Table 'scholarships' created successfully.")

        print("Database setup complete and connection closed.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    create_database()

