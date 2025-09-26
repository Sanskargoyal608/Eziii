-- This query finds all government jobs and scholarships a specific student is eligible for
-- based on their verified academic and income documents.

-- We use Common Table Expressions (CTEs) to logically separate the steps.

WITH VerifiedStudentData AS (
    -- Step 1: Find all 'Verified' documents for a specific student (e.g., student_id = 15)
    -- and extract their verified degree, percentage, and income into separate columns.
    SELECT
        s.student_id,
        s.full_name,
        s.email,
        -- Extract the verified degree from any verified certificate or marksheet.
        -- We use MAX() because a student might have multiple such documents, but the degree should be the same.
        MAX(d.verified_data ->> 'degree') AS verified_degree,
        -- Extract and cast the verified percentage to a numeric type for comparison.
        MAX((d.verified_data ->> 'percentage')::numeric) AS verified_percentage,
        -- Extract and cast the verified income.
        MAX((d.verified_data ->> 'income_pa')::numeric) AS verified_income
    FROM
        students s
    JOIN
        documents d ON s.student_id = d.student_id
    WHERE
        s.student_id = 15 -- <-- CHANGE THIS ID TO TEST DIFFERENT STUDENTS
        AND d.verification_status = 'Verified'
        AND d.verified_data IS NOT NULL
    GROUP BY
        s.student_id, s.full_name, s.email
),
EligibleJobs AS (
    -- Step 2: Find all government jobs where the student's verified data meets the job's eligibility criteria.
    SELECT
        v.student_id,
        gj.job_id,
        gj.job_title,
        gj.eligibility_criteria ->> 'degree' AS required_degree,
        (gj.eligibility_criteria ->> 'min_cgpa')::numeric * 10 AS required_percentage_equivalent -- Assuming CGPA * 10 = Percentage
    FROM
        govt_jobs gj,
        VerifiedStudentData v
    WHERE
        -- Match degree (or if job takes 'Any Graduate')
        (v.verified_degree = gj.eligibility_criteria ->> 'degree' OR gj.eligibility_criteria ->> 'degree' = 'Any Graduate')
        -- Check if student's percentage is sufficient
        AND v.verified_percentage >= ((gj.eligibility_criteria ->> 'min_cgpa')::numeric * 10)
),
EligibleScholarships AS (
    -- Step 3: Find all scholarships where the student's verified data meets the scholarship's eligibility criteria.
    SELECT
        v.student_id,
        s.scholarship_id,
        s.scholarship_name,
        (s.eligibility_criteria ->> 'max_income_pa')::numeric AS max_income,
        (s.eligibility_criteria ->> 'min_percentage')::numeric AS min_percentage
    FROM
        scholarships s,
        VerifiedStudentData v
    WHERE
        -- Check if student's income is low enough
        v.verified_income <= (s.eligibility_criteria ->> 'max_income_pa')::numeric
        -- Check if student's percentage is high enough
        AND v.verified_percentage >= (s.eligibility_criteria ->> 'min_percentage')::numeric
)
-- Final Step: Combine all the results to show a complete profile for the student.
SELECT
    vsd.full_name,
    vsd.email,
    vsd.verified_degree,
    vsd.verified_percentage,
    vsd.verified_income,
    ej.job_title AS eligible_job_title,
    es.scholarship_name AS eligible_scholarship_name
FROM
    VerifiedStudentData vsd
LEFT JOIN
    EligibleJobs ej ON vsd.student_id = ej.student_id
LEFT JOIN
    EligibleScholarships es ON vsd.student_id = es.student_id;
