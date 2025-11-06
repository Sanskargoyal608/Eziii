import React, { useState, useEffect } from 'react';
import { apiFetch } from '../api'; // Import our new apiFetch function
import styles from '../App.module.css'; // Re-use the same styles

const AdminHome = () => {
    const [dashboardData, setDashboardData] = useState({ students: [], documents: [] });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Fetch the dashboard data from our new backend endpoint
    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                const response = await apiFetch('/portal/dashboard/');
                if (!response.ok) {
                    throw new Error('Failed to fetch admin dashboard data');
                }
                const data = await response.json();
                setDashboardData(data);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    // Handle the "Summary" button click
    const handleGetSummary = async (studentId) => {
        alert(`Requesting summary for student ${studentId}...`);
        try {
            const response = await apiFetch(`/portal/summary/${studentId}/`);
            if (!response.ok) {
                throw new Error('Failed to fetch summary');
            }
            const data = await response.json();
            // Show the summary in a simple alert for now
            alert(`--- Summary for Student ${studentId} ---\n\n${data.summary_text}`);
        } catch (err) {
            alert(`Error: ${err.message}`);
        }
    };

    const getStatusClass = (status) => {
        if (status === 'Verified') return styles.verified;
        if (status === 'Pending') return styles.pending;
        if (status === 'Rejected') return styles.rejected;
        return '';
    };

    if (loading) return <p className={styles.infoText}>Loading admin dashboard...</p>;
    if (error) return <p className={styles.errorText}>Error: {error}</p>;

    return (
        <div>
            <h1 className={styles.mainTitle}>Admin Dashboard</h1>
            
            {/* Students Section */}
            <h2 className={styles.formTitle}>All Students ({dashboardData.students.length})</h2>
            <div className={styles.grid}>
                {dashboardData.students.map(student => (
                    <div key={student.student_id} className={styles.card}>
                        <h3 className={styles.cardTitle}>{student.full_name}</h3>
                        <p className={styles.cardInfo}>ID: {student.student_id}</p>
                        <p className={styles.cardInfo}>Email: {student.email}</p>
                        <button 
                            className={styles.authButton} 
                            onClick={() => handleGetSummary(student.student_id)}
                            style={{width: 'auto', padding: '0.5rem 1rem'}}
                        >
                            Get Summary
                        </button>
                    </div>
                ))}
            </div>

            <hr className={styles.divider} />

            {/* Documents Section */}
            <h2 className={styles.formTitle}>All Documents ({dashboardData.documents.length})</h2>
            <div className={styles.grid}>
                {dashboardData.documents.map(doc => (
                    <div key={doc.document_id} className={styles.card}>
                        <div className={styles.cardHeader}>
                            <h3 className={styles.cardTitle}>{doc.document_type}</h3>
                        </div>
                        <p className={styles.cardInfo}>Student ID: {doc.student}</p>
                        <p className={styles.cardInfo}>Issue Date: {doc.issue_date || 'N/A'}</p>
                        <div className={styles.statusBadge}>
                           <span className={getStatusClass(doc.verification_status)}>{doc.verification_status}</span>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default AdminHome;