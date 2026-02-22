-- Web Push: store push subscriptions per user for offline/closed-tab notifications
-- Run after 003_phase2_phase3_and_tech.sql

CREATE TABLE IF NOT EXISTS push_subscriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  userid VARCHAR(50) NOT NULL REFERENCES users(userid) ON DELETE CASCADE,
  endpoint TEXT NOT NULL,
  p256dh TEXT NOT NULL,
  auth TEXT NOT NULL,
  user_agent TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(userid, endpoint)
);
CREATE INDEX IF NOT EXISTS idx_push_subscriptions_userid ON push_subscriptions(userid);
