-- Run this in your Supabase SQL editor to add tables/columns for new features.
-- Refresh tokens (for /auth/refresh)
CREATE TABLE IF NOT EXISTS refresh_tokens (
  id BIGSERIAL PRIMARY KEY,
  userid TEXT NOT NULL REFERENCES users(userid) ON DELETE CASCADE,
  token_hash TEXT NOT NULL UNIQUE,
  expires_at TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_refresh_tokens_token_hash ON refresh_tokens(token_hash);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_expires_at ON refresh_tokens(expires_at);

-- Password reset OTPs (for /auth/forgot-password and /auth/reset-password)
CREATE TABLE IF NOT EXISTS password_reset_otps (
  email TEXT NOT NULL PRIMARY KEY,
  otp TEXT NOT NULL,
  expires_at TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Task submission file URL (for student task submit with attachment)
ALTER TABLE task_assignments
  ADD COLUMN IF NOT EXISTS submission_file_url TEXT;

-- Storage bucket: create "task-submissions" in Supabase Dashboard > Storage if not exists.
-- Set bucket to public if you want public URLs, or use signed URLs in code.
