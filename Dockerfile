# Dockerfile for Clipboard Sync Desktop App
# Use this if you want to run the desktop app in Docker (headless mode only)

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    xvfb \
    x11-utils \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Linux-specific Python dependencies
RUN pip install --no-cache-dir python-magic>=0.4.27

# Copy application files
COPY . .

# Create logs directory
RUN mkdir -p logs

# Run in CLI mode (no GUI in Docker)
CMD ["python", "main.py", "--mode", "cli", "--name", "Docker-Desktop"]
