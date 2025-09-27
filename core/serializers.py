# core/serializers.py

from rest_framework import serializers
from .models import Document

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        # Specify the fields you want to include in the API response
        fields = ['document_id', 'student', 'document_type', 'verification_status', 'issue_date', 'verified_data']