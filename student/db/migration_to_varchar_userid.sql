-- Run in Supabase SQL Editor
-- Fixes: "Key columns are of incompatible types: character varying and uuid"
-- This DROPS existing tables and recreates with VARCHAR userid.
-- BACKUP your data first if needed!

-- 1. Drop students first (has FK to users)
DROP TABLE IF EXISTS students CASCADE;

-- 2. Drop users
DROP TABLE IF EXISTS users CASCADE;

-- 3. Create users with VARCHAR userid (roll number)
CREATE TABLE users (
  userid VARCHAR(50) PRIMARY KEY,
  username VARCHAR(100) NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  role VARCHAR(50) NOT NULL DEFAULT 'student',
  active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- 4. Create students with VARCHAR userid (FK matches)
CREATE TABLE students (
  studentid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  userid VARCHAR(50) UNIQUE NOT NULL REFERENCES users(userid) ON DELETE CASCADE,
  first_name VARCHAR(100) NOT NULL,
  last_name VARCHAR(100) NOT NULL,
  phone VARCHAR(20) NOT NULL,
  email VARCHAR(255) NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);
