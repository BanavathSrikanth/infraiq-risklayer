FROM python:3.12-slim
WORKDIR /service
COPY apps/services/integration-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY apps/services/integration-service .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
