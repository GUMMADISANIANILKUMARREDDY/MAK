# Backend folder structure (production)

```
backend/
├── app.py              # FastAPI app, middleware, router includes
├── main.py             # CLI entry: uvicorn app:app
├── config/             # Settings (env, CORS, etc.)
├── api/                # Routes and dependencies
│   └── routes/         # Route modules (auth, admin_*, dashboard, …)
├── services/           # Business logic
├── schemas/            # Pydantic models (if present)
├── utils/              # Helpers (if present)
├── db/                 # DB access (if present)
├── requirements.txt    # Runtime deps (Docker, venv)
├── requirements-dev.txt
├── pyproject.toml      # Package metadata + deps (wheel build)
├── Dockerfile          # Production image (no tests in image)
├── .dockerignore       # Excludes venv, tests, .env from image
├── BUILD.md            # How to build wheel and Docker
├── STRUCTURE.md        # This file
└── tests/              # Pytest (not in Docker image)
    ├── conftest.py     # Fixtures, TestClient, auth overrides
    └── test_*.py
```

**Production image** (Docker) contains only runtime code and `requirements.txt`; no `tests/`, no `.env`, no venv.
