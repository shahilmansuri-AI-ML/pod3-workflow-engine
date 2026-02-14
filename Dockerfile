FROM python:3.11-slim

# Prevent Python from writing pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# System deps (minimal)
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY runtime ./runtime
COPY adapters ./adapters
COPY agents ./agents
COPY db ./db
COPY api ./api

# Set Python path
ENV PYTHONPATH=/app

# Default command: run one execution
CMD ["python", "runtime/coordinator.py"]
