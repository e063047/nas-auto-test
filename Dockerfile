FROM python:3.11-slim

WORKDIR /app

# System deps for Playwright (Chromium) — needed only for real test mode
RUN apt-get update && apt-get install -y \
    libglib2.0-0 libnss3 libnspr4 libdbus-1-3 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libxkbcommon0 libatspi2.0-0 libx11-6 libxcomposite1 libxdamage1 \
    libxext6 libxfixes3 libxrandr2 libgbm1 libdrm2 libpango-1.0-0 libcairo2 \
    libasound2 wget curl \
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright + Chromium
RUN playwright install chromium --with-deps

# Copy application
COPY backend/ /app/backend/
COPY frontend/ /app/frontend/
COPY demo/ /app/demo/

WORKDIR /app/backend

# Create runtime dirs
RUN mkdir -p /app/reports/screenshots

EXPOSE 8000

# Railway injects $PORT; fall back to 8000 for local Docker runs
CMD ["sh", "-c", "python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
