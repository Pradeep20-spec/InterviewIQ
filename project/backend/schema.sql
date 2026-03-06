-- InterviewIQ Database Schema
-- Run this script to set up your MySQL database

-- Create database
CREATE DATABASE IF NOT EXISTS interviewiq;
USE interviewiq;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    name VARCHAR(255),
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Interview sessions table
CREATE TABLE IF NOT EXISTS interview_sessions (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36),
    resume_text TEXT,
    resume_filename VARCHAR(255),
    personality VARCHAR(50) NOT NULL,
    status ENUM('in_progress', 'completed', 'abandoned') DEFAULT 'in_progress',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Interview responses table
CREATE TABLE IF NOT EXISTS interview_responses (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(36) NOT NULL,
    question_index INT NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    input_mode ENUM('text', 'audio', 'video') DEFAULT 'text',
    recording_duration INT DEFAULT 0,
    timestamp BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES interview_sessions(id) ON DELETE CASCADE
);

-- Performance results table
CREATE TABLE IF NOT EXISTS performance_results (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(36) NOT NULL UNIQUE,
    technical_accuracy DECIMAL(5,2),
    language_proficiency DECIMAL(5,2),
    confidence_level DECIMAL(5,2),
    sentiment_score DECIMAL(5,2),
    emotional_stability DECIMAL(5,2),
    overall_score DECIMAL(5,2),
    feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES interview_sessions(id) ON DELETE CASCADE
);

-- Questions bank table
CREATE TABLE IF NOT EXISTS questions_bank (
    id VARCHAR(36) PRIMARY KEY,
    category VARCHAR(50) NOT NULL,
    personality VARCHAR(50) NOT NULL,
    question TEXT NOT NULL,
    difficulty ENUM('easy', 'medium', 'hard') DEFAULT 'medium',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default questions
INSERT INTO questions_bank (id, category, personality, question, difficulty) VALUES
(UUID(), 'general', 'friendly', 'Tell me about yourself and your background.', 'easy'),
(UUID(), 'general', 'friendly', 'What interests you most about this position?', 'easy'),
(UUID(), 'general', 'friendly', 'Can you describe a project you are particularly proud of?', 'medium'),
(UUID(), 'general', 'friendly', 'What are your greatest strengths?', 'easy'),
(UUID(), 'general', 'friendly', 'Where do you see yourself in five years?', 'medium'),
(UUID(), 'technical', 'technical', 'Explain the difference between let, const, and var in JavaScript.', 'easy'),
(UUID(), 'technical', 'technical', 'How would you optimize a slow database query?', 'hard'),
(UUID(), 'technical', 'technical', 'Describe the SOLID principles and give examples.', 'hard'),
(UUID(), 'technical', 'technical', 'What is the time complexity of your solution?', 'medium'),
(UUID(), 'technical', 'technical', 'Explain how garbage collection works in your preferred language.', 'hard'),
(UUID(), 'behavioral', 'stress', 'Why should we hire you over other candidates?', 'hard'),
(UUID(), 'behavioral', 'stress', 'Tell me about a time you failed. What happened?', 'hard'),
(UUID(), 'behavioral', 'stress', 'How do you handle tight deadlines with conflicting priorities?', 'hard'),
(UUID(), 'behavioral', 'stress', 'What is your biggest weakness?', 'medium'),
(UUID(), 'behavioral', 'stress', 'Convince me why this solution is better than the alternative.', 'hard'),
(UUID(), 'team', 'panel', 'How do you approach problem-solving in a team environment?', 'medium'),
(UUID(), 'team', 'panel', 'Describe your experience with agile methodologies.', 'medium'),
(UUID(), 'team', 'panel', 'What is your approach to code reviews?', 'medium'),
(UUID(), 'team', 'panel', 'How do you stay updated with new technologies?', 'easy'),
(UUID(), 'team', 'panel', 'Tell us about a time you had to make a difficult technical decision.', 'hard');

-- Create indexes
CREATE INDEX idx_sessions_user ON interview_sessions(user_id);
CREATE INDEX idx_sessions_status ON interview_sessions(status);
CREATE INDEX idx_responses_session ON interview_responses(session_id);
CREATE INDEX idx_results_session ON performance_results(session_id);
CREATE INDEX idx_questions_personality ON questions_bank(personality);
