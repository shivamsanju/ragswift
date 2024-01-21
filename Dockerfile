# Use the official Python image from Docker Hub as the base image
FROM rayproject/ray

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Create and set the working directory
WORKDIR /app

# Add requirements.txt
ADD requirements.txt /app/requirements.txt

# Install dependencies from requirements.txt
RUN pip install -r requirements.txt
RUN pip install llama-hub

# Copy the contents of the current directory (where Dockerfile is located) into the container at /app
ADD . /app

# Set the absolute path for the temporary directory
ENV TEMP_DIR=/app/tmp

# EXPOSE PORT
EXPOSE 5005
EXPOSE 8265

# Deploy serve app
CMD ray start --head --temp-dir=$TEMP_DIR --include-dashboard=true & serve run main:app --port 5005