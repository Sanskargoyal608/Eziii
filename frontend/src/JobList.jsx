import React, { useState, useEffect } from 'react';
import styles from './JobList.module.css';
import { apiFetch } from './api';

export const JobList = () => {
    const [jobs, setJobs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchRecommendedJobs = async () => {
            try {
                // CHANGED: Now hits your Django backend, not the Partner API directly
                const response = await apiFetch('/jobs/recommended/'); 
                
                if (!response.ok) {
                    throw new Error('Failed to fetch recommendations');
                }
                const data = await response.json();
                setJobs(data);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchRecommendedJobs();
    }, []);

    if (loading) return <div className={styles.loading}>Finding best matches for you...</div>;
    if (error) return <div className={styles.error}>Error: {error}</div>;

    return (
        <div className={styles.container}>
            <h2>Recommended Jobs for You</h2>
            {jobs.length === 0 ? (
                <p>No matching jobs found for your profile yet.</p>
            ) : (
                <div className={styles.grid}>
                    {jobs.map((job, index) => (
                        <div key={index} className={styles.card}>
                            <h3>{job.job_title}</h3>
                            {/* Display the AI's match reason */}
                            <p className={styles.matchBadge}>✨ {job.match_reason}</p>
                            <p>{job.job_description.substring(0, 100)}...</p>
                            <a href={job.source_url} target="_blank" rel="noreferrer">Apply Now</a>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};