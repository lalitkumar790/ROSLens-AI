# ROSLens AI

**An open-source, safety-first debugging copilot for ROS 2 and Gazebo.**

ROSLens AI analyzes ROS 2 logs, surfaces evidence-backed diagnostic hypotheses, and recommends read-only checks. It combines deterministic diagnostic rules with an optional OpenAI-compatible LLM endpoint, so it can operate in heuristic-only mode or use a configured local/cloud model.

> **Status:** early MVP. Diagnoses are hypotheses, not confirmed root causes. Model inference, screenshot diagnosis, and broad real-world evaluation remain work in progress.

## Features

- Deterministic pattern matching for common ROS 2 / Gazebo errors:
  - missing packages and executables
  - TF extrapolation and clock mismatches
  - topic publisher / QoS issues
  - node crashes
  - Gazebo resources
  - serial-device access
- Evidence lines, explanatory hypotheses, next checks and suggested commands.
- Optional model-generated explanation using an OpenAI-compatible `/chat/completions` endpoint.
- Graceful fallback when the model isn't configured or unavailable.
- Small browser UI, FastAPI API, sample logs and automated tests.
- Docker and GitHub Actions CI configuration.

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

Open http://127.0.0.1:8000. API docs: http://127.0.0.1:8000/docs.

On Windows, create the environment file with `Copy-Item .env.example .env` instead of `cp`.

## Enable a model endpoint

Edit `.env`:

```dotenv
LLM_BASE_URL=http://localhost:11434/v1
LLM_MODEL=your-installed-model-name
LLM_API_KEY=ollama
LLM_TIMEOUT_SECONDS=45
MAX_LOG_CHARS=20000
```

The base URL should be the OpenAI-compatible API root; the app appends `/chat/completions`. Use a model name actually served by your selected endpoint. Keep credentials in the local `.env` and never commit secrets. Without endpoint/model settings, deterministic diagnostics still work.

## API

`GET /api/health` reports app health and whether a model endpoint is configured.

`POST /api/diagnose` request:

```json
{
  "log_text": "Package 'example_pkg' not found",
  "use_ai": false
}
```

The response contains `summary`, `diagnostics`, `signal_lines`, `input_lines`, `ai_used`, and optional AI status/explanation fields.

## Docker

```bash
docker compose up --build
```

Then open http://localhost:8000.

## Tests

```bash
pytest -q
```

The tests cover known log signatures and API behavior. They are not a proof of model accuracy. A labelled benchmark and evaluation protocol are planned.

## Safety and privacy

- Logs are untrusted input. The model prompt directs the LLM not to follow instructions inside logs.
- ROSLens AI does not execute suggested shell commands.
- Treat AI output as a hypothesis and inspect commands before running them.
- Logs may contain hostnames, usernames, paths, network addresses or secrets. Redact sensitive material before sending logs to any remote model.
- Configure API keys only through environment variables; never expose them in frontend code.
- See [SECURITY.md](SECURITY.md).

## Roadmap

- [ ] Add a labelled diagnostic benchmark with per-class precision/recall and reproducible evaluation.
- [ ] Validate Gemma through a real compatible endpoint and document tested model IDs.
- [ ] Add multimodal screenshot analysis with MIME, size and endpoint capability validation.
- [ ] Improve ROS 2 distribution / Gazebo-version context and user-visible confidence calibration.
- [ ] Add Docker-based smoke testing and deploy a public demo.

## Contributing

Issues and focused pull requests are welcome. Please include a reproduction, expected behaviour, and tests where possible.

## License

MIT. See [LICENSE](LICENSE).
