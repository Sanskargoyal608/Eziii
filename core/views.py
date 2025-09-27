# core/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Document
from .serializers import DocumentSerializer

class DocumentListView(APIView):
    """
    A view to list all documents in the system.
    * For now, it lists all documents. Later, we will filter by logged-in user.
    """
    def get(self, request, format=None):
        # 1. Get the data from the database
        documents = Document.objects.all()
        # 2. Use the serializer to translate it to JSON
        serializer = DocumentSerializer(documents, many=True)
        # 3. Return the JSON response
        return Response(serializer.data)