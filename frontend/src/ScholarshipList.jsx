import React, { useState, useEffect } from 'react';
import styles from './ScholarshipList.module.css'; // Using a separate CSS module

export const ScholarshipList = () => {
  const [scholarships, setScholarships] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchScholarships = async () => {
      try {
        const response = await fetch('http://192.168.52.109:5000/api/scholarships');
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const data = await response.json();
        setScholarships(data);
      } catch (error) {
        setError('Failed to fetch scholarships. Make sure the Flask API server is running.');
        console.error("Error fetching scholarships:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchScholarships();
  }, []);

  return (
    <div className={styles.listContainer}>
      <h2 className={styles.listTitle}>Available Scholarships</h2>
      {loading && <p>Loading scholarships...</p>}
      {error && <p className={styles.errorText}>{error}</p>}
      {!loading && !error && scholarships.map((scholarship) => (
        <div key={scholarship.scholarship_id} className={styles.card}>
          <div className={styles.cardHeader}>
            <h3 className={styles.cardTitle}>{scholarship.name}</h3>
            <span className={styles.amount}>${scholarship.amount.toLocaleString()}</span>
          </div>
          <p className={styles.cardSubtitle}>{scholarship.provider}</p>
          <p className={styles.cardDescription}>{scholarship.description}</p>
          <div className={styles.cardFooter}>
            <span>Apply by: {scholarship.deadline}</span>
            <a href={scholarship.url} target="_blank" rel="noopener noreferrer" className={styles.applyButton}>Learn More</a>
          </div>
        </div>
      ))}
    </div>
  );
};