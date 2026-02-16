-- Run in Supabase SQL Editor
-- If you had UUID userid before: run db/migration_to_varchar_userid.sql first
-- Roles: student, mentor, clgadmin, admin, manager
-- Password: bcrypt hash only, never plain text

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

-- If migrating from UUID userid, backup data first and recreate table
