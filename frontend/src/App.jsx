import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import styles from './App.module.css';

// --- ICONS (No Change) ---
const HomeIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className={styles.icon} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" /></svg>
);
const ChatIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className={styles.icon} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" /></svg>
);
const SendIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className={styles.icon} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" /></svg>
);


// --- FEDERATED CHAT COMPONENT (No Change) ---
const FederatedChat = () => {
    const [messages, setMessages] = useState([
        { id: 1, text: "Welcome! Ask me to find eligible jobs or scholarships based on your verified documents.", sender: 'bot' }
    ]);
    const [input, setInput] = useState('');

    const handleSend = () => {
        if (input.trim() === '') return;
        const newMessages = [...messages, { id: Date.now(), text: input, sender: 'user' }];
        setMessages(newMessages);
        setInput('');
        setTimeout(() => {
            setMessages(prev => [...prev, { id: Date.now() + 1, text: "Query received. Decomposing and fetching from sources...", sender: 'bot' }]);
        }, 1000);
    };

    return (
        <div className={styles.chatContainer}>
            <div className={styles.messageList}>
                {messages.map((msg) => (
                    <div key={msg.id} className={`${styles.message} ${msg.sender === 'user' ? styles.userMessage : styles.botMessage}`}>
                        {msg.text}
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


// --- HOME COMPONENT (UPDATED) ---
const Home = () => {
    const [documents, setDocuments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        // Fetch documents from your Django API
        fetch('http://127.0.0.1:8000/api/documents/')
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


// --- APP COMPONENT (No Change) ---
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
                        <NavLink to="/chat" className={({ isActive }) => isActive ? `${styles.navLink} ${styles.activeLink}` : styles.navLink}>
                            <ChatIcon />
                            <span>Federated Chat</span>
                        </NavLink>
                    </nav>
                </aside>
                <main className={styles.mainContent}>
                    <Routes>
                        <Route path="/" element={<Home />} />
                        <Route path="/chat" element={<FederatedChat />} />
                    </Routes>
                </main>
            </div>
        </Router>
    );
}

export default App;

