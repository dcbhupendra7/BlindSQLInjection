#!/usr/bin/env python3
"""
Helper script to setup or modify users in the vulnerable database.
This makes it easier to customize test data without editing app.py directly.
"""

import sqlite3
import sys
import os

DB_PATH = 'lab/vulnerable.db'

def create_default_users():
    """Create default users in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            email TEXT
        )
    ''')
    
    # Clear existing users
    cursor.execute('DELETE FROM users')
    
    # Insert default users
    users = [
        ('admin', 'password123', 'admin@example.com'),
        ('alice', 'alice_secret', 'alice@example.com'),
        ('bob', 'bob_password', 'bob@example.com'),
        ('charlie', 'charlie123', 'charlie@example.com'),
        ('diana', 'diana_pass', 'diana@example.com'),
    ]
    cursor.executemany('INSERT INTO users (username, password, email) VALUES (?, ?, ?)', users)
    
    conn.commit()
    conn.close()
    print("[+] Default users created successfully!")

def add_user(username, password, email=None):
    """Add a single user to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            email TEXT
        )
    ''')
    
    # Insert user
    cursor.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)', 
                   (username, password, email or f'{username}@example.com'))
    
    conn.commit()
    conn.close()
    print(f"[+] User '{username}' added successfully!")

def list_users():
    """List all users in the database."""
    if not os.path.exists(DB_PATH):
        print("[!] Database does not exist. Run 'python app.py' first to create it.")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, username, password, email FROM users ORDER BY id')
    users = cursor.fetchall()
    
    if not users:
        print("[!] No users found in database.")
    else:
        print("\n" + "="*60)
        print("Current Users in Database:")
        print("="*60)
        print(f"{'ID':<5} {'Username':<20} {'Password':<25} {'Email':<30}")
        print("-"*60)
        for user in users:
            print(f"{user[0]:<5} {user[1]:<20} {user[2]:<25} {user[3]:<30}")
        print("="*60)
        print(f"\nTotal users: {len(users)}")
    
    conn.close()

def delete_user(username):
    """Delete a user from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM users WHERE username = ?', (username,))
    deleted = cursor.rowcount
    
    conn.commit()
    conn.close()
    
    if deleted > 0:
        print(f"[+] User '{username}' deleted successfully!")
    else:
        print(f"[!] User '{username}' not found.")

def clear_all_users():
    """Clear all users from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM users')
    conn.commit()
    conn.close()
    
    print("[+] All users cleared!")

def interactive_setup():
    """Interactive mode to add users."""
    print("\n" + "="*60)
    print("Interactive User Setup")
    print("="*60)
    print("Enter user details (press Enter with empty username to finish)\n")
    
    users = []
    while True:
        username = input("Username: ").strip()
        if not username:
            break
        
        password = input("Password: ").strip()
        if not password:
            print("[!] Password cannot be empty. Skipping this user.")
            continue
        
        email = input("Email (optional, press Enter for default): ").strip()
        if not email:
            email = f'{username}@example.com'
        
        users.append((username, password, email))
        print(f"[+] Added: {username}\n")
    
    if not users:
        print("[!] No users added.")
        return
    
    # Create table if needed
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            email TEXT
        )
    ''')
    
    # Clear existing users if requested
    clear = input("\nClear existing users? (y/N): ").strip().lower()
    if clear == 'y':
        cursor.execute('DELETE FROM users')
    
    # Insert new users
    cursor.executemany('INSERT INTO users (username, password, email) VALUES (?, ?, ?)', users)
    conn.commit()
    conn.close()
    
    print(f"\n[+] {len(users)} user(s) added successfully!")

def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("""
Usage: python setup_users.py <command> [options]

Commands:
  list                    - List all users in database
  default                 - Create default users (admin, alice, bob, etc.)
  add <user> <pass> [email] - Add a single user
  delete <username>       - Delete a user
  clear                   - Clear all users
  interactive             - Interactive mode to add multiple users

Examples:
  python setup_users.py list
  python setup_users.py default
  python setup_users.py add john mypassword john@example.com
  python setup_users.py delete john
  python setup_users.py clear
  python setup_users.py interactive
        """)
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    # Make sure database directory exists
    os.makedirs('lab', exist_ok=True)
    
    if command == 'list':
        list_users()
    
    elif command == 'default':
        create_default_users()
        list_users()
    
    elif command == 'add':
        if len(sys.argv) < 4:
            print("[!] Usage: python setup_users.py add <username> <password> [email]")
            sys.exit(1)
        username = sys.argv[2]
        password = sys.argv[3]
        email = sys.argv[4] if len(sys.argv) > 4 else None
        add_user(username, password, email)
        list_users()
    
    elif command == 'delete':
        if len(sys.argv) < 3:
            print("[!] Usage: python setup_users.py delete <username>")
            sys.exit(1)
        delete_user(sys.argv[2])
        list_users()
    
    elif command == 'clear':
        confirm = input("Are you sure you want to clear all users? (yes/no): ").strip().lower()
        if confirm == 'yes':
            clear_all_users()
        else:
            print("[!] Cancelled.")
    
    elif command == 'interactive':
        interactive_setup()
        list_users()
    
    else:
        print(f"[!] Unknown command: {command}")
        print("Run 'python setup_users.py' without arguments for help.")
        sys.exit(1)

if __name__ == '__main__':
    main()

