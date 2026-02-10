-- Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS training_db;
USE training_db;

-- Users table (stores both Students and Trainers)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('student', 'trainer') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Student Profiles (additional details for students)
CREATE TABLE IF NOT EXISTS student_profiles (
    user_id INT PRIMARY KEY,
    full_name VARCHAR(100),
    current_course VARCHAR(100),
    current_level VARCHAR(50),
    goal_course VARCHAR(100),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Training Recommendations (stores generated roadmaps)
CREATE TABLE IF NOT EXISTS training_recommendations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    course_name VARCHAR(100),
    roadmap_json JSON, -- Stores the roadmap data structure (Day 1, Day 2...)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- MCQ Test Results
CREATE TABLE IF NOT EXISTS mcq_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    topic VARCHAR(100),
    score INT,
    total_questions INT,
    test_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- OCR Generated Questions (stores history of uploads)
CREATE TABLE IF NOT EXISTS ocr_uploads (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    image_filename VARCHAR(255),
    generated_text TEXT,
    generated_questions JSON,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
select * from users;

