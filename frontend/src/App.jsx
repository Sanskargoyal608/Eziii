import React, { useState, useEffect, createContext, useContext } from 'react';
// --- MODIFICATION: Import Admin components we WILL create ---
import { BrowserRouter as Router, Routes, Route, NavLink, Navigate, useLocation ,useNavigate } from 'react-router-dom';
import styles from './App.module.css';
import AdminLayout from './components/AdminLayout'; // We will create this
import AdminHome from './components/AdminHome';   // We will create this
import AdminChat from './components/AdminChat';   // We will create this
// --- NEW: Import the new components ---
import { JobList } from './JobList';
import { ScholarshipList } from './ScholarshipList';
// ---



// --- (Icons: HomeIcon, ChatIcon, SendIcon, LogoutIcon remain exactly the same) ---
const HomeIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className={styles.icon} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" /></svg>
);
const ChatIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className={styles.icon} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" /></svg>
);
const SendIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className={styles.icon} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" /></svg>
);
const LogoutIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className={styles.icon} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" /></svg>
);

// --- NEW: Icons for Jobs and Scholarships ---
const JobsIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className={styles.icon} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 13V6a2 2 0 00-2-2H8a2 2 0 00-2 2v7m12 0v5a2 2 0 01-2 2H8a2 2 0 01-2-2v-5m12 0h-2.586a1 1 0 00-.707.293l-1.414 1.414a1 1 0 01-1.414 0l-1.414-1.414a1 1 0 00-.707-.293H8m10 0z" /></svg>
);
const ScholarshipIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className={styles.icon} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l9-5-9-5-9 5 9 5z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l9-5-9-5-9 5 9 5zm0 0v-5.5M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14zm-4 6v-5.5m0 5.5v-5.5m0 5.5l4-2.222" /></svg>
);

import { apiFetch } from './api';



// --- (Auth Context: AuthContext, useAuth, AuthProvider remain exactly the same) ---
const AuthContext = createContext(null);

const useAuth = () => {
    return useContext(AuthContext);
};

const AuthProvider = ({ children }) => {
    // --- (This component's content is unchanged) ---
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);


    useEffect(() => {
        const token = localStorage.getItem('accessToken');
        if (token) {
            try {
                const payload = JSON.parse(atob(token.split('.')[1]));
                setUser({ 
                    student_id: payload.student_id, 
                    full_name: "Student",
                    email: "..."
                });
            } catch (e) {
                console.error("Error decoding token", e);
                localStorage.clear();
            }
        }
        setLoading(false);
    }, []);

    const login = async (email, password) => {
        const response = await apiFetch('/login/', { // Uses /api/login/
            method: 'POST',
            body: JSON.stringify({ email, password }),
        });
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Login failed');
        }
        const data = await response.json();
        localStorage.setItem('accessToken', data.access);
        localStorage.setItem('refreshToken', data.refresh);
        setUser(data.user);
    };

    const register = async (full_name, email, password) => {
        const response = await apiFetch('/register/', { // Uses /api/register/
            method: 'POST',
            body: JSON.stringify({ full_name, email, password }),
        });
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(JSON.stringify(errorData) || 'Registration failed');
        }
        const data = await response.json();
        localStorage.setItem('accessToken', data.access);
        localStorage.setItem('refreshToken', data.refresh);
        setUser({ full_name: data.user.full_name, email: data.user.email, student_id: null });
    };

    const logout = () => {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        setUser(null);
        window.location.href = '/login';
    };

    const value = { user, login, logout, register, isAuthenticated: !!user };

    if (loading) {
        return <div className={styles.loadingPage}>Loading...</div>;
    }

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};


// --- (Protected Route: ProtectedRoute remains exactly the same) ---
const ProtectedRoute = ({ children }) => {
    const { isAuthenticated } = useAuth();
    const location = useLocation();

    if (!isAuthenticated) {
        return <Navigate to="/login" state={{ from: location }} replace />;
    }
    return children;
};

// --- (Login Page: LoginPage remains exactly the same) ---
const LoginPage = () => {
    // --- (This component's content is unchanged) ---
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const { login } = useAuth();

    const navigate = useNavigate();
    const location = useLocation();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);
        try {
            await login(email, password);
            const from = location.state?.from?.pathname || '/';
            navigate(from, { replace: true });
            window.location.href = '/'; // Redirect to home
        } catch (err) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className={styles.authContainer}>
            <form className={styles.authForm} onSubmit={handleSubmit}>
                <h2 className={styles.authTitle}>Student Portal Login</h2>
                {error && <p className={styles.authError}>{error}</p>}
                <div className={styles.inputGroup}>
                    <label htmlFor="email">Email</label>
                    <input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
                </div>
                <div className={styles.inputGroup}>
                    <label htmlFor="password">Password</label>
                    <input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
                </div>
                <button type="submit" className={styles.authButton} disabled={isLoading}>
                    {isLoading ? 'Logging in...' : 'Login'}
                </button>
                <p className={styles.authLink}>
                    Don't have an account? <NavLink to="/register">Register</NavLink>
                </p>
            </form>
        </div>
    );
};

const RegisterPage = () => {
    const [fullName, setFullName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const { register } = useAuth();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);
        try {
            await register(fullName, email, password);
            window.location.href = '/'; 
        } catch (err) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className={styles.authContainer}>
            <form className={styles.authForm} onSubmit={handleSubmit}>
                <h2 className={styles.authTitle}>Create Student Account</h2>
                {error && <p className={styles.authError}>{error}</p>}
                <div className={styles.inputGroup}>
                    <label htmlFor="fullName">Full Name</label>
                    <input id="fullName" type="text" value={fullName} onChange={(e) => setFullName(e.target.value)} required />
                </div>
                <div className={styles.inputGroup}>
                    <label htmlFor="email">Email</label>
                    <input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
                </div>
                <div className={styles.inputGroup}>
                    <label htmlFor="password">Password</label>
                    <input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
                </div>
                <button type="submit" className={styles.authButton} disabled={isLoading}>
                    {isLoading ? 'Registering...' : 'Register'}
                </button>
                <p className={styles.authLink}>
                    Already have an account? <NavLink to="/login">Login</NavLink>
                </p>
            </form>
        </div>
    );
};


// --- (Federated Chat: FederatedChat remains exactly the same) ---
const FederatedChat = () => {
    // 1. Initialize state from localStorage if available
    const [messages, setMessages] = useState(() => {
        const savedMessages = localStorage.getItem('student_chat_history');
        return savedMessages 
            ? JSON.parse(savedMessages) 
            : [{ id: 1, text: "Welcome! Ask me to find jobs, scholarships, or your documents.", sender: 'bot' }];
    });
    
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    // 2. Save to localStorage whenever messages change
    useEffect(() => {
        localStorage.setItem('student_chat_history', JSON.stringify(messages));
    }, [messages]);

    // 3. Helper to clear chat
    const clearChat = () => {
        const resetMessage = [{ id: Date.now(), text: "Chat history cleared. How can I help?", sender: 'bot' }];
        setMessages(resetMessage);
        localStorage.removeItem('student_chat_history');
    };

    const handleSend = async () => {
        if (input.trim() === '' || isLoading) return;

        const userMessage = { id: Date.now(), text: input, sender: 'user' };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        try {
            const response = await apiFetch('/federated-query/', { 
                method: 'POST',
                body: JSON.stringify({ query: input }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Network response was not ok');
            }

            const data = await response.json();
            const botResponseText = data.response_text || JSON.stringify(data, null, 2);
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
            {/* Header with Clear Button */}
            <div style={{display: 'flex', justifyContent: 'flex-end', padding: '0.5rem'}}>
                <button 
                    onClick={clearChat} 
                    style={{fontSize: '0.8rem', padding: '5px 10px', cursor: 'pointer', background: '#ff4d4d', color: 'white', border: 'none', borderRadius: '4px'}}
                >
                    Clear History
                </button>
            </div>

            <div className={styles.messageList}>
                {messages.map((msg) => (
                    <div key={msg.id} className={`${styles.message} ${msg.sender === 'user' ? styles.userMessage : styles.botMessage}`}>
                        <pre className={styles.preformatted}>{msg.text}</pre>
                    </div>
                ))}
                 {isLoading && <div className={`${styles.message} ${styles.botMessage}`}><span className={styles.loading}></span></div>}
            </div>
            <div className={styles.inputArea}>
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                    placeholder="Type your query here..."
                    className={styles.textInput}
                    disabled={isLoading}
                />
                <button onClick={handleSend} className={styles.sendButton} disabled={isLoading}>
                    <SendIcon />
                </button>
            </div>
        </div>
    );
};

// --- (Document Upload: DocumentUpload remains exactly the same) ---
const DocumentUpload = ({ onUploadSuccess }) => {
    // --- (This component's content is unchanged) ---
    const [file, setFile] = useState(null);
    const [documentType, setDocumentType] = useState('Aadhar Card');
    const [error, setError] = useState('');
    const [isUploading, setIsUploading] = useState(false);

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!file) {
            setError('Please select a file to upload.');
            return;
        }
        setError('');
        setIsUploading(true);

        const formData = new FormData();
        formData.append('document_type', documentType);
        formData.append('uploaded_file', file);

        try {
            const response = await apiFetch('/documents/upload/', { // Uses /api/documents/upload/
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(JSON.stringify(errorData));
            }

            const newDocument = await response.json();
            onUploadSuccess(newDocument);
            setFile(null);
            e.target.reset();
        } catch (err) {
            setError(err.message);
        } finally {
            setIsUploading(false);
        }
    };

    return (
        <form className={styles.uploadForm} onSubmit={handleSubmit}>
            <h3 className={styles.formTitle}>Upload New Document</h3>
            {error && <p className={styles.authError}>{error}</p>}
            <div className={styles.inputGroup}>
                <label htmlFor="docType">Document Type</label>
                <select id="docType" value={documentType} onChange={(e) => setDocumentType(e.target.value)} className={styles.selectInput}>
                    <option value="Aadhar Card">Aadhar Card</option>
                    <option value="PAN Card">PAN Card</option>
                    <option value="Resume">Resume</option>
                    <option value="10th Marksheet">10th Marksheet</option>
                    <option value="12th Marksheet">12th Marksheet</option>
                    <option value="B.Tech Marksheet">B.Tech Marksheet</option>
                    <option value="Income Certificate">Income Certificate</option>
                    <option value="Other">Other</option>
                </select>
            </div>
            <div className={styles.inputGroup}>
                <label htmlFor="file">File (PDF or Image)</label>
                <input id="file" type="file" onChange={handleFileChange} accept=".pdf,.png,.jpg,.jpeg" />
            </div>
            <button type="submit" className={styles.authButton} disabled={isUploading}>
                {isUploading ? 'Uploading...' : 'Upload'}
            </button>
        </form>
    );
};

// --- (PDF Generator: PDFGenerator remains exactly the same) ---
const PDFGenerator = ({ selectedDocs, hasDocs }) => {
    // --- (This component's content is unchanged) ---
    const [isGenerating, setIsGenerating] = useState(false);

    const handleGenerate = async () => {
        const docIds = Object.keys(selectedDocs).filter(id => selectedDocs[id]);
        if (docIds.length === 0) {
            alert("Please select at least one document to include in the PDF.");
            return;
        }
        setIsGenerating(true);
        try {
            const response = await apiFetch('/generate-pdf/', { // Uses /api/generate-pdf/
                method: 'POST',
                body: JSON.stringify({ document_ids: docIds.map(Number) }),
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'PDF generation failed');
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = "EduVerify_Documents.pdf";
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);

        } catch (err) {
            alert(`Error: ${err.message}`);
        } finally {
            setIsGenerating(false);
        }
    };

    if (!hasDocs) return null;

    return (
        <div className={styles.pdfGenerator}>
            <button className={styles.authButton} onClick={handleGenerate} disabled={isGenerating}>
                {isGenerating ? 'Generating...' : 'Generate PDF for Selected'}
            </button>
        </div>
    );
};


// --- (Home Component: Home remains exactly the same) ---
const Home = () => {
    // --- (This component's content is unchanged) ---
    const [documents, setDocuments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [selectedDocs, setSelectedDocs] = useState({});

    const fetchDocuments = async () => {
        setLoading(true);
        try {
            const response = await apiFetch('/documents/'); // Uses /api/documents/
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to fetch documents');
            }
            const data = await response.json();
            setDocuments(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchDocuments();
    }, []);

    const handleUploadSuccess = (newDocument) => {
        setDocuments(prevDocs => [newDocument, ...prevDocs]);
    };

    const handleDocSelect = (docId) => {
        setSelectedDocs(prev => ({
            ...prev,
            [docId]: !prev[docId]
        }));
    };

    const getStatusClass = (status) => {
        if (status === 'Verified') return styles.verified;
        if (status === 'Pending') return styles.pending;
        if (status === 'Rejected') return styles.rejected;
        return '';
    };

    return (
        <div>
            <h1 className={styles.mainTitle}>My Documents</h1>
            <DocumentUpload onUploadSuccess={handleUploadSuccess} />
            <hr className={styles.divider} />
            <PDFGenerator selectedDocs={selectedDocs} hasDocs={documents.length > 0} />
            
            {loading && <p className={styles.infoText}>Loading documents...</p>}
            {error && <p className={styles.errorText}>Error: {error}</p>}
            
            {!loading && !error && documents.length === 0 && (
                <p className={styles.infoText}>No documents found. Try uploading one!</p>
            )}

            <div className={styles.grid}>
                {documents.map(doc => (
                    <div key={doc.document_id} className={`${styles.card} ${selectedDocs[doc.document_id] ? styles.cardSelected : ''}`}>
                        <div className={styles.cardHeader}>
                             <input 
                                type="checkbox"
                                checked={!!selectedDocs[doc.document_id]}
                                onChange={() => handleDocSelect(doc.document_id)}
                            />
                            <h3 className={styles.cardTitle}>{doc.document_type}</h3>
                        </div>
                        <p className={styles.cardInfo}>Issue Date: {doc.issue_date || 'N/A'}</p>
                        <div className={styles.statusBadge}>
                           <span className={getStatusClass(doc.verification_status)}>{doc.verification_status}</span>
                        </div>
                        {doc.extracted_text && (
                            <details className={styles.cardDetails}>
                                <summary>View Extracted Text</summary>
                                <pre>{doc.extracted_text.substring(0, 200)}...</pre>
                            </details>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
};


// --- (App Layout: AppLayout remains exactly the same) ---
// This is the sidebar and main content for the LOGGED-IN USER
const AppLayout = () => {
    // --- (This component's content is unchanged) ---
    const { user, logout } = useAuth();
    
    return (
        <div className={styles.appContainer}>
            <aside className={styles.sidebar}>
                <div className={styles.sidebarHeader}>
                    <h2 className={styles.sidebarTitle}>EduVerify</h2>
                    {user && <p className={styles.sidebarUser}>Welcome, {user.full_name}</p>}
                </div>
                <nav className={styles.nav}>
                    <NavLink to="/" className={({ isActive }) => isActive ? `${styles.navLink} ${styles.active}` : styles.navLink}>
                        <HomeIcon />
                        <span>Home</span>
                    </NavLink>
                    <NavLink to="/chat" className={({ isActive }) => isActive ? `${styles.navLink} ${styles.active}` : styles.navLink}>
                        <ChatIcon />
                        <span>Federated Chat</span>
                    </NavLink>
                    {/* --- NEW Link 3: Jobs --- */}
                    <NavLink to="/jobs" className={({ isActive }) => isActive ? `${styles.navLink} ${styles.active}` : styles.navLink}>
                        <JobsIcon />
                        <span>Jobs</span>
                    </NavLink>

                    {/* --- NEW Link 4: Scholarships --- */}
                    <NavLink to="/scholarships" className={({ isActive }) => isActive ? `${styles.navLink} ${styles.active}` : styles.navLink}>
                        <ScholarshipIcon />
                        <span>Scholarships</span>
                    </NavLink>


                </nav>
                <div className={styles.sidebarFooter}>
                    <button onClick={logout} className={`${styles.navLink} ${styles.logoutButton}`}>
                        <LogoutIcon />
                        <span>Logout</span>
                    </button>
                </div>
            </aside>
            <main className={styles.mainContent}>
                <Routes>
                    <Route path="/" element={<Home />} />
                    <Route path="/chat" element={<FederatedChat />} />
                    <Route path="*" element={<Navigate to="/" replace />} />
                    <Route path="/jobs" element={<JobList />} />
                    <Route path="/scholarships" element={<ScholarshipList />} />
                </Routes>
            </main>
        </div>
    );
};


// --- *** NEW: Main App Component (Top-Level Router) *** ---
// This is the component that has been refactored.
const App = () => (
    <AuthProvider>
        <Router>
            <Routes>
                {/* === ADMIN PORTAL (PUBLIC) === */}
                <Route path="/portal" element={<AdminLayout />}>
                    
                    {/* --- THIS IS THE FIX --- */}
                    {/* Redirect /portal to /portal/dashboard */}
                    <Route index element={<Navigate to="/portal/dashboard" replace />} /> 
                    <Route path="dashboard" element={<AdminHome />} /> 
                    <Route path="chat" element={<AdminChat />} />
                    <Route path="jobs" element={<JobList />} />
                    <Route path="scholarships" element={<ScholarshipList />} />

                </Route>

                {/* === AUTH PAGES (PUBLIC) === */}
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />

                {/* === USER PORTAL (PROTECTED) === */}
                {/* All other paths "/*" are protected */}
                <Route path="/*" element={
                    <ProtectedRoute>
                        <AppLayout />
                    </ProtectedRoute>
                } />
            </Routes>
        </Router>
    </AuthProvider>
);

export default App;