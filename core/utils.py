import os
import PyPDF2
import pytesseract
from PIL import Image
from django.conf import settings
import shutil
# --- NEW IMPORT ---
from pdf2image import convert_from_path

PARTNER_IP = "192.168.52.109" # Ensure this matches your settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

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

def get_recommended_jobs_from_llm(student_profile):
    """
    Fetches ALL jobs from the partner API, then uses LLM to filter 
    them based on the student_profile.
    """
    print(f"--- Fetching and Filtering Jobs for Profile: {student_profile} ---")
    
    # 1. Fetch All Jobs
    jobs_url = f'http://{PARTNER_IP}:5000/api/jobs'
    try:
        response = requests.get(jobs_url, timeout=10)
        response.raise_for_status()
        all_jobs = response.json()
    except Exception as e:
        return {"error": f"Failed to fetch jobs from partner: {e}"}

    # 2. Filter with LLM
    # We send the profile + jobs list to Gemini
    
    # Optimization: Limit to first 30 jobs to avoid token limits if list is huge
    jobs_context = all_jobs[:30] 
    
    prompt = f"""
    You are a Recruiting AI.
    
    Student Profile:
    {json.dumps(student_profile)}

    Job List (JSON):
    {json.dumps(jobs_context)}

    Task:
    1. Analyze the 'description' or 'eligibility' of each job.
    2. Compare it with the Student Profile (Skills, Degree, Percentage).
    3. Return a JSON List of ONLY the jobs the student is eligible for.
    4. Add a field "match_reason" to each job explaining why it fits (e.g., "Matches Python skill").
    
    Return ONLY valid JSON. Empty list [] if no matches.
    """

    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json"}
    }

    try:
        response = requests.post(api_url, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        text_response = result['candidates'][0]['content']['parts'][0]['text']
        return json.loads(text_response)
    except Exception as e:
        print(f"LLM Filtering failed: {e}")
        return [] # Return empty list on failure rather than crashing