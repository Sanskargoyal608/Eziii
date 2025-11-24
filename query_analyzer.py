# This script contains the core logic for the federated query engine.
import requests
import re
import os
import json
from dotenv import load_dotenv
from core.models import Student, Document, StudentProfile
from django.db.models import Avg, Count
from django.db import connection

# --- Load Environment Variables ---
load_dotenv()

# --- IMPORTANT ---
# This IP is from your partner's JobList.jsx file.
PARTNER_IP = "192.168.52.109" 
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ==============================================================================
# 1. DATABASE SCHEMA
# ==============================================================================

def get_db_schema():
    """
    Returns a simplified schema of the tables the LLM is allowed to query.
    Uses the *correct* table names from models.py (db_table).
    """
    return """
    Table: students
    Columns: student_id (INTEGER, PRIMARY KEY), full_name (TEXT)

    Table: core_studentprofile
    Columns: student_id (INTEGER, PRIMARY KEY, FOREIGN KEY to students.student_id), highest_percentage (FLOAT), degrees (JSON_ARRAY), annual_income (INTEGER), verified_skills (JSON_ARRAY)

    Table: documents
    Columns: document_id (INTEGER, PRIMARY KEY), student_id (INTEGER, FOREIGN KEY to students.student_id), document_type (TEXT), verification_status (TEXT)
    """

# ==============================================================================
# 2. ETL & PROFILE MANAGEMENT (Extract, Transform, Load)
# ==============================================================================

def update_profile_from_text(student, doc_type, text):
    """
    Parses raw text from a document AND updates the student's
    structured StudentProfile in the database. (Called by views.py on upload)
    """
    print(f"--- Updating Profile for {student.full_name} from {doc_type} ---")
    if not GEMINI_API_KEY: 
        return

    # 1. Define the extraction goal based on document type
    if "marksheet" in doc_type.lower():
        extraction_prompt = "Extract the final 'percentage' (float) and 'degrees' (list of strings)."
        json_format = "{\"percentage\": 85.2, \"degrees\": [\"B.Tech\"]}"
    elif "income" in doc_type.lower():
        extraction_prompt = "Extract the final 'income' (integer) value."
        json_format = "{\"income\": 500000}"
    elif "resume" in doc_type.lower():
        extraction_prompt = "Extract all 'skills' (list of strings)."
        json_format = "{\"skills\": [\"Python\", \"React\", \"Data Analysis\"]}"
    else:
        return # Not a type we parse

    prompt = f"""
    You are a data extraction tool. From the following raw text from a {doc_type},
    perform the task: {extraction_prompt}
    Raw Text: "{text[:1500]}"
    Return ONLY a JSON output in this format: {json_format}
    If nothing is found, return {{}}.
    Output:
    """
    
    # 2. Call LLM to get structured JSON
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json"}
    }
    
    try:
        response = requests.post(api_url, json=payload, timeout=20)
        response.raise_for_status()
        result = response.json()
        text_response = result['candidates'][0]['content']['parts'][0]['text']
        
        # Clean and parse the JSON (Fix for None vs null)
        text_response = text_response.replace("None", "null")
        start = text_response.find('{')
        end = text_response.rfind('}') + 1
        if start == -1 or end == 0: 
            raise ValueError("No JSON object found in response")
        cleaned_json_text = text_response[start:end]
        parsed_data = json.loads(cleaned_json_text)
        
        # 3. Get or Create the profile
        profile, created = StudentProfile.objects.get_or_create(student=student)
        
        # 4. Save the structured data to the StudentProfile model
        if "percentage" in parsed_data and parsed_data.get("percentage"):
            profile.highest_percentage = max(profile.highest_percentage or 0, float(parsed_data["percentage"]))
        if "income" in parsed_data and parsed_data.get("income"):
            profile.annual_income = int(parsed_data["income"])
        if "degrees" in parsed_data and parsed_data.get("degrees"):
            profile.degrees = list(set((profile.degrees or []) + parsed_data["degrees"])) # Merge lists
        if "skills" in parsed_data and parsed_data.get("skills"):
            profile.verified_skills = list(set((profile.verified_skills or []) + parsed_data["skills"])) # Merge lists
            
        profile.save()
        print(f"Profile for {student.full_name} updated successfully: {parsed_data}")
        
    except Exception as e:
        print(f"ERROR: LLM Profile update failed: {e}")

# ==============================================================================
# 3. TOOLKIT (The functions our "Executor" can run)
# ==============================================================================

def get_student_qualifications(student_id):
    """
    Tool: [GET_STUDENT_PROFILE]
    Fetches the pre-structured qualifications from the database.
    """
    print("Running tool: GET_STUDENT_PROFILE")
    if not student_id: return {}
    try:
        profile = StudentProfile.objects.get(student_id=student_id)
        qualifications = {
            'full_name': profile.student.full_name,   # <--- Added Name
            'email': profile.student.email,
            'income': profile.annual_income,
            'degrees': profile.degrees,
            'highest_percentage': profile.highest_percentage,
            'skills': profile.verified_skills
        }
        print(f"Fetched structured qualifications: {qualifications}")
        return qualifications
    except StudentProfile.DoesNotExist:
        print(f"No profile found for student {student_id}")
        return {}

def get_all_student_profiles_from_db():
    """Tool: [GET_ALL_STUDENT_PROFILES] Fetches all student profiles."""
    print("Running tool: GET_ALL_STUDENT_PROFILES")
    try:
        profiles = StudentProfile.objects.select_related('student').all()
        return [
            {
                "student_id": p.student.student_id,
                "full_name": p.student.full_name,
                "highest_percentage": p.highest_percentage,
                "degrees": p.degrees,
                "annual_income": p.annual_income,
                "verified_skills": p.verified_skills
            }
            for p in profiles
        ]
    except Exception as e:
        return {"error": f"Failed to get all profiles: {e}"}

def get_student_documents_from_db(student_id):
    """Tool: [GET_STUDENT_DOCUMENTS] Fetches documents for a specific student."""
    print("Running tool: GET_STUDENT_DOCUMENTS")
    if not student_id: return {"error": "No student_id provided"}
    try:
        docs = Document.objects.filter(student_id=student_id)
        return [
            {"type": d.document_type, "status": d.verification_status}
            for d in docs
        ]
    except Exception as e:
        return {"error": f"Failed to get documents: {e}"}

def get_all_documents_from_db():
    """Tool: [GET_ALL_DOCUMENTS] Fetches all documents."""
    print("Running tool: GET_ALL_DOCUMENTS")
    try:
        return [
            {"student_id": d.student_id, "type": d.document_type, "status": d.verification_status}
            for d in Document.objects.all()
        ]
    except Exception as e:
        return {"error": f"Failed to get all documents: {e}"}

def get_all_jobs_from_api():
    """Tool: [GET_ALL_JOBS] Fetches all jobs from partner API."""
    print("Running tool: GET_ALL_JOBS")
    try:
        endpoint = f'http://{PARTNER_IP}:5000/api/jobs'
        response = requests.get(endpoint, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": f"Failed to fetch jobs: {e}"}

def get_all_scholarships_from_api():
    """Tool: [GET_ALL_SCHOLARSHIPS] Fetches all scholarships from partner API."""
    print("Running tool: GET_ALL_SCHOLARSHIPS")
    try:
        endpoint = f'http://{PARTNER_IP}:5000/api/scholarships'
        response = requests.get(endpoint, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": f"Failed to fetch scholarships: {e}"}

# ==============================================================================
# 4. AI "BRAIN" - STEP 1: DECOMPOSER (Decides which tools to use)
# ==============================================================================

def analyze_query_for_tools(query_text, student_id=None):
    """
    Uses an LLM to decompose a query into a list of "tools" to run.
    This is the new "Multi-Tool" Decomposer.
    """
    print(f"--- Decomposing query for tools: '{query_text}' ---")
    if not GEMINI_API_KEY: 
        return {"error": "GEMINI_API_KEY not found."}

    schema = get_db_schema()
    
    prompt = f"""
    You are a query planner. Your job is to list all the data "tools" needed to answer the user's query.
    Respond with *only* a JSON list of tool names.

    --- AVAILABLE TOOLS ---
    
    1. USER DATA TOOLS (For queries about "me", "my", "I"):
    - "GET_STUDENT_PROFILE": Use for "my name", "my skills", "my income", "am I eligible".
    - "GET_STUDENT_DOCUMENTS": Use for "my verified documents", "my aadhar", "my resume status".

    2. ADMIN AGGREGATE TOOLS (For queries about "students", "all", "how many"):
    - "GET_ALL_STUDENT_PROFILES": Use ONLY for skills, income, or degrees. (e.g., "avg income", "students who know Python").
    - "GET_ALL_DOCUMENTS": Use for ANY check regarding verification status or document types. (e.g., "how many verified", "students with Aadhar", "pending documents").

    3. EXTERNAL DATA TOOLS:
    - "GET_ALL_JOBS": Use for "jobs", "vacancies".
    - "GET_ALL_SCHOLARSHIPS": Use for "scholarships".

    4. GENERAL:
    - "CREATIVE_COACH": Use for generic advice ("roadmap", "what should I do", "hello").

    --- EXAMPLES ---
    
    Query: "what is my name"
    Output: ["GET_STUDENT_PROFILE"]

    Query: "how many students have aadhar verified"
    Output: ["GET_ALL_DOCUMENTS"]  <-- Corrects the previous error

    Query: "show me verified students"
    Output: ["GET_ALL_DOCUMENTS"]

    Query: "which students know Django"
    Output: ["GET_ALL_STUDENT_PROFILES"]

    --- USER QUERY ---
    Query: "{query_text}"
    Output:
    """
    
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json"}
    }
    
    try:
        response = requests.post(api_url, json=payload, timeout=20)
        response.raise_for_status()
        result = response.json()
        
        if 'candidates' not in result:
            return {"error": "LLM returned no candidates."}

        text_response = result['candidates'][0]['content']['parts'][0]['text'].strip()
        
        # Robust JSON parsing
        text_response = text_response.replace("None", "null")
        start = text_response.find('[')
        end = text_response.rfind(']') + 1
        if start == -1 or end == 0:
            raise ValueError("No JSON array found in response")
        
        cleaned_json_text = text_response[start:end]
        tool_list = json.loads(cleaned_json_text)
        
        return {"tools": tool_list}

    except Exception as e:
        print(f"ERROR: LLM Tool generation failed: {e}")
        return {"error": f"LLM Tool generation failed: {e}"}

# ==============================================================================
# 5. AI "BRAIN" - STEP 2: EXECUTOR (Runs the tools)
# ==============================================================================

def execute_tool_plan(plan, student_id=None):
    """
    Executes the list of tools from the decomposer
    and gathers all data into a single context object.
    """
    print(f"--- Executing Tool Plan (Context: student_id={student_id}) ---")
    
    if "error" in plan:
        return {"error": plan['error']}
    
    tool_list = plan.get("tools", [])
    if not tool_list:
        return {"error": "No tools were specified by the planner."}
    
    # This is where we will store all the data we fetch
    context_data = {
        "student_id_context": student_id
    }
    
    # This is a special flag for creative queries
    if "CREATIVE_COACH" in tool_list:
        context_data["creative_request"] = True
    
    try:
        for tool in tool_list:
            if tool == "GET_STUDENT_PROFILE":
                context_data["student_profile"] = get_student_qualifications(student_id)
            elif tool == "GET_ALL_STUDENT_PROFILES":
                context_data["all_student_profiles"] = get_all_student_profiles_from_db()
            elif tool == "GET_STUDENT_DOCUMENTS":
                context_data["student_documents"] = get_student_documents_from_db(student_id)
            elif tool == "GET_ALL_DOCUMENTS":
                context_data["all_documents"] = get_all_documents_from_db()
            elif tool == "GET_ALL_JOBS":
                context_data["jobs_list"] = get_all_jobs_from_api()
            elif tool == "GET_ALL_SCHOLARSHIPS":
                context_data["scholarships_list"] = get_all_scholarships_from_api()
        
        # This is the "Data Context" we will send to the final AI
        return context_data
    
    except Exception as e:
        print(f"ERROR: Tool execution failed: {e}")
        return {"error": f"A tool failed to run: {e}"}

# ==============================================================================
# 6. AI "BRAIN" - STEP 3: SYNTHESIZER (Answers the query)
# ==============================================================================

def get_synthesized_answer(context_data, original_query):
    """
    The "Synthesizer" AI.
    Receives all fetched data and the user's query,
    and formulates the final answer.
    """
    print("--- Synthesizing Final Answer ---")
    if not GEMINI_API_KEY:
        return {"error": "LLM not configured for synthesis."}
    
    if "error" in context_data:
        # If a tool failed, just summarize that error
        return summarize_results_fallback(context_data, original_query) # Call fallback
    
    # --- THIS SOLVES THE TOKEN LIMIT ---
    # We must truncate the data we send to the AI.
    
    if "jobs_list" in context_data and isinstance(context_data["jobs_list"], list):
        job_count = len(context_data["jobs_list"])
        # If the list is too big, only send the first 50 and a summary
        if job_count > 50:
            context_data["jobs_list"] = context_data["jobs_list"][:50]
            context_data["jobs_list_summary"] = f"Showing 50 out of {job_count} total jobs."
    
    if "all_student_profiles" in context_data and isinstance(context_data["all_student_profiles"], list):
        profile_count = len(context_data["all_student_profiles"])
        if profile_count > 50:
            context_data["all_student_profiles"] = context_data["all_student_profiles"][:50]
            context_data["all_student_profiles_summary"] = f"Showing 50 out of {profile_count} total profiles."
    
    if "all_documents" in context_data and isinstance(context_data["all_documents"], list):
        doc_count = len(context_data["all_documents"])
        if doc_count > 50:
            context_data["all_documents"] = context_data["all_documents"][:50]
            context_data["all_documents_summary"] = f"Showing 50 out of {doc_count} total documents."
    
    if "scholarships_list" in context_data and isinstance(context_data["scholarships_list"], list):
        schol_count = len(context_data["scholarships_list"])
        if schol_count > 50:
            context_data["scholarships_list"] = context_data["scholarships_list"][:50]
            context_data["scholarships_list_summary"] = f"Showing 50 out of {schol_count} total scholarships."
    # --- END OF TOKEN LIMIT FIX ---
    
    context_string = json.dumps(context_data, indent=2)
    
    # If this is a creative query, we use the "Career Coach" prompt
    if context_data.get("creative_request"):
        prompt_type = "CAREER COACH"
        prompt = f"""
        You are a helpful and inspiring student career coach.
        You will be given a student's query and their profile data.
        Your job is to provide a thoughtful, encouraging, and actionable response.
        
        User's Query: "{original_query}"
        Data Context (JSON):
        {context_string}
        
        Instructions:
        - Analyze their query in the context of their "student_profile".
        - If they ask for a "roadmap", provide a step-by-step plan.
        - If they ask "what job is best for me", analyze their "verified_skills"
          against the "jobs_list" and recommend the top 3 matches, explaining *why*.
        - Be conversational and encouraging.

        Your Answer:
        """
    else:
        # This is a pure data query
        prompt_type = "DATA ANALYST"
        prompt = f"""
        You are a world-class data analyst. Your job is to answer the user's question
        using the provided data context.
        
        User's Query: "{original_query}"
        Data Context (JSON):
        {context_string}
        
        Instructions:
        - Analyze the data to find the answer.
        - Perform any required calculations (average, count, mode, max, min).
        - You can *cross-reference* data. (e.g., find profiles in 'all_student_profiles' that match documents in 'all_documents').
        - Be concise, factual, and answer the question directly.

        Your Answer:
        """
    
    print(f"--- Calling Synthesizer AI as: {prompt_type} ---")
    
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        response = requests.post(api_url, json=payload, timeout=45)
        response.raise_for_status()
        result = response.json()
        text_response = result['candidates'][0]['content']['parts'][0]['text']
        return {"response_text": text_response}
    except Exception as e:
        print(f"ERROR: LLM Synthesis failed: {e}")
        return {"response_text": f"Sorry, I encountered an error: {e}"}

# ==============================================================================
# 7. FALLBACK SUMMARIZER (Error handling)
# ==============================================================================

def summarize_results_fallback(results, original_query):
    """
    FALLBACK: Takes a simple JSON error and summarizes it.
    """
    print("--- Summarizing results (Fallback) ---")
    results_string = json.dumps(results, indent=2)
    prompt = f"Politely summarize this data or error message for a user. Query: '{original_query}'. Data: {results_string}"
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(api_url, json=payload, timeout =20)
        response.raise_for_status(); result = response.json()
        return {"response_text": result['candidates'][0]['content']['parts'][0]['text']}
    except Exception as e:
        return {"response_text": f"Sorry, an error occurred: {e}"}