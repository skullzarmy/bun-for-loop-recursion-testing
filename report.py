import json
import glob
from statistics import mean

import matplotlib.pyplot as plt

def load_test_results():
    """
    Load test results from all JSON files that match the pattern 'test_results_*.json'.
    Returns a dictionary containing lists of test results, grouped by environment.
    """
    results_by_env = {'bun.sh': [], 'node.js': []}
    for file_name in glob.glob('test_results_*.json'):
        try:
            with open(file_name, 'r') as file:
                data = json.load(file)
                environment = data.get('environment', 'bun.sh')
                results_by_env.setdefault(environment, []).extend(data.get('test_results', {}).values())
        except (json.JSONDecodeError, FileNotFoundError, KeyError, EOFError) as e:
            print(f"Error loading {file_name}: {e}")
            continue
    return results_by_env

def analyze_environment(results, environment):
    """
    Analyze test results for a specific environment and generate a report and graphs.
    """
    depth_data = {}
    for tests in results:
        for test in tests:
            depth = test['depth']
            metrics = depth_data.setdefault(depth, {'times': [], 'memories': [], 'results': []})
            metrics['times'].append(test['executionTime'])
            metrics['memories'].append(test['memoryUsage'])
            metrics['results'].append(test)
    generate_report(depth_data, environment)
    plot_graphs(depth_data, environment)
    return depth_data

def generate_report(depth_data, environment):
    """
    Generate a markdown report file with a detailed analysis of the test results.
    """
    report_filename = f'test_analysis_report_{environment}.md'
    with open(report_filename, 'w') as report_file:
        report_file.write(f"# Test Analysis Report for {environment}\n\n")
        report_file.write(f"![Graphs for {environment}](test_analysis_graphs_{environment}.png)\n\n")
        report_file.write("## Test Results Summary\n\n")
        for depth, metrics in depth_data.items():
            report_file.write(f"### Depth {depth}\n")
            report_file.write(f"- Execution Time:\n")
            report_file.write(f"    - Mean: {mean(metrics['times']):.4f} ms\n")
            report_file.write(f"    - Max: {max(metrics['times']):.4f} ms\n")
            report_file.write(f"    - Min: {min(metrics['times']):.4f} ms\n")
            report_file.write(f"- Memory Usage:\n")
            report_file.write(f"    - Mean: {mean(metrics['memories']):.4f} MB\n")
            report_file.write(f"    - Max: {max(metrics['memories']):.4f} MB\n")
            report_file.write(f"    - Min: {min(metrics['memories']):.4f} MB\n\n")
            report_file.write("<details>\n<summary>Detailed Test Results</summary>\n\n")
            report_file.write("| Test | Execution Time (ms) | Memory Usage (MB) |\n| --- | --- | --- |\n")
            for result in metrics['results']:
                report_file.write(f"| Test at Depth {depth} | {result['executionTime']:.4f} | {result['memoryUsage']:.4f} |\n")
            report_file.write("</details>\n\n")

def plot_graphs(depth_data, environment):
    """
    Plot graphs for the average execution time and memory usage by depth.
    """
    depths = list(depth_data.keys())
    avg_times = [mean(metrics['times']) for metrics in depth_data.values()]
    avg_memories = [mean(metrics['memories']) for metrics in depth_data.values()]
    plt.figure(figsize=(12, 6), dpi=75)
    plt.subplot(1, 2, 1)
    plt.plot(depths, avg_times, marker='o', color='k', linestyle='--', linewidth=2, markersize=6)
    plt.yscale('log')
    plt.title(f'Execution Time by Depth - {environment}')
    plt.xlabel('Depth')
    plt.ylabel('Average Execution Time (ms)')
    plt.subplot(1, 2, 2)
    plt.plot(depths, avg_memories, marker='o', color='r')
    plt.title(f'Memory Usage by Depth - {environment}')
    plt.xlabel('Depth')
    plt.ylabel('Average Memory Usage (MB)')
    plt.tight_layout()
    plt.savefig(f'test_analysis_graphs_{environment}.png')

def create_master_report(depth_data_by_env):
    """
    Create a master report comparing test results across different environments.
    """
    master_report_filename = 'test_analysis_master_report.md'
    with open(master_report_filename, 'w') as master_report:
        master_report.write("# Master Test Analysis Report\n\n")
        master_report.write("## Comparison of Environments\n\n")
        master_report.write("![Comparison Graphs](test_analysis_comparison_graphs.png)\n\n")
        for depth in sorted(next(iter(depth_data_by_env.values())).keys()):
            master_report.write(f"### Depth {depth}\n")
            for env, depth_data in depth_data_by_env.items():
                metrics = depth_data.get(depth, {'times': [], 'memories': []})
                master_report.write(f"- Environment: {env}\n")
                master_report.write(f"  - Execution Time: Mean: {mean(metrics['times']):.4f} ms, Max: {max(metrics['times']):.4f} ms, Min: {min(metrics['times']):.4f} ms\n")
                master_report.write(f"  - Memory Usage: Mean: {mean(metrics['memories']):.4f} MB, Max: {max(metrics['memories']):.4f} MB, Min: {min(metrics['memories']):.4f} MB\n\n")

def plot_comparison_graphs(depth_data_by_env):
    """
    Plot comparison graphs for average execution time and memory usage across environments.
    """
    plt.figure(figsize=(12, 6), dpi=75)
    plt.subplot(1, 2, 1)
    for env, depth_data in depth_data_by_env.items():
        depths = list(depth_data.keys())
        avg_times = [mean(metrics['times']) for metrics in depth_data.values()]
        plt.plot(depths, avg_times, marker='o', linestyle='--', label=env)
    plt.yscale('log')
    plt.title('Execution Time Comparison by Depth')
    plt.xlabel('Depth')
    plt.ylabel('Average Execution Time (ms)')
    plt.legend()
    plt.subplot(1, 2, 2)
    for env, depth_data in depth_data_by_env.items():
        depths = list(depth_data.keys())
        avg_memories = [mean(metrics['memories']) for metrics in depth_data.values()]
        plt.plot(depths, avg_memories, marker='o', label=env)
    plt.title('Memory Usage Comparison by Depth')
    plt.xlabel('Depth')
    plt.ylabel('Average Memory Usage (MB)')
    plt.legend()
    plt.tight_layout()
    plt.savefig('test_analysis_comparison_graphs.png')

def analyze_results(results_by_env):
    """
    Analyze test results for each environment and create a master report comparing environments.
    """
    depth_data_by_env = {}
    for env, results in results_by_env.items():
        depth_data = analyze_environment(results, env)
        depth_data_by_env[env] = depth_data
    create_master_report(depth_data_by_env)
    plot_comparison_graphs(depth_data_by_env)

def main():
    """
    Main execution function of the script.
    Loads test results, analyzes them by environment, and generates reports and comparison graphs.
    """
    results_by_env = load_test_results()
    analyze_results(results_by_env)

if __name__ == '__main__':
    main()
