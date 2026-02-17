-- ============================================================================
-- MAK Backend - Complete Database Schema
-- Run in Supabase SQL Editor. Run in order (top to bottom).
-- ============================================================================

-- ============================================================================
-- OPTIONAL: Migration from UUID userid to VARCHAR (run only if needed)
-- DROPS users and students - BACKUP data first!
-- ============================================================================
-- DROP TABLE IF EXISTS students CASCADE;
-- DROP TABLE IF EXISTS users CASCADE;

-- ============================================================================
-- 1. USERS
-- Roles: student, mentor, clgadmin, admin, manager
-- Password: bcrypt hash only, never plain text
-- ============================================================================
CREATE TABLE IF NOT EXISTS users (
  userid VARCHAR(50) PRIMARY KEY,
  username VARCHAR(100) NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  role VARCHAR(50) NOT NULL DEFAULT 'student',
  active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================================
-- 2. STUDENTS (userid = roll number, links to users.userid)
-- ============================================================================
CREATE TABLE IF NOT EXISTS students (
  studentid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  userid VARCHAR(50) UNIQUE NOT NULL REFERENCES users(userid) ON DELETE CASCADE,
  first_name VARCHAR(100) NOT NULL,
  last_name VARCHAR(100) NOT NULL,
  phone VARCHAR(20) NOT NULL,
  email VARCHAR(255) NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================================
-- 3. PENDING REGISTRATIONS (until email OTP verified)
-- ============================================================================
CREATE TABLE IF NOT EXISTS pending_registrations (
  email VARCHAR(255) PRIMARY KEY,
  userid VARCHAR(50) NOT NULL,
  first_name VARCHAR(100) NOT NULL,
  last_name VARCHAR(100) NOT NULL,
  phone VARCHAR(20) NOT NULL,
  password VARCHAR(255) NOT NULL,
  otp VARCHAR(6) NOT NULL,
  expires_at TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================================
-- 4. REFRESH TOKENS (for /auth/refresh)
-- ============================================================================
CREATE TABLE IF NOT EXISTS refresh_tokens (
  id BIGSERIAL PRIMARY KEY,
  userid TEXT NOT NULL REFERENCES users(userid) ON DELETE CASCADE,
  token_hash TEXT NOT NULL UNIQUE,
  expires_at TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_token_hash ON refresh_tokens(token_hash);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_expires_at ON refresh_tokens(expires_at);

-- ============================================================================
-- 5. PASSWORD RESET OTPs (for forgot-password and reset-password)
-- ============================================================================
CREATE TABLE IF NOT EXISTS password_reset_otps (
  email TEXT NOT NULL PRIMARY KEY,
  otp TEXT NOT NULL,
  expires_at TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 6. PROJECT MANAGEMENT - Projects (Admin creates)
-- ============================================================================
CREATE TABLE IF NOT EXISTS projects (
  projectid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title VARCHAR(255) NOT NULL,
  description TEXT,
  created_by VARCHAR(50) NOT NULL REFERENCES users(userid),
  status VARCHAR(50) NOT NULL DEFAULT 'active',
  start_date DATE,
  end_date DATE,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================================
-- 7. PROJECT ASSIGNMENTS (Admin assigns to Manager)
-- ============================================================================
CREATE TABLE IF NOT EXISTS project_assignments (
  assignment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  projectid UUID NOT NULL REFERENCES projects(projectid) ON DELETE CASCADE,
  manager_userid VARCHAR(50) NOT NULL REFERENCES users(userid),
  assigned_by VARCHAR(50) NOT NULL REFERENCES users(userid),
  assigned_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================================
-- 8. MODULES (Manager creates within Project)
-- ============================================================================
CREATE TABLE IF NOT EXISTS modules (
  moduleid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  projectid UUID NOT NULL REFERENCES projects(projectid) ON DELETE CASCADE,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  created_by VARCHAR(50) NOT NULL REFERENCES users(userid),
  status VARCHAR(50) NOT NULL DEFAULT 'pending',
  priority VARCHAR(50) DEFAULT 'medium',
  due_date DATE,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================================
-- 9. MODULE ASSIGNMENTS (Manager assigns to Mentor)
-- ============================================================================
CREATE TABLE IF NOT EXISTS module_assignments (
  assignment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  moduleid UUID NOT NULL REFERENCES modules(moduleid) ON DELETE CASCADE,
  mentor_userid VARCHAR(50) NOT NULL REFERENCES users(userid),
  assigned_by VARCHAR(50) NOT NULL REFERENCES users(userid),
  assigned_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================================
-- 10. TEAMS (Mentor creates student teams)
-- ============================================================================
CREATE TABLE IF NOT EXISTS teams (
  teamid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  team_name VARCHAR(255) NOT NULL,
  mentor_userid VARCHAR(50) NOT NULL REFERENCES users(userid),
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================================
-- 11. TEAM MEMBERS (Students in a team)
-- ============================================================================
CREATE TABLE IF NOT EXISTS team_members (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  teamid UUID NOT NULL REFERENCES teams(teamid) ON DELETE CASCADE,
  student_userid VARCHAR(50) NOT NULL REFERENCES users(userid),
  added_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(teamid, student_userid)
);

-- ============================================================================
-- 12. TASKS (Mentor creates within Module)
-- ============================================================================
CREATE TABLE IF NOT EXISTS tasks (
  taskid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  moduleid UUID NOT NULL REFERENCES modules(moduleid) ON DELETE CASCADE,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  task_type VARCHAR(50) DEFAULT 'task',
  created_by VARCHAR(50) NOT NULL REFERENCES users(userid),
  priority VARCHAR(50) DEFAULT 'medium',
  story_points INT DEFAULT 0,
  status VARCHAR(50) NOT NULL DEFAULT 'backlog',
  due_date DATE,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================================
-- 13. TASK ASSIGNMENTS (Mentor assigns to Student)
-- ============================================================================
CREATE TABLE IF NOT EXISTS task_assignments (
  assignment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  taskid UUID NOT NULL REFERENCES tasks(taskid) ON DELETE CASCADE,
  student_userid VARCHAR(50) NOT NULL REFERENCES users(userid),
  assigned_by VARCHAR(50) NOT NULL REFERENCES users(userid),
  status VARCHAR(50) NOT NULL DEFAULT 'assigned',
  assigned_at TIMESTAMPTZ DEFAULT now(),
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  notes TEXT
);

-- Task submission file URL
ALTER TABLE task_assignments ADD COLUMN IF NOT EXISTS submission_file_url TEXT;

-- ============================================================================
-- 14. NOTIFICATIONS
-- ============================================================================
CREATE TABLE IF NOT EXISTS notifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  userid VARCHAR(50) NOT NULL REFERENCES users(userid) ON DELETE CASCADE,
  type VARCHAR(50) NOT NULL,
  title VARCHAR(255) NOT NULL,
  message TEXT,
  link TEXT,
  read BOOLEAN NOT NULL DEFAULT FALSE,
  read_at TIMESTAMPTZ,
  deleted_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_notifications_userid_read ON notifications(userid, read);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_notifications_deleted_at ON notifications(deleted_at);

-- Add columns if table already exists (migration)
ALTER TABLE notifications ADD COLUMN IF NOT EXISTS read_at TIMESTAMPTZ;
ALTER TABLE notifications ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

-- ============================================================================
-- 15. TASK REVIEW COLUMNS (on task_assignments)
-- ============================================================================
ALTER TABLE task_assignments ADD COLUMN IF NOT EXISTS review_result VARCHAR(50);
ALTER TABLE task_assignments ADD COLUMN IF NOT EXISTS review_feedback TEXT;
ALTER TABLE task_assignments ADD COLUMN IF NOT EXISTS review_score INT;
ALTER TABLE task_assignments ADD COLUMN IF NOT EXISTS reviewed_at TIMESTAMPTZ;
ALTER TABLE task_assignments ADD COLUMN IF NOT EXISTS reviewed_by VARCHAR(50) REFERENCES users(userid);

-- ============================================================================
-- 16. INDEXES FOR SEARCH/FILTERS
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);
CREATE INDEX IF NOT EXISTS idx_task_assignments_status ON task_assignments(status);
CREATE INDEX IF NOT EXISTS idx_modules_status ON modules(status);

-- ============================================================================
-- 17. PROJECT MANAGEMENT INDEXES
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_projects_created_by ON projects(created_by);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_project_assignments_manager ON project_assignments(manager_userid);
CREATE INDEX IF NOT EXISTS idx_modules_project ON modules(projectid);
CREATE INDEX IF NOT EXISTS idx_modules_created_by ON modules(created_by);
CREATE INDEX IF NOT EXISTS idx_module_assignments_mentor ON module_assignments(mentor_userid);
CREATE INDEX IF NOT EXISTS idx_teams_mentor ON teams(mentor_userid);
CREATE INDEX IF NOT EXISTS idx_team_members_student ON team_members(student_userid);
CREATE INDEX IF NOT EXISTS idx_tasks_module ON tasks(moduleid);
CREATE INDEX IF NOT EXISTS idx_tasks_created_by ON tasks(created_by);
CREATE INDEX IF NOT EXISTS idx_task_assignments_student ON task_assignments(student_userid);
CREATE INDEX IF NOT EXISTS idx_task_assignments_task ON task_assignments(taskid);

-- ============================================================================
-- 18. ACTIVITY LOGS / AUDIT TRAIL
-- ============================================================================
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

-- ============================================================================
-- 19. TASK COMMENTS
-- ============================================================================
CREATE TABLE IF NOT EXISTS task_comments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  assignment_id UUID NOT NULL REFERENCES task_assignments(assignment_id) ON DELETE CASCADE,
  userid VARCHAR(50) NOT NULL REFERENCES users(userid),
  comment TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_task_comments_assignment ON task_comments(assignment_id);

-- ============================================================================
-- 20. TASK SUBMISSION FILE COLUMNS AND VERSIONS
-- ============================================================================
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

-- ============================================================================
-- 21. COLLEGES (multi-tenant)
-- ============================================================================
CREATE TABLE IF NOT EXISTS colleges (
  collegeid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  code VARCHAR(50) UNIQUE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE users ADD COLUMN IF NOT EXISTS collegeid UUID REFERENCES colleges(collegeid);
ALTER TABLE projects ADD COLUMN IF NOT EXISTS collegeid UUID REFERENCES colleges(collegeid);
CREATE INDEX IF NOT EXISTS idx_users_collegeid ON users(collegeid);
CREATE INDEX IF NOT EXISTS idx_projects_collegeid ON projects(collegeid);

-- ============================================================================
-- 22. ROLE PERMISSIONS
-- ============================================================================
CREATE TABLE IF NOT EXISTS role_permissions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  role VARCHAR(50) NOT NULL,
  resource VARCHAR(50) NOT NULL,
  action VARCHAR(50) NOT NULL,
  UNIQUE(role, resource, action)
);
CREATE INDEX IF NOT EXISTS idx_role_permissions_role ON role_permissions(role);

-- ============================================================================
-- 23. CHAT - CONVERSATIONS AND MESSAGES
-- ============================================================================
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

-- ============================================================================
-- 24. ACCOUNT LOCK (failed login)
-- ============================================================================
ALTER TABLE users ADD COLUMN IF NOT EXISTS failed_login_attempts INT NOT NULL DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS locked_until TIMESTAMPTZ;

-- ============================================================================
-- 25. SOFT DELETE
-- ============================================================================
ALTER TABLE users ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
ALTER TABLE projects ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
ALTER TABLE modules ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
CREATE INDEX IF NOT EXISTS idx_users_deleted_at ON users(deleted_at);
CREATE INDEX IF NOT EXISTS idx_projects_deleted_at ON projects(deleted_at);
CREATE INDEX IF NOT EXISTS idx_modules_deleted_at ON modules(deleted_at);
CREATE INDEX IF NOT EXISTS idx_tasks_deleted_at ON tasks(deleted_at);

-- ============================================================================
-- Storage bucket: create "task-submissions" in Supabase Dashboard > Storage if not exists.
-- ============================================================================
