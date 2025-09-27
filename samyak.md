# Frontend Lead & UI/UX Developer Tasks

This document outlines your specific tasks as the Frontend Lead & UI/UX Developer, aligning with the revised project roadmap.

---

## Weeks 1-6: Foundation (COMPLETE)

### Recap:
- Successfully set up the frontend project using Vite and CSS Modules.
- Overcame earlier technical challenges and now have a stable application.
- The application is correctly displaying document data fetched from the primary Django API.

---

## Week 7: Build New UI Components

### Goal:
Create the visual components for displaying jobs and scholarships.

### Tasks:

1. **Create two new components:**
   - `JobList.jsx`
   - `ScholarshipList.jsx`

2. **Create corresponding CSS module files:**
   - `JobList.module.css`
   - `ScholarshipList.module.css`

3. **Populate these components with static, hard-coded data:**
   - Create small, fake arrays of job/scholarship objects inside each component file.
   - Render the data in a card-based design, similar to the `DocumentList` component.

4. **Update `App.jsx`:**
   - Import these new components into `App.jsx`.
   - Add new sections to the `Home` component to display the `JobList` and `ScholarshipList` components, similar to how "My Documents" is displayed.

---

## Week 8: Connect to the Federated API

### Goal:
Transition from static data to live data from the new Flask API.

### Tasks:

1. **Coordinate with Team Member A** to get the URL for the new Flask API (e.g., `http://<TEAM_A_IP_ADDRESS>:5000/api/jobs`).

2. **Modify `JobList.jsx` and `ScholarshipList.jsx` components:**
   - Use the `useEffect` and `useState` hooks to fetch data from the Flask API endpoints when the components load.

3. **Implement loading and error states:**
   - Implement loading and error states, similar to the `DocumentList` component, to provide good user feedback.

---

## Week 9: Integrate the Query Engine

### Goal:
Connect the chat interface to the backend's query analyzer.

### Tasks:

1. **Refine the UI of `FederatedChat.jsx`:**
   - Ensure the chat interface looks clean and is easy to use.

2. **Create a new function in `FederatedChat`** that handles sending a user's query to the backend:
   - This function will make a POST request to a new endpoint on the Django server (e.g., `/api/query/`), which Team Member A will create.

3. **Modify the POST request:**
   - The body of the request will contain the user's text, e.g.:
     ```json
     {'query': 'show me my jobs'}
     ```

4. **Update the chat logic**:
   - Ensure that the results sent back from the backend are displayed correctly in the chat window.

---

## Week 10: Task 2 Evaluation

### Goal:
Prepare for and present a successful demonstration.

### Tasks:

1. **Ensure the end-to-end flow is working:**
   - A user should type a query, the frontend sends it to Django, Django runs the analyzer, the analyzer calls the correct API (Django or Flask), and the results are displayed back in the chat window.

2. **Collaborate with Team Member A** to write the user-facing sections of the submission document:
   - Project statement.
   - Objectives.
   - Example queries.

3. **Prepare to demonstrate the project to the TA:**
   - Be ready to explain your role, the frontend architecture, and how everything integrates.

