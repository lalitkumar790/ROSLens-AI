from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_homepage():
    response = client.get("/")
    assert response.status_code == 200
    assert "ROSLens" in response.text


def test_diagnose_without_ai():
    response = client.post("/api/diagnose", json={
        "log_text": "Package 'example_pkg' not found",
        "use_ai": False,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["ai_used"] is False
    assert data["diagnostics"][0]["id"] == "package-not-found"


def test_reject_empty_log():
    response = client.post("/api/diagnose", json={"log_text": "   ", "use_ai": False})
    assert response.status_code == 422


def test_reject_missing_log():
    response = client.post("/api/diagnose", json={"use_ai": False})
    assert response.status_code == 422
