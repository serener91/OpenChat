-- Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS chat_history;

-- Use the database
USE chat_history;

-- Create sessions table
CREATE TABLE IF NOT EXISTS sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_key CHAR(36) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create messages table
CREATE TABLE IF NOT EXISTS messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id CHAR(36) NOT NULL,
    sender ENUM('user', 'assistant') NOT NULL,  -- ENUM is predefined data type
    message_text TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_session_id (session_id),  -- Regular index on session_id
    FOREIGN KEY (session_id) REFERENCES sessions(session_key) ON DELETE CASCADE -- deleting a session will automatically delete all related messages
);

-- Insert initial keys
--INSERT INTO sessions (session_key) VALUES (UUID());
--INSERT INTO sessions (session_key) VALUES (UUID());
--INSERT INTO sessions (session_key) VALUES (UUID());
INSERT INTO sessions (session_key) VALUES ("kitty");
INSERT INTO sessions (session_key) VALUES ("bunny");
INSERT INTO sessions (session_key) VALUES ("pony");