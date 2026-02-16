-- Run in Supabase SQL Editor
-- Project Management System - Hierarchical Task Management (Jira-like)
-- Admin → Projects → Managers → Modules → Mentors → Tasks → Students

-- 1. PROJECTS (Created by Admin)
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

-- 2. PROJECT ASSIGNMENTS (Admin assigns to Manager)
CREATE TABLE IF NOT EXISTS project_assignments (
  assignment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  projectid UUID NOT NULL REFERENCES projects(projectid) ON DELETE CASCADE,
  manager_userid VARCHAR(50) NOT NULL REFERENCES users(userid),
  assigned_by VARCHAR(50) NOT NULL REFERENCES users(userid),
  assigned_at TIMESTAMPTZ DEFAULT now()
);

-- 3. MODULES (Created by Manager within Project)
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

-- 4. MODULE ASSIGNMENTS (Manager assigns to Mentor)
CREATE TABLE IF NOT EXISTS module_assignments (
  assignment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  moduleid UUID NOT NULL REFERENCES modules(moduleid) ON DELETE CASCADE,
  mentor_userid VARCHAR(50) NOT NULL REFERENCES users(userid),
  assigned_by VARCHAR(50) NOT NULL REFERENCES users(userid),
  assigned_at TIMESTAMPTZ DEFAULT now()
);

-- 5. TEAMS (Mentor creates student teams)
CREATE TABLE IF NOT EXISTS teams (
  teamid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  team_name VARCHAR(255) NOT NULL,
  mentor_userid VARCHAR(50) NOT NULL REFERENCES users(userid),
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- 6. TEAM MEMBERS (Students in a team)
CREATE TABLE IF NOT EXISTS team_members (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  teamid UUID NOT NULL REFERENCES teams(teamid) ON DELETE CASCADE,
  student_userid VARCHAR(50) NOT NULL REFERENCES users(userid),
  added_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(teamid, student_userid)
);

-- 7. TASKS (Created by Mentor within Module)
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

-- 8. TASK ASSIGNMENTS (Mentor assigns to Student)
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

-- Indexes for performance
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
