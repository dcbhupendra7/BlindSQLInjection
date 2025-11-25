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


def plot_algorithm_complexity(results: Dict = None):
    """
    Create algorithm complexity comparison chart showing O(log n) vs O(n).
    Uses actual query count data from benchmarks if available, otherwise uses theoretical calculations.
    
    Args:
        results: Benchmark results dictionary (optional). If provided and contains query_counts,
                 will use actual data. Otherwise uses theoretical calculations.
    """
    # Character range for printable ASCII (32-126 = 95 characters)
    n_range = np.arange(10, 101, 5)  # Range sizes from 10 to 100
    
    # Try to use actual data from benchmarks if available
    use_real_data = False
    if results and 'query_counts' in results:
        query_counts = results['query_counts']
        statsqli_queries = query_counts.get('statsqli', [])
        manual_queries = query_counts.get('manual', [])
        
        if statsqli_queries and manual_queries:
            # Calculate average queries per character
            # Assuming we extracted a string, calculate queries per character
            # For simplicity, we'll use the average queries from all iterations
            avg_statsqli = np.mean([q for q in statsqli_queries if q > 0]) if statsqli_queries else None
            avg_manual = np.mean([q for q in manual_queries if q > 0]) if manual_queries else None
            
            # Estimate queries per character (rough approximation)
            # This is a simplified model - in reality it depends on string length
            if avg_statsqli and avg_manual:
                # Estimate: queries ≈ queries_per_char * string_length
                # For a typical 5-char username, estimate queries per char
                estimated_string_length = 5  # Typical username length
                statsqli_per_char = avg_statsqli / estimated_string_length if estimated_string_length > 0 else 7
                manual_per_char = avg_manual / estimated_string_length if estimated_string_length > 0 else 48
                
                # Use actual data point for 95 character range
                use_real_data = True
                real_binary_queries = statsqli_per_char
                real_linear_avg = manual_per_char
    
    # Binary search: O(log n) - queries needed to find a character
    # For binary search, we need log2(n) comparisons in worst case
    binary_search_queries = np.ceil(np.log2(n_range))
    
    # Linear search: O(n) - queries needed in worst case (average is n/2)
    # Worst case: need to check all characters until found
    linear_search_worst = n_range
    linear_search_avg = n_range / 2
    
    # If we have real data, create a hybrid chart
    if use_real_data:
        # Scale theoretical curves to match real data point at n=95
        idx_95 = np.argmin(np.abs(n_range - 95))
        theoretical_binary_95 = binary_search_queries[idx_95]
        theoretical_linear_95 = linear_search_avg[idx_95]
        
        scale_factor_binary = real_binary_queries / theoretical_binary_95 if theoretical_binary_95 > 0 else 1.0
        scale_factor_linear = real_linear_avg / theoretical_linear_95 if theoretical_linear_95 > 0 else 1.0
        
        # Apply scaling (but keep theoretical shape)
        binary_search_queries = binary_search_queries * scale_factor_binary
        linear_search_avg = linear_search_avg * scale_factor_linear
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Left plot: Queries vs Character Range Size
    ax1.plot(n_range, binary_search_queries, 'o-', label='Binary Search (O(log n))', 
             linewidth=3, markersize=8, color='#2ecc71')
    ax1.plot(n_range, linear_search_worst, marker='s', label='Linear Search Worst Case (O(n))', 
             linewidth=2, markersize=6, color='#e74c3c', linestyle='--')
    ax1.plot(n_range, linear_search_avg, marker='^', label='Linear Search Average (O(n/2))', 
             linewidth=2, markersize=6, color='#f39c12', linestyle=':')
    
    ax1.set_xlabel('Character Range Size (n)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Number of Queries Required', fontsize=12, fontweight='bold')
    title = 'Algorithm Complexity: Queries vs Range Size'
    if use_real_data:
        title += ' (Based on Actual Benchmark Data)'
    else:
        title += ' (Theoretical)'
    ax1.set_title(title, fontsize=14, fontweight='bold')
    ax1.legend(loc='upper left', fontsize=10)
    ax1.grid(alpha=0.3, linestyle='--')
    ax1.set_xlim(10, 100)
    
    # Add annotations for key points (using 95 character range)
    idx_95 = np.argmin(np.abs(n_range - 95))
    binary_95 = binary_search_queries[idx_95]
    linear_95_avg = linear_search_avg[idx_95]
    
    ax1.annotate(f'Binary Search: ~{int(binary_95)} queries\nfor 95 characters', 
                xy=(95, binary_95), xytext=(60, 20),
                arrowprops=dict(arrowstyle='->', color='#2ecc71', lw=2),
                fontsize=10, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    ax1.annotate(f'Linear Search: ~{int(linear_95_avg)} queries\n(average) for 95 characters', 
                xy=(95, linear_95_avg), xytext=(60, 70),
                arrowprops=dict(arrowstyle='->', color='#f39c12', lw=2),
                fontsize=10, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    # Right plot: Speedup Factor
    speedup_worst = linear_search_worst / binary_search_queries
    speedup_avg = linear_search_avg / binary_search_queries
    
    ax2.plot(n_range, speedup_worst, marker='s', label='Speedup vs Worst Case', 
             linewidth=2, markersize=6, color='#e74c3c', linestyle='--')
    ax2.plot(n_range, speedup_avg, marker='^', label='Speedup vs Average Case', 
             linewidth=2, markersize=6, color='#f39c12', linestyle=':')
    ax2.axhline(y=1, color='gray', linestyle='-', linewidth=1, alpha=0.5)
    
    ax2.set_xlabel('Character Range Size (n)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Speedup Factor (x times faster)', fontsize=12, fontweight='bold')
    ax2.set_title('Binary Search Speedup Over Linear Search', fontsize=14, fontweight='bold')
    ax2.legend(loc='upper left', fontsize=10)
    ax2.grid(alpha=0.3, linestyle='--')
    ax2.set_xlim(10, 100)
    ax2.set_ylim(0, max(speedup_worst) * 1.1)
    
    # Add annotation for 95 character range
    # Find index closest to 95
    idx_95 = np.argmin(np.abs(n_range - 95))
    speedup_95_worst = linear_search_worst[idx_95] / binary_search_queries[idx_95]
    speedup_95_avg = linear_search_avg[idx_95] / binary_search_queries[idx_95]
    ax2.annotate(f'At n=95:\nWorst: {speedup_95_worst:.1f}× faster\nAvg: {speedup_95_avg:.1f}× faster', 
                xy=(95, speedup_95_avg), xytext=(60, speedup_95_worst * 0.6),
                arrowprops=dict(arrowstyle='->', color='#3498db', lw=2),
                fontsize=10, bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
    
    plt.tight_layout()
    plt.savefig('algorithm_complexity.png', dpi=300, bbox_inches='tight')
    print("[+] Saved algorithm_complexity.png")
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
        plot_algorithm_complexity(results)  # Algorithm complexity comparison (uses real data if available)
        
        print("\n[+] All charts generated successfully!")
        
    except Exception as e:
        print(f"[!] Error generating charts: {e}")


if __name__ == '__main__':
    main()

