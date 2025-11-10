from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated # Import permissions
from .models import Document, Student, GovtJob
from rest_framework.permissions import AllowAny, IsAuthenticated 
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import DocumentSerializer, StudentSerializer , DocumentUploadSerializer, StudentRegistrationSerializer
from .utils import extract_text_from_file
import os

from django.conf import settings
from PIL import Image # <-- ADD THIS
from pypdf import PdfWriter, PdfReader # <-- ADD THIS
from reportlab.lib.utils import ImageReader as ReportLabImageReader # <-- ADD THIS
from reportlab.lib.colors import green, red, black # <-- ADD THIS

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
                
                # --- THIS IS THE FIX ---
                if not extracted_text:
                    # Case 1: The function returned empty string (e.g., blank PDF)
                    document.extracted_text = "No text could be extracted from this document."
                    print("Warning: No text extracted.")
                elif extracted_text.startswith("Error extracting text:"):
                    # Case 2: The function returned an error message
                    document.extracted_text = extracted_text
                    print(f"Error: {extracted_text}")
                else:
                    # Case 3: Success
                    document.extracted_text = extracted_text
                    print("Extracted text saved to document.")
                
                document.save() # Save the result (success, error, or empty)
                # --- END OF FIX ---
            
            return Response(DocumentSerializer(document).data, status=status.HTTP_201_CREATED)
        
        print(f"Serializer errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class FederatedQueryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        query = request.data.get('query')
        student_id = request.user.student_id 

        if not query:
            return Response({"error": "No query provided."}, status=status.HTTP_400_BAD_REQUEST)

        plan = analyze_and_decompose_query_with_llm(query)
        
        # --- THIS IS THE CHANGE ---
        # We now pass the original query text along with the plan
        results = execute_query_plan(plan, student_id=student_id, original_query=query)
        
        return Response(results)


    

class GeneratePDFView(APIView):
    """
    Generates a combined PDF from a list of a student's documents.
    This new version merges actual PDFs and Images, stamping them
    with their verification status.
    """
    permission_classes = [IsAuthenticated]

    def _create_stamp_page(self, text, status):
        """Helper function to create an in-memory PDF page with a stamp."""
        stamp_buffer = io.BytesIO()
        stamp_canvas = canvas.Canvas(stamp_buffer, pagesize=letter)
        
        # Set font and color
        stamp_canvas.setFont("Helvetica-Bold", 12)
        if status == 'Verified':
            stamp_canvas.setFillColor(green)
        elif status == 'Rejected':
            stamp_canvas.setFillColor(red)
        else:
            stamp_canvas.setFillColor(black) # Pending or other

        # Draw the text at the top-left corner
        stamp_canvas.drawString(0.75 * inch, letter[1] - (0.75 * inch), f"STATUS: {text.upper()}")
        stamp_canvas.save()
        stamp_buffer.seek(0)
        return PdfReader(stamp_buffer).pages[0]

    def post(self, request, format=None):
        document_ids = request.data.get('document_ids')

        if not document_ids or not isinstance(document_ids, list):
            return Response({"error": "A list of 'document_ids' is required."}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Fetch only documents that belong to the authenticated user
        docs_to_export = Document.objects.filter(
            student=request.user, 
            document_id__in=document_ids
        ).order_by('document_type')

        if not docs_to_export.exists():
            return Response({"error": "No valid documents found for this user."}, status=status.HTTP_404_NOT_FOUND)

        # 2. Create the output PDF in memory
        output_pdf_writer = PdfWriter()
        
        for doc in docs_to_export:
            # 3. Create the appropriate stamp for this document
            stamp_page = self._create_stamp_page(doc.verification_status, doc.verification_status)
            
            # 4. Get the full path to the uploaded file
            if not doc.uploaded_file:
                continue # Skip if there's no file
                
            file_path = os.path.join(settings.MEDIA_ROOT, doc.uploaded_file.name)
            if not os.path.exists(file_path):
                continue # Skip if file is missing

            file_ext = os.path.splitext(file_path)[1].lower()

            try:
                # --- 5A. If the file is a PDF ---
                if file_ext == '.pdf':
                    pdf_reader = PdfReader(file_path)
                    for page in pdf_reader.pages:
                        # Add the stamp to the original page
                        page.merge_page(stamp_page) 
                        output_pdf_writer.add_page(page)
                
                # --- 5B. If the file is an Image ---
                elif file_ext in ['.png', '.jpg', '.jpeg']:
                    # Open the image to get its dimensions
                    img = Image.open(file_path)
                    img_width, img_height = img.size
                    img.close()
                    
                    # Create a new PDF page with the image's dimensions
                    page_buffer = io.BytesIO()
                    img_canvas = canvas.Canvas(page_buffer, pagesize=(img_width, img_height))
                    
                    # Draw the image on the page
                    img_canvas.drawImage(ReportLabImageReader(file_path), 0, 0, width=img_width, height=img_height)
                    img_canvas.save()
                    page_buffer.seek(0)
                    
                    # Merge the stamp with the new image-page
                    image_pdf_page = PdfReader(page_buffer).pages[0]
                    image_pdf_page.merge_page(stamp_page)
                    output_pdf_writer.add_page(image_pdf_page)

            except Exception as e:
                print(f"Error processing file {file_path}: {e}")
                # Create a simple error page and add it to the PDF
                error_buffer = io.BytesIO()
                error_canvas = canvas.Canvas(error_buffer, pagesize=letter)
                error_canvas.drawString(1 * inch, 10 * inch, f"Error processing file: {doc.document_type}")
                error_canvas.drawString(1 * inch, 9.5 * inch, str(e))
                error_canvas.save()
                error_buffer.seek(0)
                output_pdf_writer.add_page(PdfReader(error_buffer).pages[0])

        # 6. Save the final merged PDF to a buffer
        final_buffer = io.BytesIO()
        output_pdf_writer.write(final_buffer)
        final_buffer.seek(0)

        # 7. Create and return the HTTP response
        response = HttpResponse(
            final_buffer,
            content_type='application/pdf'
        )
        response['Content-Disposition'] = 'attachment; filename="EduVerify_Documents.pdf"'
        return response
    

class AdminDashboardView(APIView):
    """
    Public view for the admin dashboard.
    Fetches all students and all documents.
    """
    permission_classes = [AllowAny] # Publicly accessible

    def get(self, request, format=None):
        try:
            students = Student.objects.all().order_by('full_name')
            documents = Document.objects.all().order_by('-issue_date')

            student_serializer = StudentSerializer(students, many=True)
            document_serializer = DocumentSerializer(documents, many=True)

            return Response({
                'students': student_serializer.data,
                'documents': document_serializer.data
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StudentSummaryView(APIView):
    """
    Public view to get an AI-generated summary for a specific student.
    """
    permission_classes = [AllowAny] # Publicly accessible

    def get(self, request, student_id, format=None):
        try:
            student = Student.objects.get(student_id=student_id)
            documents = Document.objects.filter(student=student)
            
            # --- We will build this LLM function in a later step ---
            # For now, let's return the raw data.
            # In Phase 3, we'll replace this with:
            # summary = get_student_summary_with_llm(student, documents)
            
            student_data = StudentSerializer(student).data
            documents_data = DocumentSerializer(documents, many=True).data

            # Placeholder summary
            summary = f"Student {student.full_name} (ID: {student.student_id}) has {documents.count()} document(s). "
            summary += "Verification status: "
            summary += ", ".join([doc.verification_status for doc in documents])

            return Response({
                "summary_text": summary,
                "raw_student": student_data,
                "raw_documents": documents_data
            }, status=status.HTTP_200_OK)

        except Student.DoesNotExist:
            return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminChatView(APIView):
    """
    Public view for the admin's federated chat.
    Accepts a 'student_id' (or 'all') to provide context to the query.
    """
    permission_classes = [AllowAny] # Publicly accessible

    def post(self, request, format=None):
        query = request.data.get('query')
        
        # Admin can select a specific student or 'all'
        student_id_str = request.data.get('student_id') # e.g., "1", "5", or "all"

        student_context_id = None
        if student_id_str and student_id_str != 'all':
            try:
                student_context_id = int(student_id_str)
            except ValueError:
                return Response({"error": "Invalid student_id format."}, status=status.HTTP_400_BAD_REQUEST)

        if not query:
            return Response({"error": "No query provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Analyze the query (this is the same as the user's chat)
        plan = analyze_and_decompose_query_with_llm(query)
        
        # Execute the plan, but now pass the specific student_id (or None if 'all')
        # The query_analyzer will handle aggregate queries like "how many students..."
        results = execute_query_plan(plan, student_id=student_context_id, original_query=query)
        
        return Response(results)
