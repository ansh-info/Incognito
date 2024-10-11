const express = require('express');
const bcrypt = require('bcrypt');
const { db } = require('../db/database');
const { hashPassword } = require('../utils/passwordUtils');

const router = express.Router();

router.post("/register", async (req, res) => {
  const { username, email, password, is_admin, admin_code } = req.body;
  const correctAdminCode = "1234"; // Replace with your actual admin code

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

router.post("/login", (req, res) => {
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

module.exports = router;
