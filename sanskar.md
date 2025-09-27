# Backend Lead & Federated Engine Architect Tasks

This document outlines your specific tasks as the Backend Lead & Federated Engine Architect, aligning with the revised project roadmap.

---

## Weeks 1-6: Foundation (COMPLETE)

### Recap:
- Successfully built the Django backend with a PostgreSQL database.
- Created a working API for documents.
- Assisted in troubleshooting the frontend migration to Vite.

---

## Week 7: Set Up the Second Data Source

### Goal:
Create a separate, independent database for jobs and scholarships to simulate a distributed environment.

### Tasks:

1. **Create a new Python script (`setup_sqlite.py`):**
   - Use the `sqlite3` library to create a database file named `federated_data.db`.

2. **Write the `CREATE TABLE` SQL statements** for the following tables:
   - `govt_jobs`: Structure should match the models in your Django project.
   - `scholarships`: Structure should match the models in your Django project.

3. **Modify your `generate_dummy_data.py` script**:
   - Add functions that connect to the new `federated_data.db` and populate the `govt_jobs` and `scholarships` tables.
   - Keep the existing logic that populates students and documents in the PostgreSQL database.

---

## Week 8: Build the Federated API

### Goal:
Create a separate microservice to expose the data from the new SQLite database.

### Tasks:

1. **Install Flask and Flask-CORS**:
   - Run the following command:
     ```bash
     pip install Flask Flask-Cors
     ```

2. **Create a new file `federated_api.py`**:
   - In this file, build a simple Flask application.

3. **Create two API endpoints**:
   - `/api/jobs`: Query the `govt_jobs` table in `federated_data.db` and return the results as JSON.
   - `/api/scholarships`: Query the `scholarships` table and return the results as JSON.

4. **Configure CORS** in your Flask app to allow requests from the partner's React frontend (`http://localhost:5173`).

---

## Week 9: Develop the Query Decomposer

### Goal:
Build the core logic for your Task 2 evaluation.

### Tasks:

1. **Work primarily in the `query_analyzer.py` script**:
   - Create a main function that accepts a natural language text query as input (e.g., "Show me my verified documents").

2. **Implement a simple keyword-based decomposition logic**:
   - If the query contains "document" or "certificate", identify the target as the "Django Document API".
   - If the query contains "job" or "career", identify the target as the "Flask Job API".
   - If the query contains "scholarship" or "funding", identify the target as the "Flask Scholarship API".

3. **Output**:
   - Your script's output should be a simple plan, e.g.,:
     ```python
     {'target': 'http://localhost:8000/api/documents/', 'params': {}}
     ```

---

## Week 10: Task 2 Evaluation

### Goal:
Prepare for and present a successful demonstration.

### Tasks:

1. **Enhance `query_analyzer.py`** to execute the plan:
   - The script should now make the fetch call to the identified API (e.g., `Django` or `Flask`).

2. **Collaborate with the partner** to integrate the script with the React chat UI:
   - The frontend will send the user's query to a new "query" endpoint on your Django server, which will then run your script.

3. **Write the technical sections** of the submission document:
   - Database schemas.
   - Architecture choice.
   - Pseudo-algorithm.
