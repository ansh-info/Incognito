const express = require('express');
const { db } = require('../db/database');
const { hashPassword } = require('../utils/passwordUtils');

const router = express.Router();

router.get("/users", (req, res) => {
  const query = "SELECT * FROM users";
  db.query(query, (error, results) => {
    if (error) {
      return res.status(500).send(error);
    }
    res.json(results);
  });
});

router.put("/users/:id", async (req, res) => {
  const userId = req.params.id;
  const { username, email, password, is_admin } = req.body;

  try {
    const hashedPassword = password ? await hashPassword(password) : undefined;
    const updateFields = [];
    const updateValues = [];

    if (username) {
      updateFields.push("username = ?");
      updateValues.push(username);
    }
    if (email) {
      updateFields.push("email = ?");
      updateValues.push(email);
    }
    if (hashedPassword) {
      updateFields.push("password = ?");
      updateValues.push(hashedPassword);
    }
    if (is_admin !== undefined) {
      updateFields.push("is_admin = ?");
      updateValues.push(is_admin);
    }

    updateValues.push(userId);

    const query = `UPDATE users SET ${updateFields.join(", ")} WHERE user_id = ?`;
    db.query(query, updateValues, (error, results) => {
      if (error) {
        return res.status(500).json({ error });
      }
      res.json({ message: "User updated successfully" });
    });
  } catch (error) {
    res.status(500).json({ error });
  }
});

router.delete("/users/:id", (req, res) => {
  const userId = req.params.id;

  const deleteSubmissions = new Promise((resolve, reject) => {
    const query = "DELETE FROM submissions WHERE user_id = ?";
    db.query(query, [userId], (error, results) => {
      if (error) {
        reject(error);
      } else {
        resolve(results);
      }
    });
  });

  deleteSubmissions
    .then(() => {
      const query = "DELETE FROM users WHERE user_id = ?";
      db.query(query, [userId], (error, results) => {
        if (error) {
          return res.status(500).send(error);
        }
        res.json({ message: "User deleted successfully" });
      });
    })
    .catch((error) => {
      res.status(500).send(error);
    });
});

router.post("/questions", (req, res) => {
  const { title, description, difficulty } = req.body;
  const query =
    "INSERT INTO questions (title, description, difficulty) VALUES (?, ?, ?)";
  db.query(query, [title, description, difficulty], (error, results) => {
    if (error) {
      return res.status(500).send(error);
    }
    res.status(201).json({ message: "Question added successfully" });
  });
});

router.put("/questions/:id", (req, res) => {
  const questionId = req.params.id;
  const { title, description, difficulty } = req.body;
  const query =
    "UPDATE questions SET title = ?, description = ?, difficulty = ? WHERE question_id = ?";
  db.query(
    query,
    [title, description, difficulty, questionId],
    (error, results) => {
      if (error) {
        return res.status(500).send(error);
      }
      res.json({ message: "Question updated successfully" });
    },
  );
});

router.delete("/questions/:id", (req, res) => {
  const questionId = req.params.id;

  const deleteSubmissions = new Promise((resolve, reject) => {
    const query = "DELETE FROM submissions WHERE question_id = ?";
    db.query(query, [questionId], (error, results) => {
      if (error) {
        reject(error);
      } else {
        resolve(results);
      }
    });
  });

  deleteSubmissions
    .then(() => {
      const query = "DELETE FROM questions WHERE question_id = ?";
      db.query(query, [questionId], (error, results) => {
        if (error) {
          return res.status(500).send(error);
        }
        res.json({ message: "Question deleted successfully" });
      });
    })
    .catch((error) => {
      res.status(500).send(error);
    });
});

router.get("/test_cases", (req, res) => {
  const query = "SELECT * FROM test_cases";
  db.query(query, (error, results) => {
    if (error) {
      return res.status(500).send(error);
    }
    res.json(results);
  });
});

router.post("/test_cases", (req, res) => {
  const { question_id, input, expected_output } = req.body;
  const query =
    "INSERT INTO test_cases (question_id, input, expected_output) VALUES (?, ?, ?)";
  db.query(query, [question_id, input, expected_output], (error, results) => {
    if (error) {
      return res.status(500).send(error);
    }
    res.status(201).json({ message: "Test case added successfully" });
  });
});

router.put("/test_cases/:id", (req, res) => {
  const testCaseId = req.params.id;
  const { question_id, input, expected_output } = req.body;
  const query =
    "UPDATE test_cases SET question_id = ?, input = ?, expected_output = ? WHERE test_case_id = ?";
  db.query(
    query,
    [question_id, input, expected_output, testCaseId],
    (error, results) => {
      if (error) {
        return res.status(500).send(error);
      }
      res.json({ message: "Test case updated successfully" });
    },
  );
});

router.delete("/test_cases/:id", (req, res) => {
  const testCaseId = req.params.id;
  const query = "DELETE FROM test_cases WHERE test_case_id = ?";
  db.query(query, [testCaseId], (error, results) => {
    if (error) {
      return res.status(500).send(error);
    }
    res.json({ message: "Test case deleted successfully" });
  });
});

module.exports = router;
