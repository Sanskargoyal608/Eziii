# Revised Roadmap (Hybrid App & Federated Engine)

This roadmap integrates the development of a React frontend and a distributed database architecture with the core academic goal of building a federated query engine. The primary objective remains the Task 2 evaluation in Week 10, focusing on a chat-based query interface.

## Phase 1: Foundational Setup (Complete)
**Weeks 1-3:**

- [✓] **Task**: PostgreSQL & Django backend foundation established.
- [✓] **Task**: PostgreSQL populated with student/document data.
- [✓] **Task**: Initial schema and data validated.

## Phase 2: Distributed Architecture & API Development (Current Focus: Weeks 4-7)
The goal of this phase is to establish the distributed database environment and build the basic APIs needed for both the frontend and the federated engine.

### Week 4: Distributed Database & API Scaffolding
**Team A (You):**
- Configure PostgreSQL to accept remote connections (for your partner).
- Create initial Django REST Framework API endpoints for user authentication and to list a student's documents.
- Build the Django Admin interface to add/edit data in the tables.

**Team B (Partner):**
- Set up the SQLite database for jobs/scholarships.
- Create a simple Flask API to expose the data from the SQLite database over the network.

**Goal**: Team A can access Team B's database via an API, and vice-versa. A basic admin panel is functional.

### Week 5-6: Frontend Foundation & Initial API Integration
**Team A (You):**
- Set up the React project structure with `react-router-dom` and Tailwind CSS.
- Build the main layout components (Navbar, Sidebar, Footer).
- Create the "chat" interface component for querying.

**Team B (Partner):**
- Build the UI components for the Dashboard (document list, job/scholarship carousels).
- Connect the document list component to Team A's Django API endpoint.

**Goal**: A functional React frontend skeleton where a user can log in (mocked) and see their documents fetched live from the backend.

### Week 7: Federated Engine - Initial Connection
**Team A (You):**
- Modify `query_analyzer.py` to connect to your local PostgreSQL and to Team B's remote Flask API.

**Team B (Partner):**
- Refine the Flask API with specific endpoints for searching jobs and scholarships based on criteria.

**Goal**: The `query_analyzer.py` script can successfully fetch data from both independent, distributed databases.

## Phase 3: Core Logic & Feature Implementation (Weeks 8-10)
This phase is about making the system intelligent and preparing for the Task 2 demo.

### Week 8-9: LLM Integration & Chat Functionality
**Team A (You):**
- Integrate the Gemini API into `query_analyzer.py` to replace the simulation.
- Create a new Django API endpoint that takes a text query, runs it through the federated engine, and returns the integrated result.

**Team B (Partner):**
- Connect the React "chat" interface to the new Django API endpoint.
- Implement the logic to display the integrated results from the API in the chat window.

**Goal**: A fully demonstrable chat interface where a user can type a query and get a federated answer from all three data sources. This completes the Task 2 deliverable.

### Week 10: Task 2 Submission & Demo
**Both:**
- Prepare the submission document and rehearse the demonstration of the chat interface.

**Deliverable**: Successful Task 2 evaluation.

## Phase 4: Full Feature & Final Deliverables (Weeks 11-14)

### Week 11-12: Full Dashboard Integration & Paper Writing
**Team A (You):**
- Create backend logic to proactively find and cache eligible jobs/scholarships for each user.

**Team B (Partner):**
- Connect the job and scholarship UI components on the main dashboard to the new backend logic.

**Both:**
- Write the final conference-style paper (Task 4).

### Week 13-14: Final Polish & Poster Presentation
**Both:**
- Refine the UI, fix bugs, and prepare the poster for the final presentation (Task 5).
