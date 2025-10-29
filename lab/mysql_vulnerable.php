<?php
/**
 * Vulnerable PHP application for testing time-based blind SQL injection (MySQL).
 * DO NOT USE IN PRODUCTION - FOR TESTING ONLY
 */

// Database configuration
$servername = "localhost";
$username = "root";
$password = "";
$dbname = "vulnerable_db";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Initialize database if needed
$conn->query("CREATE DATABASE IF NOT EXISTS $dbname");
$conn->select_db($dbname);

$conn->query("CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(100) NOT NULL,
    email VARCHAR(100)
)");

// Insert sample data
$conn->query("DELETE FROM users");
$conn->query("INSERT INTO users (username, password, email) VALUES 
    ('admin', 'password123', 'admin@example.com'),
    ('alice', 'alice_secret', 'alice@example.com'),
    ('bob', 'bob_password', 'bob@example.com'),
    ('charlie', 'charlie123', 'charlie@example.com'),
    ('diana', 'diana_pass', 'diana@example.com')
");

// Handle request
$id = $_GET['id'] ?? '1';

// VULNERABLE: Direct string interpolation - DO NOT DO THIS IN PRODUCTION
$query = "SELECT * FROM users WHERE id = $id";

$start_time = microtime(true);

// Execute query (vulnerable to time-based injection)
$result = $conn->query($query);

$elapsed = microtime(true) - $start_time;

// Return minimal response (blind injection - no visible results)
header('Content-Type: application/json');
echo json_encode([
    'status' => 'ok',
    'time' => round($elapsed, 3) . 's'
]);

$conn->close();
?>

