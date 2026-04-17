FROM python:3.11-slim

WORKDIR /app/backend

RUN apt-get update && apt-get install -y \
    libgbm-dev \
    libasound2 \
    libnss3 \
    libxss1 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libpango-1.0-0 \
    libcairo2 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN python -m playwright install chromium
RUN python -m playwright install-deps chromium

COPY src/ ./src/

EXPOSE 8003

CMD ["uvicorn", "src.server:app", "--host", "0.0.0.0", "--port", "8003","--reload"]