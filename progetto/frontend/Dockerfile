FROM python:3.11-slim

WORKDIR /app/frontend

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY templates/ ./templates/

EXPOSE 8000

CMD ["uvicorn", "src.frontend:app", "--host", "0.0.0.0", "--port", "8000"]