# Backend environment (dev vs production)

The backend supports **two environments** via env files.

## 1. Development

- **Template:** `.env.development.example`  
  Copy to **`.env.development`** (or use a single **`.env`** with `ENVIRONMENT=development`).
- **Use for:** local runs, debugging, dev Supabase project.
- **Load order:** `.env` → `.env.development` (overrides).

## 2. Production

- **Template:** `.env.production.example`  
  On the server (or in CI/CD), create **`.env.production`** with real secrets.
- **Use for:** deployed app, production Supabase, real SMTP, strong `SECRET_KEY` and `CRON_SECRET`.
- **Load order:** `.env` → `.env.production` (overrides).

## How the app chooses the file

- Set **`ENVIRONMENT`** to `development` or `production`.
- If `ENVIRONMENT` is unset, it defaults to **development** and loads `.env.development`.
- You can set `ENVIRONMENT` in the env file itself (e.g. first line of `.env`: `ENVIRONMENT=development`) or in the shell/process.

## Quick start

**Local dev:**

```bash
cd backend
cp .env.development.example .env.development
# Edit .env.development and add your Supabase URL/key, etc.
# Optional: set ENVIRONMENT=development in .env or in the shell
python -m uvicorn app:app --reload
```

**Production (e.g. on server):**

- Create `.env.production` from `.env.production.example`.
- Set `ENVIRONMENT=production` (in the file or in the process).
- Never commit `.env`, `.env.development`, or `.env.production` (they are in `.gitignore`).
