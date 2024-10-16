# Incognito

Inspired by Google's Foobar challenge. It automates secretive candidate selection based on online activity, provides timed coding challenges, and allows hiring managers to evaluate submissions

## Project Overview

Key Features:

- Interactive UI: A responsive and intuitive user interface where users can select problems, write code in multiple languages, and receive real-time feedback.
- Dockerized Environment: The platform runs entirely within Docker containers, ensuring consistency across all systems. Test cases are executed in isolated containers.
- Database-Driven Challenges: Questions and corresponding test cases are stored in a MySQL database, allowing for easy management and scalability.
- Automated Test Case Execution: Solutions are automatically tested against multiple test cases stored in the database, providing immediate feedback to the user.
<!-- - Multi-Language Support: The platform supports multiple programming languages, allowing users to practice in their language of choice. -->

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

### To run the repo locally

- Firstly make sure to set the **env** variables in the connection folder for your mysql database container.
- connection/.env and emailclient/.env for the emailclient - smtp password and the server
- Then pull and start the mysql docker container and connect it to the docker network.

Docker Command to run the mysql container:

```bash
docker run --name mysql -p 3306:3306 -e MYSQL_ROOT_PASSWORD=root -d mysql
```

Docker Command to connect the mysql container:

```bash
docker network create python
docker network connect python mysql                                                                                                                                                        
```

Then Build the Isolated Docker container to run the python test-cases

```bash
cd sandbox
docker build -t runtestcases .
cd .. # To Return to the root 
```

Create a python virtual environment

```bash
conda create --name webapp python=3.10
conda activate webapp
pip install -r requirements.txt
python3 scripts.py
```

Install node dependencies:

```bash
npm install
npm start
```

### To build repo as a docker container

Build and run Docker containers: The entire environment, including the MySQL database and Node.js backend, is encapsulated within Docker containers. Run the following command to build and start the containers:

```bash
docker-compose up --build
```

```bash
docker run --name webapp --network webapp -p 5001:5001 -p 3000:3000 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  webapp
```

#### What This Command Does:
- Sets up the **MySQL database** with tables for questions and test cases.
- Launches the **Node.js backend**.
- Serves the **frontend** on [http://localhost:3000](http://localhost:3000).

#### Database Configuration:
- By default, the Docker environment creates a **MySQL container** where all the questions and test cases are stored.
- You can modify the database schema by editing the migration files located in `/config/db.js`.

#### Accessing the Application:
Once the containers are running:
- Open your browser.
- Go to [http://localhost:3000](http://localhost:3000) to access the platform.

### Admindashboard
![Admin Dashboard](/images/admindashboard.png)

## Database Schema

The MySQL database stores all the coding problems, test cases, and user solutions. Below is a high-level overview of the database schema:

- questions: Stores the coding problems, including problem statement, difficulty level, and tags.
- test_cases: Each question has associated test cases that validate the correctness of the submitted solution.
- user_submissions: Stores user submissions and execution results, including status (pass/fail) and runtime.

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


**2. Connect Existing MySQL Container to the Network**

If you already have a MySQL container running, you need to connect it to the newly created network. This allows the container running the Python script to communicate with the MySQL database.

**3. Dockerfile for the Python Script**

We created a Dockerfile to build an image for running the Python script **runtestcases.py**. The image includes Python and the required dependencies.

## To run test cases:

- When a user submits their solution, it is passed to a Docker container with a pre-configured environment.
- The RunTestCases.py script is executed inside the container, where it fetches the relevant test cases from the MySQL database and runs them against the user's solution.
- The result is sent back to the frontend, displaying whether the test cases passed or failed, along with execution details.

## Example Flow:

- User selects a question.
- User writes and submits code.
- Backend fetches the corresponding test cases from the database.
- Code is run inside a Docker container.
- Results are returned to the user, showing test case pass/fail status and execution time.

## Technology Stack:

- Backend: Node.js, Express.js
- Frontend: HTML, CSS, JavaScript
- Database: MySQL (for questions and test case storage)
- Containerization: Docker, Docker Compose
- Programming Languages Supported: Python(additional languages to be added)

## Future Updates

Planned updates include:

- Advanced Test Case Management: Allow users to create custom test cases.
- Leaderboard Feature: Rank users based on their performance across various challenges.
- Additional Language Support: Expanding support to include languages like Java, C++, and Ruby.
- Improved Analytics: Provide users with detailed metrics on their performance, such as time complexity and memory usage.