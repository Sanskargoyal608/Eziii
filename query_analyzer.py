# This script contains the core logic for the federated query engine.
import requests
import re
import os
import json
from dotenv import load_dotenv
from core.models import Student, Document

# --- Load Environment Variables ---
load_dotenv()

# --- IMPORTANT ---
PARTNER_IP = "192.168.52.109"  # Replace with your partner's actual local IP
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- Helper function to get a student's verified qualifications ---
def get_student_qualifications(student_id):
    """Fetches and consolidates verified qualifications for a given student."""
    if not student_id:
        return {}
    
    qualifications = {
        'income': None,
        'degrees': set(),
        'highest_percentage': 0.0
    }
    
    # Query the database for verified documents for the student
    verified_docs = Document.objects.filter(student_id=student_id, verification_status='Verified')
    
    for doc in verified_docs:
        if doc.verified_data:
            if 'income' in doc.verified_data:
                qualifications['income'] = doc.verified_data['income']
            if 'percentage' in doc.verified_data:
                qualifications['highest_percentage'] = max(qualifications['highest_percentage'], doc.verified_data['percentage'])
            if 'B.Tech' in doc.document_type:
                qualifications['degrees'].add('B.Tech')
            if 'Diploma' in doc.document_type:
                qualifications['degrees'].add('Diploma')
    
    # Convert set to list for easier use
    qualifications['degrees'] = list(qualifications['degrees'])
    print(f"Found qualifications for student {student_id}: {qualifications}")
    return qualifications


def analyze_and_decompose_query_with_llm(query_text):
    """
    Uses a schema-grounded LLM to analyze a natural language query and decompose it 
    into a structured plan.
    """
    print(f"--- Decomposing query with LLM: '{query_text}' ---")

    if not GEMINI_API_KEY:
        return {"error": "GEMINI_API_KEY not found in .env file."}

    prompt = f"""
    You are a sophisticated query decomposition engine. Your job is to analyze the user's query 
    and convert it into a structured JSON plan based on the available data sources.

    ### Data Source Schema ###
    1.  **primary_db**: Handles student-specific data (intents: "GET_DOCUMENTS").
    2.  **secondary_db**: Handles general opportunity data (intents: "GET_JOBS").
    3.  **llm_service**: Handles complex analysis (intents: "ANALYZE_SKILLS").

    ### Instructions ###
    - Identify the user's name, intents, and any filters or aggregations.
    - If the user asks if they are "eligible", set "filter_by_eligibility" to true.
    - Return ONLY the JSON plan.

    ### Examples ###
    Query: "show me my verified documents"
    Output: {{"user_name": null, "intents": [{{"target": "GET_DOCUMENTS", "params": {{"verification_status": "Verified"}}}}]}}

    Query: "what skills do I need for a data scientist position"
    Output: {{"user_name": null, "intents": [{{"target": "ANALYZE_SKILLS", "params": {{"job_title": "data scientist"}}}}]}}

    Query: "How many jobs are there?"
    Output: {{"user_name": null, "intents": [{{"target": "GET_JOBS", "params": {{"aggregate": "count"}}}}]}}

    Query: "show me jobs i am eligible for"
    Output: {{"user_name": null, "intents": [{{"target": "GET_JOBS", "params": {{"filter_by_eligibility": true}}}}]}}

    ### User Query ###
    Query: "{query_text}"
    Output:
    """

    # UPDATED to use the model name you requested
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        response = requests.post(api_url, json=payload, timeout=20)
        response.raise_for_status()
        result = response.json()
        text_response = result['candidates'][0]['content']['parts'][0]['text']
        
        cleaned_text = text_response.strip().replace('```json', '').replace('```', '')
        plan = json.loads(cleaned_text)
        print(f"LLM generated plan: {plan}")
        return plan
    except Exception as e:
        print(f"ERROR: LLM processing failed. {e}")
        return {"error": f"Could not get a valid plan from the LLM: {e}"}


def execute_query_plan(plan, student_id=None):
    """
    Executes all intents in the query plan, making live API calls and filtering results.
    """
    print(f"--- Executing Full Query Plan (Context: student_id={student_id}) ---")
    if "error" in plan or not plan.get("intents"):
        return {"error": "Invalid query plan received."}
    
    final_results = {}
    if not student_id and plan.get("user_name"):
        try:
            student = Student.objects.get(full_name__iexact=plan.get("user_name"))
            student_id = student.student_id
        except Student.DoesNotExist:
            pass
    
    for intent_data in plan["intents"]:
        intent = intent_data.get("target")
        params = intent_data.get("params", {})
        
        if intent == "GET_JOBS":
            endpoint = f'http://{PARTNER_IP}:5000/api/jobs'
            try:
                print(f"Making REAL API call to: {endpoint}")
                response = requests.get(endpoint, timeout=10)
                response.raise_for_status()
                all_jobs = response.json()

                if params.get("aggregate") == "count":
                    final_results['jobs_count'] = {"count": len(all_jobs)}
                elif params.get("filter_by_eligibility") and student_id:
                    qualifications = get_student_qualifications(student_id)
                    eligible_jobs = [
                        job for job in all_jobs 
                        if qualifications.get('highest_percentage', 0) / 10 >= job.get('eligibility_criteria', {}).get('min_cgpa', 0)
                        and job.get('eligibility_criteria', {}).get('degree_required') in qualifications.get('degrees', [])
                    ]
                    final_results['jobs'] = eligible_jobs
                else:
                    final_results['jobs'] = all_jobs

            except requests.exceptions.RequestException as e:
                final_results['jobs'] = {"error": f"Failed to fetch jobs from partner API: {e}"}

        elif intent == "GET_DOCUMENTS":
            # ... (this part remains the same)
            endpoint = 'http://127.0.0.1:8000/api/documents/'
            try:
                response = requests.get(endpoint, timeout=5)
                response.raise_for_status()
                all_documents = response.json()
                filtered_documents = all_documents
                if student_id:
                    filtered_documents = [doc for doc in all_documents if doc.get('student') == student_id]
                status_filter = params.get('verification_status')
                if status_filter:
                    filtered_documents = [doc for doc in filtered_documents if doc.get('verification_status') == status_filter]
                final_results['documents'] = filtered_documents
            except requests.exceptions.RequestException as e:
                final_results['documents'] = {"error": f"Failed to fetch documents: {e}"}

        elif intent == "ANALYZE_SKILLS":
             # ... (this part remains the same)
            job_title_param = params.get('job_title', 'a generic job')
            mock_job_description = f"We are looking for a {job_title_param} to help us with our government projects."
            skills = get_skills_from_llm(mock_job_description)
            final_results['skill_analysis'] = {"job_title": job_title_param, "required_skills": skills}

    if not final_results:
        return {"error": "No executable intents were found in the query."}
        
    return final_results


def get_skills_from_llm(job_description):
    """Sends a job description to the Gemini API to extract required skills."""
    if not GEMINI_API_KEY:
        return ["Error: GEMINI_API_KEY not found."]

    # UPDATED to use the model name you requested
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={GEMINI_API_KEY}"
    prompt = f"Based on the following job description, list the top 5 most important technical skills. Return only a JSON array of strings. Description: '{job_description}'"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(api_url, json=payload, timeout=15)
        response.raise_for_status()
        result = response.json()
        text_response = result['candidates'][0]['content']['parts'][0]['text']
        cleaned_text = text_response.strip().replace('```json', '').replace('```', '')
        return json.loads(cleaned_text)
    except Exception as e:
        return [f"Error fetching skills: {e}"]

