# This script contains the core logic for the federated query engine.
import requests
import re
import os
import json
from dotenv import load_dotenv
from core.models import Student, Document, StudentProfile
from django.db.models import Avg, Count

# --- Load Environment Variables ---
load_dotenv()

# --- IMPORTANT ---
PARTNER_IP = "192.168.52.109"  # Your partner's local IP
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ==============================================================================
# 1. FINAL RESPONSE SUMMARIZATION
# ==============================================================================

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
        
        text_response = result['candidates'][0]['content']['parts'][0]['text']
        return {"response_text": text_response}
    
    except Exception as e:
        print(f"ERROR: LLM Summarization failed. {e}")
        return {"response_text": f"Sorry, I encountered an error while processing the results: {e}"}

# ==============================================================================
# 2. ETL & PROFILE MANAGEMENT (Extract, Transform, Load)
# ==============================================================================

def update_profile_from_text(student, doc_type, text):
    """
    Parses raw text from a document AND updates the student's
    structured StudentProfile in the database.
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
        if "percentage" in parsed_data and parsed_data["percentage"]:
            profile.highest_percentage = max(profile.highest_percentage or 0, float(parsed_data["percentage"]))
        if "income" in parsed_data and parsed_data["income"]:
            profile.annual_income = int(parsed_data["income"])
        if "degrees" in parsed_data and parsed_data["degrees"]:
            profile.degrees = list(set((profile.degrees or []) + parsed_data["degrees"])) # Merge lists
        if "skills" in parsed_data and parsed_data["skills"]:
            profile.verified_skills = list(set((profile.verified_skills or []) + parsed_data["skills"])) # Merge lists
            
        profile.save()
        print(f"Profile for {student.full_name} updated successfully: {parsed_data}")
        
    except Exception as e:
        print(f"ERROR: LLM Profile update failed: {e}")

def get_student_qualifications(student_id):
    """
    Fetches the pre-structured qualifications from the database.
    No LLM calls.
    """
    if not student_id: return {}
    try:
        profile = StudentProfile.objects.get(student_id=student_id)
        qualifications = {
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

# ==============================================================================
# 3. QUERY DECOMPOSITION (LLM)
# ==============================================================================

def analyze_and_decompose_query_with_llm(query_text):
    """
    Uses a schema-grounded LLM to analyze a natural language query and decompose it 
    into a structured plan.
    NOW WITH ROBUST JSON CLEANING.
    """
    print(f"--- Decomposing query with LLM: '{query_text}' ---")
    if not GEMINI_API_KEY: 
        return {"error": "GEMINI_API_KEY not found."}
    
    prompt = f"""
    You are a query decomposition engine. Your job is to analyze the user's query and convert it into a structured JSON plan.
    You have access to two main data sources:
    1.  DOCUMENT_FILES: The user's uploaded files (e.g., "resume", "aadhar card").
    2.  STUDENT_PROFILES: Structured data extracted from documents (e.g., skills, income, percentage).

    ### Schema & Intents ###
    
    # Use this for queries about FILES
    - "GET_DOCUMENTS": Fetches *files*. Use for queries about 'resume', 'marksheet file', 'aadhar'.
        - 'params': {{"aggregate": "count", "value": "resume"}} (for "how many resumes")
        - 'params': {{"verification_status": "Verified"}} (for "which documents are verified")

    # Use this for queries about structured DATA
    - "ANALYZE_PROFILES": Analyzes *student data*. Use for queries about 'skills', 'income', 'percentage'.
        - 'params': {{"aggregate": "average", "field": "highest_percentage"}} (for "what is the average percentage")
        - 'params': {{"aggregate": "count", "field": "skills", "value": "Python"}} (for "how many students know Python")

    - "GET_JOBS": Fetches job listings.
    - "GET_SCHOLARSHIPS": Fetches scholarship listings.
    
    ### Examples ###
    Query: "what is the average class 12% of all students"
    Output: {{"user_name": null, "intents": [{{"target": "ANALYZE_PROFILES", "params": {{"aggregate": "average", "field": "highest_percentage"}}}}]}}

    Query: "how many students know Python"
    Output: {{"user_name": null, "intents": [{{"target": "ANALYZE_PROFILES", "params": {{"aggregate": "count", "field": "skills", "value": "Python"}}}}]}}

    Query: "which documents of mine are verified"
    Output: {{"user_name": null, "intents": [{{"target": "GET_DOCUMENTS", "params": {{"verification_status": "Verified"}}}}]}}

    # --- THIS IS THE CRITICAL NEW EXAMPLE ---
    Query: "how many students have a resume uploaded"
    Output: {{"user_name": null, "intents": [{{"target": "GET_DOCUMENTS", "params": {{"aggregate": "count", "value": "resume"}}}}]}}

    Query: "show me my resume"
    Output: {{"user_name": null, "intents": [{{"target": "GET_DOCUMENTS", "params": {{"value": "resume"}}}}]}}

    Query: "Which scholarship or job am I eligible in"
    Output: {{"user_name": null, "intents": [{{"target": "GET_JOBS", "params": {{"filter_by_eligibility": true}}}}, {{"target": "GET_SCHOLARSHIPS", "params": {{"filter_by_eligibility": true}}}}]}}

    ### User Query ###
    Query: "{query_text}"
    Output:
    """
    
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }
    
    try:
        response = requests.post(api_url, json=payload, timeout=20)
        response.raise_for_status()
        result = response.json()
        
        if 'candidates' not in result:
            print(f"ERROR: LLM returned no candidates. Response: {result}")
            return {"error": f"LLM returned no candidates. {result.get('error', {}).get('message', '')}"}

        text_response = result['candidates'][0]['content']['parts'][0]['text']
        
        # --- ROBUST JSON PARSING ---
        text_response = text_response.replace("None", "null") # Fix Python None vs JSON null
        
        try:
            plan = json.loads(text_response)
            print(f"LLM generated plan (direct): {plan}") 
            return plan
        except json.JSONDecodeError:
            print("Direct JSON load failed. Attempting to clean response...")
            try:
                start = text_response.find('{')
                end = text_response.rfind('}') + 1
                if start == -1 or end == 0:
                    raise ValueError("No JSON object found in response")
                
                cleaned_json_text = text_response[start:end]
                plan = json.loads(cleaned_json_text)
                print(f"LLM generated plan (cleaned): {plan}") 
                return plan
            except Exception as e:
                print(f"ERROR: LLM returned invalid JSON. Cleaning failed. Error: {e}")
                print(f"--- LLM Raw Response Text ---")
                print(text_response)
                print(f"--- End of Raw Response ---")
                return {"error": f"LLM returned invalid JSON: {text_response}"}

    except Exception as e:
        print(f"ERROR: LLM API call failed. {e}")
        return {"error": f"Could not get a valid plan from the LLM: {e}"}

# ==============================================================================
# 4. QUERY EXECUTION (The "Smart Filter")
# ==============================================================================

def execute_query_plan(plan, student_id=None, original_query=""):
    """
    Executes all intents in the query plan.
    Uses the "Smart Filter" (local Python) for jobs/scholarships.
    Uses direct DB queries for documents.
    """
    print(f"--- Executing Full Query Plan (Context: student_id={student_id}) ---")
    
    if "error" in plan:
        return summarize_results_with_llm(plan, original_query)
    if not plan.get("intents"): 
        return summarize_results_with_llm(
            {"message": "I'm sorry, I couldn't understand that request. Please ask about jobs, scholarships, or your documents."},
            original_query
        )
    
    final_results = {}
    
    # Get student qualifications *once* from our fast, local DB
    qualifications = get_student_qualifications(student_id) if student_id else {}

    for intent_data in plan["intents"]:
        intent = intent_data.get("target")
        params = intent_data.get("params", {})

        # --- INTENT: GET_JOBS ---
        if intent == "GET_JOBS":
            try:
                # 1. Fetch ALL jobs from partner
                endpoint = f'http://{PARTNER_IP}:5000/api/jobs'
                print(f"Making REAL API call for all jobs to: {endpoint}")
                response = requests.get(endpoint, timeout=10)
                response.raise_for_status()
                all_jobs = response.json()
                
                if params.get("aggregate") == "count" and not params.get("filter_by_eligibility"):
                    final_results['jobs_count'] = {"count": len(all_jobs)}
                
                # 2. "Smart Filter" (local Python)
                elif params.get("filter_by_eligibility") and student_id:
                    print(f"Filtering {len(all_jobs)} jobs based on profile: {qualifications}")
                    eligible_jobs = []
                    student_skills = [s.lower() for s in qualifications.get("skills", [])]
                    
                    for job in all_jobs:
                        try:
                            criteria = json.loads(job.get("eligibility_criteria", "{}"))
                            job_skills = criteria.get("skills", "").lower()
                            
                            if any(skill in job_skills for skill in student_skills if skill):
                                eligible_jobs.append(job)
                                
                        except Exception as e:
                            print(f"Skipping job, bad criteria: {e}")
                            continue 
                    
                    if params.get("aggregate") == "count":
                        final_results['jobs_count'] = {"count": len(eligible_jobs)}
                    else:
                        final_results['jobs'] = eligible_jobs
                
                else:
                    final_results['jobs'] = all_jobs # Return all jobs if no filter
                    
            except requests.exceptions.RequestException as e:
                final_results['jobs'] = {"error": f"Failed to fetch jobs: {e}"}

        # --- INTENT: GET_SCHOLARSHIPS ---
        elif intent == "GET_SCHOLARSHIPS":
            try:
                # 1. Fetch ALL scholarships
                endpoint = f'http://{PARTNER_IP}:5000/api/scholarships'
                print(f"Making REAL API call for all scholarships to: {endpoint}")
                response = requests.get(endpoint, timeout=10)
                response.raise_for_status()
                all_scholarships = response.json()

                if params.get("aggregate") == "count" and not params.get("filter_by_eligibility"):
                    final_results['scholarships_count'] = {"count": len(all_scholarships)}

                # 2. "Smart Filter" (local Python)
                elif params.get("filter_by_eligibility") and student_id:
                    print(f"Filtering {len(all_scholarships)} scholarships based on profile: {qualifications}")
                    eligible_scholarships = []
                    student_income = qualifications.get("income")
                    student_perc = qualifications.get("highest_percentage")

                    for schol in all_scholarships:
                        try:
                            criteria = json.loads(schol.get("eligibility_criteria", "{}"))
                            max_income = criteria.get("income")
                            min_perc = criteria.get("annual_percentage")

                            income_eligible = True
                            perc_eligible = True
                            
                            if student_income and max_income:
                                income_eligible = student_income <= int(max_income)
                            
                            if student_perc and min_perc:
                                perc_eligible = student_perc >= float(min_perc)
                                
                            if income_eligible and perc_eligible:
                                eligible_scholarships.append(schol)

                        except Exception as e:
                            print(f"Skipping scholarship, bad criteria: {e}")
                            continue

                    if params.get("aggregate") == "count":
                        final_results['scholarships_count'] = {"count": len(eligible_scholarships)}
                    else:
                        final_results['scholarships'] = eligible_scholarships
                
                else:
                     final_results['scholarships'] = all_scholarships
            
            except requests.exceptions.RequestException as e:
                final_results['scholarships'] = {"error": f"Failed to fetch scholarships: {e}"}

        # --- INTENT: GET_DOCUMENTS ---
        elif intent == "GET_DOCUMENTS":
            print("--- Querying Document Files ---")
            try:
                docs_query = Document.objects.all()

                # A. Admin "All Students" context
                if not student_id: 
                    pass # Start with all documents
                # B. Specific Student context
                else: 
                    docs_query = docs_query.filter(student_id=student_id)
                
                # Check for file type filter (e.g., "resume", "aadhar")
                value_filter = params.get("value")
                if value_filter:
                    docs_query = docs_query.filter(document_type__icontains=value_filter)

                # Check for status filter
                status_filter = params.get('verification_status')
                if status_filter:
                    docs_query = docs_query.filter(verification_status=status_filter)
                
                # Check for aggregation
                if params.get("aggregate") == "count":
                    count = docs_query.count()
                    final_results['document_aggregate'] = {"count": count, "query_details": f"documents matching {params}"}
                else:
                    # Return the list of documents
                    final_results['documents'] = [
                        {"type": d.document_type, "status": d.verification_status, "id": d.document_id} 
                        for d in docs_query
                    ]
            
            except Exception as e:
                final_results['documents'] = {"error": f"Failed to fetch documents locally: {e}"}

        elif intent == "ANALYZE_PROFILES":
            print("--- Analyzing Student Profiles ---")
            try:
                profile_query = StudentProfile.objects.all()
                
                # Check for filters (e.g., "how many students know Python")
                field_to_filter = params.get("field")
                value_to_filter = params.get("value")
                
                if field_to_filter == "skills" and value_to_filter:
                    profile_query = profile_query.filter(verified_skills__icontains=value_to_filter)
                
                aggregation_type = params.get("aggregate")
                field_to_aggregate = params.get("field")

                if aggregation_type == "count":
                    count = profile_query.count()
                    final_results['profile_analysis'] = {"count": count, "query_details": f"students matching {params}"}
                
                elif aggregation_type == "average":
                    if field_to_aggregate == "highest_percentage":
                        result = profile_query.aggregate(average=Avg('highest_percentage'))
                        final_results['profile_analysis'] = {"average_percentage": result['average']}
                    elif field_to_aggregate == "income":
                        result = profile_query.aggregate(average=Avg('annual_income'))
                        final_results['profile_analysis'] = {"average_income": result['average']}
                    else:
                        final_results['profile_analysis'] = {"error": "Average calculation is only supported for 'income' or 'highest_percentage'."}
                
                # --- NEW: Gracefully handle 'mode' ---
                elif aggregation_type == "mode":
                    # (A real 'mode' query is very complex. We'll handle it gracefully.)
                    avg_result = profile_query.aggregate(average=Avg('highest_percentage'))
                    final_results['profile_analysis'] = {
                        "message": "Mode calculation is not supported, but I can give you the average!",
                        "average_percentage": avg_result['average']
                    }
                
                else:
                    final_results['profile_analysis'] = {"message": "I understood you want to analyze profiles, but I'm not sure how."}
                    
            except Exception as e:
                print(f"ERROR: Profile analysis failed: {e}")
                final_results['profile_analysis'] = {"error": f"Error analyzing profiles: {e}"}
        # --- INTENT: ANALYZE_SKILLS ---

        elif intent == "ANALYZE_SKILLS":
            job_title_param = params.get('job_title', 'a generic job')
            mock_job_description = f"We are looking for a {job_title_param} to help us with our government projects."
            
            skills_endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={GEMINI_API_KEY}"
            prompt = f"Based on the following job description, list the top 5 most important technical skills. Return only a JSON array of strings. Description: '{mock_job_description}'"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "responseMimeType": "application/json"
                }
            }
            try:
                response = requests.post(skills_endpoint, json=payload, timeout=15)
                response.raise_for_status()
                result = response.json()
                text_response = result['candidates'][0]['content']['parts'][0]['text']
                
                text_response = text_response.replace("None", "null") # Fix Python None vs JSON null
                
                try:
                    skills = json.loads(text_response)
                except json.JSONDecodeError:
                    start = text_response.find('[')
                    end = text_response.rfind(']') + 1
                    cleaned_json_text = text_response[start:end]
                    skills = json.loads(cleaned_json_text)

                final_results['skill_analysis'] = {"job_title": job_title_param, "required_skills": skills}
            except Exception as e:
                 final_results['skill_analysis'] = {"error": f"Error fetching skills: {e}"}

    if not final_results:
        final_results = {"message": "I understood the request, but couldn't find any relevant data."}
    
    # --- Final Step: Summarize all results ---
    return summarize_results_with_llm(final_results, original_query)