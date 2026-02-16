-- Run in Supabase SQL Editor AFTER users table (or use migration_to_varchar_userid.sql)
-- students table: NO password - stored only in users table
-- userid = roll number, links to users.userid

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
