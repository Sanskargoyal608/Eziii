import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import styles from '../App.module.css'; // We'll re-use the styles from App.module.css

// Re-using the same icons from App.jsx
const HomeIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className={styles.icon} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" /></svg>
);
const ChatIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className={styles.icon} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" /></svg>
);


const AdminLayout = () => {
    return (
        <div className={styles.appContainer}>
            <aside className={styles.sidebar}>
                <div className={styles.sidebarHeader}>
                    <h2 className={styles.sidebarTitle}>Admin Portal</h2>
                    <p className={styles.sidebarUser}>Public Access Panel</p>
                </div>
                <nav className={styles.nav}>
                    {/* --- CORRECTION --- */}
                    <NavLink 
                        to="/portal" // CHANGED from /admin
                        end 
                        className={({ isActive }) => isActive ? `${styles.navLink} ${styles.active}` : styles.navLink}
                    >
                        <HomeIcon />
                        <span>Admin Home</span>
                    </NavLink>
                    {/* --- CORRECTION --- */}
                    <NavLink 
                        to="/portal/chat" // CHANGED from /admin/chat
                        className={({ isActive }) => isActive ? `${styles.navLink} ${styles.active}` : styles.navLink}
                    >
                        <ChatIcon />
                        <span>Admin Chat</span>
                    </NavLink>
                </nav>
                {/* ... (footer is the same) ... */}
            </aside>
            <main className={styles.mainContent}>
                <Outlet />
            </main>
        </div>
    );
};

export default AdminLayout;