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
PARTNER_IP = "192.168.1.107"  # Replace with your partner's actual local IP
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def summarize_results_with_llm(results, original_query):
    """
    Takes the structured JSON results and the user's query,
    and returns a human-readable text response.
    """
    print("--- Summarizing results with LLM ---")
    if not GEMINI_API_KEY:
        return {"error": "LLM not configured for summarization."}

    # Convert the structured results to a string
    results_string = json.dumps(results, indent=2)

    prompt = f"""
    You are a helpful student career advisor. Your job is to answer a user's question in a clear, friendly, and conversational way.
    You will be given the user's original question and a JSON object containing the data you need to answer it.

    User's Original Question:
    "{original_query}"

    Data to Use (JSON):
    {results_string}

    Instructions:
    1. Analyze the user's question and the provided data.
    2. Formulate a single, concise, human-readable response.
    3. If the data contains an error message, explain the error politely.
    4. If the data is an empty list (like `[]`), inform the user that no items were found.
    5. Do not just repeat the JSON. Summarize it.

    Example:
    If the data is {{"jobs": [{{"job_title": "Data Analyst"}}]}},
    your response should be: "Based on your qualifications, I found one job you are eligible for: 'Data Analyst'."

    Example:
    If the data is {{"documents": []}},
    your response should be: "I checked your profile, but it looks like you haven't uploaded any documents that match that description yet."
    
    Now, please generate the response for the given data and query.

    Your Answer:
    """

    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        response = requests.post(api_url, json=payload, timeout=20)
        response.raise_for_status()
        result = response.json()
        
        # Extract the text and wrap it in a simple JSON for the frontend
        text_response = result['candidates'][0]['content']['parts'][0]['text']
        return {"response_text": text_response}
    
    except Exception as e:
        print(f"ERROR: LLM Summarization failed. {e}")
        return {"response_text": f"Sorry, I encountered an error while processing the results: {e}"}



# --- NEW: LLM Helper for parsing extracted text ---
def parse_qualifications_from_text(text, doc_type):
    """
    Uses the LLM to parse raw extracted text from a document
    into a structured JSON of qualifications.
    """
    print(f"--- Parsing raw text from {doc_type} with LLM ---")
    if not GEMINI_API_KEY:
        return {}

    # Define the extraction goal based on document type
    if "marksheet" in doc_type.lower() or "certificate" in doc_type.lower():
        extraction_prompt = "Extract the final 'percentage' (float) or 'cgpa' (float). If CGPA, convert it to percentage (CGPA * 9.5). Return as JSON: {\"percentage\": 85.2}"
    elif "income" in doc_type.lower():
        extraction_prompt = "Extract the final 'income' (integer) value. Return as JSON: {\"income\": 500000}"
    else:
        return {} # Not a document type we can parse for qualifications

    prompt = f"""
    You are a data extraction tool. From the following raw text from a {doc_type},
    perform the following task: {extraction_prompt}
    
    Raw Text:
    "{text[:1000]}"

    Return ONLY the JSON output.
    Output:
    """

    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        response = requests.post(api_url, json=payload, timeout=15)
        response.raise_for_status()
        result = response.json()
        text_response = result['candidates'][0]['content']['parts'][0]['text']
        cleaned_text = text_response.strip().replace('```json', '').replace('```', '')
        parsed_data = json.loads(cleaned_text)
        print(f"LLM parsed data: {parsed_data}")
        return parsed_data
    except Exception as e:
        print(f"ERROR: LLM parsing of extracted text failed: {e}")
        return {}

# --- UPDATED Helper function to get qualifications ---
def get_student_qualifications(student_id):
    """
    Fetches and consolidates verified qualifications for a given student.
    It now checks verified_data first, then falls back to parsing extracted_text.
    """
    if not student_id: return {}
    qualifications = {'income': None, 'degrees': set(), 'highest_percentage': 0.0}
    
    # We only trust 'Verified' documents for eligibility
    verified_docs = Document.objects.filter(student_id=student_id, verification_status='Verified')
    print(f"Found {len(verified_docs)} verified documents for student {student_id}.")
    
    for doc in verified_docs:
        data_to_use = None
        
        if doc.verified_data:
            # 1. Prioritize clean, structured data if it exists (from dummy data)
            print(f"Using 'verified_data' for doc {doc.document_id}")
            data_to_use = doc.verified_data
        elif doc.extracted_text:
            # 2. Fallback: If no structured data, parse the raw text
            print(f"Using 'extracted_text' for doc {doc.document_id}")
            data_to_use = parse_qualifications_from_text(doc.extracted_text, doc.document_type)

        if data_to_use:
            if 'income' in data_to_use: 
                qualifications['income'] = data_to_use['income']
            
            if 'percentage' in data_to_use: 
                qualifications['highest_percentage'] = max(qualifications['highest_percentage'], data_to_use['percentage'])
            
            # Simple degree check (can be expanded)
            if 'B.Tech Certificate' in doc.document_type: 
                qualifications['degrees'].add('B.Tech')
            if 'Diploma Certificate' in doc.document_type: 
                qualifications['degrees'].add('Diploma')

    qualifications['degrees'] = list(qualifications['degrees'])
    print(f"Final qualifications for student {student_id}: {qualifications}")
    return qualifications

# --- UPDATED: analyze_and_decompose_query_with_llm ---
def analyze_and_decompose_query_with_llm(query_text):
    """
    Uses a schema-grounded LLM to analyze a natural language query and decompose it 
    into a structured plan.
    """
    print(f"--- Decomposing query with LLM: '{query_text}' ---")
    if not GEMINI_API_KEY: return {"error": "GEMINI_API_KEY not found."}
    
    prompt = f"""
    You are a query decomposition engine. Your job is to analyze the user's query and convert it into a structured JSON plan.
    If the query is conversational (e.g., "Hello"), return an empty intents list.
    If the query asks for general data (e.g., "show my data", "SHow me my documents"), interpret it as a "GET_DOCUMENTS" intent.
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
    
    Query: "SHow me my documents"
    Output: {{"user_name": null, "intents": [{{"target": "GET_DOCUMENTS", "params": {{}}}}]}}
    
    Query: "Hello"
    Output: {{"user_name": null, "intents": []}}

    ### User Query ###
    Query: "{query_text}"
    Output:
    """
    # --- UPDATED MODEL NAME ---
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

# --- UPDATED: filter_items_with_llm ---
def filter_items_with_llm(items, qualifications, item_type):
    """
    Uses a single LLM call to filter a list of items based on qualifications.
    """
    print(f"--- Filtering {len(items)} {item_type}s with a single LLM call ---")
    if not items or not qualifications: return []
    if not GEMINI_API_KEY: return {"error": "GEMINI_API_KEY not found."}

    items_json_string = json.dumps(items, indent=2)
    
    if item_type == 'jobs':
        eligibility_field = "'description'" 
        eligibility_logic = """
        A student is eligible for a job if their CGPA (highest_percentage / 10) is >= the job's 'min_cgpa',
        AND their degree (from 'degrees' list) matches the job's 'degree_required'.
        Extract 'min_cgpa' (float) and 'degree_required' (string) from the unstructured text in the 'description' field.
        """
    else: # scholarships
        eligibility_field = "'eligibility'" 
        eligibility_logic = """
        A student is eligible for a scholarship if their 'highest_percentage' is >= the scholarship's 'min_percentage',
        AND their 'income' is <= the scholarship's 'max_income_pa'.
        Extract 'min_percentage' (integer) and 'max_income_pa' (integer) from the unstructured text in the 'eligibility' field.
        """

    prompt = f"""
    You are an intelligent filtering agent for a student database.
    
    Student Qualifications:
    {json.dumps(qualifications, indent=2)}

    List of {item_type}s (JSON Array):
    {items_json_string}

    Instructions:
    1. Analyze the student's qualifications.
    2. For each item in the list:
       a. Read the unstructured text from the item's {eligibility_field} field.
       b. Extract the necessary criteria values (min_cgpa, degree_required, min_percentage, max_income_pa) from this text.
       c. {eligibility_logic}
       d. Compare the extracted criteria with the student's qualifications.
    3. Return a new JSON array containing ONLY the full objects of the {item_type}s for which the student meets the criteria.
    4. If no items meet the criteria, you MUST return an empty array [].
    5. Respond ONLY with the filtered JSON array. Do not add explanations.

    Filtered JSON Array Output:
    """

    # --- UPDATED MODEL NAME ---
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(api_url, json=payload, timeout=60) 
        response.raise_for_status()
        result = response.json()
        text_response = result['candidates'][0]['content']['parts'][0]['text']
        cleaned_text = text_response.strip().replace('```json', '').replace('```', '')
        
        try:
            filtered_list = json.loads(cleaned_text)
            if not isinstance(filtered_list, list): 
                 raise json.JSONDecodeError("LLM did not return a list.", cleaned_text, 0)
            print(f"LLM returned {len(filtered_list)} eligible {item_type}s.")
            return filtered_list
        except json.JSONDecodeError as json_e:
             print(f"ERROR: LLM returned invalid JSON for filtering. Response: {cleaned_text}. Error: {json_e}")
             return {"error": f"LLM returned invalid JSON during filtering."}

    except Exception as e:
        print(f"ERROR: LLM batch filtering failed. {e}")
        return {"error": f"LLM filtering process failed: {e}"}

# --- UPDATED: execute_query_plan ---
def execute_query_plan(plan, student_id=None, original_query=""):
    """
    Executes all intents in the query plan, then sends the final
    results to the LLM for summarization.
    """
    print(f"--- Executing Full Query Plan (Context: student_id={student_id}) ---")
    
    if "error" in plan:
        return summarize_results_with_llm(plan, original_query) # Let LLM explain the error
    if not plan.get("intents"): 
        return summarize_results_with_llm(
            {"message": "I'm sorry, I couldn't understand that request. Please ask about jobs, scholarships, or your documents."},
            original_query
        )
    
    final_results = {}
    if not student_id and plan.get("user_name"):
        try:
            student = Student.objects.get(full_name__iexact=plan.get("user_name"))
            student_id = student.student_id
        except Student.DoesNotExist: pass
    
    qualifications = get_student_qualifications(student_id) if student_id else {}

    # --- (This whole loop for intents is the same as before) ---
    for intent_data in plan["intents"]:
        intent = intent_data.get("target")
        params = intent_data.get("params", {})
        
        if intent == "GET_JOBS":
            # ... (code for GET_JOBS as before, using batch filtering) ...
            endpoint = f'http://{PARTNER_IP}:5000/api/jobs'
            try:
                print(f"Making REAL API call for all jobs to: {endpoint}")
                response = requests.get(endpoint, timeout=10)
                response.raise_for_status()
                all_jobs = response.json()
                if params.get("aggregate") == "count":
                    final_results['jobs_count'] = {"count": len(all_jobs)}
                elif params.get("filter_by_eligibility") and student_id:
                    if not qualifications.get('degrees'):
                         final_results['jobs'] = {"message": "Cannot check job eligibility: No verified degree found."}
                         continue
                    eligible_jobs = filter_items_with_llm(all_jobs, qualifications, 'jobs')
                    final_results['jobs'] = eligible_jobs
                else:
                    final_results['jobs'] = all_jobs
            except requests.exceptions.RequestException as e:
                final_results['jobs'] = {"error": f"Failed to fetch jobs: {e}"}

        elif intent == "GET_SCHOLARSHIPS":
            # ... (code for GET_SCHOLARSHIPS as before, using batch filtering) ...
            endpoint = f'http://{PARTNER_IP}:5000/api/scholarships'
            try:
                print(f"Making REAL API call for all scholarships to: {endpoint}")
                response = requests.get(endpoint, timeout=10)
                response.raise_for_status()
                all_scholarships = response.json()
                if params.get("filter_by_eligibility") and student_id:
                    if qualifications.get('income') is None:
                        final_results['scholarships'] = {"message": "Cannot check scholarship eligibility: No verified income found."}
                        continue
                    eligible_scholarships = filter_items_with_llm(all_scholarships, qualifications, 'scholarships')
                    final_results['scholarships'] = eligible_scholarships
                else:
                    final_results['scholarships'] = all_scholarships
            except requests.exceptions.RequestException as e:
                final_results['scholarships'] = {"error": f"Failed to fetch scholarships: {e}"}

        elif intent == "GET_DOCUMENTS":
            # ... (code for GET_DOCUMENTS as before) ...
            endpoint = 'http://127.0.0.1:8000/api/documents/'
            try:
                response = requests.get(endpoint, timeout=5)
                response.raise_for_status()
                all_documents = response.json()
                filtered_documents = all_documents
                if student_id:
                    try:
                        student_id_int = int(student_id)
                        filtered_documents = [doc for doc in all_documents if doc.get('student') == student_id_int]
                    except (ValueError, TypeError): pass
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
            # ... (code for ANALYZE_SKILLS as before, using gemini-2.5-flash-lite) ...
            job_title_param = params.get('job_title', 'a generic job')
            mock_job_description = f"We are looking for a {job_title_param} to help us with our government projects."
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
        final_results = {"message": "I understood the request, but couldn't find any relevant data."}
    
    # --- THIS IS THE NEW FINAL STEP ---
    # Instead of returning raw JSON, summarize it.
    return summarize_results_with_llm(final_results, original_query)
  
    # --- UPDATED to use the new, smarter function ---
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
                    if not qualifications.get('degrees'):
                         final_results['jobs'] = {"message": "Cannot check job eligibility: No verified degree found."}
                         continue
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
                    if qualifications.get('income') is None:
                        final_results['scholarships'] = {"message": "Cannot check scholarship eligibility: No verified income found."}
                        continue
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
            job_title_param = params.get('job_title', 'a generic job')
            mock_job_description = f"We are looking for a {job_title_param} to help us with our government projects."
            
            # --- UPDATED MODEL NAME ---
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
        return {"message": "I couldn't determine a specific task from your query."}
        
    return final_results

