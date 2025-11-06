import os
import PyPDF2
import pytesseract
from PIL import Image
from django.conf import settings
import shutil
# --- NEW IMPORT ---
from pdf2image import convert_from_path

# Diagnostic check for Tesseract
if not shutil.which("tesseract"):
    print("="*50)
    print("WARNING: Tesseract-OCR executable not found in your system's PATH.")
    print("Text extraction from images (OCR) will fail.")
    print("Install Tesseract: https://github.com/tesseract-ocr/tesseract")
    print("="*50)

# --- REPLACED FUNCTION ---
def extract_text_from_file(file_path):
    """
    Extracts text from an uploaded PDF (digital or scanned) or Image file.
    """
    print(f"--- Extracting text from: {file_path} ---")
    full_path = os.path.join(settings.MEDIA_ROOT, file_path)
    file_extension = os.path.splitext(full_path)[1].lower()
    
    text = ""
    try:
        if file_extension == '.pdf':
            # --- UPDATED PDF LOGIC ---
            
            # 1. First, try to extract digital text
            try:
                with open(full_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for page in pdf_reader.pages:
                        text += page.extract_text()
                print("Successfully extracted digital text from PDF.")
            except Exception as e:
                print(f"PyPDF2 error: {e}. Assuming scanned PDF.")
                text = "" # Ensure text is empty if PyPDF2 fails

            # 2. If no digital text was found, use OCR
            if not text.strip():
                print("No digital text found. Attempting OCR on PDF...")
                
                # Convert PDF pages to a list of PIL Images
                # You may need to provide the poppler_path if not in PATH
                # images = convert_from_path(full_path, poppler_path=r'C:\path\to\poppler\bin')
                images = convert_from_path(full_path)
                
                # Run Tesseract OCR on each image
                for img in images:
                    text += pytesseract.image_to_string(img)
                print("Successfully extracted text from scanned PDF using OCR.")
            
        elif file_extension in ['.png', '.jpg', '.jpeg', '.tiff']:
            # --- (This image logic is unchanged) ---
            image = Image.open(full_path)
            text = pytesseract.image_to_string(image)
            print("Successfully extracted text from Image (OCR).")
        
        else:
            print(f"Unsupported file type: {file_extension}")
            return f"Error extracting text: Unsupported file type {file_extension}"
            
    except Exception as e:
        print(f"Error during text extraction: {e}")
        # Return the error message so it gets saved to the DB
        return f"Error extracting text: {e}"
    
    return text