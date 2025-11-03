from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Document, Student
from rest_framework.permissions import AllowAny, IsAuthenticated 
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import DocumentSerializer, StudentSerializer , DocumentUploadSerializer
from .utils import extract_text_from_file


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


class DocumentUploadView(APIView):
    permission_classes = [IsAuthenticated] # This now works
    
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, format=None):
        print(f"Document upload request received for user: {request.user.full_name}")
        
        serializer = DocumentUploadSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            document = serializer.save()
            
            if document.uploaded_file:
                file_relative_path = document.uploaded_file.name
                extracted_text = extract_text_from_file(file_relative_path)
                
                if extracted_text:
                    document.extracted_text = extracted_text
                    document.save()
                    print("Extracted text saved to document.")
            
            return Response(DocumentSerializer(document).data, status=status.HTTP_201_CREATED)
        
        print(f"Serializer errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



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

