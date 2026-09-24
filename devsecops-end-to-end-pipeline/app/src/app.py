"""
Sample microservice used as the deployable workload for the DevSecOps pipeline.
Deliberately simple — the point of this repo is the pipeline/security/infra around it,
not the business logic.
"""
import logging
import os
import time

from flask import Flask, jsonify
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("devsecops-app")

REQUEST_COUNT = Counter("app_requests_total", "Total requests", ["endpoint", "status"])
REQUEST_LATENCY = Histogram("app_request_latency_seconds", "Request latency", ["endpoint"])

APP_VERSION = os.getenv("APP_VERSION", "dev")


@app.route("/")
def index():
    start = time.time()
    response = jsonify(
        {
            "service": "devsecops-demo-app",
            "version": APP_VERSION,
            "message": "It works!",
        }
    )
    REQUEST_LATENCY.labels(endpoint="/").observe(time.time() - start)
    REQUEST_COUNT.labels(endpoint="/", status="200").inc()
    return response


@app.route("/healthz")
def healthz():
    """Kubernetes liveness/readiness probe target."""
    return jsonify({"status": "healthy"}), 200


@app.route("/metrics")
def metrics():
    """Prometheus scrape endpoint."""
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


if __name__ == "__main__":
    # Never run Flask's dev server in production — gunicorn is used in the Dockerfile (CMD).
    app.run(host="0.0.0.0", port=8080)
