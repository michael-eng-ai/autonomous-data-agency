FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Install the package in editable mode
RUN pip install -e .

# Create directory for local database
RUN mkdir -p /app/data

# Environment variables
ENV PYTHONUNBUFFERED=1

# Entry point
ENTRYPOINT ["python", "cli.py"]
CMD ["--help"]
