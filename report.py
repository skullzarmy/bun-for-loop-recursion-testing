import json
import glob
from statistics import mean
import matplotlib.pyplot as plt

def load_test_results():
    """
    Load test results from all JSON files that match the pattern 'test_results_*.json'.

    Returns:
        all_results (list): A list of dictionaries with test results from all valid files.
        
    The function attempts to open each file and extend the overall list with the test results.
    If an error occurs (e.g., file not found, invalid JSON, etc.), an error message is printed,
    and the function continues to the next file.
    """
    all_results = []
    for file_name in glob.glob('test_results_*.json'):
        try:
            with open(file_name, 'r') as file:
                data = json.load(file)
                all_results.extend(data.get('test_results', {}).values())
        except (json.JSONDecodeError, FileNotFoundError, KeyError, EOFError) as e:
            print(f"Error loading {file_name}: {e}")
            continue
    return all_results

def analyze_results(all_results):
    """
    Analyze test results, calculating the average execution time and memory usage for each depth.

    Parameters:
        all_results (list): A list of dictionaries containing the test results.

    Outputs:
        A markdown report file with a detailed analysis of the test results and
        a graph image file depicting the average execution time and memory usage by depth.

    The markdown report includes a table of average times and memory usage, detailed statistics
    for each depth, and expandable sections for individual test results at each depth.
    The graph depicts the average execution time and memory usage on a logarithmic scale.
    """
    depth_data = {}
    for tests in all_results:
        for test in tests:
            depth = test['depth']
            metrics = depth_data.setdefault(depth, {'times': [], 'memories': []})
            metrics['times'].append(test['executionTime'])
            metrics['memories'].append(test['memoryUsage'])

    with open('test_analysis_report.md', 'w') as report_file:
        # Writing header and test parameters
        header = (
            "# Test Analysis Report\n"
            "## Test Parameters\n"
            f"- Number of Tests: {len(all_results)}\n"
            f"- Number of Depths: {len(depth_data)}\n"
            f"- Depths: {', '.join(map(str, depth_data.keys()))}\n\n"
            "## Test Results\n"
            "![Test Analysis Graphs](test_analysis_graphs.png)\n\n"
        )
        report_file.write(header)

        # Creating and writing a summary table for the markdown report
        table = "| Depth | Average Time (ms) | Average Memory Usage (MB) |\n| --- | --- | --- |\n"
        table += "\n".join(
            f"| {depth} | {mean(metrics['times']):.4f} | {mean(metrics['memories']):.4f} |"
            for depth, metrics in depth_data.items()
        )
        report_file.write(table + '\n\n')
  
        # Detailed report for each depth including max, min, and average times and memory usage
        for depth, metrics in depth_data.items():
            report = (
                f"### Depth {depth}\n"
                f"- Number of Tests: {len(metrics['times'])}\n"
                f"- Execution Time:\n"
                f"  - Mean (Avg): {mean(metrics['times']):.4f} ms\n"
                f"  - Max: {max(metrics['times']):.4f} ms\n"
                f"  - Min: {min(metrics['times']):.4f} ms\n"
                f"- Memory Usage:\n"
                f"  - Mean (Avg): {mean(metrics['memories']):.4f} MB\n"
                f"  - Max: {max(metrics['memories']):.4f} MB\n"
                f"  - Min: {min(metrics['memories']):.4f} MB\n\n"
            )
            report_file.write(report)

             # Writing detailed test results for each depth
            table = "<details>\n<summary>Test Results</summary>\n\n"
            table += "| Depth | Time (ms) | Memory Usage (MB) |\n| --- | --- | --- |\n"
            table += "\n".join(
                f"| {depth} | {test['executionTime']:.4f} | {test['memoryUsage']:.4f} |"
                for tests in all_results
                for test in tests
                if test['depth'] == depth
            )
            table += "\n\n</details>\n\n"
            report_file.write(table + '\n\n')

    # Plotting the graphs for average execution time and memory usage
    depths = list(depth_data.keys())
    avg_times = [mean(metrics['times']) for metrics in depth_data.values()]
    avg_memories = [mean(metrics['memories']) for metrics in depth_data.values()]

    plt.figure(figsize=(12, 6), dpi=75)

    # Plot for average execution time with a logarithmic scale
    plt.subplot(1, 2, 1)
    plt.plot(depths, avg_times, marker='o', color='k', linestyle='--', linewidth=2, markersize=6)
    plt.yscale('log')
    plt.title('Average Execution Time by Depth (Log Scale)')
    plt.xlabel('Depth')
    plt.ylabel('Average Execution Time (ms)')

    # Plot for average memory usage
    plt.subplot(1, 2, 2)
    plt.plot(depths, avg_memories, marker='o', color='r')
    plt.title('Average Memory Usage by Depth')
    plt.xlabel('Depth')
    plt.ylabel('Average Memory Usage (MB)')

    plt.tight_layout()
    plt.savefig('test_analysis_graphs.png')

def main():
    """
    The main execution function of the script.

    Calls the function to load test results from JSON files and passes them to the analysis function.
    It acts as the entry point for the script when run as a standalone program.
    """
    all_results = load_test_results()
    analyze_results(all_results)

if __name__ == '__main__':
    main()
