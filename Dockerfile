# DocFlow image: runs the existing CLI (inventory.py) and the pytest suite.
FROM python:3.14-slim

# uv installs dependencies from pyproject.toml and uv.lock (pinned uv version).
COPY --from=ghcr.io/astral-sh/uv:0.13.8 /uv /bin/uv

# No .pyc files in the image, logs appear immediately, and uv uses the image's Python
# instead of downloading one and does not keep a download cache.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_NO_CACHE=1

# All commands run from /app, so relative paths like data/ and tests/ work as they do locally.
WORKDIR /app

# Install the locked dev dependency group first, so this layer is cached until the lock file changes.
# --locked fails the build if uv.lock is out of date instead of silently changing versions.
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --group dev --no-install-project

# Use the project's virtual environment for python and pytest.
ENV PATH="/app/.venv/bin:$PATH"

# Copy the project (filtered by .dockerignore).
COPY . .

# Run as a non-root user.
RUN useradd --create-home docflow
USER docflow

# Default: inventory summary of the sample data. Override the command to run anything else.
CMD ["python", "inventory.py", "data/sample_metadata.json"]
