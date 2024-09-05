# Use a Node.js base image
FROM node:20.16.0

# Set the working directory inside the container
WORKDIR /app

# Install Docker CLI inside the container
RUN apt-get update && apt-get install -y docker.io

# Copy package.json and package-lock.json to the working directory
COPY package*.json ./

# Copy the client package.json to leverage Docker caching
COPY client/package*.json ./client/

# Install dependencies and rebuild native modules
RUN npm install --build-from-source

# Copy the entire project into the working directory
COPY . .

# Rebuild native dependencies in case of updates
RUN npm rebuild bcrypt --build-from-source

# Expose the ports that your application uses
EXPOSE 5001 3000

# Start the application
CMD ["npm", "start"]
