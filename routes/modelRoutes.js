const express = require('express');
const { exec } = require('child_process');
const { db } = require('../db/database');

const router = express.Router();

router.post('/train-model', (req, res) => {
  const { userId } = req.body;

  // Execute the Python script to train model
  exec(`python3 selection_algorithm/prediction.py --user_id=${userId}`, (err, stdout, stderr) => {
    if (err) {
      console.error("Error executing train-model script:", err);
      return res.status(500).json({ message: "Failed to train-model.", error: err.message });
    }
    console.log("train-model script output:", stdout);
    res.json({ message: "Candidate Selection Completed Successfully." });
  });
});

router.get('/candidates', (req, res) => {
  const query = "SELECT * FROM suitable_candidates WHERE prediction = 0";
  db.query(query, (error, results) => {
    if (error) return res.status(500).send(error);
    res.json(results);
  });
});

router.get('/passed-candidates', (req, res) => {
  const query = "SELECT * FROM submissions";
  db.query(query, (error, results) => {
    if (error) return res.status(500).send(error);
    res.json(results);
  });
});

router.post('/send-email-interview', (req, res) => {
  const { userId } = req.body;

  // Execute the Python script to send interview emails
  exec(`python3 emailclient/email-notification/email_interview.py --user_id=${userId}`, (err, stdout, stderr) => {
    if (err) {
      console.error("Error executing interview email script:", err);
      return res.status(500).json({ message: "Failed to send interview email.", error: err.message });
    }
    console.log("Interview email script output:", stdout);
    res.json({ message: "Interview email sent successfully." });
  });
});

router.post('/send-email-selected', (req, res) => {
  const { userId } = req.body;

  // Execute the Python script to send selection emails
  exec(`python3 emailclient/email-notification/email_selected.py --user_id=${userId}`, (err, stdout, stderr) => {
    if (err) {
      console.error("Error executing selected email script:", err);
      return res.status(500).json({ message: "Failed to send selected email.", error: err.message });
    }
    console.log("Selected email script output:", stdout);
    res.json({ message: "Selected email sent successfully." });
  });
});

module.exports = router;
