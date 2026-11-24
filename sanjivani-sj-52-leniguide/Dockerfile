FROM python:3.11-slim

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install curl for container health checks if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency specifications first for optimal layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user for security (Day 11 requirement)
RUN useradd -m -u 1000 leniguide && \
    chown -R leniguide:leniguide /app

# Copy application code, datasets, prompts, and evaluation suites
COPY --chown=leniguide:leniguide app/ ./app/
COPY --chown=leniguide:leniguide ui/ ./ui/
COPY --chown=leniguide:leniguide data/ ./data/
COPY --chown=leniguide:leniguide prompts/ ./prompts/
COPY --chown=leniguide:leniguide eval/ ./eval/
COPY --chown=leniguide:leniguide analysis/ ./analysis/
COPY --chown=leniguide:leniguide pyproject.toml .
COPY --chown=leniguide:leniguide README.md .

# Switch to non-root user
USER leniguide

# Expose default FastAPI backend port (overridden by $PORT on cloud hosts)
EXPOSE 8000

# Default command: start FastAPI backend server
# Cloud hosts (Render, HF Spaces) inject $PORT; locally defaults to 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
