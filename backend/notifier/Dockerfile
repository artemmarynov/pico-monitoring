# notifier/Dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .
RUN groupadd --gid 1000 maker \
    && useradd --uid 1000 --gid 1000 --no-create-home maker \
    && pip3 install --no-cache-dir -r requirements.txt \
    && rm requirements.txt
COPY src/ /app

USER maker
CMD ["/usr/bin/env", "python3", "main.py"]

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD ["python3", "/app/healthcheck.py"] || exit 1