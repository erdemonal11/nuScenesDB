# Use Debian Bullseye slim as base image
FROM debian:bullseye-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set the working directory
WORKDIR /app

# Install system dependencies and Python 3.10
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    git \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/apt/lists/*

# Copy all files
COPY . /app/


# Upgrade pip
RUN python3 -m pip install --upgrade pip

# Install Python packages
RUN pip3 install --no-cache-dir -r requirements.txt

# Set environment variables for the application
ENV NUSCENES_DATAROOT=/mnt/c/Users/mrifk/Desktop/v1.0-mini

# Make sure files have correct permissions
RUN chmod -R 755 /app

# Run the application
CMD ["python3", "dbconnect.py"]