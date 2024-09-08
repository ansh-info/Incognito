import React, { useState } from 'react';
import axios from 'axios';
import './Login.css';

function Login({ setUser }) {
    const [login, setLogin] = useState('');
    const [password, setPassword] = useState('');
    const [passwordVisible, setPasswordVisible] = useState(false);
    const [isRegistering, setIsRegistering] = useState(false);
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [isAdmin, setIsAdmin] = useState(false);
    const [adminCode, setAdminCode] = useState('');
    const [showAdminCodeInput, setShowAdminCodeInput] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const endpoint = isRegistering ? '/register' : '/login';
            const payload = isRegistering 
                ? { username, email, password, is_admin: isAdmin, admin_code: adminCode }
                : { login, password };
            const response = await axios.post(`${process.env.REACT_APP_BACKEND_URL}${endpoint}`, payload);
            alert(response.data.message);
            if (!isRegistering) {
                if (response.data.user.is_admin) {
                    const goToAdminDashboard = window.confirm("Do you want to go to the Admin Dashboard?");
                    setUser({ ...response.data.user, adminRedirect: goToAdminDashboard });
                } else {
                    setUser(response.data.user);
                }
            } else if (isRegistering && response.data.user) {
                setUser(response.data.user);
            }
        } catch (error) {
            alert(error.response.data.message || 'Error occurred');
        }
    };

    const handleSwitch = () => {
        setIsRegistering(!isRegistering);
        setLogin('');
        setPassword('');
        setUsername('');
        setEmail('');
        setIsAdmin(false);
        setAdminCode('');
        setShowAdminCodeInput(false);
    };

    const handleAdminCheckboxChange = (e) => {
        setIsAdmin(e.target.checked);
        setShowAdminCodeInput(e.target.checked);
    };

    return (
        <div className="login-container">
            <div className="login-box">
                <h2 className="login-title">{isRegistering ? 'Register' : 'Login'}</h2>
                <form onSubmit={handleSubmit} className="login-form">
                    {isRegistering ? (
                        <>
                            <div className="form-group">
                                <label className="form-label">Username</label>
                                <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} className="form-input" required />
                            </div>
                            <div className="form-group">
                                <label className="form-label">Email</label>
                                <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} className="form-input" required />
                            </div>
                        </>
                    ) : (
                        <div className="form-group">
                            <label className="form-label">Username/Email</label>
                            <input type="text" value={login} onChange={(e) => setLogin(e.target.value)} className="form-input" required />
                        </div>
                    )}
                    <div className="form-group">
                        <label className="form-label">Password</label>
                        <div className="password-input-container">
                            <input
                                type={passwordVisible ? 'text' : 'password'}
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="form-input"
                                required
                            />
                            <span
                                className="password-toggle-icon"
                                onClick={() => setPasswordVisible(!passwordVisible)}
                                onMouseEnter={() => setPasswordVisible(true)}
                                onMouseLeave={() => setPasswordVisible(false)}
                            >
                                {passwordVisible ? '🙈' : '👁️'}
                            </span>
                        </div>
                    </div>
                    {isRegistering && (
                        <>
                            <div className="form-group">
                                <label className="form-label">
                                    <input type="checkbox" checked={isAdmin} onChange={handleAdminCheckboxChange} />
                                    {' '} Register as Admin
                                </label>
                            </div>
                            {showAdminCodeInput && (
                                <div className="form-group">
                                    <label className="form-label">Admin Code</label>
                                    <input
                                        type="password"
                                        value={adminCode}
                                        onChange={(e) => setAdminCode(e.target.value)}
                                        className="form-input"
                                        required={isAdmin}
                                    />
                                </div>
                            )}
                        </>
                    )}
                    <button type="submit" className="submit-btn">
                        {isRegistering ? 'Register' : 'Login'}
                    </button>
                    <button type="button" onClick={handleSwitch} className="switch-btn">
                        {isRegistering ? 'Switch to Login' : 'Switch to Register'}
                    </button>
                </form>
            </div>
        </div>
    );
}

export default Login;
