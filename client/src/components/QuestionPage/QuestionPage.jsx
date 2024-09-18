import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Editor } from '@monaco-editor/react';
import './QuestionPage.css';

function QuestionPage({ selectedQuestionId, setSelectedQuestion, user, setAdminRedirect }) {
    const [code, setCode] = useState('');
    const [testCaseResults, setTestCaseResults] = useState([]);
    const [question, setQuestion] = useState(null);

    useEffect(() => {
        axios.get(`${process.env.REACT_APP_BACKEND_URL}/questions/${selectedQuestionId}`)
            .then(response => {
                setQuestion(response.data);
            })
            .catch(error => {
                console.error('There was an error fetching the question!', error);
            });
    }, [selectedQuestionId]);

    const handleBackToQuestions = () => {
        setSelectedQuestion(null);
        setCode('');
        setTestCaseResults([]); // Clear test results when going back
    };

    const handleSubmitCode = () => {
        axios
            .post(`${process.env.REACT_APP_BACKEND_URL}/submit`, { user_id: user.id, email: user.email, question_id: selectedQuestionId, code })
            .then(({ data }) => {
                console.log('Received test case results:', data.results);
                setTestCaseResults(data.results); // Set test results when code is submitted
                alert("Test cases have been run. Check the results below.");
            })
            .catch((err) => {
                console.log('Error submitting code:', err);
            });
    };

    const handleRunCode = () => {
        axios
            .post(`${process.env.REACT_APP_BACKEND_URL}/run`, { user_id: user.id, email: user.email, question_id: selectedQuestionId, code })
            .then(({ data }) => {
                console.log('Received test case results:', data.results);
                setTestCaseResults(data.results); // Set test results when code is submitted
                alert("Test cases have been run. Check the results below.");
            })
            .catch((err) => {
                console.log('Error submitting code:', err);
            });
    };

    if (!question) {
        return <div>Loading...</div>;
    }

    return (
        <div className="question-page-container">
            <div className="top-buttons">
                <button onClick={handleBackToQuestions} className="back-btn">
                    Back to Questions
                </button>
            </div>
            <div className="question-box">
                <div className="question-title">{question.title}</div>
                <div className="question-description">{question.description}</div>
            </div>
            {testCaseResults.length > 0 && (
                <div className="test-results">
                    {testCaseResults.map((result) => (
                        <div key={result.test_case_id} className={`result-box ${result.passed ? 'passed' : 'failed'}`}>
                            {result.passed ? '✅ Passed' : `❌ Failed: ${result.error || 'Incorrect output'}`} (Test Case ID: {result.test_case_id})
                        </div>
                    ))}
                </div>
            )}
            <Editor
                height="60vh"
                width="100%"
                theme="vs-dark"
                language="python"
                value={code}
                onChange={(value) => setCode(value)}
                options={{ fontSize: 20 }} // Set the font size here
                className="editor"
            />
            <button onClick={handleSubmitCode} className="submit-btn">
                Submit Code
            </button>
            <button onClick={handleRunCode} className="submit-btn">
                Run Code
            </button>
        </div>
    );
}

export default QuestionPage;
