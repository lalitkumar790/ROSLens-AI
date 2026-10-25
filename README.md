# ROSLens AI

**An open-source, safety-first debugging copilot for ROS 2 and Gazebo.**

ROSLens AI analyzes ROS 2 logs, surfaces evidence-backed diagnostic hypotheses, and recommends read-only checks. It combines deterministic diagnostic rules with an optional OpenAI-compatible LLM endpoint, so it can operate in heuristic-only mode or use a configured local/cloud model.

> **Status:** early MVP. Diagnoses are hypotheses, not confirmed root causes. Model inference, screenshot diagnosis, and broad real-world evaluation remain work in progress.

## Features

- Deterministic pattern matching for common ROS 2 / Gazebo errors: missing packages/executables, TF extrapolation, topic/QoS issues, node crashes, Gazebo resource paths and serial-device access.
- Evidence lines, explanatory hypotheses, next checks and suggested commands.
- Optional model-generated explanation using an OpenAI-compatible `/chat/completions` endpoint.
- Graceful fallback when the model isn't configured or unavailable.
- Browser UI, FastAPI API, sample logs and automated tests.
- Docker and GitHub Actions CI configuration.
- A small labelled synthetic diagnostic regression benchmark.

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

## Enable a model endpoint

Edit `.env`:

```dotenv
LLM_BASE_URL=http://localhost:11434/v1
LLM_MODEL=your-installed-model-name
LLM_API_KEY=ollama
LLM_TIMEOUT_SECONDS=45
MAX_LOG_CHARS=20000
```

The app appends `/chat/completions` to the base URL. Use a model name actually served by your endpoint. Without endpoint/model settings, deterministic diagnostics still work. Keep credentials out of git.

## API

- `GET /api/health`: app health and model configuration.
- `POST /api/diagnose`: JSON body with `log_text` and optional `use_ai`.

Example:

```json
{"log_text":"Package 'example_pkg' not found","use_ai":false}
```

The response includes `summary`, `diagnostics`, `signal_lines`, `input_lines`, `ai_used`, and optional AI status/explanation fields.

## Run tests and benchmark

```bash
pytest -q
python benchmarks/run_benchmark.py
```

The benchmark currently uses synthetic regression cases. Its score is not a real-world accuracy claim. See [docs/benchmarking.md](docs/benchmarking.md).

## Docker

```bash
docker compose up --build
```

Then open http://localhost:8000.

## Safety and privacy

- Logs are untrusted input. The model prompt directs the LLM not to follow instructions inside logs.
- ROSLens AI does not execute suggested shell commands.
- Treat AI output as a hypothesis and inspect commands before running them.
- Logs may contain hostnames, usernames, paths, network addresses or secrets. Redact sensitive material before sending logs to any remote model.
- Store API keys only in local environment configuration, never frontend code.
- See [SECURITY.md](SECURITY.md).

## Roadmap

- [x] Initial deterministic ROS diagnostics and web UI.
- [x] Synthetic labelled regression benchmark.
- [ ] Verify model inference against a real, configured Gemma endpoint.
- [ ] Add multimodal screenshot analysis with size/type/capability validation.
- [ ] Add reviewed, privacy-scrubbed real-world benchmark cases.
- [ ] Improve ROS distribution, middleware and simulator context.

## Contributing

Focused bug reports and pull requests are welcome. Please include a reproduction and tests where possible.

## License

MIT. See [LICENSE](LICENSE).
