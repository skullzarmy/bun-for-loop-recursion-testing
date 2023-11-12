const fs = require("fs").promises;
const crypto = require("crypto");
const { spawn } = require("child_process");

/**
 * Simulates a computation that would typically require deep recursion by using an iterative approach.
 * The function's workload can be adjusted to more accurately reflect a real-world scenario.
 *
 * @param {number} depth - The nesting level to simulate.
 * @param {number} range - The range of the loop counters, to simulate variable-sized loops.
 * @param {Function} workload - A function representing the workload to be performed at the deepest level.
 * @returns {number} - The result of the simulated computation.
 */
function executeNestedForLoops(depth, range, workload) {
    let result = 0;
    let multiplier = 1;
    const stack = [{ depth: 0, multiplier }];

    while (stack.length > 0) {
        const { depth: currentDepth, multiplier: currentMultiplier } = stack.pop();

        if (currentDepth === depth) {
            for (let i = 0; i < range; i++) {
                for (let j = 0; j < range; j++) {
                    result += workload(i, j, currentMultiplier);
                }
            }
        } else {
            const nextMultiplier = currentDepth % 2 === 0 ? currentMultiplier : -currentMultiplier;
            for (let k = 0; k < range; k++) {
                stack.push({ depth: currentDepth + 1, multiplier: nextMultiplier });
            }
        }
    }

    return result;
}

/**
 * Represents a workload function to be performed at the deepest level of the nested loops.
 * This can be replaced with any computationally intensive task for testing.
 *
 * @param {number} i - The first loop counter.
 * @param {number} j - The second loop counter.
 * @param {number} multiplier - A multiplier affecting the result.
 * @returns {number} - The result of a single workload computation.
 */
function workload(i, j, multiplier) {
    // A dummy workload function that could be replaced with a more complex computation.
    return Math.pow(i * j * multiplier, 2);
}

/**
 * Runs a single test iteration and measures its execution time and memory usage.
 * Now also checks for asynchronous operations and properly awaits them.
 *
 * @param {number} depth - The depth of nested loops to test.
 * @param {number} range - The range of the loop counters.
 * @param {Function} workload - The workload function to execute.
 * @returns {object} - The metrics collected during the test execution.
 */
function runTest(depth, range, workload) {
    const startTime = process.hrtime.bigint();
    const result = executeNestedForLoops(depth, range, workload);
    const endTime = process.hrtime.bigint();

    // For memory usage, calculate the heap used after the test is run.
    const memoryUsage = process.memoryUsage().heapUsed / 1024 / 1024; // Convert bytes to megabytes

    return {
        executionTime: Number(endTime - startTime) / 1e6, // Convert nanoseconds to milliseconds
        result,
        memoryUsage,
    };
}

/**
 * Generates a unique filename for storing test results, incorporating a random component to ensure uniqueness.
 * This filename is designed to be descriptive, including the number of tests and the depth of loops, allowing
 * for easy identification of the test parameters from the filename alone.
 *
 * @param {number} testCount - The number of tests that will be run, included in the filename for reference.
 * @param {number} depthCount - The depth of each test, included in the filename to indicate the test complexity.
 * @returns {string} - A filename string unique to the test parameters, combining test details and a random string.
 */
function generateUniqueFilename(testCount, depthCount) {
    const randomString = crypto.randomBytes(8).toString("hex");
    return `test_results_${testCount}x${depthCount}_${randomString}.json`;
}

/**
 * Parses a string to determine if it's a single number, a range, or a list of numbers.
 * This method validates the input to ensure all numbers are positive and within the required limits,
 * throwing errors and exiting the process for any invalid inputs.
 *
 * @param {string} inputStr - A string that represents a single number, a range, or a list of numbers.
 *                            Valid examples include "5", "[1-5]", "1,3,5", and "[1-3],5".
 * @param {boolean} isDepth - A flag indicating if the input is for depth counts, which have specific limits.
 *                            This allows for extra validation, such as ensuring depth is between 1 and 10.
 * @returns {number[]} - An array of numbers parsed from the input string, used for generating test parameters.
 */
async function parseInput(inputStr, isDepth = false) {
    const components = inputStr.split(",").map((s) => s.trim());
    let parsedNumbers = [];

    for (const component of components) {
        if (/^\[(\d+)-(\d+)\]$/.test(component)) {
            // Handle ranges in square brackets
            const [, startStr, endStr] = component.match(/^\[(\d+)-(\d+)\]$/);
            const start = parseInt(startStr, 10);
            const end = parseInt(endStr, 10);

            if (start < 0 || end < 0 || start > end) {
                console.error(`Error: Invalid range '${component}'. Please provide a valid positive integer range.`);
                process.exit(1);
            }

            if (isDepth && (start > 10 || end > 10)) {
                console.error(`Error: Maximum depth count is 10. Trust me, this is a HARD limit.`);
                process.exit(1);
            }

            if (isDepth && start < 1) {
                console.error(`Error: Depth count must be at least 1.`);
                process.exit(1);
            }

            parsedNumbers = parsedNumbers.concat(Array.from({ length: end - start + 1 }, (_, i) => start + i));
        } else {
            // Handle single numbers and ranges without square brackets
            const singleOrRange = component.split("-").map((s) => parseInt(s.trim(), 10));
            if (singleOrRange.some(isNaN) || singleOrRange.some((n) => n < 0)) {
                console.error(`Error: Invalid input '${component}'. Please provide valid positive integers or ranges.`);
                process.exit(1);
            }

            if (singleOrRange.length === 1) {
                // Single number
                const number = singleOrRange[0];
                if (isDepth && (number < 1 || number > 10)) {
                    console.error(`Error: Depth count must be between 1 and 10.`);
                    process.exit(1);
                }
                if (isDepth && number == 10) {
                    console.log(
                        "Warning: Depth count greater than 8 is not generally advised. Here thar be dragons..."
                    );
                    // Give the user a chance to cancel the test.
                    const response = await prompt("Continue? (y/n) ");
                    if (response !== "y") {
                        console.log("Test cancelled, good call.");
                        return false;
                    }
                    console.log("OK, you asked for it. Wait here... FYI depth of 10 can take upwards of 22 minutes.");
                    console.log("Test starting");
                }
                parsedNumbers.push(number);
            } else if (singleOrRange.length === 2) {
                // Range without square brackets
                const [start, end] = singleOrRange;
                if (start > end) {
                    console.error(
                        `Error: Invalid range '${component}'. The start of the range must not exceed the end.`
                    );
                    process.exit(1);
                }
                if (isDepth && end > 10) {
                    console.error(`Error: Maximum depth count is 10. Trust me, this is a HARD limit.`);
                    process.exit(1);
                }
                if (isDepth && end == 10) {
                    console.log(
                        "Warning: Depth count greater than 8 is not generally advised. Here thar be dragons..."
                    );
                    // Give the user a chance to cancel the test.
                    const response = await prompt("Continue? (y/n) ");
                    if (response !== "y") {
                        console.log("Test cancelled, good call.");
                        return false;
                    }
                    console.log("OK, you asked for it. Wait here... FYI depth of 10 can take upwards of 22 minutes.");
                    console.log("Test starting");
                }
                parsedNumbers = parsedNumbers.concat(Array.from({ length: end - start + 1 }, (_, i) => start + i));
            } else {
                console.error(`Error: Too many dashes in input '${component}'.`);
                process.exit(1);
            }
        }
    }

    return parsedNumbers;
}

/**
 * The main function that runs performance tests on a nested loops function.
 * It accepts command-line arguments to define the scope of the tests.
 *
 * Input format for test and depth counts:
 * - Single numbers (e.g., "5" will run tests for count 5).
 * - Ranges in square brackets to include all integers in the range (e.g., "[1-5]" will process 1, 2, 3, 4, and 5).
 * - Comma-separated lists to include specific integers (e.g., "1,3,5" will process 1, 3, and 5).
 * - A combination of the above (e.g., "[1-3],5" will process 1, 2, 3, and 5).
 *
 * Allowed integers:
 * - For test counts, any positive integer is allowed.
 * - For depth counts, positive integers from 1 to 10 are allowed due to the heavy computation beyond this range.
 *
 * Output:
 * - For each test and depth count, the function generates a unique JSON file with the test results.
 * - The JSON file includes the test count, depth count, and an array of test results with execution time and result.
 * - The filename is constructed with the test parameters and a random component for uniqueness.
 *
 * @param {string} testCountArg - The command-line argument representing the number of tests or test ranges.
 * @param {string} depthCountArg - The command-line argument representing the depth of nested loops or depth ranges.
 * @async - Marks the function as asynchronous due to file writing operations.
 * @returns {Promise<void>} - No return value but outputs files with test results.
 */
async function main() {
    const testCountArg = process.argv[2] || "1";
    const depthCountArg = process.argv[3] || "8";

    const testCounts = await parseInput(testCountArg);
    const depthCounts = await parseInput(depthCountArg, true);

    if (!testCounts || !depthCounts || testCounts.length === 0 || depthCounts.length === 0) {
        return;
    }

    for (const testCount of testCounts) {
        for (const depthCount of depthCounts) {
            const outputFileName = generateUniqueFilename(testCount, depthCount);

            const jsonStructure = {
                environment: "node.js", // Add environment designation
                test_count: testCount,
                depth_count: depthCount,
                test_results: {},
            };

            for (let i = 0; i < testCount; i++) {
                const range = 10; // This value can be changed to simulate different loop ranges
                jsonStructure.test_results[`iteration_${i + 1}`] = [];

                for (let depth = 1; depth <= depthCount; depth++) {
                    const testResult = runTest(depth, range, workload);
                    jsonStructure.test_results[`iteration_${i + 1}`].push({
                        depth,
                        ...testResult,
                    });
                }
            }

            try {
                await fs.writeFile(outputFileName, JSON.stringify(jsonStructure, null, 2));
                console.log(`Results saved to ${outputFileName}`);
            } catch (error) {
                console.error(`Error writing results to file: ${error.message}`);
            }
        }
    }
}

/**
 * Prompts the user for input and returns the response.
 *
 * @param {string} prompt - The prompt to display to the user.
 * @returns {Promise<string>} - The user's response.
 */
let report = process.argv.includes("--report");

main().then(() => {
    if (report) {
        const pyprog = spawn("python3", ["report.py"]);

        pyprog.stdout.on("data", (data) => {
            console.log(data.toString());
        });

        pyprog.stderr.on("data", (data) => {
            console.error(`stderr: ${data}`);
        });

        pyprog.on("close", (code) => {
            console.log(`child process exited with code ${code}`);
        });
    }
});
