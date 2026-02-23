-- Pending chat emails: delay email by 5 min, only send if message still unread
-- Run after 004_push_subscriptions.sql

CREATE TABLE IF NOT EXISTS pending_chat_emails (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  message_id UUID NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
  recipient_userid VARCHAR(50) NOT NULL REFERENCES users(userid) ON DELETE CASCADE,
  sender_username VARCHAR(100) NOT NULL,
  message_preview TEXT NOT NULL,
  link TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_pending_chat_emails_created_at ON pending_chat_emails(created_at);
