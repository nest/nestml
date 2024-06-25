import argparse
import subprocess
import re
import json
import math
from time import sleep
import matplotlib.pyplot as plt
from jinja2 import Environment, FileSystemLoader
import numpy as np
import os

parser = argparse.ArgumentParser(description='Run a Benchmark with NEST')
parser.add_argument('--noRunSim', action="store_false", help='Run the Benchmark with NEST Simulator')

current_dir = os.path.dirname(os.path.abspath(__file__))
PATHTOFILE = os.path.join(current_dir, "examples/brunel_alpha_nest.py")

# for aeif_psc_alpha neurons
BASELINENEURON = "aeif_psc_alpha"
NEURONMODELS = [
    "aeif_psc_alpha_neuron_Nestml_Plastic__with_stdp_synapse_Nestml_Plastic",
    "aeif_psc_alpha_neuron_Nestml",
    BASELINENEURON,
    "aeif_psc_alpha_neuron_Nestml_Plastic_noco__with_stdp_synapse_Nestml_Plastic_noco"
]

legend = {
    "aeif_psc_alpha_neuron_Nestml_Plastic__with_stdp_synapse_Nestml_Plastic": "NESTML neur, NESTML syn",
    "aeif_psc_alpha_neuron_Nestml": "NESTML neur, NEST syn",
    BASELINENEURON: "NEST neur + syn",
    "aeif_psc_alpha_neuron_Nestml_Plastic_noco__with_stdp_synapse_Nestml_Plastic_noco": "NESTML neur, NESTML syn NOCO",
}

colors = {
    BASELINENEURON: 0,
    "aeif_psc_alpha_neuron_Nestml_Plastic__with_stdp_synapse_Nestml_Plastic": 1,
    "aeif_psc_alpha_neuron_Nestml": 2,
    "aeif_psc_alpha_neuron_Nestml_Plastic_noco__with_stdp_synapse_Nestml_Plastic_noco": 3
}

# MPI scaling
DEBUG = True
ITERATIONS = 2  # XXXXXXXXXXXX: was 10
NUMTHREADS = 128  # Total number of threads per node
NETWORKSCALES = np.logspace(3, math.log10(20000), 5, dtype=int)  # XXXXXXXXXXXX: was 10 and 30000

# MPI Strong scaling
MPI_SCALES = np.logspace(1, math.log2(64), num=6, base=2, dtype=int)
MPI_STRONG_SCALE_NEURONS = NETWORKSCALES[-1]
STRONGSCALINGMPIFOLDERNAME = "timings_strong_scaling_mpi"

# MPI Weak scaling
MPI_WEAK_SCALE_NEURONS = 20000
WEAKSCALINGMPIFOLDERNAME = "timings_weak_scaling_mpi"

output_folder = os.path.join(os.path.dirname(__file__), os.pardir, 'Output_MPI', BASELINENEURON)

# Plotting variables
palette = plt.get_cmap("Set1")


def log(message):
    print(message)
    with open(os.path.join(output_folder, "log.txt"), "a") as f:
        f.write(f"{message}\n")
        f.close()


def render_sbatch_template(combination, filename):
    template = setup_template_env()
    namespace = {}
    namespace["nodes"] = combination["nodes"]  # number of nodes
    namespace["ntasks_per_node"] = 2
    namespace["cpus_per_task"] = int(combination["threads"] / 2)
    namespace["combination"] = combination
    file = template.render(namespace)
    log("Rendering template: " + template.filename)

    log("Rendered template file name: " + filename)
    with open(filename, "w+") as f:
        f.write(str(file))
        f.close()


def start_strong_scaling_benchmark_mpi(iteration):
    dirname = os.path.join(output_folder, STRONGSCALINGMPIFOLDERNAME)
    combinations = [
        {
            "nodes": compute_nodes,
            "simulated_neuron": neuronmodel,
            "network_scale": MPI_STRONG_SCALE_NEURONS,
            "threads": NUMTHREADS,
            "iteration": iteration,
            "output_file": f"run_simulation_{neuronmodel}_{compute_nodes}_{iteration}_%j.out",
            "error_file": f"run_simulation_{neuronmodel}_{compute_nodes}_{iteration}_%j.err",
            "benchmarkPath": dirname
        } for neuronmodel in NEURONMODELS for compute_nodes in MPI_SCALES]

    for combination in combinations:
        print("RUNNING FOR " + str(combination))
        combined = combination["simulated_neuron"] + "," + str(combination["nodes"])
        log(f"\033[93m{combined}\033[0m" if DEBUG else combined)

        filename = "sbatch_run_" + combination["simulated_neuron"] + "_" + str(combination["nodes"]) + "_[iter=" + str(
            iteration) + "].sh"
        filename = os.path.join(dirname, "sbatch", filename)
        # Create the sbatch file
        render_sbatch_template(combination, filename)
        command = ["sbatch", f"{filename}"]
        result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def start_weak_scaling_benchmark_mpi(iteration):
    dirname = os.path.join(output_folder, WEAKSCALINGMPIFOLDERNAME)
    combinations = [
        {
            "nodes": compute_nodes,
            "simulated_neuron": neuronmodel,
            "network_scale": MPI_WEAK_SCALE_NEURONS * compute_nodes,
            "threads": NUMTHREADS,
            "iteration": iteration,
            "output_file": f"run_simulation_{neuronmodel}_{compute_nodes}_{MPI_WEAK_SCALE_NEURONS * compute_nodes}_{iteration}_%j.out",
            "error_file": f"run_simulation_{neuronmodel}_{compute_nodes}_{MPI_WEAK_SCALE_NEURONS * compute_nodes}_{iteration}_%j.err",
            "benchmarkPath": dirname
        } for neuronmodel in NEURONMODELS for compute_nodes in MPI_SCALES]
    for combination in combinations:
        print("RUNNING FOR " + str(combination))
        combined = combination["simulated_neuron"] + "," + str(combination["nodes"]) + "," + str(
            combination["network_scale"])
        log(f"\033[93m{combined}\033[0m" if DEBUG else combined)

        filename = "sbatch_run_" + combination["simulated_neuron"] + "_" + str(combination["nodes"]) + "_" + str(
            combination["network_scale"]) + "_[iter=" + str(iteration) + "].sh"
        filename = os.path.join(dirname, "sbatch", filename)
        # Create the sbatch file
        render_sbatch_template(combination, filename)
        command = ["sbatch", f"{filename}"]
        result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def extract_value_from_filename(filename, key):
    pattern = fr"\[{key}=(.*?)\]"
    match = re.search(pattern, filename)
    return match.group(1) if match else None


def plot_scaling_data(sim_data: dict, file_prefix: str):
    plt.figure()
    neurons = []
    for neuron, values in sim_data.items():
        neurons.append(neuron)
        x = sorted(values.keys(), key=lambda k: int(k))
        for threads in x:
            _ = [print(iteration_data['time_simulate']) for iteration_data in values[threads].values()]
        for threads in x:
            _ = [print(iteration_data['biological_time']) for iteration_data in values[threads].values()]
        y = np.array([np.mean(
            [iteration_data['time_simulate'] / (iteration_data["biological_time"] / 1000) for iteration_data in
             values[threads].values()]) for threads in x])
        y_std = np.array([np.std(
            [iteration_data['time_simulate'] / (iteration_data["biological_time"] / 1000) for iteration_data in
             values[threads].values()]) for threads in x])

        x = np.array([int(val) for val in x], dtype=int)
        plt.errorbar(x, y, yerr=y_std, label=legend[neuron], color=palette(colors[neuron]), linestyle='-', marker='o',
                     markersize=4, ecolor='gray', capsize=2)

    plt.xlabel('Number of nodes')
    plt.ylabel('Wall clock time (s)')
    plt.xscale('log')
    # plt.yscale('log')
    plt.xticks(MPI_SCALES, MPI_SCALES)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, file_prefix + '_abs.png'))

    plt.figure()
    neurons = []
    referenceValues = sim_data[BASELINENEURON]
    for neuron, values in sim_data.items():
        neurons.append(neuron)
        x = sorted(values.keys(), key=lambda k: int(k))
        # Real Time Factor
        reference_y = np.array([np.mean(
            [iteration_data['time_simulate'] / (iteration_data["biological_time"] / 1000) for iteration_data in
             referenceValues[threads].values()]) for threads in x])
        y = np.array([np.mean(
            [iteration_data['time_simulate'] / (iteration_data["biological_time"] / 1000) for iteration_data in
             values[threads].values()]) for threads in x])
        y_factor = y / reference_y  # Calculate the factor of y in comparison to the reference value

        y_std = np.array([np.std(
            [iteration_data['time_simulate'] / (iteration_data["biological_time"] / 1000) for iteration_data in
             values[threads].values()]) for threads in x])
        y_factor_std = y_std / reference_y  # Calculate the standard deviation of the factor

        x = np.array([int(val) for val in x], dtype=int)
        plt.errorbar(x, y_factor, yerr=y_factor_std, label=legend[neuron], color=palette(colors[neuron]), linestyle='-',
                     marker='o', markersize=4, ecolor='gray', capsize=2)

    plt.xlabel('Number of nodes')
    plt.ylabel('Wall clock time (ratio)')

    plt.xscale('log')
    # plt.yscale('log')
    plt.xticks(MPI_SCALES, MPI_SCALES)

    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, file_prefix + '_rel.png'))


def process_data(dir_name: str):
    scaling_data = {}
    for filename in os.listdir(os.path.join(output_folder, dir_name)):
        if filename.endswith(".json"):
            simulated_neuron = extract_value_from_filename(filename, "simulated_neuron")
            nodes = int(extract_value_from_filename(filename, "nodes"))
            iteration = int(extract_value_from_filename(filename, "iteration"))
            with open(os.path.join(output_folder, dir_name, filename), "r") as f:
                data = f.read()
                json_data = clean_json_content(data)
                scaling_data.setdefault(simulated_neuron, {}).setdefault(nodes, {}).setdefault(iteration, json_data)
                f.close()

    return scaling_data


def plot_strong_scaling_benchmark():
    strong_scaling_data = process_data(STRONGSCALINGMPIFOLDERNAME)
    plot_scaling_data(strong_scaling_data, "strong_scaling_mpi")


def plot_weak_scaling_benchmark():
    weak_scaling_data = process_data(WEAKSCALINGMPIFOLDERNAME)
    plot_scaling_data(weak_scaling_data, "weak_scaling_mpi")


def deleteDat():
    for filename in os.listdir("./"):
        if filename.endswith(".dat"):
            os.remove(f"./{filename}")


def deleteJson():
    for filename in os.listdir(os.path.join(output_folder, WEAKSCALINGMPIFOLDERNAME)):
        if filename.endswith(".json"):
            os.remove(os.path.join(output_folder, WEAKSCALINGMPIFOLDERNAME, filename))
    for filename in os.listdir(os.path.join(output_folder, STRONGSCALINGMPIFOLDERNAME)):
        if filename.endswith(".json"):
            os.remove(os.path.join(output_folder, STRONGSCALINGMPIFOLDERNAME, filename))


def setup_template_env():
    template_file = "sbatch_run.sh.jinja2"
    template_dir = os.path.realpath(os.path.join(os.path.dirname(__file__)))
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_file)
    return template


def check_for_completion():
    command = ["squeue", "--me"]
    while True:
        result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        nlines = len(result.stdout.splitlines())
        log("Checking for running jobs. Number of jobs running: " + str(nlines - 1))
        if nlines == 1:  # column headers in the output counts to one line
            break
        sleep(10.)


def clean_json_content(content):
    """
    Clean JSON content by iteratively removing characters from the end until it parses successfully.
    """
    while content:
        try:
            data = json.loads(content)
            return data
        except json.JSONDecodeError:
            content = content[:-1]  # Remove last character and try again
    return None


if __name__ == "__main__":
    args = parser.parse_args()
    runSim = args.noRunSim

    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(os.path.join(output_folder, STRONGSCALINGMPIFOLDERNAME), exist_ok=True)
    os.makedirs(os.path.join(output_folder, WEAKSCALINGMPIFOLDERNAME), exist_ok=True)

    # create dirs for sbatch scripts
    os.makedirs(os.path.join(output_folder, STRONGSCALINGMPIFOLDERNAME, "sbatch"), exist_ok=True)
    os.makedirs(os.path.join(output_folder, WEAKSCALINGMPIFOLDERNAME, "sbatch"), exist_ok=True)

    if os.path.isfile(os.path.join(output_folder, "log.txt")):
        os.remove(os.path.join(output_folder, "log.txt"))

    # Run simulation
    if runSim:
        # deleteJson()
        deleteDat()
        for i in range(ITERATIONS):
            start_strong_scaling_benchmark_mpi(i)
            start_weak_scaling_benchmark_mpi(i)

    check_for_completion()
    log("Finished")
    deleteDat()

    plot_strong_scaling_benchmark()
    plot_weak_scaling_benchmark()
