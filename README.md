# ROSLens AI

**An open-source, safety-first debugging copilot for ROS 2 and Gazebo.**

ROSLens AI analyzes ROS 2 logs, surfaces evidence-backed diagnostic hypotheses, and recommends read-only checks. It combines deterministic diagnostic rules with an optional OpenAI-compatible LLM endpoint.

> **Status:** early MVP. Diagnoses are hypotheses, not confirmed root causes. Text-model inference and screenshot diagnosis need validation against a real vision-capable endpoint.

## Features

- Deterministic matching for missing packages and executables, TF extrapolation, topic/QoS issues, node crashes, Gazebo resources and serial access.
- Evidence lines, explanations, next checks and suggested commands.
- Optional OpenAI-compatible text model explanation with graceful fallback.
- Screenshot analysis for PNG/JPEG/WebP with file-size and signature checks; supports Ollama/OpenAI-compatible vision payload formats and requires a vision-capable model endpoint.
- Browser UI, FastAPI API, sample logs, tests, Docker and GitHub Actions CI.
- Small labelled synthetic regression benchmark.

## Quick start

Python 3.10+ recommended.

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env
python -m uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000. API docs: http://127.0.0.1:8000/docs. On Windows use `Copy-Item .env.example .env`.

## Configure a model endpoint

Set in `.env`:

```dotenv
LLM_BASE_URL=http://localhost:11434/v1
LLM_MODEL=your-installed-model-name
LLM_API_KEY=ollama
LLM_TIMEOUT_SECONDS=45
MAX_LOG_CHARS=20000
MAX_IMAGE_BYTES=5242880
LLM_VISION_FORMAT=auto
```

The app appends `/chat/completions` to the base URL. Use a model name actually served by your endpoint. `LLM_VISION_FORMAT=auto` selects Ollama-style image payloads for URLs containing `ollama` or port `11434`, and OpenAI-style payloads otherwise. Override with `ollama` or `openai` if needed. For local Ollama, install Ollama, run `ollama pull gemma4:e4b`, then use `LLM_BASE_URL=http://localhost:11434/v1` and `LLM_MODEL=gemma4:e4b`. Text-only models cannot analyze screenshots. When running ROSLens in Docker on Docker Desktop, use `http://host.docker.internal:11434/v1` rather than `localhost` so the container can reach the host model server; confirm Ollama is listening on an address reachable from Docker. Without endpoint/model settings, deterministic diagnostics still work. Never commit secrets.

## API

- `GET /api/health`: health and model configuration.
- `POST /api/diagnose`: JSON with `log_text` and optional `use_ai`.
- `POST /api/diagnose-image`: multipart image field `image` plus optional `question`; accepts PNG/JPEG/WebP, up to 5 MiB by default. ROSLens does not intentionally persist uploaded images to the project directory. FastAPI's upload handling may temporarily spool files to system temporary storage; the image is then sent to your configured model endpoint. A configured vision-capable model is required.

Example: `{"log_text":"Package 'example_pkg' not found","use_ai":false}`.

## Tests and benchmark

```bash
pytest -q
python benchmarks/run_benchmark.py
```

The benchmark currently contains synthetic regression cases only. Its score is not a real-world accuracy claim. See [docs/benchmarking.md](docs/benchmarking.md).

## Docker

```bash
docker compose up --build
```

Then open http://localhost:8000.

## Safety and privacy

- Logs are untrusted input; the prompt tells the model not to follow instructions embedded in logs.
- ROSLens AI never executes suggested shell commands.
- Treat AI output as a hypothesis and review commands before running them.
- Logs may contain hostnames, usernames, paths, network addresses or secrets. Redact them before sending logs to a remote model.
- Store API keys only in local environment configuration, never in frontend code.
- See [SECURITY.md](SECURITY.md).

## Roadmap

- [x] Initial deterministic ROS diagnostics and web UI.
- [x] Synthetic labelled regression benchmark.
- [ ] Validate a real Gemma-compatible endpoint.
- [x] Add screenshot endpoint and browser controls with type/size checks (requires a vision-capable model).
- [ ] Add reviewed, permissioned and privacy-scrubbed real-world benchmark cases.
- [ ] Improve ROS distribution, middleware and simulator context.

## Contributing

Focused bug reports and pull requests are welcome. Include reproduction steps and tests when possible.

## License

MIT. See [LICENSE](LICENSE).
