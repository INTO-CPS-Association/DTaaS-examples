# Use Python 3.10 as base image (matching the GitLab CI)
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Install system dependencies (required for matplotlib and scientific libraries)
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy the entire project structure (required for imports to work)
COPY . /app/

# Change to the heart_dt directory
WORKDIR /app/digital_twins/heart_dt

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/data/heart_dt /app/digital_twins/heart_dt/logs

# Expose port for Flask application
EXPOSE 5000

# Run the application (matching GitLab CI script)
CMD ["python", "run.py"]
