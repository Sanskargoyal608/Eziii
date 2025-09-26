# Team Member A (Your) Task List

This is your focused set of responsibilities. You will manage the core infrastructure, the primary database, the main backend, and the federated engine itself.

## Phase 2: Distributed Architecture & API Development (Weeks 4-7)

### Week 4: PostgreSQL & Django Admin/API
- [ ] **Configure Remote Access**: Modify your PostgreSQL `pg_hba.conf` and `postgresql.conf` files to allow connections from your partner's IP address.
- [ ] **Firewall Rules**: Ensure your OS firewall allows traffic on port 5432.
- [ ] **Django Admin Panel**: In `core/admin.py`, register all your models (Student, Document, etc.) so you can easily add/edit data through the built-in admin interface. This fulfills the admin requirement.
- [ ] **Create API Endpoint**: Using Django REST Framework, create a read-only API view that lists all documents for a given student.

### Week 5-6: React Frontend Structure
- [ ] **Initialize React App**: Use `create-react-app` to set up the frontend project.
- [ ] **Install Libraries**: Run `npm install react-router-dom tailwindcss`.
- [ ] **Build Core Layout**: Create the main `App.js` with routing, a `Navbar` component, and a main content area.
- [ ] **Build Chat Component**: Design and build the `ChatQueryInterface.js` component. It should have a text input field and a display area for results.

### Week 7: Federated Engine Connection
- [ ] **Modify `query_analyzer.py`**: Update the script's database connection logic.
  - The PostgreSQL connection will remain direct (using `psycopg2`).
- [ ] **Add Function for Flask API**: Add a new function that uses the `requests` library to make an HTTP call to your partner's Flask API to fetch jobs/scholarships.

## Phase 3: Core Logic & Feature Implementation (Weeks 8-10)

### Week 8-9: LLM Integration & Federated API
- [ ] **Integrate Gemini API**: In `query_analyzer.py`, replace the simulated LLM function with actual API calls to Google's Gemini for analysis and Text-to-SQL.
- [ ] **Create Federated API Endpoint**: Build a new Django view that receives a POST request with a user's text query.
  - This view will call your `query_analyzer.py`'s main function, wait for the integrated result, and then return that result as a JSON response. This is the critical link between your frontend and the federated engine.

### Week 10: Task 2 Demo
- [ ] **Lead the Demonstration**: Lead the demonstration of the chat interface and be prepared to explain the backend architecture.

## Phase 4: Full Feature & Final Deliverables (Weeks 11-14)

### Week 11-12: Proactive Recommendations
- [ ] **Design Backend Logic**: Design and build the backend logic (e.g., a scheduled task or a background worker) that periodically analyzes student profiles and pre-calculates their job/scholarship eligibility.
- [ ] **Create New API Endpoints**: Create new API endpoints that serve these pre-calculated results for the main dashboard.
