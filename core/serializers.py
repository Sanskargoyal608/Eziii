# core/serializers.py

from rest_framework import serializers
from .models import Document, Student, GovtJob, Scholarship, StudentProfile, Skill, StudentSkill
from django.contrib.auth.hashers import make_password

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        # Specify the fields you want to include in the API response
        fields = ['document_id', 'student', 'document_type', 'verification_status', 'issue_date', 'verified_data']

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        # We only need the ID and name for the dropdown
        fields = ['student_id', 'full_name', 'email']

class StudentRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['full_name', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True} # Password should not be returned in the response
        }

    def create(self, validated_data):
        # Hash the password before saving
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)
        fields = ['student_id', 'full_name']


class DocumentUploadSerializer(serializers.ModelSerializer):
        class Meta:
            model = Document
            # We'll get the student from the authenticated user, not the request body
            fields = ['document_type', 'uploaded_file']
    
        def create(self, validated_data):
            # 1. Get the authenticated student from the request context
            student = self.context['request'].user
            
            # 2. Create the document object
            document = Document.objects.create(
                student=student,
                document_type=validated_data['document_type'],
                uploaded_file=validated_data['uploaded_file']
            )
            
            # 3. (This part is not yet implemented, will be a part of a background task)
            # For now, we're just saving the file. Text extraction will be
            # triggered by a different process (or we can add it here).
            # We'll add the extraction logic in the View for simplicity for now.
            return document

class GovtJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = GovtJob
        fields = '__all__'
