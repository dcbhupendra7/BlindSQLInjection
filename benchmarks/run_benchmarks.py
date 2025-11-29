#!/usr/bin/env python3
"""
Simple script to execute benchmarks for StatSQLi.
This script runs the benchmark comparison and optionally generates charts.
"""

import sys
import subprocess
import requests
import time
from pathlib import Path

# Default configuration
DEFAULT_URL = "http://127.0.0.1:5000/vulnerable?id=1"
DEFAULT_PAYLOAD = "' OR ({condition}) AND SLEEP(2) -- -"
DEFAULT_ITERATIONS = 5
DEFAULT_USER_ID = 1
DEFAULT_OUTPUT = "benchmark_results.json"


def check_server_running(url: str, timeout: int = 2) -> bool:
    """Check if the vulnerable server is running."""
    try:
        # Try to connect to the server
        response = requests.get(url.split('?')[0] if '?' in url else url, timeout=timeout)
        return response.status_code in [200, 404, 500]  # Any response means server is up
    except requests.exceptions.RequestException:
        return False


def start_lab_server():
    """Start the lab server in the background."""
    print("[*] Starting lab server...")
    lab_path = Path(__file__).parent.parent / "lab" / "app.py"
    
    if not lab_path.exists():
        print(f"[!] Lab server not found at {lab_path}")
        return None
    
    # Start server in background
    process = subprocess.Popen(
        [sys.executable, str(lab_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait a bit for server to start
    time.sleep(2)
    
    if process.poll() is None:  # Process is still running
        print("[+] Lab server started")
        return process
    else:
        print("[!] Failed to start lab server")
        return None


def run_benchmarks(url: str, payload: str, iterations: int, user_id: int, output: str):
    """Run the benchmark comparison."""
    print("\n" + "=" * 60)
    print("RUNNING BENCHMARKS")
    print("=" * 60)
    
    benchmark_script = Path(__file__).parent / "compare_tools.py"
    
    if not benchmark_script.exists():
        print(f"[!] Benchmark script not found at {benchmark_script}")
        return False
    
    cmd = [
        sys.executable,
        str(benchmark_script),
        url,
        "--payload", payload,
        "--iterations", str(iterations),
        "--user-id", str(user_id),
        "--output", output
    ]
    
    print(f"[*] Command: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(cmd, check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"[!] Benchmark failed with error: {e}")
        return False


def generate_charts(results_file: str):
    """Generate visualization charts from benchmark results."""
    print("\n" + "=" * 60)
    print("GENERATING CHARTS")
    print("=" * 60)
    
    chart_script = Path(__file__).parent / "generate_charts.py"
    
    if not chart_script.exists():
        print(f"[!] Chart generation script not found at {chart_script}")
        return False
    
    if not Path(results_file).exists():
        print(f"[!] Results file not found: {results_file}")
        return False
    
    cmd = [
        sys.executable,
        str(chart_script),
        "--input", results_file
    ]
    
    print(f"[*] Command: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(cmd, check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"[!] Chart generation failed with error: {e}")
        return False


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Execute benchmarks for StatSQLi',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run benchmarks with defaults
  python run_benchmarks.py

  # Run with custom URL and iterations
  python run_benchmarks.py --url "http://127.0.0.1:5000/vulnerable?id=1" --iterations 10

  # Run benchmarks and generate charts
  python run_benchmarks.py --charts

  # Run without checking server (assume it's already running)
  python run_benchmarks.py --no-check-server
        """
    )
    
    parser.add_argument('--url', '-u', default=DEFAULT_URL,
                       help=f'Target vulnerable URL (default: {DEFAULT_URL})')
    parser.add_argument('--payload', '-p', default=DEFAULT_PAYLOAD,
                       help=f'Payload template (default: {DEFAULT_PAYLOAD})')
    parser.add_argument('--iterations', '-i', type=int, default=DEFAULT_ITERATIONS,
                       help=f'Number of iterations per tool (default: {DEFAULT_ITERATIONS})')
    parser.add_argument('--user-id', type=int, default=DEFAULT_USER_ID,
                       help=f'User ID to extract (default: {DEFAULT_USER_ID})')
    parser.add_argument('--output', '-o', default=DEFAULT_OUTPUT,
                       help=f'Output JSON file (default: {DEFAULT_OUTPUT})')
    parser.add_argument('--charts', '-c', action='store_true',
                       help='Generate charts after running benchmarks')
    parser.add_argument('--no-check-server', action='store_true',
                       help='Skip server check (assume server is already running)')
    parser.add_argument('--start-server', action='store_true',
                       help='Start lab server automatically if not running')
    
    args = parser.parse_args()
    
    # Check if server is running
    server_process = None
    if not args.no_check_server:
        print("[*] Checking if lab server is running...")
        if not check_server_running(args.url):
            print("[!] Lab server is not running!")
            
            if args.start_server:
                server_process = start_lab_server()
                if server_process:
                    # Wait a bit more and check again
                    time.sleep(1)
                    if not check_server_running(args.url):
                        print("[!] Server started but not responding. Please check manually.")
                        if server_process:
                            server_process.terminate()
                        return 1
                else:
                    return 1
            else:
                print("[!] Please start the lab server first:")
                print("    cd lab && python app.py")
                print("\n    Or use --start-server to start it automatically")
                return 1
        else:
            print("[+] Lab server is running")
    
    # Run benchmarks
    success = run_benchmarks(
        args.url,
        args.payload,
        args.iterations,
        args.user_id,
        args.output
    )
    
    if not success:
        if server_process:
            server_process.terminate()
        return 1
    
    # Generate charts if requested
    if args.charts:
        generate_charts(args.output)
    
    # Cleanup
    if server_process:
        print("\n[*] Stopping lab server...")
        server_process.terminate()
        server_process.wait()
        print("[+] Lab server stopped")
    
    print("\n" + "=" * 60)
    print("BENCHMARKS COMPLETED")
    print("=" * 60)
    print(f"\n[+] Results saved to: {args.output}")
    if args.charts:
        print("[+] Charts generated in current directory")
    print()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

