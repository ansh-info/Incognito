# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY utils/requirements.txt .

# Install the dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the specific runtestcases.py file into the container
COPY utils/runtestcases.py .

# Command to run the script (this will be overridden by the command passed in exec)
CMD ["python", "runtestcases.py"]
