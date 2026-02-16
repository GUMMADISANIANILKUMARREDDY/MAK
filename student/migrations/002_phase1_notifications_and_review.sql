-- Phase 1: Notifications + Task Review + Search indexes
-- Run in Supabase SQL editor after 001_auth_and_submissions.sql

-- 1. NOTIFICATIONS TABLE
CREATE TABLE IF NOT EXISTS notifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  userid VARCHAR(50) NOT NULL REFERENCES users(userid) ON DELETE CASCADE,
  type VARCHAR(50) NOT NULL,
  title VARCHAR(255) NOT NULL,
  message TEXT,
  link TEXT,
  read BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_notifications_userid_read ON notifications(userid, read);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at DESC);

-- 2. TASK REVIEW COLUMNS (Option B: on task_assignments)
-- submission_file_url added in 001_auth_and_submissions.sql
ALTER TABLE task_assignments ADD COLUMN IF NOT EXISTS review_result VARCHAR(50);
ALTER TABLE task_assignments ADD COLUMN IF NOT EXISTS review_feedback TEXT;
ALTER TABLE task_assignments ADD COLUMN IF NOT EXISTS review_score INT;
ALTER TABLE task_assignments ADD COLUMN IF NOT EXISTS reviewed_at TIMESTAMPTZ;
ALTER TABLE task_assignments ADD COLUMN IF NOT EXISTS reviewed_by VARCHAR(50) REFERENCES users(userid);

-- 3. INDEXES FOR SEARCH/FILTERS
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);
CREATE INDEX IF NOT EXISTS idx_task_assignments_status ON task_assignments(status);
CREATE INDEX IF NOT EXISTS idx_modules_status ON modules(status);
dd