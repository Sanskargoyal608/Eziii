# core/serializers.py

from rest_framework import serializers
from .models import Document , Student
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