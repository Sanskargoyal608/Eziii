# EduVerify & Career Compass (Student Portal Phase)

## Project Overview
EduVerify & Career Compass is a full-featured student portal designed to streamline the process of career exploration and academic guidance. The platform includes functionalities such as user authentication, document management, intelligent job and scholarship recommendations, PDF generation, and an enhanced conversational chat interface. The portal also retains existing admin functionalities for management.

## Technology Stack

### Frontend
- **React (Vite)** for building the user interface.
- **CSS Modules** for styling.

### Backend
- **Main Backend (You)**: 
  - **Python (Django)** for the primary backend framework.
  - **Django REST Framework** for building RESTful APIs.
  - **PostgreSQL** as the database system.
  - **Google Gemini API** for advanced conversational and AI features.

- **Secondary Backend (Partner)**:
  - **Python (Flask)** for the partner API.
  - **SQLite** for a lightweight database.
  - **Web Scraping Libraries** (e.g., **BeautifulSoup**, **Scrapy**) for data scraping.

### Version Control
- **Git** and **GitHub** for version control and collaboration.

---

## Phases & Timeline

### Phase 1: Foundation (Completed)
Duration: **Weeks 1-9**

- Initial project setup (Git, Django, React/Vite, PostgreSQL).
- Basic API endpoints for documents/students.
- Core federated query engine (LLM decomposition, execution logic).
- Connection between frontend and backend.
- Basic chat interface connected to the federated engine.
- Task 2 deliverables prepared.

---

### Phase 2: Student Portal & Real Data Integration
Duration: **Weeks 10-14**

#### **Week 10: Authentication & Scraping Setup**

**Backend (Auth)**:
- Implemented user registration (Email/Password).
- Implemented user login using JWT (JSON Web Tokens).
- Created protected API endpoints requiring authentication.

**Partner (Scraping & API)**:
- Researched and selected 2-3 target websites for scraping jobs/scholarships.
- Set up scraping environment (Python, BeautifulSoup/Scrapy).
- Developed initial scraping scripts to fetch basic data (titles, links).
- Enhanced Flask API to serve scraped data.

#### **Week 11: Frontend Auth & Document Upload UI**

**Backend (Document Processing)**:
- Designed API endpoint for document upload (POST `/api/documents/upload/`).
- Implemented basic file handling (saving uploaded PDF/images).
- Implemented text extraction logic using OCR libraries (e.g., `pytesseract`, `PyPDF2`).

**Partner (Frontend - Auth & Upload)**:
- Built Login/Registration pages in React.
- Integrated frontend with JWT authentication endpoints.
- Built the Document Upload form UI (category selection, file input/ID input).

#### **Week 12: Core Features - Backend Logic & Frontend Pages**

**Backend (Core Logic)**:
- Refined `get_student_qualifications` to use extracted text/data.
- Enhanced query execution logic to use extracted text for richer eligibility filtering.
- Designed API endpoint for PDF generation (POST `/api/generate-pdf/`).
- Implemented PDF generation logic using `reportlab`.

**Partner (Frontend - Core Pages)**:
- Built dedicated pages for Jobs and Scholarships.
- Integrated Flask API to fetch live data for job and scholarship listings.
- Enhanced Homepage document list to display only the logged-in user's documents.
- Built UI for selecting documents and triggering PDF generation.

#### **Week 13: Advanced Scraping & Chat Enhancements**

**Backend (Chat LLM)**:
- Refined chat functionality to handle more conversational queries.
- Integrated eligibility chance calculation based on data (if feasible).
- Improved the response generation to be more "human-like" by summarizing with the Gemini API.

**Partner (Scraping & API)**:
- Implemented more advanced scraping logic (e.g., extracting details from PDF job postings).
- Stored structured data in SQLite.
- Refined Flask API to serve advanced scraping results.

#### **Week 14: Final Integration, Testing & Polish**

- Merged all feature branches into `main`.
- Thorough end-to-end testing: login, document upload, job/scholarship display, PDF generation, chat functionality.
- Debugged and fixed any issues.
- Final integration and deployment.

---

### Phase 3: Project Completion
Duration: **Weeks 15-16**

#### **Week 15: Task 3 (Innovation) & Task 4 (Paper)**

- Reviewed Task 3 requirements and identified innovative aspects (e.g., LLM-based decomposition, eligibility parsing, adaptive chat responses).
- Started writing the final conference-style paper (using LaTeX template `iia_main.tex`).
- Documented architecture, algorithms, results, and innovations.

#### **Week 16: Task 5 (Poster) & Final Submission Prep**

- Prepared poster presentation content.
- Practiced project demonstration.
- Finalized paper and submitted the final ZIP package (Code + Report PDF).

---

## Features

- **Authentication**: User login and registration with JWT authentication.
- **Document Management**: Upload and manage academic and career-related documents.
- **Scraped Data Integration**: Real-time job and scholarship listings fetched from external websites using web scraping techniques.
- **Intelligent Recommendations**: Based on user data, the platform provides job and scholarship recommendations.
- **PDF Generation**: Ability to generate PDF summaries from documents.
- **Conversational Chat Interface**: An AI-powered chat interface for students to interact with the system and get personalized responses.

---

## Installation

### Backend (Django)

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/eduverify-career-compass.git
   cd eduverify-career-compass
   ```
2. Set up a virtual environment and install dependencies:
   ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
   ```


## Set up the database

```bash
python manage.py migrate
```

## Run the server

```bash
python manage.py runserver
```

## Frontend (React)

### Navigate to the frontend directory

```bash
cd frontend
```

### Install dependencies

```bash
npm install
```

### Start the development server

```bash
npm run dev
```

## Contribution

**Fork the repository.**

**Create a new branch for your feature:**
```bash
git checkout -b feature/your-feature
```

**Commit your changes:**
```bash
git commit -m 'Add feature'
```

**Push to your branch:**
```bash
git push origin feature/your-feature
```

**Open a pull request.**

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- **Django**: Backend framework used for building the core application.  
- **React/Vite**: Frontend technology for a fast and responsive user interface.  
- **Google Gemini API**: Used for advanced conversational AI features.  
- **BeautifulSoup/Scrapy**: Web scraping libraries used for gathering data.  
- **ReportLab**: PDF generation library.  
- **pytesseract**: OCR library for text extraction from images/PDFs.  
