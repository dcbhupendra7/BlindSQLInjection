-- MySQL setup script for vulnerable database
-- Run this before testing with MySQL-based tools

CREATE DATABASE IF NOT EXISTS vulnerable_db;
USE vulnerable_db;

CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(100) NOT NULL,
    email VARCHAR(100)
);

DELETE FROM users;
INSERT INTO users (username, password, email) VALUES
    ('admin', 'password123', 'admin@example.com'),
    ('alice', 'alice_secret', 'alice@example.com'),
    ('bob', 'bob_password', 'bob@example.com'),
    ('charlie', 'charlie123', 'charlie@example.com'),
    ('diana', 'diana_pass', 'diana@example.com');

