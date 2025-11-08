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
# Use absolute path or relative to where app is run from
# Check which database actually has tables
def find_db_with_tables():
    """Find the database file that has tables."""
    import sqlite3
    # Check databases that likely have tables first
    for db_path in ['lab/lab/vulnerable.db', 'lab/vulnerable.db', 'vulnerable.db']:
        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                conn.close()
                if tables:
                    print(f"[DEBUG] Using database with tables: {db_path}")
                    return db_path
            except Exception as e:
                print(f"[DEBUG] Error checking {db_path}: {e}")
                pass
    # If no database with tables found, use default (will be initialized)
    default_path = 'lab/vulnerable.db'
    print(f"[DEBUG] No database with tables found, using default: {default_path}")
    return default_path

DB_PATH = find_db_with_tables()

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
        condition_sql = None
        condition_match = False  # Initialize condition_match
        
        if sleep_match:
            delay_val = float(sleep_match.group(1))
            
            # Debug: print what we're looking for
            print(f"[DEBUG] Found SLEEP({delay_val}) in: {user_id[:100]}")
            
            # Check if there's a condition before the SLEEP
            # Pattern: (condition) AND SLEEP(...)
            # Need to handle nested parentheses correctly
            # Look for: ... OR (condition) AND SLEEP
            # Note: user_id comes from URL params, so it's already decoded
            user_id_upper = user_id.upper()
            or_pos = user_id_upper.find('OR')
            if or_pos != -1:
                # Find the opening paren after OR (skip whitespace)
                search_start = or_pos + 2  # Skip "OR"
                open_paren = -1
                for i in range(search_start, len(user_id)):
                    if user_id[i] == '(':
                        open_paren = i
                        break
                    elif user_id[i] not in [' ', '\t']:
                        # Not whitespace and not opening paren - no condition
                        break
                
                if open_paren != -1:
                    # Find " AND SLEEP" after the opening paren
                    and_sleep_pos = user_id_upper.find(' AND SLEEP', open_paren)
                    if and_sleep_pos != -1:
                        # Count parentheses to find the matching closing one
                        # Start with paren_count = 1 since we're already inside the opening paren
                        paren_count = 1
                        close_paren = -1
                        for i in range(open_paren + 1, and_sleep_pos):
                            if user_id[i] == '(':
                                paren_count += 1
                            elif user_id[i] == ')':
                                paren_count -= 1
                                if paren_count == 0:
                                    close_paren = i
                                    break
                        
                        if close_paren != -1:
                            # Extract condition between the matching parentheses
                            condition_sql = user_id[open_paren + 1:close_paren]
                            condition_match = True
                            # Debug: print extracted condition
                            print(f"[DEBUG] Extracted condition: {condition_sql[:100]}")
                        else:
                            print(f"[DEBUG] Could not find matching closing paren")
                            condition_match = False
                    else:
                        print(f"[DEBUG] Could not find ' AND SLEEP' after opening paren")
                        condition_match = False
                else:
                    print(f"[DEBUG] Could not find opening paren after OR")
                    condition_match = False
            else:
                print(f"[DEBUG] Could not find 'OR' in payload")
                condition_match = False
            
            if condition_match:
                
                # Try to evaluate the condition by executing it against the database
                try:
                    # Build a test query to evaluate the condition
                    # Example: ASCII(SUBSTRING((SELECT username FROM users WHERE 1=1 LIMIT 1), 1, 1)) >= 64
                    # For SQLite, we need to handle the condition properly
                    test_query = f"SELECT CASE WHEN ({condition_sql}) THEN 1 ELSE 0 END"
                    # Debug: print test query
                    print(f"[DEBUG] Test query: {test_query[:150]}")
                    cursor.execute(test_query)
                    test_result = cursor.fetchone()
                    
                    # Debug: print result
                    print(f"[DEBUG] Test result: {test_result}, should_delay will be: {test_result and test_result[0] == 1}")
                    
                    if test_result and test_result[0] == 1:
                        should_delay = True
                    else:
                        should_delay = False
                except Exception as e:
                    # If condition evaluation fails, don't delay
                    # This can happen with complex SQL that SQLite doesn't support
                    # Debug: print error
                    print(f"[DEBUG] Condition evaluation error: {e}")
                    should_delay = False
            else:
                # No condition, just SLEEP() - always delay
                print(f"[DEBUG] No condition found, always delaying")
                should_delay = True
        
        # Apply delay BEFORE executing query (in case query fails)
        # This ensures delays are applied even if the SQL query has syntax errors
        if should_delay and delay_val:
            print(f"[DEBUG] Applying delay of {delay_val}s")
            time.sleep(delay_val)
        else:
            if delay_val:
                print(f"[DEBUG] NOT delaying (should_delay={should_delay}, delay_val={delay_val})")
        
        # Execute the actual query (always executed, but timing may vary)
        # Note: This query may fail if it contains SQLite-incompatible functions like SLEEP()
        # but we've already applied the delay above if needed
        try:
            cursor.execute(query)
            results = cursor.fetchall()
        except Exception as query_error:
            # Query execution failed (e.g., SLEEP() doesn't exist in SQLite)
            # This is expected - we've already applied the delay if needed
            print(f"[DEBUG] Query execution error (expected for SLEEP): {type(query_error).__name__}")
            results = []
        
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

