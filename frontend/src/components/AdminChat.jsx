import React, { useState, useEffect } from 'react';
import { apiFetch } from '../api'; // Import our apiFetch function
import styles from '../App.module.css'; // Re-use the same styles

// Re-using the SendIcon
const SendIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className={styles.icon} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" /></svg>
);

const AdminChat = () => {
    const [messages, setMessages] = useState([
        { id: 1, text: "Welcome, Admin. Select a student context and ask a query.", sender: 'bot' }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    
    // --- NEW: State for student list and selection ---
    const [students, setStudents] = useState([]);
    const [selectedStudentId, setSelectedStudentId] = useState('all'); // Default to 'all'

    // --- NEW: Fetch all students for the dropdown ---
    useEffect(() => {
        const fetchStudents = async () => {
            try {
                // We can re-use the dashboard endpoint to get the student list
                const response = await apiFetch('/portal/dashboard/');
                if (!response.ok) {
                    throw new Error('Failed to fetch students');
                }
                const data = await response.json();
                setStudents(data.students);
            } catch (err) {
                console.error("Error fetching students for chat:", err);
            }
        };
        fetchStudents();
    }, []); // Runs once on component mount

    const handleSend = async () => {
        if (input.trim() === '' || isLoading) return;

        const userMessage = { id: Date.now(), text: input, sender: 'user' };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        try {
            // --- MODIFIED: Send to the new admin chat endpoint ---
            const response = await apiFetch('/portal/chat/', {
                method: 'POST',
                body: JSON.stringify({ 
                    query: input,
                    student_id: selectedStudentId // --- NEW: Send the selected student ID
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
            {/* --- NEW: Student Selector Dropdown --- */}
            <div className={styles.inputGroup} style={{ padding: '1rem', borderBottom: `1px solid ${styles.borderColor}` }}>
                <label htmlFor="studentSelect" style={{color: 'white', marginBottom: '0.5rem'}}>Query Context:</label>
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
            {/* --- End of new section --- */}
            
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