// frontend/src/components/AdminChat.jsx
import React, { useState, useEffect } from 'react';
import { apiFetch } from '../api'; 
import styles from '../App.module.css'; 

const SendIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className={styles.icon} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" /></svg>
);

const AdminChat = () => {
    // 1. Initialize from localStorage
    const [messages, setMessages] = useState(() => {
        const savedMessages = localStorage.getItem('admin_chat_history');
        return savedMessages 
            ? JSON.parse(savedMessages) 
            : [{ id: 1, text: "Welcome, Admin. Select a student context and ask a query.", sender: 'bot' }];
    });

    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [students, setStudents] = useState([]);
    
    // Initialize student selection from localStorage or default to 'all'
    const [selectedStudentId, setSelectedStudentId] = useState(() => {
        return localStorage.getItem('admin_chat_context') || 'all';
    });

    // 2. Fetch students
    useEffect(() => {
        const fetchStudents = async () => {
            try {
                const response = await apiFetch('/portal/dashboard/');
                if (!response.ok) throw new Error('Failed to fetch students');
                const data = await response.json();
                setStudents(data.students);
            } catch (err) {
                console.error("Error fetching students:", err);
            }
        };
        fetchStudents();
    }, []); 

    // 3. Save messages to localStorage whenever they change
    useEffect(() => {
        localStorage.setItem('admin_chat_history', JSON.stringify(messages));
    }, [messages]);

    // 4. Save selected context to localStorage whenever it changes
    useEffect(() => {
        localStorage.setItem('admin_chat_context', selectedStudentId);
    }, [selectedStudentId]);

    const clearChat = () => {
        const resetMessage = [{ id: Date.now(), text: "Admin chat history cleared.", sender: 'bot' }];
        setMessages(resetMessage);
        localStorage.removeItem('admin_chat_history');
    };

    const handleSend = async () => {
        if (input.trim() === '' || isLoading) return;

        const userMessage = { id: Date.now(), text: input, sender: 'user' };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        try {
            const response = await apiFetch('/portal/chat/', {
                method: 'POST',
                body: JSON.stringify({ 
                    query: input,
                    student_id: selectedStudentId 
                }),
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
            console.error("Error during admin federated query:", error);
            const errorMessage = { id: Date.now() + 1, text: `Error: ${error.message}`, sender: 'bot' };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className={styles.chatContainer}>
            <div className={styles.inputGroup} style={{ padding: '1rem', borderBottom: `1px solid ${styles.borderColor}`, display:'flex', justifyContent:'space-between', alignItems:'center' }}>
                <div style={{flex: 1}}>
                    <label htmlFor="studentSelect" style={{color: 'white', marginBottom: '0.5rem', display:'block'}}>Query Context:</label>
                    <select 
                        id="studentSelect" 
                        className={styles.selectInput}
                        value={selectedStudentId}
                        onChange={(e) => setSelectedStudentId(e.target.value)}
                    >
                        <option value="all">All Students (Aggregate Queries)</option>
                        {students.map(student => (
                            <option key={student.student_id} value={student.student_id}>
                                {student.full_name} (ID: {student.student_id})
                            </option>
                        ))}
                    </select>
                </div>
                <button 
                    onClick={clearChat} 
                    style={{marginLeft: '15px', fontSize: '0.8rem', padding: '8px 12px', cursor: 'pointer', background: '#ff4d4d', color: 'white', border: 'none', borderRadius: '4px', height: 'fit-content'}}
                >
                    Clear Chat
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
                    placeholder="Type your admin query here..."
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

export default AdminChat;