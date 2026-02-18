-- Phase 2, Phase 3 & Tech: Activity logs, Comments, File/versioning, Colleges, Permissions, Chat, Security, Soft delete
-- Run after 002_phase1_notifications_and_review.sql

-- ========== PHASE 2 ==========

-- Activity logs / Audit trail
CREATE TABLE IF NOT EXISTS activity_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  userid VARCHAR(50) REFERENCES users(userid),
  action VARCHAR(50) NOT NULL,
  entity_type VARCHAR(50) NOT NULL,
  entity_id VARCHAR(255),
  payload JSONB,
  ip VARCHAR(45),
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_activity_logs_userid ON activity_logs(userid);
CREATE INDEX IF NOT EXISTS idx_activity_logs_entity ON activity_logs(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_activity_logs_created_at ON activity_logs(created_at DESC);

-- Task comments
CREATE TABLE IF NOT EXISTS task_comments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  assignment_id UUID NOT NULL REFERENCES task_assignments(assignment_id) ON DELETE CASCADE,
  userid VARCHAR(50) NOT NULL REFERENCES users(userid),
  comment TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_task_comments_assignment ON task_comments(assignment_id);

-- File: review_file_url and submission path for signed URL
ALTER TABLE task_assignments ADD COLUMN IF NOT EXISTS review_file_url TEXT;
ALTER TABLE task_assignments ADD COLUMN IF NOT EXISTS submission_file_path TEXT;

CREATE TABLE IF NOT EXISTS task_submission_versions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  assignment_id UUID NOT NULL REFERENCES task_assignments(assignment_id) ON DELETE CASCADE,
  file_url TEXT NOT NULL,
  version INT NOT NULL DEFAULT 1,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_task_submission_versions_assignment ON task_submission_versions(assignment_id);

-- ========== PHASE 3 ==========

-- Colleges (multi-tenant)
CREATE TABLE IF NOT EXISTS colleges (
  collegeid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  code VARCHAR(50) UNIQUE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add collegeid to users and projects (nullable for migration; default college later)
ALTER TABLE users ADD COLUMN IF NOT EXISTS collegeid UUID REFERENCES colleges(collegeid);
ALTER TABLE projects ADD COLUMN IF NOT EXISTS collegeid UUID REFERENCES colleges(collegeid);
CREATE INDEX IF NOT EXISTS idx_users_collegeid ON users(collegeid);
CREATE INDEX IF NOT EXISTS idx_projects_collegeid ON projects(collegeid);

-- Role permissions
CREATE TABLE IF NOT EXISTS role_permissions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  role VARCHAR(50) NOT NULL,
  resource VARCHAR(50) NOT NULL,
  action VARCHAR(50) NOT NULL,
  UNIQUE(role, resource, action)
);
CREATE INDEX IF NOT EXISTS idx_role_permissions_role ON role_permissions(role);

-- Chat: conversations and messages
CREATE TABLE IF NOT EXISTS conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  mentor_userid VARCHAR(50) NOT NULL REFERENCES users(userid),
  student_userid VARCHAR(50) NOT NULL REFERENCES users(userid),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(mentor_userid, student_userid)
);
CREATE TABLE IF NOT EXISTS messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
  sender_userid VARCHAR(50) NOT NULL REFERENCES users(userid),
  body TEXT NOT NULL,
  read_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_conversations_mentor ON conversations(mentor_userid);
CREATE INDEX IF NOT EXISTS idx_conversations_student ON conversations(student_userid);

-- ========== TECH: Security & Soft delete ==========

-- Account lock (failed login)
ALTER TABLE users ADD COLUMN IF NOT EXISTS failed_login_attempts INT NOT NULL DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS locked_until TIMESTAMPTZ;

-- Soft delete
ALTER TABLE users ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
ALTER TABLE projects ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
ALTER TABLE modules ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
CREATE INDEX IF NOT EXISTS idx_users_deleted_at ON users(deleted_at);
CREATE INDEX IF NOT EXISTS idx_projects_deleted_at ON projects(deleted_at);
CREATE INDEX IF NOT EXISTS idx_modules_deleted_at ON modules(deleted_at);
CREATE INDEX IF NOT EXISTS idx_tasks_deleted_at ON tasks(deleted_at);
