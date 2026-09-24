# --- Stage 1: build dependencies in an isolated layer ---
FROM python:3.12-slim AS builder

WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# --- Stage 2: minimal runtime image ---
FROM python:3.12-slim AS runtime

# Security hardening:
# 1. Run as a non-root, unprivileged user (never root inside the container)
# 2. Copy only the installed packages + app source — no build tools in the final image
# 3. Pin the base image tag (never use `latest`) so builds are reproducible and scannable
RUN groupadd -r appgroup && useradd -r -g appgroup -u 1001 appuser

WORKDIR /app
COPY --from=builder /root/.local /home/appuser/.local
COPY src/ ./src/

ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1

RUN chown -R appuser:appgroup /app
USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/healthz')" || exit 1

# gunicorn, not `flask run` — production-grade WSGI server
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--chdir", "src", "app:app"]
