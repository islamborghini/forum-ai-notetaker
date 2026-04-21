# syntax=docker/dockerfile:1.7

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    XDG_CACHE_HOME=/root/.cache

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Separate ENV so apt cache above is preserved; these vars apply to every
# pip/sub-pip call below, including PEP 517 build-isolation subprocesses.
ENV PIP_DEFAULT_TIMEOUT=300 \
    PIP_RETRIES=10

COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install -r /app/backend/requirements.txt

# Preload Whisper base.en so first request is fast and works offline.
RUN python -c "import whisper; whisper.load_model('base.en')"

COPY backend /app/backend

RUN mkdir -p /app/data /app/backend/uploads

WORKDIR /app/backend

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "4", "--timeout", "600", "app:app"]
