FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python deps
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy source
COPY . .

EXPOSE 8000

# Use gunicorn to run the Flask app via the factory. Use shell form so $PORT is expanded
# Default to 8000 if PORT not provided by the environment (e.g., Render sets PORT).
CMD ["sh", "-c", "gunicorn \"app:create_app()\" -w 4 -b 0.0.0.0:${PORT:-8000} --log-level info"]
