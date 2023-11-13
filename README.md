# Recursive Loop Testing for bun.sh

This repository contains a [SoCalTechLab.com](https://socaltechlab.com/) project aimed at testing recursive for loops in [bun.sh](https://bun.sh), a purportedly fast all-in-one JavaScript runtime.

[![SoCalTechLab.com logo - click to visit](./sctl_xs_rounded_white_text.webp)](https://socaltechlab.com/?rel=bunRecursionGitHubRepo)

[a SoCalTechLab.com project](https://socaltechlab.com/?rel=bunRecursionGitHubRepo)

## Overview

The purpose of this project is to assess the performance of recursive for loops in bun.sh, versus standard node.js, by simulating deep recursion with iterative approaches. The project consists of two main components:

-   Test Running
    -   A TypeScript script (`test.ts`) that generates test data by simulating recursive for loops in bun.sh.
    -   A TypeScript script (`test_node.ts`) that generates test data by simulating recursive for loops in standard node.js.
-   Reporting
    -   A Python script (`report.py`) that analyzes the generated test results and produces a detailed report along with visual graphs for each environment and a master report comparing all environments.

## Repository Structure

-   `test_node.ts`: The TypeScript script used for generating test data within the node.js environment.
-   `test.ts`: The TypeScript script used for generating test data within the bun.sh environment.
-   `report.py`: The Python script for analyzing test data and producing reports.
    -   **Results:** [test_analysis_master_report.md](./test_analysis_master_report.md)

## Getting Started

To run the tests and generate reports, follow these steps:

1. Install [bun.sh](https://bun.sh) on your system.
2. Execute the TypeScript script to generate test data:

    ```
    bun test.ts [testCountArg] [depthCountArg] --report
    ```

    - `testCountArg`: (Optional) Defines the number of tests to run. Default is 1.
    - `depthCountArg`: (Optional) Specifies the depth of nested loops to test. Default is 8.
    - `--report`: (Optional) Calls the python report.py script upon completion of tests.

    This script will simulate recursive for loops and store the results in JSON format.

3. Once the test data is generated, run the Python script to analyze the results and produce a report:

    ```
    python report.py
    ```

    The script will create a series of `test_analysis_report_{environment}.md` files containing the analysis and save a graph depicting the performance as `test_analysis_graphs_{environment}.png`.

    Additionally it will generate a master [test_analysis_master_report.md](./test_analysis_master_report.md) report, comparing all environments.

## Contributing

We welcome contributions from the community. Please read our contributing guidelines before submitting your pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

This project is developed and maintained by the SoCalTechLab team. Visit [SoCalTechLab.com](https://socaltechlab.com) for more information on our other projects and research initiatives.
