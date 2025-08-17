-- EduBot Database Schema
-- MySQL 8.0 Compatible

CREATE DATABASE IF NOT EXISTS edubot_db;
USE edubot_db;

-- Users table (students, faculty, admin)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('student', 'faculty', 'admin') NOT NULL DEFAULT 'student',
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    student_id VARCHAR(20) UNIQUE,
    course_id INT,
    year_of_study INT,
    phone VARCHAR(15),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Faculty table
CREATE TABLE faculty (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    employee_id VARCHAR(20) UNIQUE NOT NULL,
    department VARCHAR(100) NOT NULL,
    designation VARCHAR(100) NOT NULL,
    specialization TEXT,
    office_location VARCHAR(100),
    office_hours VARCHAR(100),
    bio TEXT,
    image_url VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Courses table
CREATE TABLE courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_code VARCHAR(20) UNIQUE NOT NULL,
    course_name VARCHAR(100) NOT NULL,
    description TEXT,
    credits INT DEFAULT 3,
    semester INT NOT NULL,
    year INT NOT NULL,
    department VARCHAR(100) NOT NULL,
    faculty_id INT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (faculty_id) REFERENCES faculty(id) ON DELETE SET NULL
);

-- Attendance table
CREATE TABLE attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    date DATE NOT NULL,
    status ENUM('present', 'absent', 'late') NOT NULL DEFAULT 'absent',
    marked_by INT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    FOREIGN KEY (marked_by) REFERENCES users(id) ON DELETE SET NULL,
    UNIQUE KEY unique_attendance (student_id, course_id, date)
);

-- Events table
CREATE TABLE events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    event_type ENUM('academic', 'cultural', 'sports', 'holiday', 'exam', 'other') NOT NULL DEFAULT 'other',
    start_date DATE NOT NULL,
    end_date DATE,
    start_time TIME,
    end_time TIME,
    location VARCHAR(200),
    organizer VARCHAR(100),
    is_holiday BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Syllabus files table
CREATE TABLE syllabus_files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    original_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INT NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    description TEXT,
    uploaded_by INT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Notes table
CREATE TABLE notes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    content LONGTEXT,
    file_name VARCHAR(255),
    original_name VARCHAR(255),
    file_path VARCHAR(500),
    file_size INT,
    file_type VARCHAR(50),
    topic VARCHAR(100),
    chapter VARCHAR(100),
    uploaded_by INT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Groups table
CREATE TABLE groups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    group_type ENUM('study', 'project', 'general', 'course') NOT NULL DEFAULT 'general',
    course_id INT,
    created_by INT NOT NULL,
    is_private BOOLEAN DEFAULT FALSE,
    max_members INT DEFAULT 50,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
);

-- Group members table
CREATE TABLE group_members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    group_id INT NOT NULL,
    user_id INT NOT NULL,
    role ENUM('member', 'admin', 'moderator') NOT NULL DEFAULT 'member',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_membership (group_id, user_id)
);

-- Group messages table
CREATE TABLE group_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    group_id INT NOT NULL,
    user_id INT NOT NULL,
    message LONGTEXT NOT NULL,
    message_type ENUM('text', 'file', 'image', 'link') NOT NULL DEFAULT 'text',
    file_path VARCHAR(500),
    file_name VARCHAR(255),
    is_edited BOOLEAN DEFAULT FALSE,
    edited_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Motivational quotes table
CREATE TABLE quotes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    quote TEXT NOT NULL,
    author VARCHAR(100),
    category ENUM('motivation', 'success', 'learning', 'life', 'education') NOT NULL DEFAULT 'motivation',
    is_active BOOLEAN DEFAULT TRUE,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Chat logs table
CREATE TABLE chat_logs (

    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    session_id VARCHAR(100),
    user_message LONGTEXT NOT NULL,
    bot_response LONGTEXT NOT NULL,
    intent VARCHAR(100),
    confidence_score DECIMAL(3,2),
    
    response_time_ms INT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Site content table (for About Us, etc.)
CREATE TABLE site_content (
    id INT AUTO_INCREMENT PRIMARY KEY,
    content_key VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(200) NOT NULL,
    content LONGTEXT NOT NULL,
    content_type ENUM('text', 'html', 'markdown') NOT NULL DEFAULT 'html',
    is_active BOOLEAN DEFAULT TRUE,
    updated_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Intents table (for chatbot pattern matching)
CREATE TABLE intents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    intent_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    patterns TEXT NOT NULL, -- JSON array of regex patterns
    responses TEXT NOT NULL, -- JSON array of possible responses
    handler_function VARCHAR(100), -- Python function to handle this intent
    priority INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Insert default admin user (password: admin123)
INSERT INTO users (username, email, password_hash, role, first_name, last_name) 
VALUES ('admin', 'admin@edubot.com', 'scrypt:32768:8:1$gKfaQqf3ZIKh3o1y$8f2c8e9a7b6d4c3f2e1a0b9c8d7e6f5a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a', 'admin', 'Admin', 'User');

-- Insert some default quotes
INSERT INTO quotes (quote, author, category) VALUES 
('The only way to do great work is to love what you do.', 'Steve Jobs', 'motivation'),
('Education is the most powerful weapon which you can use to change the world.', 'Nelson Mandela', 'education'),
('Success is not final, failure is not fatal: it is the courage to continue that counts.', 'Winston Churchill', 'success'),
('The future belongs to those who believe in the beauty of their dreams.', 'Eleanor Roosevelt', 'motivation'),
('Learning never exhausts the mind.', 'Leonardo da Vinci', 'learning');

-- Insert default site content
INSERT INTO site_content (content_key, title, content, content_type) VALUES 
('about_us', 'About Us', '<p>Welcome to EduBot - Your intelligent college assistant!</p><p>EduBot is designed to help students with their academic journey by providing quick access to faculty information, attendance records, upcoming events, and much more.</p>', 'html'),
('privacy_policy', 'Privacy Policy', '<p>Your privacy is important to us. This policy explains how we collect, use, and protect your information.</p>', 'html'),
('terms_of_service', 'Terms of Service', '<p>By using EduBot, you agree to these terms and conditions.</p>', 'html');

-- Insert default intents
INSERT INTO intents (intent_name, description, patterns, responses, handler_function, priority) VALUES 
('greeting', 'Greetings and hello messages', '["hello", "hi", "hey", "good morning", "good afternoon", "good evening", "greetings"]', '["Hello! How can I help you today?", "Hi there! What would you like to know?", "Hey! I\'m here to assist you.", "Greetings! How may I assist you?"]', 'handle_greeting', 10),
('faculty_info', 'Faculty information queries', '["faculty", "teacher", "professor", "instructor", "staff", "who teaches", "faculty details"]', '["I can help you find faculty information. Which faculty member are you looking for?", "Let me help you with faculty details. Please specify the faculty name or department."]', 'handle_faculty', 5),
('attendance', 'Attendance related queries', '["attendance", "present", "absent", "attendance record", "my attendance", "attendance percentage"]', '["Let me check your attendance records.", "I\'ll fetch your attendance information."]', 'handle_attendance', 5),
('events', 'Events and holidays information', '["events", "holiday", "holidays", "upcoming events", "college events", "festival", "celebration"]', '["Here are the upcoming events and holidays.", "Let me show you the college calendar."]', 'handle_events', 5),
('motivational', 'Motivational quotes and encouragement', '["quote", "motivation", "inspire", "encourage", "motivational quote", "need motivation", "feeling down"]', '["Here\'s a motivational quote for you!", "Hope this inspires you!"]', 'handle_quotes', 3),
('default', 'Default fallback response', '[".*"]', '["I\'m sorry, I didn\'t understand that. Could you please rephrase?", "I\'m not sure how to help with that. Try asking about faculty, attendance, events, or motivational quotes.", "Could you please be more specific? I can help with faculty info, attendance, events, and more!"]', 'handle_default', 1);

-- Create indexes for better performance
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_student_id ON users(student_id);
CREATE INDEX idx_attendance_student_date ON attendance(student_id, date);
CREATE INDEX idx_events_date ON events(start_date);
CREATE INDEX idx_chat_logs_user_date ON chat_logs(user_id, created_at);
CREATE INDEX idx_group_messages_group_date ON group_messages(group_id, created_at);
CREATE INDEX idx_intents_active ON intents(is_active);
