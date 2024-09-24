import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './QuestionsListPage.css';

function QuestionsListPage({ setSelectedQuestion, user, setAdminRedirect }) {
    const [questions, setQuestions] = useState({});

    useEffect(() => {
        if (user) {
            axios.get('http://localhost:5001/questions')
                .then(response => {
                    const questionMap = response.data.reduce((acc, question) => {
                        acc[question.question_id] = question;
                        return acc;
                    }, {});
                    setQuestions(questionMap);
                })
                .catch(error => {
                    console.error('There was an error fetching the questions!', error);
                });
        }
    }, [user]);

    return (
        <div className="questions-list-container">
            <div className="top-buttons">
                <h2 className="questions-title">Questions</h2>
            </div>
            <div className="questions-list">
                {Object.values(questions).map(question => (
                    <div key={question.question_id} className="question-item" onClick={() => setSelectedQuestion(question.question_id)}>
                        <h3>{question.title}</h3>
                        {/* <p>{question.description}</p> */}
                    </div>
                ))}
            </div>
        </div>
    );
}

export default QuestionsListPage;
