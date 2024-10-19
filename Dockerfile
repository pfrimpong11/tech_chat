# Use official Python image as the base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .

# Install dependencies (including NLTK and the other necessary modules)
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data during build
RUN python -m nltk.downloader punkt wordnet

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on (if needed for Flask or other frameworks)
EXPOSE 5000

# Define the command to run the app
CMD ["python", "app.py"]
