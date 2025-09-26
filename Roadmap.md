# Project Roadmap: EduVerify & Career Compass

This roadmap is divided into four main phases, starting with the database as requested. Each phase includes key tasks and milestones.

---

## Phase 1: Database & Foundation (Weeks 1-3)

**Goal:** Design, implement, and populate a robust database schema. This is the backbone of the entire application.

**Primary Technologies:** SQL (e.g., PostgreSQL, MySQL)

### Tasks:

#### Week 1: Database Design
- [ ] **Task:** Define the complete database schema.
    - Students table (student_id, name, email, password_hash, contact_info, income_details).
    - Documents table (document_id, student_id, document_type, submitted_url/application_no, verified_status, digital_signature, verified_data_json).
    - Govt_Jobs table (job_id, title, description, eligibility_criteria_json, required_skills_raw, source_url).
    - Scholarships table (scholarship_id, name, description, eligibility_criteria_json, amount, source_url).
    - Skills table (skill_id, skill_name).
    - Student_Skills junction table (student_id, skill_id).
- [ ] **Task:** Finalize data types, constraints (Primary Keys, Foreign Keys), and relationships.
- [ ] **Task:** Write the SQL script to create these tables (`database_schema.sql`).

#### Week 2: Database Setup & Dummy Data Generation
- [ ] **Task:** Set up the database server (e.g., local PostgreSQL instance).
- [ ] **Task:** Run the `database_schema.sql` script to create the database structure.
- [ ] **Task:** Develop a Python script (`generate_dummy_data.py`) to generate realistic fake data for all tables. This is crucial for testing.
    - Generate 100+ students.
    - Generate 5-10 documents per student (some verified, some pending).
    - Generate 50+ government jobs with varied eligibility.
    - Generate 30+ scholarships.
- [ ] **Task:** Populate the database with this dummy data.

#### Week 3: Initial Query Testing
- [ ] **Task:** Write and execute complex SQL queries to test the database logic. This is the key task for your initial evaluation.
    - Query 1: "Find all jobs a specific student is eligible for based on their verified degree and grades."
    - Query 2: "List all students who are eligible for a specific scholarship based on their income and academic performance."
    - Query 3: "Retrieve all verified documents for a given student."
- [ ] **Milestone:** Database is fully functional and passes all predefined query tests.

---

## Phase 2: Backend Development (Weeks 4-7)

**Goal:** Build the server-side logic, APIs, and business rules.

**Primary Technologies:** Python, Django REST Framework

### Tasks:

#### Week 4: Project Setup & User Authentication
- [ ] **Task:** Initialize Django project and configure database connection.
- [ ] **Task:** Implement user registration and login APIs (JWT-based).
- [ ] **Task:** Create API endpoints for basic user profile management (CRUD operations).

#### Week 5: Document Management APIs
- [ ] **Task:** Create API endpoints for document upload.
- [ ] **Task:** Develop a "mock" verification service that randomly marks documents as verified/rejected.
- [ ] **Task:** Implement endpoints to list a user's documents (both verified and pending).
- [ ] **Task:** Create a secure endpoint to view/share a specific digitally signed document.

#### Week 6-7: Recommendation Engine Core Logic
- [ ] **Task:** Build a web scraper/service to fetch job and scholarship data from predefined sources (for now, populate from the dummy DB).
- [ ] **Task:** Develop the core matching algorithm in Python.
    - Function to match a student's profile against job/scholarship `eligibility_criteria_json`.
- [ ] **Task:** Create API endpoints:
    - `/api/recommendations/jobs`
    - `/api/recommendations/scholarships`
- [ ] **Milestone:** Backend APIs are complete, tested (using a tool like Postman), and ready for frontend integration.

---

## Phase 3: Frontend Development (Weeks 8-11)

**Goal:** Create a responsive and intuitive user interface.

**Primary Technologies:** React, Tailwind CSS

### Tasks:

#### Week 8: Setup & Dashboard
- [ ] **Task:** Set up React project (`create-react-app`).
- [ ] **Task:** Implement routing (e.g., React Router).
- [ ] **Task:** Build the main dashboard layout, login page, and registration page.
- [ ] **Task:** Connect the login/registration forms to the backend APIs.

#### Week 9: Document Management UI
- [ ] **Task:** Create the "My Documents" page to list all documents.
- [ ] **Task:** Build the document upload component with a form and file input.
- [ ] **Task:** Develop a modal or dedicated page to display a verified document's details.

#### Week 10-11: Recommendations UI
- [ ] **Task:** Build the UI for the "Recommended Jobs" page.
- [ ] **Task:** Build the UI for the "Recommended Scholarships" page.
- [ ] **Task:** Create a detailed view for a single job, which will later display the LLM analysis.
- [ ] **Task:** Integrate all recommendation APIs with the frontend.
- [ ] **Milestone:** Frontend is fully connected to the backend. A user can log in, upload a document, and see personalized recommendations.

---

## Phase 4: LLM Integration & Refinement (Weeks 12-14)

**Goal:** Integrate the LLM to provide advanced skill analysis and polish the application.

**Primary Technologies:** LLM API (e.g., Gemini)

### Tasks:

#### Week 12: Backend LLM Service
- [ ] **Task:** Create a new Django service that takes a job description as input.
- [ ] **Task:** This service will call the LLM API with a carefully crafted prompt (e.g., "Extract all required skills from this job description. Then, given the student's skills [...], calculate a match percentage.").
- [ ] **Task:** Develop a new API endpoint `/api/jobs/<job_id>/analyze` that returns the LLM's analysis (required skills, match percentage).

#### Week 13: Frontend LLM Integration
- [ ] **Task:** In the React job details view, call the new analysis endpoint.
- [ ] **Task:** Display the required skills and the match percentage in a clean, user-friendly way (e.g., using a progress bar or chart).

#### Week 14: Testing, Deployment & Final Touches
- [ ] **Task:** Conduct end-to-end testing across the entire application.
- [ ] **Task:** Refine the UI/UX based on feedback.
- [ ] **Task:** Prepare for deployment (e.g., Dockerize the application).
- [ ] **Milestone:** Project is complete and ready for presentation.
