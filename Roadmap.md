# Updated Project Roadmap: Distributed Architecture & Federated Engine

This roadmap reflects our updated technology stack and the correct distributed architecture required for the project.

### System A (Your Machine): 
- Primary data source (PostgreSQL)
- Primary API (Django)
- Query Engine

### System B (Partner's Machine): 
- Secondary data source (SQLite)
- Secondary API (Flask)
- Frontend (React)

---

## Phase 1: Foundation & Initial Connection (Weeks 1-6) - **COMPLETE**

### Recap:
- Successfully built the primary Django backend with a populated PostgreSQL database and a working API for documents.
- The Vite/React frontend is stable and successfully fetching data from your Django API.

---

## Phase 2: Distributed Architecture & Federated Engine (Weeks 7-10)

### Week 7 (Current):

**Team A (You):**
- Configure your system for remote access.
  - Edit PostgreSQL config files (`postgresql.conf`, `pg_hba.conf`) and set up a Windows Firewall rule to allow your partner's machine to connect to your database.

**Team B (Partner):**
- Set up the second relational data source.
  - Create and populate the SQLite database (`federated_data.db`) with the `GovtJob` and `Scholarship` data.

---

### Week 8:

**Team A (You):**
- Begin core development of the `query_analyzer.py` script.
  - Implement the initial logic for query decomposition using simple keyword matching.

**Team B (Partner):**
- Build the lightweight Flask API on his machine to serve data from his SQLite database.
  - Create endpoints for `/api/jobs` and `/api/scholarships`.

---

### Week 9:

**Team A (You):**
- Refine the `query_analyzer.py` script.
  - The script should now be able to take a query, decompose it, and make a live API call to the correct target (either your local Django API or your partner's remote Flask API).

**Team B (Partner):**
- Connect his React frontend components (`JobList`, `ScholarshipList`) to his own local Flask API.
  - Build the UI for the `FederatedChat` component.
  - Work on integrating the query engine’s output into the chat interface.

---

### Week 10: Task 2 Evaluation

**Both:**
- Prepare the submission document.
- Integrate the full, end-to-end federated query process for a live demonstration.

---

## Phase 3: LLM Integration & Final Features (Weeks 11-14)

### Weeks 11-14:

**Both:**
- Integrate the LLM as the third data source.
- Implement user authentication.
- Add document upload functionality.
- Finalize the paper and presentation for submission.

