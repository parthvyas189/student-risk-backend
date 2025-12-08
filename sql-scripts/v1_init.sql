-- Version 1: Initial Schema Setup
-- Run this entire script in MySQL Workbench

-- IMPORTANT: Double-check that your database (e.g., 'defaultdb') is selected (BOLD) in the left sidebar.
-- We attempt to select the default Aiven database here:
USE defaultdb; 

-- 1. Create a table to track version changes (Future Proofing)
CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR(50) PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Users Table (Authentication for Admins, Teachers, and eventually Students)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'teacher', 'student') NOT NULL,
    full_name VARCHAR(150),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 3. Students Table (Profile Data)
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE, -- Links to users table if they have a login (Nullable for now)
    teacher_id INT NOT NULL, -- The teacher responsible for this student
    name VARCHAR(100) NOT NULL,
    roll_number VARCHAR(50) UNIQUE,
    contact_email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (teacher_id) REFERENCES users(id)
);

-- 4. Weekly Metrics Table (The inputs for the model)
CREATE TABLE IF NOT EXISTS weekly_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    week_start_date DATE NOT NULL,
    
    -- Metrics (Subject to change, so we keep them nullable)
    attendance_score INT CHECK (attendance_score BETWEEN 0 AND 100),
    homework_submission_rate INT CHECK (homework_submission_rate BETWEEN 0 AND 100),
    behavior_flag BOOLEAN DEFAULT FALSE, -- True if there was a disciplinary issue
    test_score_average FLOAT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    -- Prevent duplicate entries for the same student in the same week
    UNIQUE (student_id, week_start_date)
);

-- 5. Risk Predictions Table (The output from the Python Model)
CREATE TABLE IF NOT EXISTS risk_predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    analysis_date DATE NOT NULL,
    
    risk_score FLOAT NOT NULL, -- 0.0 to 1.0
    risk_level ENUM('Low', 'Medium', 'High') NOT NULL,
    risk_reasons TEXT, -- Will store JSON string explanation (e.g. "Low attendance")
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- 6. Log this migration
INSERT IGNORE INTO schema_migrations (version) VALUES ('v1_init');