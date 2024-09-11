require('dotenv').config();
const express = require("express");
const mysql = require("mysql2");
const bcrypt = require("bcrypt");
const cors = require("cors");
const { exec } = require("child_process");

const app = express();
app.use(cors());
app.use(express.json());

const db = mysql.createConnection({
  host: process.env.DB_HOST,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
});

db.connect((err) => {
  if (err) {
    console.error("Error connecting to MySQL:", err);
    return;
  }
  console.log("Connected to MySQL");
});

// Utility function to hash passwords
const hashPassword = async (password) => {
  const salt = await bcrypt.genSalt(10);
  return bcrypt.hash(password, salt);
};

// Endpoint to register a new user
app.post("/register", async (req, res) => {
  const { username, email, password, is_admin, admin_code } = req.body;
  const correctAdminCode = process.env.ADMIN_CODE; // Replace with your actual admin code

  if (is_admin && admin_code !== correctAdminCode) {
    return res
      .status(400)
      .json({ message: "Invalid admin code. Registration failed." });
  }

  try {
    const hashedPassword = await hashPassword(password);
    const query =
      "INSERT INTO users (username, email, password, is_admin) VALUES (?, ?, ?, ?)";
    db.query(
      query,
      [username, email, hashedPassword, is_admin || false],
      (error, results) => {
        if (error) {
          if (error.code === "ER_DUP_ENTRY") {
            return res
              .status(400)
              .json({ message: "Username or email already exists" });
          }
          return res.status(500).json({ error });
        }
        res.status(201).json({ message: "User registered successfully" });
      },
    );
  } catch (error) {
    res.status(500).json({ error });
  }
});

// Endpoint to login a user
app.post("/login", (req, res) => {
  const { login, password } = req.body;
  const query = "SELECT * FROM users WHERE username = ? OR email = ?";
  db.query(query, [login, login], async (error, results) => {
    if (error) {
      return res.status(500).json({ error });
    }
    if (results.length === 0) {
      return res
        .status(400)
        .json({ message: "Invalid username, email or password" });
    }
    const user = results[0];
    const validPassword = await bcrypt.compare(password, user.password);
    if (!validPassword) {
      return res
        .status(400)
        .json({ message: "Invalid username, email or password" });
    }
    res.json({
      message: "Login successful",
      user: {
        id: user.user_id,
        username: user.username,
        email: user.email,
        is_admin: user.is_admin,
      },
    });
  });
});

// Endpoint to get all questions
app.get("/questions", (req, res) => {
  const query = "SELECT * FROM questions";
  db.query(query, (error, results) => {
    if (error) {
      return res.status(500).send(error);
    }
    res.json(results);
  });
});

// Endpoint to get a specific question by ID
app.get("/questions/:id", (req, res) => {
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

// Endpoint to get test cases for a specific question
app.get("/questions/:id/test_cases", (req, res) => {
  const questionId = req.params.id;
  const query = "SELECT * FROM test_cases WHERE question_id = ?";
  db.query(query, [questionId], (error, results) => {
    if (error) {
      return res.status(500).send(error);
    }
    res.json(results);
  });
});

// Admin endpoints
app.get("/admin/users", (req, res) => {
  const query = "SELECT * FROM users";
  db.query(query, (error, results) => {
    if (error) {
      return res.status(500).send(error);
    }
    res.json(results);
  });
});

app.put("/admin/users/:id", async (req, res) => {
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

app.delete("/admin/users/:id", (req, res) => {
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

app.post("/admin/questions", (req, res) => {
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

app.put("/admin/questions/:id", (req, res) => {
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

app.delete("/admin/questions/:id", (req, res) => {
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

app.get("/admin/test_cases", (req, res) => {
  const query = "SELECT * FROM test_cases";
  db.query(query, (error, results) => {
    if (error) {
      return res.status(500).send(error);
    }
    res.json(results);
  });
});

app.post("/admin/test_cases", (req, res) => {
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

app.put("/admin/test_cases/:id", (req, res) => {
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

app.delete("/admin/test_cases/:id", (req, res) => {
  const testCaseId = req.params.id;
  const query = "DELETE FROM test_cases WHERE test_case_id = ?";
  db.query(query, [testCaseId], (error, results) => {
    if (error) {
      return res.status(500).send(error);
    }
    res.json({ message: "Test case deleted successfully" });
  });
});

// Endpoint to submit code
app.post("/submit", (req, res) => {
  const { user_id, email, question_id, code } = req.body;

  console.log("Received code for question ID:", question_id);
  console.log("Code:", code);

  const query = "SELECT * FROM test_cases WHERE question_id = ?";
  db.query(query, [question_id], (error, results) => {
    if (error) {
      return res.status(500).send(error);
    }

    const testCases = results;
    console.log("Fetched test cases:", testCases);

    const testCasesJson = JSON.stringify(testCases);
    const escapedCode = code
      .replace(/(["$`\\])/g, "\\$1")
      .replace(/\n/g, "\\n");
    const dockerCommand = `docker run --rm --network mynetwork runtestcases python /app/runtestcases.py ${question_id} "${escapedCode}" '${testCasesJson}'`;

    console.log("Running command:", dockerCommand);

    exec(dockerCommand, (err, stdout, stderr) => {
      if (err) {
        console.error("Error executing Python script in Docker:", err);
        return res.status(500).send(err);
      }
      console.log("Python script output:", stdout);

      try {
        const jsonOutput = stdout.trim().split("\n").slice(-1)[0];
        const parsedResults = JSON.parse(jsonOutput);

        const allPassed = parsedResults.every((result) => result.passed);

        const submissionQuery =
          "INSERT INTO submissions (user_id, question_id, code, result, output, email) VALUES (?, ?, ?, ?, ?, ?)";
        db.query(
          submissionQuery,
          [
            user_id,
            question_id,
            code,
            allPassed,
            JSON.stringify(parsedResults),
            email,
          ],
          (error, submissionResults) => {
            if (error) {
              return res.status(500).json({ error });
            }
            res.json({
              message: "Code executed successfully",
              results: parsedResults,
            });
          },
        );
      } catch (parseError) {
        console.error("Error parsing JSON output:", parseError);
        return res.status(500).send(parseError);
      }
    });
  });
});

// Endpoint to run code
app.post("/run", (req, res) => {
  const { user_id, email, question_id, code } = req.body;

  console.log("Received code for question ID:", question_id);
  console.log("Code:", code);

  const query = "SELECT * FROM test_cases WHERE question_id = ?";
  db.query(query, [question_id], (error, results) => {
    if (error) {
      return res.status(500).send(error);
    }

    const testCases = results;
    console.log("Fetched test cases:", testCases);

    const testCasesJson = JSON.stringify(testCases);
    const escapedCode = code
      .replace(/(["$`\\])/g, "\\$1")
      .replace(/\n/g, "\\n");
    const dockerCommand = `docker run --rm --network mynetwork runtestcases python /app/runtestcases.py ${question_id} "${escapedCode}" '${testCasesJson}'`;

    console.log("Running command:", dockerCommand);

    exec(dockerCommand, (err, stdout, stderr) => {
      if (err) {
        console.error("Error executing Python script in Docker:", err);
        return res.status(500).send({
          message: "Error executing code",
          error: err.message,
          stderr: stderr,
        });
      }

      console.log("Python script output:", stdout);
      console.log("Python script errors (stderr):", stderr);

      try {
        const outputLines = stdout.trim().split("\n");
        const lastLine = outputLines.slice(-1)[0];

        // Attempt to parse the last line as JSON; if it fails, just return the raw output
        let parsedResults;
        try {
          parsedResults = JSON.parse(lastLine);
        } catch (parseError) {
          console.error("Error parsing JSON output:", parseError);
          // If parsing fails, return the raw output with stderr for debugging
          return res.status(200).send({
            message: "Code executed with errors",
            stdout: stdout,
            stderr: stderr,
          });
        }

        // Check the results and return accordingly
        const allPassed = parsedResults.every((result) => result.passed);

        // Sending response without submission
        res.json({
          message: "Code executed successfully",
          results: parsedResults,
        });

      } catch (unexpectedError) {
        console.error("Unexpected error during code execution:", unexpectedError);
        return res.status(500).send({
          message: "Unexpected error during code execution",
          error: unexpectedError.message,
          stdout: stdout,
          stderr: stderr,
        });
      }
    });
  });
});

const PORT = process.env.PORT || 5001;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
