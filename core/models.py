from django.db import models

# Note: We are now explicitly defining the primary key for each model to match our SQL schema.

class Student(models.Model):
    student_id = models.AutoField(primary_key=True) # Explicitly define the primary key
    full_name = models.CharField(max_length=100)
    email = models.CharField(max_length=100, unique=True)
    password_hash = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_details = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'students'

    def __str__(self):
        return self.full_name

class GovtJob(models.Model):
    job_id = models.AutoField(primary_key=True) # Explicitly define the primary key
    job_title = models.CharField(max_length=255)
    job_description = models.TextField()
    eligibility_criteria = models.JSONField()
    required_skills_raw = models.TextField(blank=True, null=True)
    source_url = models.CharField(max_length=255, blank=True, null=True)
    posted_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'govt_jobs'

    def __str__(self):
        return self.job_title

class Scholarship(models.Model):
    scholarship_id = models.AutoField(primary_key=True) # Explicitly define the primary key
    scholarship_name = models.CharField(max_length=255)
    description = models.TextField()
    eligibility_criteria = models.JSONField()
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    source_url = models.CharField(max_length=255, blank=True, null=True)
    deadline_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'scholarships'

    def __str__(self):
        return self.scholarship_name

class Document(models.Model):
    document_id = models.AutoField(primary_key=True) # Explicitly define the primary key
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    document_type = models.CharField(max_length=50)
    submission_info = models.TextField()
    verification_status = models.CharField(max_length=20, default='Pending')
    digital_signature = models.TextField(blank=True, null=True)
    verified_data = models.JSONField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'documents'

    def __str__(self):
        return f"{self.document_type} for {self.student.full_name}"

class Skill(models.Model):
    skill_id = models.AutoField(primary_key=True) # Explicitly define the primary key
    skill_name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'skills'

    def __str__(self):
        return self.skill_name

class StudentSkill(models.Model):
    student_skill_id = models.AutoField(primary_key=True) # Explicitly define the primary key
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)

    class Meta:
        db_table = 'student_skills'
        unique_together = ('student', 'skill')

    def __str__(self):
        return f"{self.student.full_name} - {self.skill.skill_name}"

