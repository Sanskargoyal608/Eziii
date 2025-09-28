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
        const response = await fetch('http://localhost:5000/api/jobs');
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
      <h2 className={styles.listTitle}>Available Government Jobs</h2>
      {loading && <p>Loading jobs...</p>}
      {error && <p className={styles.errorText}>{error}</p>}
      {!loading && !error && jobs.map((job) => (
        <div key={job.job_id} className={styles.card}>
          <h3 className={styles.cardTitle}>{job.title}</h3>
          <p className={styles.cardSubtitle}>{job.department} - {job.location}</p>
          <p className={styles.cardDescription}>{job.description}</p>
          <div className={styles.cardFooter}>
            <span>Closes on: {job.closing_date}</span>
            <a href={job.url} target="_blank" rel="noopener noreferrer" className={styles.applyButton}>View Details</a>
          </div>
        </div>
      ))}
    </div>
  );
};