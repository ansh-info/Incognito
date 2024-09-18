import React, { useState, useEffect } from 'react';
import './App.css';
import Login from '../Login/Login';
import QuestionsListPage from '../QuestionsListPage/QuestionsListPage';
import QuestionPage from '../QuestionPage/QuestionPage';
import AdminDashboard from '../AdminDashboard/AdminDashboard';

function App() {
    const [user, setUser] = useState(null);
    const [selectedQuestionId, setSelectedQuestionId] = useState(null);
    const [adminRedirect, setAdminRedirect] = useState(false);

    useEffect(() => {
        // Retrieve user data from local storage when the component mounts
        const storedUser = localStorage.getItem('user');
        if (storedUser) {
            try {
                const parsedUser = JSON.parse(storedUser);
                if (parsedUser) {
                    setUser(parsedUser);
                    if (parsedUser.is_admin) {
                        setAdminRedirect(parsedUser.adminRedirect || false);
                    }
                }
            } catch (error) {
                console.error('Failed to parse user data from local storage:', error);
                localStorage.removeItem('user'); // Clear corrupted user data from local storage
            }
        }
    }, []);

    const handleSetUser = (userData) => {
        if (userData) {
            setUser(userData);
            // Save user data to local storage
            localStorage.setItem('user', JSON.stringify(userData));
            if (userData.is_admin && userData.adminRedirect) {
                setAdminRedirect(true);
            }
        } else {
            setUser(null);
            setAdminRedirect(false);
            localStorage.removeItem('user');
        }
    };

    const handleLogout = () => {
        handleSetUser(null);
    };

    const handleSwitchToDashboard = () => {
        setAdminRedirect(true);
    };

    if (!user) {
        return <Login setUser={handleSetUser} />;
    }

    if (adminRedirect) {
        return <AdminDashboard setUser={handleSetUser} setAdminRedirect={setAdminRedirect} />;
    }

    return (
        <div className="App">
            <header className="App-header">
                <div className="header-bar">
                    <h1 className="app-title">Doodle</h1>
                    <div className="header-buttons">
                        <button onClick={handleLogout} className="logout-btn">
                            Logout
                        </button>
                        {user.is_admin === 1 && (
                            <button onClick={handleSwitchToDashboard} className="dashboard-btn">
                                Go to Admin Dashboard
                            </button>
                        )}
                    </div>
                </div>
                {selectedQuestionId ? (
                    <QuestionPage
                        selectedQuestionId={selectedQuestionId}
                        setSelectedQuestion={setSelectedQuestionId}
                        user={user}
                    />
                ) : (
                    <QuestionsListPage
                        setSelectedQuestion={setSelectedQuestionId}
                        user={user}
                    />
                )}
            </header>
        </div>
    );
}

export default App;
