const express = require('express');
const { db } = require('../db/database');

const router = express.Router();

router.get("/", (req, res) => {
  const query = "SELECT * FROM questions";
  db.query(query, (error, results) => {
    if (error) {
      return res.status(500).send(error);
    }
    res.json(results);
  });
});

router.get("/:id", (req, res) => {
  const questionId = req.params.id;
  const query = "SELECT * FROM questions WHERE question_id = ?";
  db.query(query, [questionId], (error, results) => {
    if (error) {
      return res.status(500).send(error);
    }
    if (results.length === 0) {
      return res.status(404).json({ message: "Question not found" });
    }
    res.json(results[0]);
  });
});

router.get("/:id/test_cases", (req, res) => {
  const questionId = req.params.id;
  const query = "SELECT * FROM test_cases WHERE question_id = ?";
  db.query(query, [questionId], (error, results) => {
    if (error) {
      return res.status(500).send(error);
    }
    res.json(results);
  });
});

module.exports = router;
