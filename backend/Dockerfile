# Backend Dockerfile optimized for XTTS zero-shot cloning
# Uses Python 3.10 for better compatibility with Coqui TTS

FROM python:3.10-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# System deps for audio/TTS builds
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy backend sources
COPY . /app

# Install minimal dependencies for XTTS zero-shot cloning
# This avoids platform-specific packages from the full requirements.txt
COPY requirements-xtts.txt /app/requirements-xtts.txt
RUN python -m pip install --upgrade pip \
    && python -m pip install -r /app/requirements-xtts.txt

EXPOSE 8000

# Run the production server
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

