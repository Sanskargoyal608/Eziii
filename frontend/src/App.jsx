import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import styles from './App.module.css';
import { JobList } from './JobList';
import { ScholarshipList } from './ScholarshipList';

// --- ICONS ---
const HomeIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className={styles.icon} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" /></svg>
);
const ChatIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className={styles.icon} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" /></svg>
);
const SendIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className={styles.icon} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" /></svg>
);
const BriefcaseIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className={styles.icon} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
);
const AcademicCapIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className={styles.icon} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path d="M12 14l9-5-9-5-9 5 9 5z" /><path d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-5.998 12.078 12.078 0 01.665-6.479L12 14z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l9-5-9-5-9 5 9 5zm0 0l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-5.998 12.078 12.078 0 01.665-6.479L12 14zm-4 6v-7.5l4-2.222 4 2.222V20M1 12v7a2 2 0 002 2h18a2 2 0 002-2v-7" /></svg>
);



// --- FEDERATED CHAT COMPONENT --

const FederatedChat = () => {
    const [messages, setMessages] = useState([
        { id: 1, text: "Welcome! Select a student and ask a query.", sender: 'bot' }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    
    // --- NEW: State for students and selected student ---
    const [students, setStudents] = useState([]);
    const [selectedStudentId, setSelectedStudentId] = useState('');

    // --- NEW: Fetch the list of students when the component loads ---
    useEffect(() => {
        const fetchStudents = async () => {
            try {
                const response = await fetch('http://127.0.0.1:8000/api/students/');
                if (!response.ok) {
                    throw new Error('Failed to fetch students');
                }
                const data = await response.json();
                setStudents(data);
                if (data.length > 0) {
                    setSelectedStudentId(data[0].student_id); // Select the first student by default
                }
            } catch (error) {
                console.error("Error fetching students:", error);
                // Optionally, add an error message to the chat
                setMessages(prev => [...prev, {id: Date.now(), text: "Error: Could not load student list.", sender: 'bot'}]);
            }
        };
        fetchStudents();
    }, []);

    const handleSend = async () => {
        if (input.trim() === '' || isLoading) return;


        const userMessage = { id: Date.now(), text: input, sender: 'user' };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        try {
            // Make a REAL API call to your Django federated query endpoint
            const response = await fetch('http://127.0.0.1:8000/api/federated-query/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },

                // --- UPDATED: Send the selected student ID along with the query ---
                body: JSON.stringify({ 
                    query: input,
                    student_id: selectedStudentId 
                }),
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            

            const botResponseText = JSON.stringify(data, null, 2);

            const botMessage = { id: Date.now() + 1, text: botResponseText, sender: 'bot' };
            setMessages(prev => [...prev, botMessage]);

        } catch (error) {
            console.error("Error during federated query:", error);
            const errorMessage = { id: Date.now() + 1, text: `Error: ${error.message}`, sender: 'bot' };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className={styles.chatContainer}>
            <div className={styles.messageList}>
                {messages.map((msg) => (
                    <div key={msg.id} className={`${styles.message} ${msg.sender === 'user' ? styles.userMessage : styles.botMessage}`}>

                        <pre className={styles.preformatted}>{msg.text}</pre>
                    </div>
                ))}
            </div>
            {/* --- NEW: Student selection dropdown --- */}
            <div className={styles.chatControls}>
                <select 
                    value={selectedStudentId} 
                    onChange={(e) => setSelectedStudentId(e.target.value)}
                    className={styles.studentSelector}
                >
                    <option value="" disabled>Select a Student</option>
                    {students.map(student => (
                        <option key={student.student_id} value={student.student_id}>
                            {student.full_name}
                        </option>
                    ))}
                </select>
                <div className={styles.inputArea}>
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                        placeholder="Type your query here..."
                        className={styles.textInput}
                    />
                    <button onClick={handleSend} className={styles.sendButton} disabled={isLoading}>
                        <SendIcon />
                    </button>
                </div>
            </div>
        </div>
    );
};



// --- HOME COMPONENT ---
const Home = () => {
    const [documents, setDocuments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchDocuments = async () => {
            try {
                const response = await fetch('http://127.0.0.1:8000/api/documents/');
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                const data = await response.json();
                console.log("API Response:", data);
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
        switch (status) {
            case 'Verified': return styles.verified;
            case 'Pending': return styles.pending;
            case 'Rejected': return styles.rejected;
            default: return '';
        }
    };

    return (
        <div className={styles.pageContent}>
            <h1 className={styles.pageTitle}>My Documents</h1>
            {loading && <p className={styles.loadingText}>Loading documents...</p>}
            {error && <p className={styles.errorText}>Failed to load documents: {error}</p>}
            {!loading && !error && documents.length === 0 && (
                <p className={styles.emptyMessage}>No documents found. Your database might be empty.</p>
            )}
            <div className={styles.documentGrid}>
                {documents.map(doc => (
                    <div key={doc.document_id} className={styles.documentCard}>
                        <h3 className={styles.cardTitle}>{doc.document_type}</h3>
                        <p className={`${styles.statusBadge} ${getStatusClass(doc.verification_status)}`}>
                            {doc.verification_status}
                        </p>
                        <p className={styles.cardDate}>Issued: {new Date(doc.issue_date).toLocaleDateString()}</p>
                    </div>
                ))}
            </div>
        </div>
    );
};


// --- APP COMPONENT ---
function App() {
    return (
        <Router>
            <div className={styles.appContainer}>
                <aside className={styles.sidebar}>
                    <div className={styles.sidebarHeader}>
                        <h2 className={styles.sidebarTitle}>EduVerify</h2>
                    </div>
                    <nav className={styles.sidebarNav}>
                        <NavLink to="/" className={({ isActive }) => isActive ? `${styles.navLink} ${styles.activeLink}` : styles.navLink}>
                            <HomeIcon />
                            <span>Home</span>
                        </NavLink>
                        <NavLink to="/jobs" className={({ isActive }) => isActive ? `${styles.navLink} ${styles.activeLink}` : styles.navLink}>
                            <BriefcaseIcon />
                            <span>Jobs</span>
                        </NavLink>
                        <NavLink to="/scholarships" className={({ isActive }) => isActive ? `${styles.navLink} ${styles.activeLink}` : styles.navLink}>
                            <AcademicCapIcon />
                            <span>Scholarships</span>
                        </NavLink>
                        <NavLink to="/chat" className={({ isActive }) => isActive ? `${styles.navLink} ${styles.activeLink}` : styles.navLink}>
                            <ChatIcon />
                            <span>Federated Chat</span>
                        </NavLink>
                    </nav>
                </aside>
                <main className={styles.mainContent}>
                    <Routes>
                        <Route path="/" element={<Home />} />
                        <Route path="/jobs" element={<JobList />} />
                        <Route path="/scholarships" element={<ScholarshipList />} />
                        <Route path="/chat" element={<FederatedChat />} />
                    </Routes>
                </main>
            </div>
        </Router>
    );
}

export default App;
