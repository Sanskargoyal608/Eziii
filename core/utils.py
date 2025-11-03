import os
import PyPDF2
import pytesseract
from PIL import Image
from django.conf import settings
# --- IMPORTANT ---
# If you installed Tesseract in a custom location, you might need this:
# pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
def extract_text_from_file(file_path):
    """
    Extracts text from an uploaded PDF or Image file.
    """
    print(f"--- Extracting text from: {file_path} ---")
    full_path = os.path.join(settings.MEDIA_ROOT, file_path)
    file_extension = os.path.splitext(full_path)[1].lower()
    
    text = ""
    try:
        if file_extension == '.pdf':
            with open(full_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    text += page.extract_text()
            print("Successfully extracted text from PDF.")
        
        elif file_extension in ['.png', '.jpg', '.jpeg', '.tiff']:
            image = Image.open(full_path)
            text = pytesseract.image_to_string(image)
            print("Successfully extracted text from Image (OCR).")
        
        else:
            print(f"Unsupported file type: {file_extension}")
            return None
            
    except Exception as e:
        print(f"Error during text extraction: {e}")
        return f"Error extracting text: {e}"
    
    return text
    
