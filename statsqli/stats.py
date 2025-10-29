"""
Statistical analysis module for timing-based detection.
Uses statistical tests to determine if timing differences are significant.
"""

import numpy as np
from scipy import stats
from typing import List, Tuple


class TimingAnalyzer:
    """Analyzes timing measurements using statistical tests to avoid false positives."""
    
    def __init__(self, confidence_level: float = 0.95, min_samples: int = 5):
        """
        Initialize the timing analyzer.
        
        Args:
            confidence_level: Confidence level for statistical tests (default: 0.95)
            min_samples: Minimum number of samples before making decisions
        """
        self.confidence_level = confidence_level
        self.min_samples = min_samples
    
    def calculate_baseline(self, timings: List[float]) -> Tuple[float, float]:
        """
        Calculate baseline timing statistics (mean and std dev).
        
        Args:
            timings: List of timing measurements
            
        Returns:
            Tuple of (mean, standard_deviation)
        """
        if not timings:
            return 0.0, 0.0
        mean = np.mean(timings)
        std = np.std(timings, ddof=1) if len(timings) > 1 else 0.0
        return float(mean), float(std)
    
    def is_significant_delay(self, baseline_samples: List[float], 
                            test_samples: List[float]) -> Tuple[bool, float]:
        """
        Determine if test samples show a statistically significant delay.
        Uses Welch's t-test (unequal variances).
        
        Args:
            baseline_samples: Baseline timing measurements
            test_samples: Test timing measurements with potential delay
            
        Returns:
            Tuple of (is_significant, p_value)
        """
        if len(baseline_samples) < self.min_samples or len(test_samples) < self.min_samples:
            return False, 1.0
        
        # Perform Welch's t-test (handles unequal variances)
        t_stat, p_value = stats.ttest_ind(test_samples, baseline_samples, 
                                         equal_var=False, alternative='greater')
        
        is_significant = p_value < (1 - self.confidence_level)
        return is_significant, float(p_value)
    
    def calculate_adaptive_threshold(self, baseline_samples: List[float]) -> float:
        """
        Calculate adaptive threshold based on baseline noise.
        Uses multiple of standard deviation to account for network variability.
        
        Args:
            baseline_samples: Baseline timing measurements
            
        Returns:
            Adaptive threshold value
        """
        if len(baseline_samples) < self.min_samples:
            return 1.0  # Default threshold
        
        mean, std = self.calculate_baseline(baseline_samples)
        # Use 3 sigma rule, adjusted for confidence
        threshold = mean + (3 * std)
        return max(threshold, mean * 1.1)  # At least 10% above mean
    
    def estimate_required_samples(self, effect_size: float, 
                                  baseline_std: float) -> int:
        """
        Estimate number of samples needed to detect an effect.
        
        Args:
            effect_size: Expected effect size (delay in seconds)
            baseline_std: Standard deviation of baseline
            
        Returns:
            Estimated number of samples needed
        """
        if baseline_std == 0:
            return self.min_samples
        
        # Power analysis: aim for 80% power, 95% confidence
        # Simplified calculation
        n = (2 * (stats.norm.ppf(0.95) + stats.norm.ppf(0.8))**2 * 
             (baseline_std / effect_size)**2)
        return max(int(np.ceil(n)), self.min_samples)

