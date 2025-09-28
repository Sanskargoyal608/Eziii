from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Document, Student
from .serializers import DocumentSerializer, StudentSerializer

# Import the correct function from your query_analyzer
from query_analyzer import analyze_and_decompose_query_with_llm, execute_query_plan

class DocumentListView(APIView):
    """
    A view to list all documents in the system.
    """
    def get(self, request, format=None):
        documents = Document.objects.all()
        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data)

class StudentListView(APIView):
    """
    A view to list all students, used to populate the dropdown in the chat.
    """
    def get(self, request, format=None):
        students = Student.objects.all()
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)

class FederatedQueryView(APIView):
    """
    Receives a natural language query, decomposes it, executes the plan,
    and returns the integrated results.
    """
    def post(self, request, format=None):
        query = request.data.get('query')
        # Get the student_id from the request data
        student_id = request.data.get('student_id')

        if not query:
            return Response({"error": "No query provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Call the analyzer to get the plan
        plan = analyze_and_decompose_query_with_llm(query)
        
        # --- THIS IS THE FIX ---
        # We now pass the student_id from the request into the execution function.
        results = execute_query_plan(plan, student_id=student_id)
        
        return Response(results)

