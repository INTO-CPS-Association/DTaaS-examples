# Heart DT Docker Setup

This directory contains Docker configuration files to run the Heart Digital Twin application using Docker Compose.

## Files Created

- `Dockerfile` - Defines the container image with Python 3.10 and required dependencies
- `docker-compose.yml` - Orchestrates the application container with proper networking and volumes
- `.dockerignore` - Optimizes build performance by excluding unnecessary files

## Quick Start

### Prerequisites
- Docker installed on your system
- Docker Compose installed

### Running the Application

1. **Build and run with Docker Compose:**
   ```bash
   cd digital_twins/heart_dt
   docker-compose up --build
   ```

2. **Run in detached mode (background):**
   ```bash
   docker-compose up -d --build
   ```

3. **Stop the application:**
   ```bash
   docker-compose down
   ```

### Access the Application

- The application will be available at: `http://localhost:5000`
- Logs are persisted in the `./logs` directory
- Data is persisted in the `./data` directory

## Equivalent GitLab CI Commands

The Docker setup replicates these GitLab CI steps:
```bash
# Original GitLab CI script:
python --version
pip install --upgrade pip
cd digital_twins/heart_dt
pip install -r requirements.txt
python run.py
```

## Docker Commands (Alternative to Compose)

If you prefer using Docker directly:

```bash
# Build the image
docker build -t heart-dt ../../ -f Dockerfile

# Run the container
docker run -p 5000:5000 -v $(pwd)/logs:/app/digital_twins/heart_dt/logs heart-dt
```

## Troubleshooting

- **Port conflicts**: If port 5000 is in use, modify the port mapping in `docker-compose.yml`
- **Permission issues**: Ensure the `logs` and `data` directories have proper permissions
- **Build failures**: Check that all dependencies in `requirements.txt` are compatible

## Environment Variables

The following environment variables are set in the container:
- `PYTHONPATH=/app` - Ensures proper Python module imports
- `PYTHONUNBUFFERED=1` - Shows real-time output in logs
