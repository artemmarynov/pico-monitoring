FROM python:3.13-slim@sha256:e48f59cdba69a3cbd9ed2cf0f348d90d45a8d350d98134cf1070bc106ee9ed90
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY backend/api/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && useradd --uid 10001 --create-home app
COPY backend/api /app/api
COPY backend/common /app/common
COPY scripts /app/scripts
COPY migrations /app/migrations
USER app
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
