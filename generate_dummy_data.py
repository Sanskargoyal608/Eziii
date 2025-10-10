import os
import django
import random
from faker import Faker
from django.contrib.auth.hashers import make_password

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduverify_backend.settings')
django.setup()

from core.models import Student, Document

fake = Faker()

def clear_data():
    """Deletes all existing data from the models."""
    print("Deleting old data...")
    Document.objects.all().delete()
    Student.objects.all().delete()
    print("Old data deleted.")

def generate_students(num_students=150):
    """Generates fake student data."""
    print(f"Generating {num_students} students...")
    students = []
    for _ in range(num_students):
        profile = fake.profile()
        hashed_password = make_password('password123')
        
        profile_details = {
            'address': profile['address'],
            'birthdate': str(profile['birthdate']),
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
    """
    Generates a more realistic set of documents for each student, ensuring
    key qualifications are present and verified for eligibility checks.
    """
    print("Generating documents...")
    doc_types = ['10th Marksheet', '12th Marksheet', 'Aadhar Card']
    degree_types = ['B.Tech Certificate', 'Diploma Certificate']

    for student in students_list:
        # --- NEW LOGIC: Ensure every student has key verified documents ---
        
        # 1. Add a verified degree certificate for eligibility
        degree_to_add = random.choice(degree_types)
        Document.objects.create(
            student=student,
            document_type=degree_to_add,
            verification_status='Verified',
            issue_date=fake.date_between(start_date='-4y', end_date='-1y'),
            verified_data={'percentage': round(random.uniform(70.0, 95.0), 2)}
        )

        # 2. Add a verified income certificate for eligibility
        Document.objects.create(
            student=student,
            document_type='Income Certificate',
            verification_status='Verified',
            issue_date=fake.date_between(start_date='-1y', end_date='today'),
            verified_data={'income': student.profile_details.get('income_pa')}
        )

        # 3. Add a few other random documents for variety
        for _ in range(random.randint(2, 4)):
            Document.objects.create(
                student=student,
                document_type=random.choice(doc_types),
                verification_status=random.choice(['Verified', 'Pending', 'Rejected']),
                issue_date=fake.date_between(start_date='-5y', end_date='today'),
                verified_data=None 
            )
            
def main():
    """Main function to run the seeding process."""
    clear_data()
    students_list = generate_students()
    generate_documents(students_list)
    print("✅ Database seeding successful with improved data!")

if __name__ == '__main__':
    main()

