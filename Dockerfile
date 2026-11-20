# Build from repository root: docker build -f phase-4/Dockerfile .
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PULSEIQ_DB_PATH=/app/phase-3/outputs/pulseiq.duckdb
WORKDIR /app
COPY phase-4/requirements.txt /app/phase-4/requirements.txt
RUN pip install --no-cache-dir -r /app/phase-4/requirements.txt
COPY phase-3/outputs/pulseiq.duckdb /app/phase-3/outputs/pulseiq.duckdb
COPY phase-4/ /app/phase-4/
WORKDIR /app/phase-4
EXPOSE 8000 8501
CMD ["uvicorn","api:app","--host","0.0.0.0","--port","8000"]
