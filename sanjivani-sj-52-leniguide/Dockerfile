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

# Copy application code, datasets, prompts, and evaluation suites
COPY app/ ./app/
COPY ui/ ./ui/
COPY data/ ./data/
COPY prompts/ ./prompts/
COPY eval/ ./eval/
COPY analysis/ ./analysis/
COPY pyproject.toml .
COPY README.md .

# Expose FastAPI backend (8000) and Streamlit UI (8501) ports
EXPOSE 8000 8501

# Default command: start FastAPI backend server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
