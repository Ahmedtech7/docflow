# DocFlow image: runs the existing CLI (inventory.py) and the pytest suite.
FROM python:3.14-slim

# No .pyc files in the image, and logs appear immediately.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# All commands run from /app, so relative paths like data/ and tests/ work as they do locally.
WORKDIR /app

# Install pinned dependencies first, so this layer is cached until requirements change.
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy the project (filtered by .dockerignore).
COPY . .

# Run as a non-root user.
RUN useradd --create-home docflow
USER docflow

# Default: inventory summary of the sample data. Override the command to run anything else.
CMD ["python", "inventory.py", "data/sample_metadata.json"]
