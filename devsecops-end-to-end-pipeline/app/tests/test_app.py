import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app import app  # noqa: E402


def client():
    app.config["TESTING"] = True
    return app.test_client()


def test_index_returns_200():
    c = client()
    resp = c.get("/")
    assert resp.status_code == 200
    assert resp.get_json()["message"] == "It works!"


def test_healthz_returns_healthy():
    c = client()
    resp = c.get("/healthz")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "healthy"


def test_metrics_endpoint_exposes_prometheus_format():
    c = client()
    resp = c.get("/metrics")
    assert resp.status_code == 200
    assert b"app_requests_total" in resp.data
