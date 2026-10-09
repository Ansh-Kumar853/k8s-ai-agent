from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_and_readiness_endpoints():
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/ready").json() == {"status": "ready"}


def test_analyze_endpoint_returns_explainable_findings():
    response = client.post("/analyze", json={
        "cluster": "test-cluster",
        "namespace": "payments",
        "workload": "checkout-api",
        "desired_replicas": 3,
        "available_replicas": 1,
        "restart_count": 8,
        "cpu_percent": 94,
        "memory_percent": 65,
        "probe_failures": 2,
    })
    assert response.status_code == 200
    body = response.json()
    assert body["status"] in {"degraded", "critical"}
    assert body["findings"]
    assert all("recommendation" in finding for finding in body["findings"])


def test_analyze_endpoint_rejects_unknown_fields():
    response = client.post("/analyze", json={
        "workload": "api", "desired_replicas": 1,
        "available_replicas": 1, "unexpected": True,
    })
    assert response.status_code == 422
