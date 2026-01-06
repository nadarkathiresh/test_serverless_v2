# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# System dependencies and pip tooling
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*
ENV PIP_NO_CACHE_DIR=1
RUN python -m pip install --upgrade pip setuptools wheel

# Python dependencies
# Note: extra index ensures CPU torch wheels resolve reliably in slim images
RUN pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Run the application
CMD ["python", "chatbot.py"]