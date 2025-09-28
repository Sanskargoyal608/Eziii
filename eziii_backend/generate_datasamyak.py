# e:\Eziii\generate_dummy_data.py
import sqlite3
from faker import Faker
from datetime import timedelta

DB_FILE = "federated_data.db"

def populate_sqlite_data():
    """Populates the SQLite database with dummy data for jobs and scholarships."""
    fake = Faker()
    # Using a 'with' statement ensures the connection is automatically managed.
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            print("Connected to SQLite database to populate data.")

            # --- Populate govt_jobs table ---
            jobs = []
            for _ in range(15):
                posted = fake.date_between(start_date='-90d', end_date='today')
                closing = posted + timedelta(days=fake.random_int(min=15, max=45))
                jobs.append((
                    f"{fake.job()} at {fake.company()}",
                    f"Ministry of {fake.word().capitalize()}",
                    fake.city(),
                    posted.strftime('%Y-%m-%d'),
                    closing.strftime('%Y-%m-%d'),
                    fake.paragraph(nb_sentences=3),
                    fake.url()
                ))
            
            cursor.executemany("""
            INSERT INTO govt_jobs (title, department, location, posted_date, closing_date, description, url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, jobs)
            print(f"Inserted {len(jobs)} records into 'govt_jobs'.")

            # --- Populate scholarships table ---
            scholarships = []
            for _ in range(15):
                deadline = fake.date_between(start_date='+30d', end_date='+180d')
                scholarships.append((
                    f"{fake.bs().title()} Scholarship",
                    f"{fake.company()} Foundation",
                    "Bachelor's Degree in Engineering or Science",
                    fake.random_int(min=1000, max=10000),
                    deadline.strftime('%Y-%m-%d'),
                    fake.paragraph(nb_sentences=2),
                    fake.url()
                ))

            cursor.executemany("""
            INSERT INTO scholarships (name, provider, eligibility, amount, deadline, description, url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, scholarships)
            print(f"Inserted {len(scholarships)} records into 'scholarships'.")

            conn.commit()
            print("Data committed and connection closed.")

    except sqlite3.Error as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    populate_sqlite_data()
