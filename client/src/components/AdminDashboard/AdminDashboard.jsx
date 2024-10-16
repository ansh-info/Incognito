import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './AdminDashboard.css';

function AdminDashboard({ setUser, setAdminRedirect }) {
    const [users, setUsers] = useState([]);
    const [questions, setQuestions] = useState([]);
    const [testCases, setTestCases] = useState([]);
    const [newUser, setNewUser] = useState({ username: '', email: '', password: '', is_admin: false });
    const [newQuestion, setNewQuestion] = useState({ title: '', description: '', difficulty: '' });
    const [newTestCase, setNewTestCase] = useState({ question_id: '', input: '', expected_output: '' });
    const [editingUser, setEditingUser] = useState(null);
    const [editingQuestion, setEditingQuestion] = useState(null);
    const [editingTestCase, setEditingTestCase] = useState(null);
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState('');

    // State variables for suitable candidates and passed candidates
    const [candidates, setCandidates] = useState([]);
    const [passedCandidates, setPassedCandidates] = useState([]);

    useEffect(() => {
        fetchData('/admin/users', setUsers);
        fetchData('/questions', setQuestions);
        fetchData('/admin/test_cases', setTestCases);
        // Fetch suitable candidates and passed candidates
        fetchData('/api/candidates', setCandidates);
        fetchData('/api/passed-candidates', setPassedCandidates);
    }, []);

    const fetchData = async (endpoint, setData) => {
        try {
            const response = await axios.get(`http://localhost:5001${endpoint}`);
            setData(response.data);
        } catch (error) {
            console.error('Error fetching data:', error);
        }
    };

    const handleInputChange = (event, setState, field) => {
        const value = event.target.value;
        setState(prevState => ({ ...prevState, [field]: value }));
    };

    const handleAddUser = async () => {
        try {
            const response = await axios.post('http://localhost:5001/register', newUser);
            alert(response.data.message);
            setNewUser({ username: '', email: '', password: '', is_admin: false });
            fetchData('/admin/users', setUsers);
        } catch (error) {
            console.error('Error adding user:', error);
        }
    };

    const handleAddQuestion = async () => {
        try {
            const response = await axios.post('http://localhost:5001/admin/questions', newQuestion);
            alert(response.data.message);
            setNewQuestion({ title: '', description: '', difficulty: '' });
            fetchData('/questions', setQuestions);
        } catch (error) {
            console.error('Error adding question:', error);
        }
    };

    const handleAddTestCase = async () => {
        try {
            const response = await axios.post('http://localhost:5001/admin/test_cases', newTestCase);
            alert(response.data.message);
            setNewTestCase({ question_id: '', input: '', expected_output: '' });
            fetchData('/admin/test_cases', setTestCases);
        } catch (error) {
            console.error('Error adding test case:', error);
        }
    };

    const handleDelete = async (endpoint, id, fetchDataFunc) => {
        try {
            const response = await axios.delete(`http://localhost:5001/admin/${endpoint}/${id}`);
            alert(response.data.message);
            fetchDataFunc();
        } catch (error) {
            console.error('Error deleting:', error);
        }
    };

    const handleEdit = (item, setEditingFunc) => {
        setEditingFunc(item);
    };

    const handleUpdateUser = async () => {
        try {
            const response = await axios.put(`http://localhost:5001/admin/users/${editingUser.user_id}`, editingUser);
            alert(response.data.message);
            setEditingUser(null);
            fetchData('/admin/users', setUsers);
        } catch (error) {
            console.error('Error updating user:', error);
        }
    };

    const handleUpdateQuestion = async () => {
        try {
            const response = await axios.put(`http://localhost:5001/admin/questions/${editingQuestion.question_id}`, editingQuestion);
            alert(response.data.message);
            setEditingQuestion(null);
            fetchData('/questions', setQuestions);
        } catch (error) {
            console.error('Error updating question:', error);
        }
    };

    const handleUpdateTestCase = async () => {
        try {
            const response = await axios.put(`http://localhost:5001/admin/test_cases/${editingTestCase.test_case_id}`, editingTestCase);
            alert(response.data.message);
            setEditingTestCase(null);
            fetchData('/admin/test_cases', setTestCases);
        } catch (error) {
            console.error('Error updating test case:', error);
        }
    };

    const handleLogout = () => {
        setUser(null);
        localStorage.removeItem('user');
    };

    const handleSwitchToQuestions = () => {
        setAdminRedirect(false);
    };

    // Function to handle sending interview emails to suitable candidates
    const handleSendInterviewEmail = async (candidate) => {
        try {
            const response = await axios.post('http://localhost:5001/api/send-email-interview', { userId: candidate.user_id });
            alert(response.data.message);
        } catch (error) {
            console.error('Error sending interview email:', error);
        }
    };

    // Function to handle sending selection emails to passed candidates
    const handleSendSelectionEmail = async (candidate) => {
        try {
            const response = await axios.post('http://localhost:5001/api/send-email-selected', { userId: candidate.user_id });
            alert(response.data.message);
        } catch (error) {
            console.error('Error sending selection email:', error);
        }
    };

    // Function to handle training/evaluating selected candidates
    const handleTrainModel = async (candidate) => {
        setLoading(true);
        try {
            // post request
            const response = await axios.post('http://localhost:5001/api/train-model', { userId: candidate.user_id });
            setMessage(response.data.message);
        } catch (error) {
            console.error('Error training model:', error);
            setMessage('Failed to train model.');
        }
        setLoading(false);
    };
    

    return (
        <div className="admin-dashboard">
            <h1>Admin Dashboard</h1>
            <div className="header-buttons">
                <button onClick={handleLogout} className="logout-btn">Logout</button>
                <button onClick={handleSwitchToQuestions} className="switch-btn">Switch to Questions</button>
            </div>

             {/* Train Model Button */}
             <div style={{ marginBottom: '20px' }}>
                <button onClick={handleTrainModel} disabled={loading}>
                    {loading ? 'Training Model...' : 'Predict Candidates'}
                </button>
                {message && <p>{message}</p>}
            </div>

            {/* Existing tables for users, questions, and test cases */}
            <div className="table-container">
                <h2>Users</h2>
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Username</th>
                            <th>Email</th>
                            <th>Is Admin</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {users.map(user => (
                            <tr key={user.user_id}>
                                <td>{user.user_id}</td>
                                <td>{user.username}</td>
                                <td>{user.email}</td>
                                <td>{user.is_admin ? 'Yes' : 'No'}</td>
                                <td>
                                    <button onClick={() => handleEdit(user, setEditingUser)}>Edit</button>
                                    <button onClick={() => handleDelete('users', user.user_id, () => fetchData('/admin/users', setUsers))}>Delete</button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                {editingUser && (
                    <div className="form-group">
                        <input
                            type="text"
                            placeholder="Username"
                            value={editingUser.username}
                            onChange={e => handleInputChange(e, setEditingUser, 'username')}
                        />
                        <input
                            type="email"
                            placeholder="Email"
                            value={editingUser.email}
                            onChange={e => handleInputChange(e, setEditingUser, 'email')}
                        />
                        <input
                            type="password"
                            placeholder="Password"
                            value={editingUser.password}
                            onChange={e => handleInputChange(e, setEditingUser, 'password')}
                        />
                        <label>
                            Is Admin:
                            <input
                                type="checkbox"
                                checked={editingUser.is_admin}
                                onChange={e => handleInputChange(e, setEditingUser, 'is_admin')}
                            />
                        </label>
                        <button onClick={handleUpdateUser}>Update User</button>
                    </div>
                )}
                <div className="form-group">
                    <input
                        type="text"
                        placeholder="Username"
                        value={newUser.username}
                        onChange={e => handleInputChange(e, setNewUser, 'username')}
                    />
                    <input
                        type="email"
                        placeholder="Email"
                        value={newUser.email}
                        onChange={e => handleInputChange(e, setNewUser, 'email')}
                    />
                    <input
                        type="password"
                        placeholder="Password"
                        value={newUser.password}
                        onChange={e => handleInputChange(e, setNewUser, 'password')}
                    />
                    <label>
                        Is Admin:
                        <input
                            type="checkbox"
                            checked={newUser.is_admin}
                            onChange={e => handleInputChange(e, setNewUser, 'is_admin')}
                        />
                    </label>
                    <button onClick={handleAddUser}>Add User</button>
                </div>
            </div>

            <div className="table-container">
                <h2>Questions</h2>
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Title</th>
                            <th>Description</th>
                            <th>Difficulty</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {questions.map(question => (
                            <tr key={question.question_id}>
                                <td>{question.question_id}</td>
                                <td>{question.title}</td>
                                <td>{question.description}</td>
                                <td>{question.difficulty}</td>
                                <td>
                                    <button onClick={() => handleEdit(question, setEditingQuestion)}>Edit</button>
                                    <button onClick={() => handleDelete('questions', question.question_id, () => fetchData('/questions', setQuestions))}>Delete</button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                {editingQuestion && (
                    <div className="form-group">
                        <input
                            type="text"
                            placeholder="Title"
                            value={editingQuestion.title}
                            onChange={e => handleInputChange(e, setEditingQuestion, 'title')}
                        />
                        <input
                            type="text"
                            placeholder="Description"
                            value={editingQuestion.description}
                            onChange={e => handleInputChange(e, setEditingQuestion, 'description')}
                        />
                        <input
                            type="text"
                            placeholder="Difficulty"
                            value={editingQuestion.difficulty}
                            onChange={e => handleInputChange(e, setEditingQuestion, 'difficulty')}
                        />
                        <button onClick={handleUpdateQuestion}>Update Question</button>
                    </div>
                )}
                <div className="form-group">
                    <input
                        type="text"
                        placeholder="Title"
                        value={newQuestion.title}
                        onChange={e => handleInputChange(e, setNewQuestion, 'title')}
                    />
                    <input
                        type="text"
                        placeholder="Description"
                        value={newQuestion.description}
                        onChange={e => handleInputChange(e, setNewQuestion, 'description')}
                    />
                    <input
                        type="text"
                        placeholder="Difficulty"
                        value={newQuestion.difficulty}
                        onChange={e => handleInputChange(e, setNewQuestion, 'difficulty')}
                    />
                    <button onClick={handleAddQuestion}>Add Question</button>
                </div>
            </div>

            <div className="table-container">
                <h2>Test Cases</h2>
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Question ID</th>
                            <th>Input</th>
                            <th>Expected Output</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {testCases.map(testCase => (
                            <tr key={testCase.test_case_id}>
                                <td>{testCase.test_case_id}</td>
                                <td>{testCase.question_id}</td>
                                <td>{testCase.input}</td>
                                <td>{testCase.expected_output}</td>
                                <td>
                                    <button onClick={() => handleEdit(testCase, setEditingTestCase)}>Edit</button>
                                    <button onClick={() => handleDelete('test_cases', testCase.test_case_id, () => fetchData('/admin/test_cases', setTestCases))}>Delete</button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                {editingTestCase && (
                    <div className="form-group">
                        <input
                            type="text"
                            placeholder="Question ID"
                            value={editingTestCase.question_id}
                            onChange={e => handleInputChange(e, setEditingTestCase, 'question_id')}
                        />
                        <input
                            type="text"
                            placeholder="Input"
                            value={editingTestCase.input}
                            onChange={e => handleInputChange(e, setEditingTestCase, 'input')}
                        />
                        <input
                            type="text"
                            placeholder="Expected Output"
                            value={editingTestCase.expected_output}
                            onChange={e => handleInputChange(e, setEditingTestCase, 'expected_output')}
                        />
                        <button onClick={handleUpdateTestCase}>Update Test Case</button>
                    </div>
                )}
                <div className="form-group">
                    <input
                        type="text"
                        placeholder="Question ID"
                        value={newTestCase.question_id}
                        onChange={e => handleInputChange(e, setNewTestCase, 'question_id')}
                    />
                    <input
                        type="text"
                        placeholder="Input"
                        value={newTestCase.input}
                        onChange={e => handleInputChange(e, setNewTestCase, 'input')}
                    />
                    <input
                        type="text"
                        placeholder="Expected Output"
                        value={newTestCase.expected_output}
                        onChange={e => handleInputChange(e, setNewTestCase, 'expected_output')}
                    />
                    <button onClick={handleAddTestCase}>Add Test Case</button>
                </div>
            </div>

            {/* Table for suitable candidates with a single interview email button */}
            <div className="table-container">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <h2>Suitable Candidates</h2>
                    {/* Button to send interview emails to all candidates */}
                    <button onClick={handleSendInterviewEmail}>
                        Send Interview Emails to All
                    </button>
                </div>

                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Username</th>
                            <th>Email</th>
                        </tr>
                    </thead>
                    <tbody>
                        {candidates.map(candidate => (
                            <tr key={candidate.user_id}>
                                <td>{candidate.user_id}</td>
                                <td>{candidate.username}</td>
                                <td>{candidate.email}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Table for passed candidates with a single selection email button */}
            <div className="table-container">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <h2>Passed Candidates</h2>
                    {/* Button to send selection emails to all passed candidates */}
                    <button onClick={handleSendSelectionEmail}>
                        Send Selection Emails to All
                    </button>
                </div>

                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Username</th>
                            <th>Email</th>
                        </tr>
                    </thead>
                    <tbody>
                        {passedCandidates.map(candidate => (
                            <tr key={candidate.user_id}>
                                <td>{candidate.user_id}</td>
                                <td>{candidate.username}</td>
                                <td>{candidate.email}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

export default AdminDashboard;
