-- SQL Schema for EduVerify & Career Compass Project

-- Drop tables if they exist to ensure a clean slate on re-runs
DROP TABLE IF EXISTS Student_Skills, Skills, Documents, Govt_Jobs, Scholarships, Students CASCADE;

-- Table to store student information
CREATE TABLE Students (
    student_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone_number VARCHAR(15),
    -- Storing complex data like address or income details as JSONB is efficient
    profile_details JSONB, -- e.g., {"address": "...", "date_of_birth": "...", "income_pa": 500000}
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table to store all government job postings
CREATE TABLE Govt_Jobs (
    job_id SERIAL PRIMARY KEY,
    job_title VARCHAR(255) NOT NULL,
    job_description TEXT NOT NULL,
    -- JSONB is ideal for storing varied and nested eligibility rules
    eligibility_criteria JSONB, -- e.g., {"degree": "B.Tech", "min_cgpa": 7.5, "required_certs": ["ID_Proof"]}
    required_skills_raw TEXT, -- The raw text from which the LLM will extract skills
    source_url VARCHAR(255),
    posted_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table to store all scholarship postings
CREATE TABLE Scholarships (
    scholarship_id SERIAL PRIMARY KEY,
    scholarship_name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    -- JSONB allows for flexible eligibility criteria
    eligibility_criteria JSONB, -- e.g., {"max_income_pa": 600000, "min_grades": "85%", "degree": "B.Sc"}
    amount NUMERIC(12, 2),
    source_url VARCHAR(255),
    deadline_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table to store student documents
CREATE TABLE Documents (
    document_id SERIAL PRIMARY KEY,
    student_id INT REFERENCES Students(student_id) ON DELETE CASCADE,
    document_type VARCHAR(50) NOT NULL, -- e.g., 'Aadhaar Card', '12th Marksheet', 'B.Tech Certificate'
    submission_info TEXT NOT NULL, -- Could be a URL to an image or an application number
    verification_status VARCHAR(20) NOT NULL DEFAULT 'Pending', -- Pending, Verified, Rejected
    digital_signature TEXT, -- To be filled in upon verification
    -- Storing the extracted and verified data from the document as JSONB
    verified_data JSONB, -- e.g., {"cgpa": 8.8, "degree": "B.Tech", "name": "...", "dob": "..."}
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    verified_at TIMESTAMP WITH TIME ZONE
);

-- Table for master list of skills
CREATE TABLE Skills (
    skill_id SERIAL PRIMARY KEY,
    skill_name VARCHAR(100) UNIQUE NOT NULL
);

-- Junction table to link students with their skills
CREATE TABLE Student_Skills (
    student_id INT REFERENCES Students(student_id) ON DELETE CASCADE,
    skill_id INT REFERENCES Skills(skill_id) ON DELETE CASCADE,
    PRIMARY KEY (student_id, skill_id)
);

-- Add some indexes for faster querying on foreign keys and commonly searched fields
CREATE INDEX idx_docs_student_id ON Documents(student_id);
CREATE INDEX idx_student_skills_student_id ON Student_Skills(student_id);
