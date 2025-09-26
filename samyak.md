# Team Member B (Partner's) Task List

This is your focused set of responsibilities. You will manage the secondary data source (jobs/scholarships) and its API, and will be the primary developer for the frontend UI components.

## Phase 2: Distributed Architecture & API Development (Weeks 4-7)

### Week 4: SQLite Database & Flask API
- [ ] **Set Up SQLite**: Create an SQLite database file (`opportunities.db`).
- [ ] **Write Schema**: Create the `govt_jobs` and `scholarships` tables.
- [ ] **Populate Database**: Adapt the existing `generate_dummy_data.py` script to connect to your SQLite file and populate these tables.
- [ ] **Build Flask API**: Create a simple Python Flask application.
  - This application should have at least one endpoint, e.g., `/api/opportunities`, that queries your SQLite database and returns the results in JSON format. This is how Team A will access your data.

### Week 5-6: Frontend UI Component Development
- [ ] **Build Dashboard Components**: Within the React project set up by Team A, create the UI components that will be on the main dashboard page.
  - `DocumentList.js`: A component that shows a list of documents.
  - `JobCarousel.js`: A component that displays job cards in a horizontal scroll view.
  - `ScholarshipCarousel.js`: Similar to the job carousel.
- [ ] **Connect Document List**: Implement the logic inside `DocumentList.js` to make an API call to Team A's Django backend, fetch the documents for the logged-in user, and display them.

### Week 7: Refine Flask API
- [ ] **Add Search Functionality**: Enhance your Flask API. Create new endpoints that allow for more specific queries, for example: `/api/jobs/search?degree=B.Tech`.
- [ ] **Work with Team A** to define the exact API request/response formats needed for the federated engine.

## Phase 3: Core Logic & Feature Implementation (Weeks 8-10)

### Week 8-9: Connect Chat UI to Backend
- [ ] **Implement API Call**: In the `ChatQueryInterface.js` component, write the code that takes the user's text from the input field.
- [ ] **Send this text in a POST request** to the new federated API endpoint created by Team A.
- [ ] **Render Results**: Write the logic to receive the integrated JSON response from the API and display it nicely within the chat window.

### Week 10: Task 2 Demo
- [ ] **Support the Demonstration** by explaining the frontend implementation and the role of your Flask API.

## Phase 4: Full Feature & Final Deliverables (Weeks 11-14)

### Week 11-12: Connect Main Dashboard
- [ ] **Connect the JobCarousel.js and ScholarshipCarousel.js** components to the new "proactive recommendation" API endpoints created by Team A.
- [ ] **Ensure the main dashboard** now displays the correct, personalized opportunities for the user.
