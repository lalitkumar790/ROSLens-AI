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


def test_ollama_vision_payload_uses_data_url_string(monkeypatch):
    import asyncio
    from app import main

    monkeypatch.setenv("LLM_BASE_URL", "http://localhost:11434/v1")
    monkeypatch.setenv("LLM_MODEL", "gemma4:e4b")
    monkeypatch.setenv("LLM_VISION_FORMAT", "auto")
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"choices":[{"message":{"content":"visible error"}}]}

    class FakeClient:
        def __init__(self, timeout):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        async def post(self, url, **kwargs):
            captured["url"] = url
            captured["payload"] = kwargs["json"]
            return FakeResponse()

    monkeypatch.setattr(main.httpx, "AsyncClient", FakeClient)
    result = asyncio.run(main.ask_model_about_image(b"pngbytes", "image/png", "read it"))
    assert result == "visible error"
    image_part = captured["payload"]["messages"][1]["content"][1]
    assert image_part["type"] == "image_url"
    assert isinstance(image_part["image_url"], str)
    assert image_part["image_url"].startswith("data:image/png;base64,")


def test_openai_vision_payload_uses_url_object(monkeypatch):
    import asyncio
    from app import main

    monkeypatch.setenv("LLM_BASE_URL", "https://api.example.test/v1")
    monkeypatch.setenv("LLM_MODEL", "vision-model")
    monkeypatch.setenv("LLM_VISION_FORMAT", "auto")
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"choices":[{"message":{"content":"visible error"}}]}

    class FakeClient:
        def __init__(self, timeout):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        async def post(self, url, **kwargs):
            captured["payload"] = kwargs["json"]
            return FakeResponse()

    monkeypatch.setattr(main.httpx, "AsyncClient", FakeClient)
    result = asyncio.run(main.ask_model_about_image(b"pngbytes", "image/png", "read it"))
    assert result == "visible error"
    image_part = captured["payload"]["messages"][1]["content"][1]
    assert image_part["type"] == "image_url"
    assert image_part["image_url"]["url"].startswith("data:image/png;base64,")
