from django.db import models
from django.contrib.auth.hashers import make_password, check_password

from django.db.models.signals import post_save
from django.dispatch import receiver

# This file contains the "blueprint" for your database.
# Each class represents a table, and each attribute represents a column.

class Student(models.Model):
    student_id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=100)
    email = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=128) # Stores hashed password
    profile_details = models.JSONField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Hash the password before saving if it's not already hashed
        if self.password and not self.password.startswith(('pbkdf2_sha256$', 'bcrypt$', 'argon2')):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)
    
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)


    class Meta:
        db_table = 'students' # Explicitly name the table

    def __str__(self):
        return self.full_name
    
    @property
    def is_authenticated(self):
        """Always return True for a Student object."""
        return True

    @property
    def is_anonymous(self):
        """Always return False for a Student object."""
        return False

    @property
    def is_active(self):
        """Assume all students in the DB are active."""
        return True
    # --- END OF FIX ---

    class Meta:
        db_table = 'students'

    def __str__(self):
        return self.full_name
    
# --- (Rest of your models: Document, GovtJob, etc.) ---
# ... (all the code from before) ...



class Document(models.Model):
    document_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    document_type = models.CharField(max_length=100)
    verification_status = models.CharField(max_length=20, default='Pending')
    issue_date = models.DateField(null=True, blank=True)
    verified_data = models.JSONField(null=True, blank=True)
    
    # --- NEW FIELDS ---
    # Stores the path to the uploaded file (e.g., "uploads/student_1/aadhar.pdf")
    uploaded_file = models.FileField(upload_to='uploads/', null=True, blank=True)
    # Stores the text extracted by OCR/PDF-parsing
    extracted_text = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'documents'

    def __str__(self):
        return f"{self.document_type} for {self.student.full_name}"

class Skill(models.Model):
    skill_id = models.AutoField(primary_key=True)
    skill_name = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'skills'

    def __str__(self):
        return self.skill_name

class StudentSkill(models.Model):
    student_skill_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)

    class Meta:
        db_table = 'student_skills'

class GovtJob(models.Model):
    job_id = models.AutoField(primary_key=True)
    job_title = models.CharField(max_length=100)
    job_description = models.TextField()
    eligibility_criteria = models.JSONField()
    source_url = models.URLField(null=True, blank=True)

    class Meta:
        db_table = 'govt_jobs'

    def __str__(self):
        return self.job_title

class Scholarship(models.Model):
    scholarship_id = models.AutoField(primary_key=True)
    scholarship_name = models.CharField(max_length=150)
    description = models.TextField()
    eligibility_criteria = models.JSONField()
    amount = models.CharField(max_length=50)

    class Meta:
        db_table = 'scholarships'

    def __str__(self):
        return self.scholarship_name
    
class StudentProfile(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, primary_key=True, related_name='studentprofile')
    highest_percentage = models.FloatField(null=True, blank=True)
    degrees = models.JSONField(default=list, blank=True)
    annual_income = models.IntegerField(null=True, blank=True)
    verified_skills = models.JSONField(default=list, blank=True)

    def __str__(self):
        return f"Profile for {self.student.full_name}"

@receiver(post_save, sender=Student)
def create_student_profile(sender, instance, created, **kwargs):
    if created:
        StudentProfile.objects.create(student=instance)

@receiver(post_save, sender=Student)
def save_student_profile(sender, instance, **kwargs):
    instance.studentprofile.save()
    



