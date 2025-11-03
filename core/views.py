from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated # Import permissions
from .models import Document, Student
from rest_framework.permissions import AllowAny, IsAuthenticated 
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import DocumentSerializer, StudentSerializer , DocumentUploadSerializer, StudentRegistrationSerializer
from .utils import extract_text_from_file


# Import the correct function from your query_analyzer
from query_analyzer import analyze_and_decompose_query_with_llm, execute_query_plan

from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q # Import for complex lookups

class RegisterView(APIView):
    permission_classes = [AllowAny] # Anyone can register

    def post(self, request, format=None):
        serializer = StudentRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Manually create tokens for the new user
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# --- NEW: Login View ---
class LoginView(APIView):
    permission_classes = [AllowAny] # Anyone can try to log in

    def post(self, request, format=None):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': 'Email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Find the student by email (case-insensitive)
        try:
            student = Student.objects.get(Q(email__iexact=email))
        except Student.DoesNotExist:
            return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Check the password
        if not student.check_password(password):
            return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Generate tokens
        refresh = RefreshToken.for_user(student)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'student_id': student.student_id,
                'full_name': student.full_name,
                'email': student.email
            }
        }, status=status.HTTP_200_OK)

class StudentListView(APIView):
    # This view now requires a valid JWT token
    permission_classes = [IsAuthenticated] 
    
    def get(self, request, format=None):
        students = Student.objects.all().order_by('full_name')
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)


class DocumentListView(APIView):
    # This view now requires a valid JWT token
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        # --- NEW: Only get documents for the logged-in user ---
        documents = Document.objects.filter(student=request.user)
        serializer = DocumentSerializer(documents, many=True)
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
    # This view now requires a valid JWT token
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        query = request.data.get('query')
        
        # --- NEW: Get student_id from the authenticated user token ---
        # We no longer trust the student_id from the frontend dropdown,
        # we use the one from the token.
        student_id = request.user.student_id

        if not query:
            return Response({"error": "No query provided."}, status=status.HTTP_400_BAD_REQUEST)

        plan = analyze_and_decompose_query_with_llm(query)
        results = execute_query_plan(plan, student_id=student_id)
        
        return Response(results)