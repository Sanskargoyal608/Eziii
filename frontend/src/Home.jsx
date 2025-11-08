import React, { useState, useEffect } from 'react';
import styles from './Home.module.css'; 

export const Home = () => {
    const [documents, setDocuments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchDocuments = async () => {
            try {
                const response = await fetch('http://192.168.52.110:8000/api/documents/');
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                const data = await response.json();
                setDocuments(data);
            } catch (error) {
                console.error("Error fetching documents:", error);
                setError(error.message);
            } finally {
                setLoading(false);
            }
        };
        fetchDocuments();
    }, []);

    const getStatusClass = (status) => {
        switch (status?.toLowerCase()) {
            case 'verified': return styles.verified;
            case 'pending': return styles.pending;
            case 'rejected': return styles.rejected;
            default: return '';
        }
    };

    return (
        <div className={styles.listContainer}>
            <h2 className={styles.listTitle}>My Documents</h2>
            {loading && <p>Loading documents...</p>}
            {error && <p className={styles.errorText}>Failed to load documents: {error}</p>}
            {!loading && !error && documents.length === 0 && (
                <p className={styles.emptyMessage}>No documents found. Your database might be empty.</p>
            )}
            {!loading && !error && documents.map(doc => (
                <div key={doc.document_id} className={styles.card}>
                    <div className={styles.cardHeader}>
                        <h3 className={styles.cardTitle}>{doc.document_type}</h3>
                        <p className={`${styles.statusBadge} ${getStatusClass(doc.verification_status)}`}>
                            {doc.verification_status}
                        </p>
                    </div>
                    <div className={styles.cardFooter}>
                        <span>Issued on: {new Date(doc.issue_date).toLocaleDateString()}</span>
                    </div>
                </div>
            ))}
        </div>
    );
};