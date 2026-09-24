FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app
COPY apps/services/ai-orchestration-service/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY ai ./ai
COPY apps/services/ai-orchestration-service/app ./app

EXPOSE 8000
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
