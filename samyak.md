# Frontend Lead (React/Vite) & Secondary Data Source Lead (Flask, SQLite, Scraping)

## Overall Goal
Build the student-facing React portal, implement real-data scraping for jobs/scholarships, and maintain the secondary Flask API.

---

## Week 10: Scraping Setup & Flask API Update

**Goal:** Set up scraping and update Flask API with initial scraped data.  
**Branch:** feature/real-data-scraping from main.

### Tasks

- [ ] Research and choose 2-3 reliable government/job/scholarship websites for scraping.  
- [ ] Set up Python environment for scraping (install requests, beautifulsoup4, potentially scrapy).  
- [ ] Write initial scraping scripts to get bashic info (e.g., job titles, scholarship names, URLs).  
- [ ] Adapt Flask API to read data from SQLite DB populated by the scraper (instead of dummy data).  
- [ ] Ensure `/api/jobs` and `/api/scholarships` endpoints return JSON matching the exact API contract provided by the partner (fields like `description` and `eligibility`).  
- [ ] Run your Flask server:

```bash
flask run --host=0.0.0.0
```

- [ ] Test your API locally (using curl or Postman).  

**GitHub:**
```bash
git push origin feature/real-data-scraping
```

---

## Week 11: Frontend Authentication & Document Upload UI

**Goal:** Build the login/registration UI and the document upload form.  
**Branch:** feature/student-auth-frontend from main.

### Tasks

- [ ] Create React components for Login and Registration forms.  
- [ ] Implement API calls to the Django backend for login/registration.  
- [ ] Implement JWT token storage (e.g., in localStorage) and retrieval.  
- [ ] Set up bashic authenticated routing (redirect to login if no token).  

**GitHub:**
```bash
git push origin feature/student-auth-frontend
```

**Branch:** feature/doc-upload-ui from feature/student-auth-frontend.

### Tasks

- [ ] Create React component for document upload form (category selection, file input, text input for Govt ID).  
- [ ] Implement API call (POST) to `/api/documents/upload/`, sending form data and JWT token in headers.  

**GitHub:**
```bash
git push origin feature/doc-upload-ui
```

---

## Week 12: Core Frontend Pages

**Goal:** Build the main data display pages.  

**GitHub:**
```bash
git checkout main
git pull origin main
git merge feature/student-auth-frontend
git push origin main
```

**Branch:** feature/core-pages from main.

### Tasks

- [ ] Create React components/pages for displaying Jobs and Scholarships.  
- [ ] Implement fetch calls to Flask API endpoints (`/api/jobs`, `/api/scholarships`).  
- [ ] Modify Home component to fetch documents belonging to the logged-in user (send JWT token).  
- [ ] Add UI for selecting documents for PDF generation.  
- [ ] Implement API call (POST) to `/api/generate-pdf/`, sending selected document IDs and JWT token.  

**GitHub:**
```bash
git push origin feature/core-pages
```

---

## Week 13: Advanced Scraping

**Goal:** Enhance scraping scripts to extract more detailed, structured data.  
**Branch:** Continue on feature/real-data-scraping.

### Tasks

- [ ] Refine scrapers to handle potential PDF downloads and extract text.  
- [ ] Use regex or rules to parse eligibility criteria (e.g., CGPA, income limit).  
- [ ] Update SQLite schema if needed to store structured data.  
- [ ] Update Flask API to serve richer data while keeping API contract consistent.  

**GitHub:**
```bash
git push origin feature/real-data-scraping
```

---

## Week 14: Final Integration & Testing

**Goal:** Merge all features and ensure the system works end-to-end.  

**GitHub:**
```bash
git checkout main
git pull origin main
```

### Tasks

- [ ] Coordinate with partner to merge all branches: `doc-upload-ui`, `core-pages`, `real-data-scraping`, and partner’s backend features.  
- [ ] Test all major flows: login, document upload, job/scholarship display, PDF generation, chat queries.  
- [ ] Fix UI bugs and API connection issues.  

**GitHub:**  
All work now happens on `main`. Push frequently.

---

## Weeks 15–16: Paper, Poster & Submission

**Goal:** Finalize academic deliverables.

### Tasks

- [ ] Collaborate with partner on the final report (`iia_main.tex`).  
- [ ] Focus on frontend implementation, scraping, Flask API, and results sections.  
- [ ] Prepare poster content related to frontend and data scraping.  
- [ ] Ensure all code (React, Flask, Scrapers) is clean and commented.  
- [ ] Prepare the final ZIP submission.
