import psycopg2
import json
from faker import Faker
import random
import hashlib

# --- DATABASE CONNECTION DETAILS ---
# Replace with your actual database connection details
DB_NAME = "your_db_name"
DB_USER = "your_db_user"
DB_PASS = "your_db_password"
DB_HOST = "localhost"
DB_PORT = "5432"

# --- CONFIGURATION ---
NUM_STUDENTS = 150
NUM_JOBS = 75
NUM_SCHOLARSHIPS = 50
DOCS_PER_STUDENT = 7

# Initialize Faker for generating fake data
fake = Faker('en_IN') # Using Indian locale for more relevant names/addresses

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT
        )
        return conn
    except psycopg2.OperationalError as e:
        print(f"Error: Could not connect to the database. Please check your connection details.")
        print(f"Details: {e}")
        return None

def generate_students(cursor):
    """Generates and inserts fake student data."""
    students = []
    print(f"Generating {NUM_STUDENTS} students...")
    for _ in range(NUM_STUDENTS):
        full_name = fake.name()
        email = fake.unique.email()
        password = "password123" # Use a default password for all
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        phone_number = fake.phone_number()
        profile = {
            "address": fake.address().replace('\n', ', '),
            "date_of_birth": fake.date_of_birth(minimum_age=18, maximum_age=25).isoformat(),
            "income_pa": random.choice([200000, 450000, 600000, 800000, 1200000])
        }
        
        cursor.execute(
            """
            INSERT INTO Students (full_name, email, password_hash, phone_number, profile_details)
            VALUES (%s, %s, %s, %s, %s) RETURNING student_id;
            """,
            (full_name, email, password_hash, phone_number, json.dumps(profile))
        )
        student_id = cursor.fetchone()[0]
        students.append({'id': student_id, 'profile': profile})
    print("Students generated.")
    return students

def generate_documents(cursor, students):
    """Generates fake documents for each student."""
    print("Generating documents...")
    doc_types = ['Aadhaar Card', '12th Marksheet', '10th Marksheet', 'B.Tech Certificate', 'Diploma Certificate', 'Income Certificate']
    statuses = ['Verified', 'Pending', 'Rejected']
    
    for student in students:
        for _ in range(DOCS_PER_STUDENT):
            doc_type = random.choice(doc_types)
            status = random.choice(statuses)
            verified_data = None
            if status == 'Verified':
                # Create some mock verified data based on doc type
                if 'Marksheet' in doc_type or 'Certificate' in doc_type:
                    verified_data = {
                        "degree": "B.Tech" if 'B.Tech' in doc_type else 'Diploma' if 'Diploma' in doc_type else 'HSC',
                        "percentage": round(random.uniform(60.0, 98.5), 2)
                    }
                elif 'Income' in doc_type:
                    verified_data = {"income_pa": student['profile']['income_pa']}
            
            cursor.execute(
                """
                INSERT INTO Documents (student_id, document_type, submission_info, verification_status, verified_data)
                VALUES (%s, %s, %s, %s, %s);
                """,
                (student['id'], doc_type, f"app_no_{random.randint(10000, 99999)}", status, json.dumps(verified_data) if verified_data else None)
            )
    print("Documents generated.")


def generate_jobs_and_scholarships(cursor):
    """Generates fake jobs and scholarships."""
    print("Generating jobs and scholarships...")
    # Jobs
    job_titles = ["Junior Engineer", "Data Analyst", "Systems Officer", "Clerk", "Technical Assistant"]
    degrees = ["B.Tech", "B.Sc", "Diploma", "Any Graduate"]
    for _ in range(NUM_JOBS):
        eligibility = {
            "degree": random.choice(degrees),
            "min_cgpa": round(random.uniform(6.0, 8.0), 1),
        }
        cursor.execute(
            """
            INSERT INTO Govt_Jobs (job_title, job_description, eligibility_criteria, source_url)
            VALUES (%s, %s, %s, %s);
            """,
            (random.choice(job_titles), fake.paragraph(nb_sentences=5), json.dumps(eligibility), fake.url())
        )
    
    # Scholarships
    scholarship_names = ["Merit Scholarship for Engineers", "Financial Aid for Students", "State Education Grant"]
    for _ in range(NUM_SCHOLARSHIPS):
        eligibility = {
            "max_income_pa": random.choice([500000, 700000, 900000]),
            "min_percentage": random.choice([75, 80, 85, 90])
        }
        cursor.execute(
            """
            INSERT INTO Scholarships (scholarship_name, description, eligibility_criteria, amount, source_url)
            VALUES (%s, %s, %s, %s, %s);
            """,
            (random.choice(scholarship_names), fake.paragraph(nb_sentences=3), json.dumps(eligibility), random.randint(10000, 50000), fake.url())
        )
    print("Jobs and scholarships generated.")


def main():
    """Main function to run the data generation process."""
    conn = get_db_connection()
    if conn is None:
        return
        
    try:
        with conn.cursor() as cursor:
            # Clear existing data in the correct order to respect foreign key constraints
            print("Clearing old data...")
            cursor.execute("TRUNCATE TABLE Student_Skills, Documents, Students, Govt_Jobs, Scholarships, Skills RESTART IDENTITY CASCADE;")
            
            # Generate and insert new data
            students = generate_students(cursor)
            generate_documents(cursor, students)
            generate_jobs_and_scholarships(cursor)
            
            print("\nDatabase seeding successful!")
    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        conn.commit()
        conn.close()
        print("Database connection closed.")


if __name__ == "__main__":
    main()
