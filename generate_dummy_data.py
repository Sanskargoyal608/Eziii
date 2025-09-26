import os
import django
import random
import hashlib
from faker import Faker

# --- SETUP DJANGO ENVIRONMENT ---
# This is crucial to allow this standalone script to access your Django models
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduverify_backend.settings')
django.setup()

# --- IMPORT YOUR MODELS ---
# Must be done *after* django.setup()
from core.models import Student, Document, GovtJob, Scholarship

# --- CONFIGURATION ---
NUM_STUDENTS = 150
NUM_JOBS = 75
NUM_SCHOLARSHIPS = 50
DOCS_PER_STUDENT = 7

# Initialize Faker for generating fake data
fake = Faker('en_IN')

def clear_data():
    """Deletes all data from the tables to start fresh."""
    print("Deleting old data...")
    Document.objects.all().delete()
    GovtJob.objects.all().delete()
    Scholarship.objects.all().delete()
    Student.objects.all().delete()
    print("Old data deleted.")

def generate_students():
    """Generates and saves fake student data."""
    students = []
    print(f"Generating {NUM_STUDENTS} students...")
    for _ in range(NUM_STUDENTS):
        profile = {
            "address": fake.address().replace('\n', ', '),
            "date_of_birth": fake.date_of_birth(minimum_age=18, maximum_age=25).isoformat(),
            "income_pa": random.choice([200000, 450000, 600000, 800000, 1200000])
        }
        password = "password123"
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        student = Student.objects.create(
            full_name=fake.name(),
            email=fake.unique.email(),
            password_hash=password_hash,
            phone_number=fake.phone_number(),
            profile_details=profile
        )
        students.append(student)
    print("Students generated successfully.")
    return students

def generate_documents(students):
    """Generates fake documents for a list of student objects."""
    print("Generating documents...")
    doc_types = ['Aadhaar Card', '12th Marksheet', '10th Marksheet', 'B.Tech Certificate', 'Diploma Certificate', 'Income Certificate']
    statuses = ['Verified', 'Pending', 'Rejected']

    for student in students:
        for _ in range(random.randint(3, DOCS_PER_STUDENT)):
            doc_type = random.choice(doc_types)
            status = random.choice(statuses)
            verified_data = None
            if status == 'Verified':
                if 'Marksheet' in doc_type or 'Certificate' in doc_type:
                    verified_data = {
                        "degree": "B.Tech" if 'B.Tech' in doc_type else 'Diploma' if 'Diploma' in doc_type else 'HSC',
                        "percentage": round(random.uniform(60.0, 98.5), 2)
                    }
                elif 'Income' in doc_type:
                    verified_data = {"income_pa": student.profile_details['income_pa']}

            Document.objects.create(
                student=student,
                document_type=doc_type,
                submission_info=f"app_no_{random.randint(10000, 99999)}",
                verification_status=status,
                verified_data=verified_data
            )
    print("Documents generated successfully.")

def generate_jobs_and_scholarships():
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
        GovtJob.objects.create(
            job_title=random.choice(job_titles),
            job_description=fake.paragraph(nb_sentences=5),
            eligibility_criteria=eligibility,
            source_url=fake.url()
        )

    # Scholarships
    scholarship_names = ["Merit Scholarship for Engineers", "Financial Aid for Students", "State Education Grant"]
    for _ in range(NUM_SCHOLARSHIPS):
        eligibility = {
            "max_income_pa": random.choice([500000, 700000, 900000]),
            "min_percentage": random.choice([75, 80, 85, 90])
        }
        Scholarship.objects.create(
            scholarship_name=random.choice(scholarship_names),
            description=fake.paragraph(nb_sentences=3),
            eligibility_criteria=eligibility,
            amount=random.randint(10000, 50000),
            source_url=fake.url()
        )
    print("Jobs and scholarships generated successfully.")


def main():
    """Main function to run the data generation process."""
    clear_data()
    students_list = generate_students()
    generate_documents(students_list)
    generate_jobs_and_scholarships()
    print("\n✅ Database seeding successful!")

if __name__ == "__main__":
    main()

