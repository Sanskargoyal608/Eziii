# Technology Stack Roadmap (Vite + CSS Modules)

This roadmap reflects our updated technology stack (Vite + CSS Modules) and the hybrid goal of building both a functional web application and a federated query engine for your academic evaluation.

## Phase 1: Foundation & Initial Connection (Weeks 1-6) - **COMPLETE**

### Weeks 1-3:
- **Recap:** 
  - Successfully set up the primary backend with Django and a PostgreSQL database.
  - Designed and implemented the core database schema.
  - Populated the database with a Python script.

### Weeks 4-6:
- **Recap:**
  - Built the initial Django REST Framework API for documents.
  - Set up the frontend project, encountering significant build issues with Create React App and Tailwind CSS.
  
- **PIVOT:** 
  - Successfully migrated the frontend from Create React App to Vite.
  - Migrated from Tailwind CSS to CSS Modules for a more stable and modern development experience.
  
- **Milestone:** 
  - The React frontend is now successfully fetching and displaying documents from the Django backend API.
  - The core full-stack connection is working.

---

## Phase 2: Distributed Architecture & Federated Engine (Weeks 7-10)

### Week 7 (Current):
- **Team A (You):**
  - Set up the second relational data source.
  - Create a separate SQLite database to hold the GovtJob and Scholarship data.
  - Modify the data generation script to populate this new database.
  
- **Team B (Partner):**
  - Build the UI components for the Jobs and Scholarships sections on the homepage using CSS Modules.
  - Use static (hard-coded) data for now.

### Week 8:
- **Team A (You):**
  - Build a lightweight Flask API to serve data from the SQLite database.
  - This API will have endpoints like `/api/jobs` and `/api/scholarships`.
  
- **Team B (Partner):**
  - Connect the new React components to the Flask API.
  - Fetch and display live job and scholarship data.
  - Configure your network for remote connections.

### Week 9:
- **Team A (You):**
  - Begin core development of the `query_analyzer.py` script.
  - Implement the initial logic for query decomposition using simple keyword matching (e.g., if a query contains "jobs", target the Flask API; if "documents", target the Django API).
  
- **Team B (Partner):**
  - Refine the UI of the `FederatedChat.jsx` component.
  - Work with Team A to integrate the `query_analyzer.py` script's output into the chat interface.

### Week 10: Task 2 Evaluation
- **Both:**
  - Prepare the submission document answering rubric points (a-j).
  - Integrate the federated query process into the application for a live demonstration.
  - A user's query in the chat should trigger your Python script, which then calls the appropriate API (Django or Flask) and returns the result.

---

## Phase 3: LLM Integration & Final Features (Weeks 11-14)

### Week 11:
- **Team A (You):**
  - Integrate the third data source: an open-source LLM.
  - Enhance the `query_analyzer.py` to send sub-queries to the LLM (e.g., "summarize the skills for this job description").
  
- **Team B (Partner):**
  - Implement user authentication UI (Login/Register pages).

### Week 12:
- **Team A (You):**
  - Implement user authentication backend logic in Django.
  
- **Team B (Partner):**
  - Implement the document upload UI.

### Weeks 13-14: Final Submission & Presentation
- **Both:**
  - Finalize the project, write the conference-style paper, and prepare the poster for the final presentation and demonstration.
