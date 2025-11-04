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

import io
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

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
    

class GeneratePDFView(APIView):
    """
    Generates a combined PDF from a list of student's documents.
    Expects a POST request with:
    {
        "document_ids": [1, 5, 12]
    }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        document_ids = request.data.get('document_ids')

        if not document_ids or not isinstance(document_ids, list):
            return Response({"error": "A list of 'document_ids' is required."}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Fetch only the documents that belong to the authenticated user
        #    and were in the requested list. This is a security check.
        docs_to_export = Document.objects.filter(
            student=request.user, 
            document_id__in=document_ids
        ).order_by('document_type')

        if not docs_to_export.exists():
            return Response({"error": "No valid documents found for this user."}, status=status.HTTP_404_NOT_FOUND)

        # 2. Create a PDF in memory
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter # Get page dimensions

        # Set a title
        p.setFont("Helvetica-Bold", 16)
        p.drawString(inch, height - inch, f"Verified Documents for: {request.user.full_name}")
        
        y_position = height - (1.5 * inch) # Start drawing below the title

        for doc in docs_to_export:
            # Check if we need to start a new page
            if y_position < 2 * inch:
                p.showPage() # End current page
                p.setFont("Helvetica-Bold", 16)
                p.drawString(inch, height - inch, f"Verified Documents (Page 2)") # Title for new page
                y_position = height - (1.5 * inch)

            # 3. Draw the document data onto the PDF
            p.setFont("Helvetica-Bold", 12)
            p.drawString(inch, y_position, f"Document Type: {doc.document_type}")
            y_position -= 0.25 * inch
            
            p.setFont("Helvetica", 10)
            p.drawString(inch, y_position, f"Status: {doc.verification_status}")
            y_position -= 0.25 * inch

            if doc.issue_date:
                p.drawString(inch, y_position, f"Issue Date: {doc.issue_date.strftime('%Y-%m-%d')}")
                y_position -= 0.25 * inch

            if doc.verified_data:
                p.drawString(inch, y_position, f"Verified Data: {json.dumps(doc.verified_data)}")
                y_position -= 0.25 * inch
            
            if doc.extracted_text:
                p.setFont("Helvetica-Oblique", 9)
                p.drawString(inch, y_position, "--- Extracted Text Start ---")
                y_position -= 0.2 * inch
                
                # Wrap extracted text
                text = p.beginText(inch, y_position)
                text.setFont("Courier", 8)
                text.setLeading(10) # Line spacing
                for line in doc.extracted_text.split('\n'):
                    text.textLine(line)
                p.drawText(text)
                y_position = text.getY() # Get new Y position after text block
                
                p.setFont("Helvetica-Oblique", 9)
                p.drawString(inch, y_position - (0.1 * inch), "--- Extracted Text End ---")
                y_position -= 0.25 * inch


            # Add a separator line
            y_position -= 0.25 * inch
            p.line(inch, y_position, width - inch, y_position)
            y_position -= 0.25 * inch


        # 4. Save the PDF and return it
        p.showPage()
        p.save()
        
        # Rewind the buffer to the beginning
        buffer.seek(0)
        
        # Create the HTTP response
        response = HttpResponse(
            buffer,
            content_type='application/pdf'
        )
        response['Content-Disposition'] = 'attachment; filename="EduVerify_Documents.pdf"'
        return response

