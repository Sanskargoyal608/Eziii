import os
import django
import random
from faker import Faker
from django.contrib.auth.hashers import make_password

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduverify_backend.settings')
django.setup()

from core.models import Student, Document, GovtJob, Scholarship, Skill, StudentSkill

fake = Faker()

def clear_data():
    """Deletes all existing data from the models."""
    print("Deleting old data...")
    # Delete in an order that respects foreign key constraints
    StudentSkill.objects.all().delete()
    Skill.objects.all().delete()
    Document.objects.all().delete()
    GovtJob.objects.all().delete()
    Scholarship.objects.all().delete()
    Student.objects.all().delete()
    print("Old data deleted.")

def generate_students(num_students=150):
    """Generates fake student data."""
    print(f"Generating {num_students} students...")
    students = []
    for _ in range(num_students):
        profile = fake.profile()
        hashed_password = make_password('password123') # Generic password for all
        
        # Define profile details to be stored in the JSON field
        profile_details = {
            'address': profile['address'],
            'birthdate': str(profile['birthdate']),
            'company': profile['company'],
            'job': profile['job'],
            'income_pa': random.choice([150000, 200000, 250000, 300000, 400000, 500000, 800000, 1000000]),
            'phone_number': fake.phone_number()
        }
        
        student = Student.objects.create(
            full_name=profile['name'],
            email=profile['mail'],
            password=hashed_password,
            profile_details=profile_details
        )
        students.append(student)
    return students

def generate_documents(students_list):
    """Generates documents for each student."""
    print("Generating documents...")
    doc_types = ['10th Marksheet', '12th Marksheet', 'B.Tech Certificate', 'Diploma Certificate', 'Income Certificate', 'Aadhar Card']
    statuses = ['Verified', 'Pending', 'Rejected']

    for student in students_list:
        num_docs = random.randint(3, 7)
        for _ in range(num_docs):
            doc_type = random.choice(doc_types)
            status = random.choice(statuses)
            issue_date = fake.date_between(start_date='-5y', end_date='today')
            
            verified_data = None
            if status == 'Verified':
                if 'Marksheet' in doc_type or 'Certificate' in doc_type:
                    verified_data = {'percentage': round(random.uniform(60.0, 95.0), 2)}
                elif 'Income' in doc_type:
                     verified_data = {'income': student.profile_details.get('income_pa')}

            Document.objects.create(
                student=student,
                document_type=doc_type,
                verification_status=status,
                issue_date=issue_date,
                verified_data=verified_data
            )
            
def generate_jobs(num_jobs=75):
    """Generates fake government job postings."""
    print(f"Generating {num_jobs} jobs...")
    degrees = ['B.Tech', 'Diploma', 'B.Sc', 'M.Tech']
    for _ in range(num_jobs):
        GovtJob.objects.create(
            job_title=fake.job() + " (Government Sector)",
            job_description=fake.paragraph(nb_sentences=5),
            eligibility_criteria={
                'degree_required': random.choice(degrees),
                'min_cgpa': round(random.uniform(6.0, 8.0), 1)
            },
            source_url=fake.url()
        )

def generate_scholarships(num_scholarships=50):
    """Generates fake scholarship opportunities."""
    print(f"Generating {num_scholarships} scholarships...")
    for _ in range(num_scholarships):
        Scholarship.objects.create(
            scholarship_name=f"{fake.company()} Educational Scholarship", # CORRECTED from 'name'
            description=fake.paragraph(nb_sentences=4),
            eligibility_criteria={
                'min_percentage': random.randint(75, 90),
                'max_income_pa': random.choice([250000, 500000, 800000])
            },
            amount=random.randint(5000, 50000)
        )

def main():
    """Main function to run the seeding process."""
    clear_data()
    students_list = generate_students()
    generate_documents(students_list)
    generate_jobs()
    generate_scholarships()
    print("✅ Database seeding successful!")

if __name__ == '__main__':
    main()