# Building the Backend

This backend is **Python** (FastAPI). There is no JAR (JAR is for Java). You can build it as:

- **Python wheel (`.whl`)** – installable package
- **Docker image** – container for deployment

---

## Dependency files: requirements.txt vs pyproject.toml

| File | Purpose | Required? |
|------|---------|-----------|
| **requirements.txt** | `pip install -r requirements.txt` — used by Docker, venv, CI. Runtime deps only. | No, but keep it for Docker and simple installs. |
| **requirements-dev.txt** | Dev/test deps (pytest, httpx, build). Use: `pip install -r requirements.txt -r requirements-dev.txt`. | No. Optional for running tests. |
| **pyproject.toml** | Package metadata + dependencies for building the wheel (`python -m build`) and `pip install -e .`. | Yes, if you build the `.whl`. |

**Both are not required** for every workflow: use **requirements.txt** when you only run the app (e.g. Docker, venv). Use **pyproject.toml** when you build the package or install in editable mode. We keep both and sync their dependency lists.

---

## 1. Build a Python wheel (`.whl`)

From the `backend` directory:

```bash
# Install build tool once
pip install build

# Build wheel and source distribution
python -m build
```

Output in `dist/`:

- `internhub_backend-1.0.0-py3-none-any.whl`  ← wheel
- `internhub_backend-1.0.0.tar.gz`             ← source distribution

### Install and run from the wheel

```bash
# Create a venv, then install the wheel
pip install dist/internhub_backend-1.0.0-py3-none-any.whl

# Run the server (entry point)
internhub-serve
```

Or run with uvicorn after install:

```bash
uvicorn app:app --host 0.0.0.0 --port 8001
```

---

## 2. Build a Docker image

From the `backend` directory (or repo root with `-f backend/Dockerfile`):

```bash
docker build -t internhub-backend:1.0 .
```

Run the container:

```bash
docker run -p 8001:8001 --env-file .env internhub-backend:1.0
```

Use your own `.env` or pass variables with `-e` for production.

---

## Summary

| Output   | Command                    | Use case              |
|----------|----------------------------|------------------------|
| `.whl`   | `python -m build`           | Install via pip       |
| Docker   | `docker build -t name .`    | Deploy as container   |
