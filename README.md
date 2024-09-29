# Incognito

Inspired by Google's Foobar challenge. It automates secretive candidate selection based on online activity, provides timed coding challenges, and allows hiring managers to evaluate submissions

## Project Overview

Key Features:

- Interactive UI: A responsive and intuitive user interface where users can select problems, write code in multiple languages, and receive real-time feedback.
- Dockerized Environment: The platform runs entirely within Docker containers, ensuring consistency across all systems. Test cases are executed in isolated containers.
- Database-Driven Challenges: Questions and corresponding test cases are stored in a MySQL database, allowing for easy management and scalability.
- Automated Test Case Execution: Solutions are automatically tested against multiple test cases stored in the database, providing immediate feedback to the user.
<!-- - Multi-Language Support: The platform supports multiple programming languages, allowing users to practice in their language of choice. -->

## Technology Stack:

- Backend: Node.js, Express.js
- Frontend: HTML, CSS, JavaScript
- Database: MySQL (for questions and test case storage)
- Containerization: Docker, Docker Compose
- Programming Languages Supported: Python(additional        languages to be added)


## Webapp

```
WEBAPP
├── client
│   ├── node_modules
│   ├── public
│   └── src
│       ├── components
│       │   ├── AdminDashboard
│       │   │   ├── AdminDashboard.css
│       │   │   └── AdminDashboard.jsx
│       │   ├── App
│       │   │   ├── App.css
│       │   │   └── App.jsx
│       │   ├── Login
│       │   │   ├── Login.css
│       │   │   └── Login.jsx
│       │   ├── QuestionPage
│       │   │   ├── QuestionPage.css
│       │   │   └── QuestionPage.jsx
│       │   └── QuestionsListPage
│       │       ├── QuestionsListPage.css
│       │       └── QuestionsListPage.jsx
│       └── styles
│           ├── index.css
│           └── index.js
├── .env
├── craco.config.js
├── package-lock.json
├── package.json
├── README.md
├── tailwind.config.js
├── yarn.lock
├── create_insert_db
├── node_modules
└── utils
    ├── answers.py
    ├── Dockerfile
    ├── requirements.txt
    ├── runtestcases.py
    ├── .dockerignore
    ├── Dockerfile
    ├── index.js
    ├── package-lock.json
    └── package.json
```
### Webapplication
![Question Page](/images/questionpage.png)

## Installation and Setup

To set up the project locally or on a server, follow these steps:

Prerequisites
Docker and Docker Compose must be installed on your system.
Node.js and npm should also be installed for local development.
Steps
Clone the repository:

````bash
git clone https://github.com/ansh-info/Incognito
cd Incognito
````

Install backend dependencies:
```bash
npm install
```

Build and run Docker containers: The entire environment, including the MySQL database and Node.js backend, is encapsulated within Docker containers. Run the following command to build and start the containers:

```bash
docker-compose up --build
```

- and 

```bash
docker run --name webapp --network webapp -p 5001:5001 -p 3000:3000 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  webapp
```

This command will:
Set up the MySQL database with the tables for questions and test cases.
Launch the Node.js backend.
Serve the frontend on http://localhost:3000.
Database Configuration: By default, the Docker environment creates a MySQL container where all the questions and test cases are stored. You can modify the database schema by editing the migration files located in the /config/db.js.

Access the application: Once the containers are running, open your browser and go to http://localhost:3000 to access the platform.

### Admindashboard
![Admin Dashboard](/images/admindashboard.png)

## Database Schema

The MySQL database stores all the coding problems, test cases, and user solutions. Below is a high-level overview of the database schema:

- questions: Stores the coding problems, including problem statement, difficulty level, and tags.
- test_cases: Each question has associated test cases that validate the correctness of the submitted solution.
- user_submissions: Stores user submissions and execution results, including status (pass/fail) and runtime.

### Prerequisites

Docker installed on your system.
A running MySQL instance that the container can connect to.

### Setup Instructions

1. Pull the Image from Docker Hub:
`docker pull anshinfo/runtestcases:latest`

2. Create a Docker Network (if not already created) to connect the Python container with MySQL:
`docker network create mynetwork`

3. Run the MySQL Container:
`docker run -d --network mynetwork --name mysql-container -e MYSQL_ROOT_PASSWORD=Passwd mysql:latest`

4. Run the Python Container:
`docker run --network mynetwork --name runtestcases anshinfo/runtestcases:latest`

````bash
#### Build the Docker Image Locally

If you want to build the Docker image yourself, you can follow these steps:

1. Clone the repository or ensure you have the Dockerfile and related source files.  
2. Navigate to the directory containing the Dockerfile.   
3. Use the following command to build the image:

docker build -t runtestcases .
````
### Sending Email to Suitable Candidates
![Sutitablecandidates](/images/sutitablecandidates.png)

## Running Test Cases in Docker

All test cases are executed within Docker containers, ensuring that each solution runs in isolation. This prevents code conflicts and ensures a secure environment.

1. **Docker Setup:**

- Created a Docker network for communication between the MySQL container and the Python script container.
- Built a Docker image to run the Python script (runtestcases.py) in an isolated environment.
- Ensured that the Docker container for the Python script can communicate with the MySQL container.

**Detailed Steps for Docker Network and Container Setup**

**1. Create a Docker Network**

We created a Docker network to allow communication between containers, specifically between the MySQL container and the container running the Python script. This ensures that the containers can find each other using container names instead of IP addresses, which can change.

**Command:**

```bash
docker network create mynetwork
```

This command creates a new network called mynetwork.(mustread-utils/README.md)

**2. Connect Existing MySQL Container to the Network**

If you already have a MySQL container running, you need to connect it to the newly created network. This allows the container running the Python script to communicate with the MySQL database.

**Command:**

```bash
docker network connect mynetwork mysql
```

This command connects the existing MySQL container (named mysql) to the mynetwork.

**3. Dockerfile for the Python Script**

We created a Dockerfile to build an image for running the Python script (runtestcases.py). The image includes Python and the required dependencies.

## To run test cases:

- When a user submits their solution, it is passed to a Docker container with a pre-configured environment.
- The RunTestCases.py script is executed inside the container, where it fetches the relevant test cases from the MySQL database and runs them against the user's solution.
- The result is sent back to the frontend, displaying whether the test cases passed or failed, along with execution details.

```bash
python RunTestCases.py --question_id=123 --language=python
```

## Example Flow:

- User selects a question.
- User writes and submits code.
- Backend fetches the corresponding test cases from the database.
- Code is run inside a Docker container.
- Results are returned to the user, showing test case pass/fail status and execution time.

## Future Updates

Planned updates include:

- Advanced Test Case Management: Allow users to create custom test cases.
- Leaderboard Feature: Rank users based on their performance across various challenges.
- Additional Language Support: Expanding support to include languages like Java, C++, and Ruby.
- Improved Analytics: Provide users with detailed metrics on their performance, such as time complexity and memory usage.