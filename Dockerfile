# Build from the repository root: docker build -t pulseiq-phase4 .
# Mount the approved Phase 3 warehouse at /data/pulseiq.duckdb at runtime.
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PULSEIQ_DB_PATH=/data/pulseiq.duckdb
WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY api.py access_control.py ./
COPY phase4_complete ./phase4_complete
COPY docs ./docs
EXPOSE 8000
CMD ["uvicorn","api:app","--host","0.0.0.0","--port","8000"]
