from unittest.mock import AsyncMock

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
    response = client.post("/api/diagnose", json={"log_text":"Package 'example_pkg' not found","use_ai":False})
    assert response.status_code == 200
    data = response.json()
    assert data["ai_used"] is False
    assert data["diagnostics"][0]["id"] == "package-not-found"


def test_reject_empty_log():
    response = client.post("/api/diagnose", json={"log_text":"   ","use_ai":False})
    assert response.status_code == 422


def test_reject_missing_log():
    response = client.post("/api/diagnose", json={"use_ai":False})
    assert response.status_code == 422


def test_reject_too_large_log():
    response = client.post("/api/diagnose", json={"log_text":"x"*21000,"use_ai":False})
    assert response.status_code == 422


def test_image_requires_vision_model(monkeypatch):
    monkeypatch.delenv("LLM_BASE_URL", raising=False)
    monkeypatch.delenv("LLM_MODEL", raising=False)
    response = client.post("/api/diagnose-image", files={"image":("screen.png",b"\\x89PNG\\r\\n\\x1a\\n" + b"x","image/png")})
    assert response.status_code == 503


def test_reject_unsupported_image_type():
    response = client.post("/api/diagnose-image", files={"image":("file.txt",b"hello","text/plain")})
    assert response.status_code == 415


def test_reject_image_with_mismatched_signature(monkeypatch):
    monkeypatch.setenv("LLM_BASE_URL", "http://localhost:11434/v1")
    monkeypatch.setenv("LLM_MODEL", "gemma4:e4b")
    response = client.post("/api/diagnose-image", files={"image":("fake.png",b"not really png","image/png")})
    assert response.status_code == 415


def test_successful_image_diagnosis_uses_ollama_format(monkeypatch):
    monkeypatch.setenv("LLM_BASE_URL", "http://localhost:11434/v1")
    monkeypatch.setenv("LLM_MODEL", "gemma4:e4b")
    mock = AsyncMock(return_value="The screenshot shows a ROS launch error.")
    monkeypatch.setattr("app.main.ask_model_about_image", mock)
    png = b"\\x89PNG\\r\\n\\x1a\\n" + b"fake-image-payload"
    response = client.post(
        "/api/diagnose-image",
        data={"question":"Focus on the launch error"},
        files={"image":("screen.png",png,"image/png")},
    )
    assert response.status_code == 200
    assert response.json()["ai_used"] is True
    assert response.json()["ai_explanation"] == "The screenshot shows a ROS launch error."
    mock.assert_awaited_once()
