# Backend Lead (Django, PostgreSQL, Query Engine, LLM Integration)

## Overall Goal
Build the secure backend infrastructure for the student portal, implement document processing logic, enhance the federated query engine, and manage integrations.

---

## Week 10: Authentication Backend

**Goal:** Implement secure user login/registration.  
**Branch:** feature/student-auth-backend from main.

### Tasks

- [ ] Implement Django models/views for user registration (Email/Password).  
- [ ] Set up JWT authentication (using `djangorestframework-simplejwt`).  
- [ ] Create login endpoint that returns a JWT token.  
- [ ] Modify existing API endpoints (e.g., `/api/documents/`) to require JWT authentication.  

**GitHub:**
```bash
git push origin feature/student-auth-backend
```

---

## Week 11: Document Processing Backend

**Goal:** Handle document uploads and bashic text extraction.  
**Branch:** feature/doc-processing-backend from main.

### Tasks

- [ ] Create a Django API endpoint (POST `/api/documents/upload/`) to accept file uploads (PDF/Image) and document IDs.  
- [ ] Implement secure file saving logic.  
- [ ] Research and integrate Python libraries for OCR/text extraction (`pytesseract`, `PyPDF2`).  
- [ ] Implement logic to extract text from uploaded files.  
- [ ] Update the Document model (add `extracted_text` and `file_path` fields). Run migrations.  

**GitHub:**
```bash
git push origin feature/doc-processing-backend
```

---

## Week 12: Core Logic & PDF Generation Backend

**Goal:** Integrate document data into eligibility and add PDF feature.  

**GitHub:**
```bash
git checkout main
git pull origin main
git merge feature/student-auth-backend
git push origin main
```

**Branch:** feature/recommendation-logic from main.

### Tasks

- [ ] Enhance `get_student_qualifications` to use `extracted_text` (if feasible).  
- [ ] Refine `execute_query_plan` filtering bashed on richer document data.  
- [ ] Create an API endpoint (POST `/api/generate-pdf/`) to accept a list of document IDs.  
- [ ] Implement PDF generation using `reportlab` (combine text and metadata).  

**GitHub:**
```bash
git push origin feature/recommendation-logic
```

---

## Week 13: Chat Enhancements

**Goal:** Make the chat responses more natural and intelligent.  
**Branch:** feature/chat-enhancements from main.

### Tasks

- [ ] Refine the LLM prompt in `analyze_and_decompose_query_with_llm` for better conversational understanding.  
- [ ] Modify `execute_query_plan` to:
  - Send structured results + original query to Gemini.
  - Generate a human-like summary/answer instead of raw JSON.  
- [ ] Research/Implement logic for calculating eligibility chance percentage.  

**GitHub:**
```bash
git push origin feature/chat-enhancements
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

- [ ] Coordinate with partner to merge all remaining feature branches:  
  `doc-processing-backend`, `recommendation-logic`, `chat-enhancements`,  
  and partner’s `core-pages`, `doc-upload-ui`, `real-data-scraping`.  
- [ ] Thoroughly test login, document upload, data display, PDF generation, and chat queries.  
- [ ] Debug issues found during integration testing.  

**GitHub:**  
All work now happens on `main`. Push frequently.

---

## Weeks 15–16: Paper, Poster & Submission

**Goal:** Finalize academic deliverables.

### Tasks

- [ ] Collaborate with partner on writing the final report (`iia_main.tex`).  
  Focus on backend architecture, algorithms, LLM integration, and innovation sections.  
- [ ] Prepare content for the poster presentation related to the backend.  
- [ ] Ensure all code (`Django app`, `query_analyzer.py`) is clean and commented.  
- [ ] Prepare the final ZIP submission.
