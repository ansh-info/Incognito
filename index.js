const express = require('express');
const cors = require('cors');
const db = require('./db/database');
const authRoutes = require('./routes/authRoutes');
const questionRoutes = require('./routes/questionRoutes');
const adminRoutes = require('./routes/adminRoutes');
const codeRoutes = require('./routes/codeRoutes');
const modelRoutes = require('./routes/modelRoutes');

const app = express();
app.use(cors());
app.use(express.json());

db.connect();

app.use('/auth', authRoutes);  // This line is important
app.use('/questions', questionRoutes);
app.use('/admin', adminRoutes);
app.use('/', codeRoutes);
app.use('/api', modelRoutes);

const PORT = process.env.PORT || 5001;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
