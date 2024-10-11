const express = require('express');
const { exec } = require('child_process');
const { db } = require('../db/database');

const router = express.Router();

router.post("/submit", (req, res) => {
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
    const dockerCommand = `docker run --rm --network python runtestcases python /app/runtestcases.py ${question_id} "${escapedCode}" '${testCasesJson}'`;

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
          }
        );
      } catch (parseError) {
        console.error("Error parsing JSON output:", parseError);
        return res.status(500).send(parseError);
      }
    });
  });
});

router.post("/run", (req, res) => {
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
    const dockerCommand = `docker run --rm --network python runtestcases python /app/runtestcases.py ${question_id} "${escapedCode}" '${testCasesJson}'`;

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

module.exports = router;
