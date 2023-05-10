# Use the official Ubuntu 18.04 as the base image
FROM ubuntu:22.04

# Set the working directory inside the container
WORKDIR /lsystems-app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip

# Copy the project files to the working directory
COPY . /lsystems-app

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Expose any necessary ports
EXPOSE 5000

# Specify the command to run your application
CMD [ "python3", "run.py" ]

