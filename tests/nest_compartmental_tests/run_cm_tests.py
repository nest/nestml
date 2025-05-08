import subprocess
import os
import matplotlib.pyplot as plt


def run_tests():
    # Enable interactive mode for matplotlib
    plt.ion()

    # Specify the directory containing the tests
    test_directory = "./"

    # Check if the directory exists
    if not os.path.exists(test_directory):
        print(f"Error: The directory '{test_directory}' does not exist.")
        return

    # Run pytest in the specified directory
    try:
        # Run pytest in the specified directory with live output
        process = subprocess.Popen(
            ["pytest", test_directory],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        # Print output line by line as it happens
        for line in iter(process.stdout.readline, ""):
            print(line, end="")  # Output each line immediately

        process.stdout.close()  # Close stdout once done
        process.wait()  # Wait for the process to finish

    except Exception as e:
        print(f"An error occurred while running the tests: {e}")


if __name__ == "__main__":
    run_tests()
