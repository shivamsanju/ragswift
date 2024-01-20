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

# Copy the contents of the current directory (where Dockerfile is located) into the container at /app
ADD . /app

EXPOSE 8000

# Deploy serve app
CMD ray start --head --include-dashboard=true & serve run main:app