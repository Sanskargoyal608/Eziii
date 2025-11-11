import React, { useState, useEffect } from 'react';
import styles from './JobList.module.css';

export const JobList = () => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        // Fetch data using apiFetch
        const response = await fetch('http://192.168.52.109:5000/api/jobs');
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const data = await response.json();
        console.log("Jobs data received:", data); // Log the data
        setJobs(data);
      } catch (error) {
        setError('Failed to fetch jobs. Make sure the API server is running.');
        console.error("Error fetching jobs:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchJobs();
  }, []); // The empty array ensures this effect runs only once on mount

  return (
    <div className={styles.listContainer}>
      <h2 className={styles.listTitle}>Available Jobs</h2>
      {loading && <p>Loading jobs...</p>}
      {error && <p className={styles.errorText}>{error}</p>}
      {!loading && !error && jobs.map((job) => (
        <div key={job.job_id} className={styles.card}>
          <h3 className={styles.cardTitle}>{job.job_title}</h3>
          <p className={styles.cardLocation}>Location: {job.location ? job.location : 'N/A'}</p>
          <p className={styles.cardPostedDate}>Posted: {job.posted_date ? new Date(job.posted_date).toLocaleString() : 'N/A'}</p>
          {job.eligibility_criteria && (() => {
            try {
              const eligibility = JSON.parse(job.eligibility_criteria);
              return (
                <>
                  <p className={styles.cardExperience}>Experience: {eligibility.experience ? eligibility.experience : 'N/A'}</p>
                  <p className={styles.cardSkills}>Skills: {eligibility.skills ? eligibility.skills : 'N/A'}</p>
                  <p className={styles.cardSalary}>Salary: {eligibility.salary ? eligibility.salary : 'N/A'}</p>
                </>
              );
            } catch (e) {
              console.error("Error parsing eligibility_criteria:", e);
              return null;
            }
          })()}
          <div className={styles.cardFooter}>
            {job.source_url && (
              <a href={job.source_url} target="_blank" rel="noopener noreferrer" className={styles.applyButton}>
                View Details
              </a>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};