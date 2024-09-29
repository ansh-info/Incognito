
**Explanation of runtestcases.py**

The runtestcases.py file is responsible for executing user-submitted code against predefined test cases fetched from a MySQL database. Here’s a breakdown of what this script does:

1. **Connect to MySQL Database:**

- Establishes a connection to the MySQL database to fetch test cases.

3. **Fetch and Parse Test Cases:**

- Retrieves test cases associated with the given question ID.

5. **Execute User Code:**

- Dynamically executes the user-submitted code.
- Runs the code against each test case input.
- Compares the output with the expected output.

7. **Return Results:**

- Returns the results (pass/fail status and any errors) in JSON format.

**What is runtestcases.py Doing?**

- The script connects to the MySQL database to fetch test cases for a specific question.
- It dynamically executes the user-submitted code and runs it against the fetched test cases.
- It then returns the results (pass/fail) for each test case.

3. **Does runtestcases.py Need to Change When Adding More Questions?**

- No, runtestcases.py does not need to be changed when adding more questions.
- The script is designed to dynamically fetch test cases from the database based on the question ID passed to it.
- You only need to use the insert_questions_db.py script or a similar method to insert new questions and test cases into the database.


# Python MySQL Test Cases Runner Using Docker

### Description
This Docker image provides an isolated environment to run Python code that interacts with a MySQL database. The container fetches questions and test cases from the database and executes the provided Python code against these test cases. The image is built on the official slim Python 3.10 image, keeping it lightweight and optimized for running test cases in a controlled environment.

### Features

- Lightweight: Based on the python:3.10-slim image, keeping the image size minimal.
- MySQL Integration: Connects to a MySQL database to fetch test cases and execute them against user-provided Python code.
- Isolated Environment: Runs Python code in an isolated environment, ensuring a consistent and safe execution context.
- Flexible Execution: Easily adaptable with customizable environment variables for database connections.

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

### Environment Variables

The container can be configured using the following environment variables:

- MYSQL_HOST: The hostname of the MySQL server (default: mysql).
- MYSQL_USER: MySQL username (default: root).
- MYSQL_PASSWORD: Password for the MySQL user.
- MYSQL_DATABASE: The MySQL database name to connect to.

These variables can be set when running the container, for example:

```bash
docker run --network mynetwork -e MYSQL_HOST=mysql -e MYSQL_USER=root -e MYSQL_PASSWORD=Passwd -e MYSQL_DATABASE=DB anshinfo/runtestcases:latest
```

### Usage

Running Tests: The container runs the runtestcases.py script by default, which connects to the MySQL database, fetches test cases for a given question, and executes the provided code against these test cases.

Passing Code and Question ID: Modify the script invocation or pass the required arguments (e.g., question ID, code) as needed based on your environment setup.

### Example Commands
To pass specific arguments or override the default command, you can run:

```bash
docker run --network mynetwork anshinfo/runtestcases python runtestcases.py <question_id> <code>
```

### Troubleshooting

- Connection Issues: Ensure that the Python and MySQL containers are on the same network.

- Environment Variables: Verify that the environment variables are correctly set and match your MySQL setup.

- Logs: Use docker logs <container_name> to view detailed error logs if the script fails to run as expected.

### License
This project is licensed under the MIT License - see the LICENSE file for details.