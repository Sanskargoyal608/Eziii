import React, { useState, useEffect } from 'react';
import styles from './JobList.module.css';

export const JobList = () => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        // Fetch data from your Flask API
        const response = await fetch('http://192.168.52.109:5000/api/jobs');
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const data = await response.json();
        setJobs(data);
      } catch (error) {
        setError('Failed to fetch jobs. Make sure the Flask API server is running.');
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
          <p className={styles.cardCompany}>Company: {job.company_name ? job.company_name : 'N/A'}</p>
          <p className={styles.cardLocation}>Location: {job.location ? job.location : 'N/A'}</p>
          <p className={styles.cardPostedDate}>Posted: {job.posted_date ? job.posted_date : 'N/A'}</p>
          <p className={styles.cardDescription}>
            {job.job_description ? job.job_description : 'No description available'}
          </p>
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