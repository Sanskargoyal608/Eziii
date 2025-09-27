# Frontend Lead & Secondary Backend Developer Tasks

This document outlines your updated tasks, which now include backend responsibilities.

### Technology Stack:
- **Frontend**: React, Vite, CSS Modules
- **Backend**: Python, Flask, SQLite

---

## Weeks 1-6: Foundation (COMPLETE)

### Recap:
- The frontend project is stable on Vite and CSS Modules.
- It is successfully displaying document data fetched from your partner's Django API.

---

## Week 7: Set Up the Second Data Source (Your Backend)

### Goal:
On your own machine, create and populate the separate SQLite database for jobs and scholarships.

### Tasks:

1. **Install Python and pip** on your machine if you haven’t already.

2. **Run the setup script provided by your partner**:
   - Your partner will provide a Python script named `setup_sqlite.py`.
   - Run this script on your computer to create the `federated_data.db` file, which will be your SQLite database.

3. **Populate the SQLite database**:
   - Your partner will also provide an updated `generate_dummy_data.py` script.
   - Run the specific function from this script to populate the `federated_data.db` with `GovtJob` and `Scholarship` data.

4. **Frontend Task**:
   - Continue your frontend work by building the static (hard-coded) components for **JobList.jsx** and **ScholarshipList.jsx** using **CSS Modules**.
   - For now, populate these components with fake data to display job and scholarship information.

---

## Week 8: Build the Secondary API (Your Backend)

### Goal:
Create a simple Flask API on your machine to serve data from your SQLite database.

### Tasks:

1. **Install Flask**:
   - Install Flask and Flask-CORS: 
     ```bash
     pip install Flask Flask-Cors
     ```

2. **Create the Flask API**:
   - Create a new file named `federated_api.py`.

3. **Build the Flask App**:
   - Connect the Flask app to your `federated_data.db` SQLite database.
   - Create two API endpoints:
     - `/api/jobs`: Queries the `govt_jobs` table and returns the results as JSON.
     - `/api/scholarships`: Queries the `scholarships` table and returns the results as JSON.

4. **Configure CORS**:
   - Configure CORS on your Flask app to allow requests from your React frontend (e.g., `http://localhost:5173`).

5. **Run the Flask Server**:
   - Run the Flask server on your local machine.

---

## Week 9: Connect Frontend & Integrate

### Goal:
Connect your React components to your new Flask API and prepare for the final demonstration.

### Tasks:

1. **Modify the `JobList.jsx` and `ScholarshipList.jsx` components**:
   - Update these components to fetch data from your local Flask API endpoints (e.g., `http://localhost:5000/api/jobs`).

2. **Federated Query Integration**:
   - Work with your partner to integrate the federated query engine.
   - Modify the `FederatedChat` component to send user queries to a new endpoint on your partner's Django server.

3. **Display Results in Chat**:
   - Display the results returned by the federated query engine in the chat window.

---

This document clearly outlines your tasks for the upcoming weeks as both a frontend lead and a secondary backend developer. Let me know if you'd like to adjust or add anything!
