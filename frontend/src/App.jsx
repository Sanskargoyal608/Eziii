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


// --- FEDERATED CHAT COMPONENT ---
const FederatedChat = () => {
    const [messages, setMessages] = useState([
        { id: 1, text: "Welcome! Ask me to find eligible jobs or scholarships based on your verified documents.", sender: 'bot' }
    ]);
    const [input, setInput] = useState('');

    const handleSend = async () => {
        if (input.trim() === '') return;

        // 1. Add user's message immediately
        const userMessage = { id: Date.now(), text: input, sender: 'user' };
        // 2. Add a "thinking" message from the bot
        const thinkingMessage = { id: Date.now() + 1, text: "Query received. Decomposing and fetching from sources...", sender: 'bot' };
        
        setMessages(prev => [...prev, userMessage, thinkingMessage]);
        setInput('');

        try {
            // 3. Send the query to the federated engine endpoint on your partner's machine
            const response = await fetch('http://192.168.52.110:8000/api/federated-query/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: input }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();
            
            // 4. Replace "thinking..." with the actual response
            const botResponse = { id: Date.now() + 2, text: JSON.stringify(data, null, 2), sender: 'bot' };
            setMessages(prev => [...prev.slice(0, -1), botResponse]);

        } catch (error) {
            console.error("Error during federated query:", error);
            const errorMessage = { id: Date.now() + 2, text: `Error: Could not connect to the federated engine. ${error.message}`, sender: 'bot' };
            setMessages(prev => [...prev.slice(0, -1), errorMessage]);
        }
    };

    return (
        <div className={styles.chatContainer}>
            <div className={styles.messageList}>
                {messages.map((msg) => (
                    <div key={msg.id} className={`${styles.message} ${msg.sender === 'user' ? styles.userMessage : styles.botMessage}`}>
                        {/* Use <pre> for formatted JSON */}
                        {msg.sender === 'bot' && msg.text.startsWith('{') ? 
                            <pre>{msg.text}</pre> : msg.text}
                    </div>
                ))}
            </div>
            <div className={styles.inputArea}>
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                    placeholder="Type your query here..."
                    className={styles.textInput}
                />
                <button onClick={handleSend} className={styles.sendButton}>
                    <SendIcon />
                </button>
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
        // Fetch documents from your Django API
        fetch('http://192.168.52.110:8000/api/documents/')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                setDocuments(data);
                setLoading(false);
            })
            .catch(error => {
                console.error("Error fetching documents:", error);
                setError("Failed to load documents. Make sure your Django server is running.");
                setLoading(false);
            });
    }, []); // The empty array means this effect runs once when the component mounts

    return (
        <div className={styles.pageContent}>
            <h1>My Documents</h1>
            {loading && <p>Loading documents...</p>}
            {error && <p className={styles.errorText}>{error}</p>}
            <div className={styles.documentGrid}>
                {documents.map(doc => (
                    <div key={doc.document_id} className={styles.documentCard}>
                        <h3 className={styles.documentTitle}>{doc.document_type}</h3>
                        <p className={`${styles.status} ${styles[doc.verification_status.toLowerCase()]}`}>
                            {doc.verification_status}
                        </p>
                        <p className={styles.issueDate}>Issued: {new Date(doc.issue_date).toLocaleDateString()}</p>
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
                        <h2 className={styles.sidebarTitle}>Dashboard</h2>
                    </div>
                    <nav className={styles.nav}>
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
