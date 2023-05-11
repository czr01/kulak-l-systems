# Use the official Ubuntu 18.04 as the base image
FROM ubuntu:22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip

# Set te working directory inside container
WORKDIR /app

# Copy the project files to the working directory
COPY . .

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Command to run application
CMD ["python3","-m","flask","run","--host=0.0.0.0"]

