# CI/CD

This folder documents CI/CD for the MAK (InternHub) repo. Pipelines run on **GitHub Actions**.

**→ Configure GitHub (secrets, branch protection):** [.github/CONFIG.md](../.github/CONFIG.md)

## Workflows

| Workflow        | Path                           | Triggers                    | What it does                          |
|----------------|---------------------------------|-----------------------------|---------------------------------------|
| **Backend CI** | `.github/workflows/backend-ci.yml` | Push/PR to `main`/`develop` (backend changes) | Test (pytest), Lint (ruff), Docker build |
| **Frontend CI**| `.github/workflows/frontend-ci.yml` | Push/PR to `main`/`develop` (frontend changes) | `npm ci` + `npm run build`              |

## Running locally (same as CI)

- **Backend** (from repo root):
  ```bash
  cd backend
  pip install -r requirements.txt -r requirements-dev.txt
  pytest -v --tb=short
  ```
- **Frontend** (from repo root):
  ```bash
  cd frontend
  npm ci
  npm run build
  ```

## Production / deploy

- **Backend**: Build and run with Docker; see `backend/BUILD.md` and `backend/Dockerfile`. Use env vars or `.env` for `SUPABASE_*` and other config.
- **Frontend**: Build artifact is `frontend/dist/`. Serve with any static host (e.g. Nginx, S3+CloudFront, Vercel).

## Secrets (GitHub)

For backend tests that hit real Supabase (optional), set in repo **Settings → Secrets and variables → Actions**:

- `SUPABASE_URL`
- `SUPABASE_SERVICE_KEY`

If unset, CI uses placeholders; tests that only use overrides will still pass.
