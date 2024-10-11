require('dotenv').config({ path: './db/.env' }); // Load environment variables from the .env file in the db folder
const mysql = require('mysql2');

// Create a MySQL connection using environment variables
const db = mysql.createConnection({
  host: process.env.DB_HOST,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
  port: process.env.DB_PORT || 3306, // Default to port 3306 if not specified
});

// Function to connect to the database
const connect = () => {
  db.connect((err) => {
    if (err) {
      console.error("Error connecting to MySQL:", err);
      return;
    }
    console.log(`Connected to MySQL on port ${process.env.DB_PORT || 3306}`);
  });
};

module.exports = { db, connect };
