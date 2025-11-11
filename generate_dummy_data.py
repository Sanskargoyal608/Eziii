import os
import django
import random
from faker import Faker

# --- CONFIGURATION ---
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduverify_backend.settings')
django.setup()

from core.models import Student, Document, StudentProfile
from django.utils import timezone

# --- SCRIPT ---
fake = Faker()
NUM_STUDENTS = 100

def create_rich_student_data():
    print(f"Deleting old data...")
    Student.objects.all().delete() # This deletes ALL students and their related data
    
    print(f"Creating {NUM_STUDENTS} new rich students...")
    
    for i in range(NUM_STUDENTS):
        # 1. Create the Student
        full_name = fake.name()
        email = f'student{i+1}@eduverify.com'
        student = Student.objects.create(
            full_name=full_name,
            email=email,
            password='123' # All students have the same password
        )

        # 2. Get the auto-created profile
        profile = student.studentprofile 
        
        # 3. Create Rich, "Verified" Data
        # 30% of students will have a high income
        is_high_income = random.choice([True] * 3 + [False] * 7)
        profile.annual_income = random.randint(600000, 1200000) if is_high_income else random.randint(50000, 400000)
        
        # Give them a random percentage and degree
        profile.highest_percentage = round(random.uniform(60.0, 95.0), 2)
        profile.degrees = random.choice([["B.Tech"], ["12th"], ["B.Tech", "12th"]])
        
        # Give them a random set of skills
        skill_pool = [
            'Python', 'React', 'Java', 'Data Analysis', 'C++', 'SQL', 'Machine Learning', 
            'Unity', 'AWS', 'JavaScript', 'HTML', 'CSS', 'Django', 'FastAPI', 'Node.js',
            'MongoDB', 'PostgreSQL', 'Git', 'Docker', 'Kubernetes', 'Terraform',
            'Data Analyst', 'Business Analyst', 'Power BI', 'Tableau', 'Excel',
            'Project Management', 'Agile', 'Scrum', 'Leadership', 'Communication',
            'C#', 'Azure', 'Google Cloud (GCP)', 'Network Security', 'Penetration Testing'
        ]
        profile.verified_skills = list(set(random.sample(skill_pool, random.randint(3, 6))))

        profile.save()
        
        # 4. Create "Pending" Documents
        doc_types = ['Aadhar Card', 'PAN Card', 'Resume']
        for doc_type in doc_types:
            Document.objects.create(
                student=student,
                document_type=doc_type,
                verification_status='Pending', # We can verify them later in the admin
                issue_date=fake.date_between(start_date='-5y', end_date='today')
            )
            
        print(f"Created student {i+1}: {full_name}")

    print(f"--- Successfully created {NUM_STUDENTS} students. ---")

if __name__ == "__main__":
    create_rich_student_data()