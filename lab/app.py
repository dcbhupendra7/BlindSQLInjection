"""
Vulnerable Flask application for testing time-based blind SQL injection.
DO NOT USE IN PRODUCTION - FOR TESTING ONLY
"""

from flask import Flask, request, jsonify
import sqlite3
import time
import os

app = Flask(__name__)

# Initialize database
DB_PATH = 'lab/vulnerable.db'

def init_db():
    """Initialize the vulnerable database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            email TEXT
        )
    ''')
    
    # Create products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL,
            description TEXT
        )
    ''')
    
    # Insert sample data
    cursor.execute('DELETE FROM users')
    users = [
        ('admin', 'password123', 'admin@example.com'),
        ('alice', 'alice_secret', 'alice@example.com'),
        ('bob', 'bob_password', 'bob@example.com'),
        ('charlie', 'charlie123', 'charlie@example.com'),
        ('diana', 'diana_pass', 'diana@example.com'),
    ]
    cursor.executemany('INSERT INTO users (username, password, email) VALUES (?, ?, ?)', users)
    
    cursor.execute('DELETE FROM products')
    products = [
        ('Laptop', 999.99, 'High-performance laptop'),
        ('Mouse', 29.99, 'Wireless mouse'),
        ('Keyboard', 79.99, 'Mechanical keyboard'),
    ]
    cursor.executemany('INSERT INTO products (name, price, description) VALUES (?, ?, ?)', products)
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    """Home page."""
    return '''
    <h1>Vulnerable Web Application</h1>
    <p>This application has intentional SQL injection vulnerabilities for testing purposes.</p>
    <h2>Endpoints:</h2>
    <ul>
        <li><code>GET /vulnerable?id=1</code> - Time-based blind SQL injection (SQLite)</li>
    </ul>
    <p><strong>WARNING:</strong> This application is intentionally vulnerable. Do not deploy in production!</p>
    '''

@app.route('/vulnerable')
def vulnerable():
    """
    Vulnerable endpoint with time-based blind SQL injection.
    Example: /vulnerable?id=1 OR (SELECT SLEEP(5))--
    """
    user_id = request.args.get('id', '1')
    
    # VULNERABLE: Direct string interpolation - DO NOT DO THIS IN PRODUCTION
    query = f"SELECT * FROM users WHERE id = {user_id}"
    
    # SQLite doesn't have SLEEP(), so we simulate with Python time.sleep
    # In real MySQL/PostgreSQL, this would be: ... OR (SELECT SLEEP(5))-- 
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    start_time = time.time()
    
    try:
        # For SQLite, we need to detect time-based delays differently
        # We'll use a payload like: 1 OR (CASE WHEN (condition) THEN (SELECT 1 FROM (SELECT RANDOM() % 99999999) x) ELSE 1 END)
        # But for simplicity, let's detect common MySQL patterns and simulate
        
        # Check for time-based injection patterns
        # SQLite doesn't have SLEEP(), but we simulate it for testing
        import re
        
        # Look for SLEEP() pattern anywhere in the query
        sleep_pattern = r'SLEEP\(([0-9.]+)\)'
        sleep_match = re.search(sleep_pattern, user_id.upper())
        
        should_delay = False
        delay_val = None
        
        if sleep_match:
            delay_val = float(sleep_match.group(1))
            
            # Check if there's a condition before the SLEEP
            # Pattern: (condition) AND SLEEP(...)
            condition_pattern = r'\(([^)]+)\)\s+AND\s+SLEEP'
            condition_match = re.search(condition_pattern, user_id.upper())
            
            if condition_match:
                # Extract the condition SQL
                condition_sql = condition_match.group(1)
                
                # Try to evaluate the condition by executing it against the database
                try:
                    # Build a test query to evaluate the condition
                    # Example: ASCII(SUBSTRING((SELECT username FROM users WHERE 1=1 LIMIT 1), 1, 1)) >= 64
                    test_query = f"SELECT CASE WHEN {condition_sql} THEN 1 ELSE 0 END"
                    cursor.execute(test_query)
                    test_result = cursor.fetchone()
                    
                    if test_result and test_result[0] == 1:
                        should_delay = True
                except:
                    # If condition evaluation fails, don't delay
                    should_delay = False
            else:
                # No condition, just SLEEP() - always delay
                should_delay = True
        
        # Execute the actual query (always executed, but timing may vary)
        cursor.execute(query)
        results = cursor.fetchall()
        
        # Apply delay if condition was true
        if should_delay and delay_val:
            time.sleep(delay_val)
        
    except Exception as e:
        # Don't reveal errors in production
        results = []
    
    conn.close()
    
    elapsed = time.time() - start_time
    
    # Return minimal response (blind injection - no visible results)
    return jsonify({
        'status': 'ok',
        'count': len(results),
        'time': f'{elapsed:.3f}s'
    }), 200, {'Content-Type': 'application/json'}

if __name__ == '__main__':
    # Create lab directory if it doesn't exist
    os.makedirs('lab', exist_ok=True)
    init_db()
    print("[*] Database initialized")
    print("[*] Starting vulnerable server on http://127.0.0.1:5000")
    print("[!] WARNING: This is a vulnerable application for testing only!")
    app.run(host='127.0.0.1', port=5000, debug=False)

