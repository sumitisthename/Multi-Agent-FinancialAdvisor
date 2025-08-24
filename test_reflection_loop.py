# test_reflection_loop.py
import subprocess
import re
import matplotlib.pyplot as plt
from utils.logger import get_logger

logger = get_logger()

def run_simulation_cycle():
    """
    Runs one full cycle of the main application and captures the output.
    """
    logger.info("Running a simulation cycle...")
    result = subprocess.run(
        ["python", "main.py"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        logger.error(f"Simulation cycle failed with return code {result.returncode}")
        logger.error(result.stderr)
        return None, result.stderr

    logger.info("Simulation cycle completed successfully.")
    return result.stdout, None

def extract_mape_from_output(output):
    """
    Extracts the MAPE value from the simulation output using regex.
    """
    mape_match = re.search(r"Average MAPE: ([\d\.]+)%", output)
    if mape_match:
        mape = float(mape_match.group(1))
        logger.info(f"Extracted MAPE: {mape:.2f}%")
        return mape
    else:
        logger.warning("Could not find MAPE in the output.")
        return None

def plot_mape_trend(mape_history):
    """
    Plots the MAPE values over iterations to visualize the trend.
    """
    if not mape_history:
        logger.warning("MAPE history is empty. Cannot generate plot.")
        return

    plt.figure(figsize=(10, 6))
    plt.plot(range(1, len(mape_history) + 1), mape_history, marker='o', linestyle='-')
    plt.title("Forecasting Agent MAPE Over Time")
    plt.xlabel("Iteration")
    plt.ylabel("MAPE (%)")
    plt.grid(True)

    # Save the plot to a file
    plot_path = "mape_trend.png"
    plt.savefig(plot_path)
    logger.info(f"MAPE trend plot saved to {plot_path}")
    print(f"\n📈 MAPE trend plot saved to {plot_path}")

def run_test(iterations=10):
    """
    Runs the automated test for a specified number of iterations.
    """
    logger.info(f"Starting automated test for {iterations} iterations...")
    mape_history = []

    for i in range(1, iterations + 1):
        logger.info(f"--- Iteration {i}/{iterations} ---")
        output, error = run_simulation_cycle()

        if error:
            logger.error("Aborting test due to simulation failure.")
            break

        mape = extract_mape_from_output(output)
        if mape is not None:
            mape_history.append(mape)

    logger.info("Automated test completed.")

    if mape_history:
        print("\n--- Test Results ---")
        for i, mape in enumerate(mape_history, 1):
            print(f"Iteration {i}: MAPE = {mape:.2f}%")

        initial_mape = mape_history[0]
        final_mape = mape_history[-1]
        improvement = initial_mape - final_mape

        print(f"\nInitial MAPE: {initial_mape:.2f}%")
        print(f"Final MAPE:   {final_mape:.2f}%")
        print(f"Improvement:  {improvement:.2f}%")

        # Plot the results
        plot_mape_trend(mape_history)
    else:
        print("\n--- Test Results ---")
        print("No MAPE values were recorded during the test.")

if __name__ == "__main__":
    # It's recommended to run this with a small number of iterations first
    # to ensure everything is working correctly.
    run_test(iterations=5)
