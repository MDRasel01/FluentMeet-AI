FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Install dependencies
RUN pip install --no-cache-dir \
    celery \
    redis \
    pydantic \
    pydantic-settings

# Copy source code
COPY . .

CMD ["celery", "-A", "app.celery_app", "worker", "--loglevel=info"]

