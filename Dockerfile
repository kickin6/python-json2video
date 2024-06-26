# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy only the requirements file to leverage caching
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app

# Install ffmpeg
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean && rm -rf /var/lib/apt/lists/*

# Make port 5003 available to the world outside this container
EXPOSE 5003

# Define environment variable
ENV FLASK_APP=app.py

# Run app.py when the container launches, explicitly setting the port
CMD ["flask", "run", "--host=0.0.0.0", "--port=5003"]

