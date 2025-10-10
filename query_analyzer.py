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

# --- Helper functions ---

def get_student_qualifications(student_id):
    """Fetches and consolidates verified qualifications for a given student."""
    if not student_id: return {}
    qualifications = {'income': None, 'degrees': set(), 'highest_percentage': 0.0}
    verified_docs = Document.objects.filter(student_id=student_id, verification_status='Verified')
    for doc in verified_docs:
        if doc.verified_data:
            if 'income' in doc.verified_data: qualifications['income'] = doc.verified_data['income']
            if 'percentage' in doc.verified_data: qualifications['highest_percentage'] = max(qualifications['highest_percentage'], doc.verified_data['percentage'])
            if 'B.Tech Certificate' in doc.document_type: qualifications['degrees'].add('B.Tech')
            if 'Diploma Certificate' in doc.document_type: qualifications['degrees'].add('Diploma')
    qualifications['degrees'] = list(qualifications['degrees'])
    print(f"Found qualifications for student {student_id}: {qualifications}")
    return qualifications

def filter_items_with_llm(items, qualifications, item_type):
    """
    NEW: Uses a single, powerful LLM call to filter a list of items (jobs or scholarships)
    based on a student's qualifications.
    """
    print(f"--- Filtering {len(items)} {item_type}s with a single LLM call ---")
    if not items or not qualifications: return []
    if not GEMINI_API_KEY: return {"error": "GEMINI_API_KEY not found."}

    items_json_string = json.dumps(items, indent=2)
    
    if item_type == 'jobs':
        eligibility_check = """
        A student is eligible for a job if their CGPA (percentage / 10) is greater than or equal to the job's 'min_cgpa',
        and if their degree is one of the job's 'degree_required'.
        The eligibility text is in the 'description' field of each job object.
        """
    else: # scholarships
        eligibility_check = """
        A student is eligible for a scholarship if their percentage is greater than or equal to the scholarship's 'min_percentage',
        and their income is less than or equal to the scholarship's 'max_income_pa'.
        The eligibility text is in the 'eligibility' field of each scholarship object.
        """

    prompt = f"""
    You are an intelligent filtering agent for a student database.
    
    Here are the student's verified qualifications:
    {json.dumps(qualifications, indent=2)}

    Here is a JSON array of all available {item_type}s:
    {items_json_string}

    Your task is to:
    1. Carefully read the student's qualifications.
    2. Analyze the unstructured eligibility text in each object in the provided list.
    3. {eligibility_check}
    4. Return a new, smaller JSON array that contains ONLY the full objects of the {item_type}s for which the student is eligible.
    5. If the student is not eligible for any, you MUST return an empty array [].
    6. Do not explain your reasoning. Your entire response must be ONLY the final, filtered JSON array.

    Filtered JSON Array Output:
    """

    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(api_url, json=payload, timeout=60) # Increased timeout for larger payload
        response.raise_for_status()
        result = response.json()
        text_response = result['candidates'][0]['content']['parts'][0]['text']
        cleaned_text = text_response.strip().replace('```json', '').replace('```', '')
        filtered_list = json.loads(cleaned_text)
        print(f"LLM returned {len(filtered_list)} eligible {item_type}s.")
        return filtered_list
    except Exception as e:
        print(f"ERROR: LLM batch filtering failed. {e}")
        return {"error": f"LLM filtering process failed: {e}"}

def analyze_and_decompose_query_with_llm(query_text):
    """
    Uses a schema-grounded LLM to analyze a natural language query and decompose it 
    into a structured plan.
    """
    print(f"--- Decomposing query with LLM: '{query_text}' ---")
    if not GEMINI_API_KEY: return {"error": "GEMINI_API_KEY not found."}
    
    prompt = f"""
    You are a query decomposition engine. Your job is to analyze the user's query and convert it into a structured JSON plan.
    If the query is conversational or has no clear data-related intent (e.g., "Hello", "show my data", "SHow me my documents"), treat it as a "GET_DOCUMENTS" intent.
    Identify the user's name, all intents, and any filters, aggregations, or eligibility requirements.

    ### Schema & Intents ###
    - "GET_DOCUMENTS": Fetches student documents. Can be filtered by "verification_status".
    - "GET_JOBS": Fetches job listings.
    - "GET_SCHOLARSHIPS": Fetches scholarship listings.
    - "ANALYZE_SKILLS": Analyzes skills for a job.

    ### Examples ###
    Query: "which documents of mine are verified"
    Output: {{"user_name": null, "intents": [{{"target": "GET_DOCUMENTS", "params": {{"verification_status": "Verified"}}}}]}}

    Query: "Show me all scholarships"
    Output: {{"user_name": null, "intents": [{{"target": "GET_SCHOLARSHIPS", "params": {{}}}}]}}

    Query: "Which scholarship or job am I eligible in"
    Output: {{"user_name": null, "intents": [{{"target": "GET_JOBS", "params": {{"filter_by_eligibility": true}}}}, {{"target": "GET_SCHOLARSHIPS", "params": {{"filter_by_eligibility": true}}}}]}}

    Query: "How many jobs are there?"
    Output: {{"user_name": null, "intents": [{{"target": "GET_JOBS", "params": {{"aggregate": "count"}}}}]}}
    
    Query: "show my data"
    Output: {{"user_name": null, "intents": [{{"target": "GET_DOCUMENTS", "params": {{}}}}]}}

    ### User Query ###
    Query: "{query_text}"
    Output:
    """
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(api_url, json=payload, timeout=20)
        response.raise_for_status()
        result = response.json()
        text_response = result['candidates'][0]['content']['parts'][0]['text']
        cleaned_text = text_response.strip().replace('```json', '').replace('```', '')
        plan = json.loads(cleaned_text)
        print(f"LLM generated plan: {plan}") # This prints the decomposed query
        return plan
    except Exception as e:
        print(f"ERROR: LLM processing failed. {e}")
        return {"error": f"Could not get a valid plan from the LLM: {e}"}

def execute_query_plan(plan, student_id=None):
    """
    Executes all intents in the query plan using the new batch filtering method.
    """
    print(f"--- Executing Full Query Plan (Context: student_id={student_id}) ---")
    if "error" in plan or not plan.get("intents"):
        return {"error": "Invalid query plan received."}
    
    final_results = {}
    if not student_id and plan.get("user_name"):
        try:
            student = Student.objects.get(full_name__iexact=plan.get("user_name"))
            student_id = student.student_id
        except Student.DoesNotExist: pass
    
    qualifications = get_student_qualifications(student_id) if student_id else {}

    for intent_data in plan["intents"]:
        intent = intent_data.get("target")
        params = intent_data.get("params", {})
        
        if intent == "GET_JOBS":
            endpoint = f'http://{PARTNER_IP}:5000/api/jobs'
            try:
                print(f"Making REAL API call for all jobs to: {endpoint}")
                response = requests.get(endpoint, timeout=10)
                response.raise_for_status()
                all_jobs = response.json()

                if params.get("aggregate") == "count":
                    final_results['jobs_count'] = {"count": len(all_jobs)}
                elif params.get("filter_by_eligibility") and student_id:
                    # --- NEW: Use the single-call LLM filter ---
                    eligible_jobs = filter_items_with_llm(all_jobs, qualifications, 'jobs')
                    final_results['jobs'] = eligible_jobs
                else:
                    final_results['jobs'] = all_jobs
            except requests.exceptions.RequestException as e:
                final_results['jobs'] = {"error": f"Failed to fetch jobs: {e}"}

        elif intent == "GET_SCHOLARSHIPS":
            endpoint = f'http://{PARTNER_IP}:5000/api/scholarships'
            try:
                print(f"Making REAL API call for all scholarships to: {endpoint}")
                response = requests.get(endpoint, timeout=10)
                response.raise_for_status()
                all_scholarships = response.json()

                if params.get("filter_by_eligibility") and student_id:
                     # --- NEW: Use the single-call LLM filter ---
                    eligible_scholarships = filter_items_with_llm(all_scholarships, qualifications, 'scholarships')
                    final_results['scholarships'] = eligible_scholarships
                else:
                    final_results['scholarships'] = all_scholarships
            except requests.exceptions.RequestException as e:
                final_results['scholarships'] = {"error": f"Failed to fetch scholarships: {e}"}
        
        elif intent == "GET_DOCUMENTS":
            endpoint = 'http://127.0.0.1:8000/api/documents/'
            try:
                response = requests.get(endpoint, timeout=5)
                response.raise_for_status()
                all_documents = response.json()
                
                filtered_documents = all_documents
                if student_id:
                    try:
                        student_id_int = int(student_id)
                        filtered_documents = [doc for doc in filtered_documents if doc.get('student') == student_id_int]
                    except (ValueError, TypeError):
                        pass

                status_filter = params.get('verification_status')
                if status_filter:
                    if isinstance(status_filter, list):
                        filtered_documents = [doc for doc in filtered_documents if doc.get('verification_status') in status_filter]
                    else:
                        filtered_documents = [doc for doc in filtered_documents if doc.get('verification_status') == status_filter]
                
                final_results['documents'] = filtered_documents

            except requests.exceptions.RequestException as e:
                final_results['documents'] = {"error": f"Failed to fetch documents: {e}"}

        elif intent == "ANALYZE_SKILLS":
            # This logic remains sequential as it's a different task
            job_title_param = params.get('job_title', 'a generic job')
            mock_job_description = f"We are looking for a {job_title_param} to help us with our government projects."
            # In a real system, you'd fetch a specific job's description first.
            skills_endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={GEMINI_API_KEY}"
            prompt = f"Based on the following job description, list the top 5 most important technical skills. Return only a JSON array of strings. Description: '{mock_job_description}'"
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            try:
                response = requests.post(skills_endpoint, json=payload, timeout=15)
                response.raise_for_status()
                result = response.json()
                text_response = result['candidates'][0]['content']['parts'][0]['text']
                cleaned_text = text_response.strip().replace('```json', '').replace('```', '')
                skills = json.loads(cleaned_text)
                final_results['skill_analysis'] = {"job_title": job_title_param, "required_skills": skills}
            except Exception as e:
                final_results['skill_analysis'] = {"error": f"Error fetching skills: {e}"}


    if not final_results:
        return {"message": "I'm sorry, I couldn't determine a specific task from your query."}
        
    return final_results

