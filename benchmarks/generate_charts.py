"""
Generate charts and visualizations from benchmark results.
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Dict, List


def load_results(filename: str = "benchmark_results.json") -> Dict:
    """Load benchmark results from JSON file."""
    with open(filename, 'r') as f:
        return json.load(f)


def plot_comparison(results: Dict):
    """Create comparison chart of tool performance."""
    tools = []
    mean_times = []
    std_times = []
    
    for tool, stats in results['summary'].items():
        if stats['mean'] != float('inf') and stats['mean'] > 0:
            tools.append(tool)
            mean_times.append(stats['mean'])
            std_times.append(stats['std'])
    
    if not tools:
        print("[!] No valid results to plot")
        return
    
    # Create bar chart
    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(tools))
    width = 0.6
    
    bars = ax.bar(x, mean_times, width, yerr=std_times, capsize=5,
                  label='Mean extraction time', color=['#2ecc71', '#3498db', '#e74c3c'][:len(tools)])
    
    ax.set_xlabel('Tool', fontsize=12)
    ax.set_ylabel('Time (seconds)', fontsize=12)
    ax.set_title('Time-Based Blind SQL Injection: Tool Comparison', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([t.upper() for t in tools])
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bar, mean in zip(bars, mean_times):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{mean:.1f}s', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('benchmark_comparison.png', dpi=300, bbox_inches='tight')
    print("[+] Saved benchmark_comparison.png")
    plt.close()


def plot_speedup(results: Dict):
    """Create speedup comparison chart."""
    statsqli_time = results['summary']['statsqli']['mean']
    
    if statsqli_time == float('inf'):
        print("[!] StatSQLi results not available")
        return
    
    speedups = {}
    baseline_tools = ['sqlmap', 'manual']
    
    for tool in baseline_tools:
        tool_time = results['summary'][tool]['mean']
        if tool_time != float('inf') and tool_time > 0:
            speedups[tool] = tool_time / statsqli_time
    
    if not speedups:
        print("[!] No valid baselines for speedup calculation")
        return
    
    fig, ax = plt.subplots(figsize=(8, 6))
    tools = list(speedups.keys())
    values = list(speedups.values())
    
    bars = ax.bar(tools, values, color=['#3498db', '#e74c3c'][:len(tools)])
    ax.set_xlabel('Baseline Tool', fontsize=12)
    ax.set_ylabel('Speedup Factor (x times faster)', fontsize=12)
    ax.set_title('StatSQLi Speedup vs Baseline Tools', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels
    for bar, value in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{value:.1f}x', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('benchmark_speedup.png', dpi=300, bbox_inches='tight')
    print("[+] Saved benchmark_speedup.png")
    plt.close()


def plot_iteration_times(results: Dict):
    """Create line chart showing iteration times."""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    for tool, times in results['raw_times'].items():
        valid_times = [t for t in times if t != float('inf')]
        if valid_times:
            iterations = range(1, len(valid_times) + 1)
            ax.plot(iterations, valid_times, marker='o', label=tool.upper(), linewidth=2)
    
    ax.set_xlabel('Iteration', fontsize=12)
    ax.set_ylabel('Time (seconds)', fontsize=12)
    ax.set_title('Extraction Time Across Iterations', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('benchmark_iterations.png', dpi=300, bbox_inches='tight')
    print("[+] Saved benchmark_iterations.png")
    plt.close()


def main():
    """Generate all charts."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate benchmark charts')
    parser.add_argument('--input', '-i', default='benchmark_results.json',
                       help='Input JSON file with results')
    
    args = parser.parse_args()
    
    if not Path(args.input).exists():
        print(f"[!] Results file not found: {args.input}")
        print("[!] Run compare_tools.py first to generate results")
        return
    
    try:
        results = load_results(args.input)
        
        print("[*] Generating charts...")
        plot_comparison(results)
        plot_speedup(results)
        plot_iteration_times(results)
        
        print("\n[+] All charts generated successfully!")
        
    except Exception as e:
        print(f"[!] Error generating charts: {e}")


if __name__ == '__main__':
    main()

