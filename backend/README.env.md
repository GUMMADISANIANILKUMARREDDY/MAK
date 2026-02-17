# Backend environment

The backend uses a single **`.env`** file for all environments (dev and production).

## Setup

1. Copy the example and add your values:

```bash
cd backend
cp .env.example .env
# Edit .env and set SUPABASE_URL, SUPABASE_KEY, SECRET_KEY, etc.
```

2. For production (e.g. Render), set the same variables in the host’s environment (or a single `.env`); use a strong `SECRET_KEY` and real SMTP/CORS values.

## Variables

- **ENVIRONMENT** – `development` or `production` (optional; affects defaults like DEBUG).
- **DEBUG** – `true` or `false`.
- **SUPABASE_URL**, **SUPABASE_KEY** – from your Supabase project.
- **SECRET_KEY** – JWT signing; must be strong and random in production.
- **CORS_ORIGINS** – comma-separated frontend origins or `*`.
- **SMTP_***, **EMAIL_FROM** – for OTP and password reset emails.

Do not commit `.env`; it is in `.gitignore`.
