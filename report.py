import json
import glob
from statistics import mean
import matplotlib.pyplot as plt

def load_test_results():
    """
    Load test results from all JSON files that match the pattern 'test_results_*.json'.
    
    Returns:
        results_by_env (dict): A dictionary containing lists of test results, grouped by environment.
    """
    results_by_env = {'bun.sh': [], 'node.js': []}
    for file_name in glob.glob('test_results_*.json'):
        try:
            with open(file_name, 'r') as file:
                data = json.load(file)
                # Default to 'bun.sh' if environment not specified
                environment = data.get('environment', 'bun.sh')
                # Aggregate results in the appropriate environment category
                results_by_env.setdefault(environment, []).extend(data.get('test_results', {}).values())
        except (json.JSONDecodeError, FileNotFoundError, KeyError, EOFError) as e:
            print(f"Error loading {file_name}: {e}")
            continue
    return results_by_env

def analyze_results(results_by_env):
    """
    Analyze test results for each environment and create a master report comparing environments.

    Parameters:
        results_by_env (dict): A dictionary containing lists of test results, grouped by environment.
    """
    # Analyze and create individual reports for each environment
    depth_data_by_env = {}
    for env, results in results_by_env.items():
        depth_data = analyze_environment(results, env)
        depth_data_by_env[env] = depth_data

    # Create a master report comparing environments
    create_master_report(depth_data_by_env)

def analyze_environment(results, environment):
    """
    Analyze test results for a specific environment and generate a report and graphs.

    Parameters:
        results (list): A list of dictionaries containing the test results for an environment.
        environment (str): The environment being analyzed.

    Returns:
        depth_data (dict): A dictionary containing aggregated test metrics for the environment.
    """
    depth_data = {}
    for tests in results:
        for test in tests:
            depth = test['depth']
            metrics = depth_data.setdefault(depth, {'times': [], 'memories': []})
            metrics['times'].append(test['executionTime'])
            metrics['memories'].append(test['memoryUsage'])

    report_filename = f'test_analysis_report_{environment}.md'
    with open(report_filename, 'w') as report_file:
        write_report(report_file, depth_data, environment)

    plot_graphs(depth_data, environment)
    return depth_data

def create_master_report(depth_data_by_env):
    """
    Create a master report comparing test results across different environments.

    Parameters:
        depth_data_by_env (dict): A dictionary of test metrics grouped by environment.
    """
    master_report_filename = 'test_analysis_master_report.md'
    with open(master_report_filename, 'w') as master_report:
        master_report.write("# Master Test Analysis Report\n\n")
        master_report.write("## Comparison of Environments\n\n")
        master_report.write("![Comparison Graphs](./test_analysis_comparison_graphs.png)\n\n")

        for depth in sorted(next(iter(depth_data_by_env.values())).keys()):
            master_report.write(f"### Depth {depth}\n")
            for env, depth_data in depth_data_by_env.items():
                if depth in depth_data:
                    metrics = depth_data[depth]
                    master_report.write(f"- Environment: {env}\n")
                    master_report.write(f"  - Mean Execution Time: {mean(metrics['times']):.4f} ms\n")
                    master_report.write(f"  - Mean Memory Usage: {mean(metrics['memories']):.4f} MB\n")

            master_report.write("\n")

    plot_comparison_graphs(depth_data_by_env)

def plot_comparison_graphs(depth_data_by_env):
    """
    Plot comparison graphs for average execution time and memory usage across environments.

    Parameters:
        depth_data_by_env (dict): A dictionary of test metrics grouped by environment.
    """
    environments = depth_data_by_env.keys()
    all_depths = sorted(set(depth for depth_data in depth_data_by_env.values() for depth in depth_data.keys()))

    plt.figure(figsize=(12, 6), dpi=75)

    # Execution Time Comparison
    plt.subplot(1, 2, 1)
    for env, depth_data in depth_data_by_env.items():
        avg_times = [mean(depth_data[depth]['times']) if depth in depth_data else None for depth in all_depths]
        plt.plot(all_depths, avg_times, marker='o', linestyle='--', label=env)
    plt.yscale('log')
    plt.title('Execution Time Comparison by Depth')
    plt.xlabel('Depth')
    plt.ylabel('Average Execution Time (ms)')
    plt.legend()

    # Memory Usage Comparison
    plt.subplot(1, 2, 2)
    for env, depth_data in depth_data_by_env.items():
        avg_memories = [mean(depth_data[depth]['memories']) if depth in depth_data else None for depth in all_depths]
        plt.plot(all_depths, avg_memories, marker='o', label=env)
    plt.title('Memory Usage Comparison by Depth')
    plt.xlabel('Depth')
    plt.ylabel('Average Memory Usage (MB)')
    plt.legend()

    plt.tight_layout()
    plt.savefig('test_analysis_comparison_graphs.png')

def write_report(report_file, depth_data, environment):
    """
    Write a markdown report file with a detailed analysis of the test results for a specific environment.

    Parameters:
        report_file (file object): The file object to write the report to.
        depth_data (dict): A dictionary containing test metrics for an environment.
        environment (str): The environment being analyzed.
    """
    graph_filename = f'./test_analysis_graphs_{environment}.png'
    
    report_file.write(f"# Test Analysis Report for {environment}\n\n")
    report_file.write(f"![Graphs for {environment}]({graph_filename})\n\n")
    report_file.write("## Test Results Summary\n\n")
    report_file.write("| Depth | Average Time (ms) | Average Memory Usage (MB) |\n| --- | --- | --- |\n")
    for depth, metrics in depth_data.items():
        report_file.write(f"| {depth} | {mean(metrics['times']):.4f} | {mean(metrics['memories']):.4f} |\n")

    report_file.write("\n## Detailed Results\n\n")
    for depth, metrics in depth_data.items():
        report_file.write(f"### Depth {depth}\n")
        report_file.write(f"- Execution Time: Mean: {mean(metrics['times']):.4f} ms\n")
        report_file.write(f"- Memory Usage: Mean: {mean(metrics['memories']):.4f} MB\n\n")

def plot_graphs(depth_data, environment):
    """
    Plot graphs for the average execution time and memory usage by depth for a specific environment.

    Parameters:
        depth_data (dict): A dictionary containing test metrics for an environment.
        environment (str): The environment being analyzed.
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

def main():
    """
    Main execution function of the script.

    Loads test results, analyzes them by environment, generates individual reports, and creates a master report for comparison.
    """
    results_by_env = load_test_results()
    analyze_results(results_by_env)

if __name__ == '__main__':
    main()
