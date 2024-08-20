# -*- coding: utf-8 -*-
#
# benchmark.py
#
# This file is part of NEST.
#
# Copyright (C) 2004 The NEST Initiative
#
# NEST is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# NEST is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NEST.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import datetime
import jinja2
import json
import math
import os
import re
import subprocess
import time

import matplotlib
import matplotlib.ticker
import matplotlib.pyplot as plt
import numpy as np

from plotting_options import *


# the benchmark script to run
current_dir = os.path.dirname(os.path.abspath(__file__))
PATHTOFILE = os.path.join(current_dir, "brunel_alpha_nest.py")

# RNG options
seed: int = int(datetime.datetime.now().timestamp() * 1000) % 2**31
rng = np.random.default_rng(seed)
max_int32 = np.iinfo(np.int32).max

# parse command line arguments
parser = argparse.ArgumentParser(description='Run a Benchmark with NEST')
parser.add_argument('--noRunSim', action="store_false", help='Skip running simulations, only do plotting')
parser.add_argument('--enable_profiling', action="store_true", help="Run the benchmark with profiling enabled with AMDuProf")
parser.add_argument("--short_sim", action="store_true", help="Run benchmark with profiling on 2 nodes with 2 iterations")
parser.add_argument("--enable_mpi", action="store_true", default=False, help="Run benchmark with MPI (default: thread-based benchmarking)")

args = parser.parse_args()
runSim = args.noRunSim
enable_profile = args.enable_profiling
short_sim = args.short_sim

# for aeif_psc_alpha neurons
BASELINENEURON = "aeif_psc_alpha"

NEURONMODELS = [
    "aeif_psc_alpha_neuron_Nestml_Plastic__with_stdp_synapse_Nestml_Plastic",
    "aeif_psc_alpha_neuron_Nestml",
    BASELINENEURON,
    # "aeif_psc_alpha_neuron_Nestml_Plastic_noco__with_stdp_synapse_Nestml_Plastic_noco"
]

legend = {
    "aeif_psc_alpha_neuron_Nestml_Plastic__with_stdp_synapse_Nestml_Plastic": "NESTML",
    "aeif_psc_alpha_neuron_Nestml": "NESTML/NEST",
    BASELINENEURON: "NEST",
    # "aeif_psc_alpha_neuron_Nestml_Plastic_noco__with_stdp_synapse_Nestml_Plastic_noco": "NESTML neur, NESTML syn NOCO",
}

colors = {
    BASELINENEURON: 0,
    "aeif_psc_alpha_neuron_Nestml_Plastic__with_stdp_synapse_Nestml_Plastic": 1,
    "aeif_psc_alpha_neuron_Nestml": 2,
    # "aeif_psc_alpha_neuron_Nestml_Plastic_noco__with_stdp_synapse_Nestml_Plastic_noco": 3
}

# MPI scaling
DEBUG = True
NUMTHREADS = 128  # Total number of threads per node
NETWORKSCALES = np.logspace(3, math.log10(20000), 5, dtype=int)  # XXXXXXXXXXXX: was 10 points, max size 30000

# MPI Strong scaling
if enable_profile:
    MPI_SCALES = [2]
    ITERATIONS = 1
else:
    if short_sim:
        MPI_SCALES = [2]
        ITERATIONS = 2
    else:
        MPI_SCALES = np.logspace(1, math.log2(64), num=6, base=2, dtype=int)
        ITERATIONS = 3

MPI_STRONG_SCALE_NEURONS = NETWORKSCALES[-1]
STRONGSCALINGFOLDERNAME = "timings_strong_scaling_mpi"

# MPI Weak scaling
MPI_WEAK_SCALE_NEURONS = 20000
WEAKSCALINGFOLDERNAME = "timings_weak_scaling_mpi"

# thread-based benchmarks
NETWORK_BASE_SCALE = 1000
N_THREADS = np.logspace(0, math.log2(64), num=7, base=2, dtype=int)
PATHTOSTARTFILE = os.path.join(current_dir, "start.sh")

# output folder
if args.enable_mpi:
    output_folder = os.path.join(os.path.dirname(__file__), os.pardir, 'Output_MPI')
else:
    output_folder = os.path.join(os.path.dirname(__file__), os.pardir, 'Output_threads')


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
    namespace["enable_profile"] = enable_profile
    file = template.render(namespace)
    log("Rendering template: " + template.filename)

    log("Rendered template file name: " + filename)
    with open(filename, "w+") as f:
        f.write(str(file))
        f.close()

def start_strong_scaling_benchmark_threads(iteration):
    log(f"Strong Scaling Benchmark {iteration}")

    dirname = os.path.join(output_folder, STRONGSCALINGFOLDERNAME)
    combinations = [{"n_threads": n_threads,
                     "neuronmodel": neuronmodel,
                     "name": f"{neuronmodel},{n_threads}"
                     } for neuronmodel in NEURONMODELS for n_threads in N_THREADS]

    for combination in combinations:
        rng_seed = rng.integers(0, max_int32)

        command = ['bash', '-c', f'source {PATHTOSTARTFILE} && python3 {PATHTOFILE} --simulated_neuron {combination["neuronmodel"]} --network_scale {MPI_STRONG_SCALE_NEURONS} --threads {combination["n_threads"]} --iteration {iteration} --rng_seed {rng_seed} --benchmarkPath {dirname}']

        log(combination["name"])

        combined = combination["name"]

        result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.stdout:
            fname = "stdout_strong_run_" + combined + "_[iter=" + str(iteration) + "].txt"
            with open(fname, "w") as f:
                f.write(result.stdout)

        if result.stderr:
            fname = "stderr_strong_run_" + combined + "_[iter=" + str(iteration) + "].txt"
            with open(fname, "w") as f:
                f.write(result.stderr)

        if result.returncode != 0:
            log(f"\033[91m{combination['name']} failed\033[0m")
            log(f"\033[91m{result.stderr} failed\033[0m")

def start_strong_scaling_benchmark_mpi(iteration):
    dirname = os.path.join(output_folder, STRONGSCALINGFOLDERNAME)
    combinations = [
        {
            "nodes": compute_nodes,
            "simulated_neuron": neuronmodel,
            "network_scale": MPI_STRONG_SCALE_NEURONS,
            "threads": NUMTHREADS,
            "iteration": iteration,
            "output_file": f"run_simulation_{neuronmodel}_{compute_nodes}_{iteration}_%j.out",
            "error_file": f"run_simulation_{neuronmodel}_{compute_nodes}_{iteration}_%j.err",
            "benchmarkPath": dirname,
            "rng_seed": rng.integers(0, max_int32),
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

def start_weak_scaling_benchmark_threads(iteration):
    dirname = os.path.join(output_folder, WEAKSCALINGFOLDERNAME)
    combinations = [
        {
            "n_threads": n_threads,
            "neuronmodel": f"{neuronmodel}",
            "networksize": NETWORK_BASE_SCALE * n_threads} for neuronmodel in NEURONMODELS for n_threads in N_THREADS]
    log(f"\033[93mWeak Scaling Benchmark {iteration}\033[0m")

    for combination in combinations:
        rng_seed = rng.integers(0, max_int32)

        command = ['bash', '-c', f'source {PATHTOSTARTFILE} && python3 {PATHTOFILE} --simulated_neuron {combination["neuronmodel"]} --network_scale {NETWORK_BASE_SCALE * combination["n_threads"]} --threads {combination["n_threads"]} --rng_seed {rng_seed} --iteration {iteration} --benchmarkPath {dirname}']

        combined = combination["neuronmodel"]+","+str(combination["networksize"])
        log(f"\033[93m{combined}\033[0m" if DEBUG else combined)
        result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.stdout:
            fname = "stdout_weak_run_" + combined + "_[iter=" + str(iteration) + "].txt"
            with open(fname, "w") as f:
                f.write(result.stdout)

        if result.stderr:
            fname = "stderr_weak_run_" + combined + "_[iter=" + str(iteration) + "].txt"
            with open(fname, "w") as f:
                f.write(result.stderr)

        if result.returncode != 0:
            log(f"\033[91m{combination['neuronmodel']} failed\033[0m")
            log(f"\033[91m{result.stderr} failed\033[0m")

def start_weak_scaling_benchmark_mpi(iteration):
    dirname = os.path.join(output_folder, WEAKSCALINGFOLDERNAME)
    combinations = [
        {
            "nodes": compute_nodes,
            "simulated_neuron": neuronmodel,
            "network_scale": MPI_WEAK_SCALE_NEURONS * compute_nodes,
            "threads": NUMTHREADS,
            "iteration": iteration,
            "output_file": f"run_simulation_{neuronmodel}_{compute_nodes}_{MPI_WEAK_SCALE_NEURONS * compute_nodes}_{iteration}_%j.out",
            "error_file": f"run_simulation_{neuronmodel}_{compute_nodes}_{MPI_WEAK_SCALE_NEURONS * compute_nodes}_{iteration}_%j.err",
            "benchmarkPath": dirname,
            "rng_seed": rng.integers(0, max_int32),
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

    # Compute max simulation time between MPI ranks and add it to the data
    for neuron, values in sim_data.items():
        neurons.append(neuron)
        x = sorted(values.keys(), key=lambda k: int(k))
        for nodes in x:
            for it_data in values[nodes].values():
                max_time_simulate = np.max([rank_data["time_simulate"] for rank_data in it_data.values()])
                biological_time = it_data[0]["biological_time"]

                rss_sum = np.sum([rank_data["memory_benchmark"]["rss"] for rank_data in it_data.values()])
                vmsize_sum = np.sum([rank_data["memory_benchmark"]["vmsize"] for rank_data in it_data.values()])
                vmpeak_sum = np.sum([rank_data["memory_benchmark"]["vmpeak"] for rank_data in it_data.values()])

                it_data["memory_benchmark"] = {}
                it_data["max_time_simulate"] = max_time_simulate
                it_data["biological_time"] = biological_time
                it_data["memory_benchmark"]["rss"] = rss_sum
                it_data["memory_benchmark"]["vmsize"] = vmsize_sum
                it_data["memory_benchmark"]["vmpeak"] = vmpeak_sum

    for neuron, values in sim_data.items():
        if not neuron in NEURONMODELS:
            continue

        x = sorted(values.keys(), key=lambda k: int(k))
        y = np.array([np.mean(
            [iteration_data['max_time_simulate'] / (iteration_data["biological_time"] / 1000) for iteration_data in
             values[nodes].values()]) for nodes in x])
        y_std = np.array([np.std(
            [iteration_data['max_time_simulate'] / (iteration_data["biological_time"] / 1000) for iteration_data in
             values[nodes].values()]) for nodes in x])

        x = np.array([int(val) for val in x], dtype=int)
        plt.errorbar(x, y, yerr=y_std, label=legend[neuron], color=palette(colors[neuron]), linestyle='-', marker='o',
                     markersize=4, ecolor='gray', capsize=2)

    if args.enable_mpi:
        plt.xlabel('Number of nodes')
    else:
        plt.xlabel('Number of threads')
    plt.ylabel('Wall clock time (s)')
    plt.xscale('log')
    # plt.yscale('log')
    plt.xticks(MPI_SCALES, MPI_SCALES)
    plt.gca().xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, file_prefix + '_abs.png'))
    plt.savefig(os.path.join(output_folder, file_prefix + '_abs.pdf'))

    plt.figure()
    neurons = []
    referenceValues = sim_data[BASELINENEURON]
    for neuron, values in sim_data.items():
        if not neuron in NEURONMODELS:
            continue

        neurons.append(neuron)
        x = sorted(values.keys(), key=lambda k: int(k))
        # Real Time Factor
        reference_y = np.array([np.mean(
            [iteration_data['max_time_simulate'] / (iteration_data["biological_time"] / 1000) for iteration_data in
             referenceValues[nodes].values()]) for nodes in x])
        y = np.array([np.mean(
            [iteration_data['max_time_simulate'] / (iteration_data["biological_time"] / 1000) for iteration_data in
             values[nodes].values()]) for nodes in x])
        y_factor = y / reference_y  # Calculate the factor of y in comparison to the reference value

        y_std = np.array([np.std(
            [iteration_data['max_time_simulate'] / (iteration_data["biological_time"] / 1000) for iteration_data in
             values[nodes].values()]) for nodes in x])
        y_factor_std = y_std / reference_y  # Calculate the standard deviation of the factor

        x = np.array([int(val) for val in x], dtype=int)
        plt.errorbar(x, y_factor, yerr=y_factor_std, label=legend[neuron], color=palette(colors[neuron]), linestyle='-',
                     marker='o', markersize=4, ecolor='gray', capsize=2)

    if args.enable_mpi:
        plt.xlabel('Number of nodes')
    else:
        plt.xlabel('Number of threads')
    plt.ylabel('Wall clock time (ratio)')

    plt.xscale('log')
    # plt.yscale('log')
    plt.xticks(MPI_SCALES, MPI_SCALES)
    plt.gca().xaxis.set_minor_locator(matplotlib.ticker.NullLocator())

    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, file_prefix + '_rel.png'))
    plt.savefig(os.path.join(output_folder, file_prefix + '_rel.pdf'))


def plot_memory_scaling_benchmark(sim_data: dict, file_prefix: str):

    # Memory benchmark
    plt.figure()
    plot_lines = []
    linestyles = {
        "rss": "--",
        "vmsize": "-.",
        "vmpeak": ":"
    }
    for neuron, values in sim_data.items():
        if not neuron in NEURONMODELS:
            continue

        x = sorted(values.keys(), key=lambda k: int(k))
        rss = np.array([np.mean(
            [(iteration_data["memory_benchmark"]["rss"] / 1024 / 1024)  for iteration_data in
             values[nodes].values()]) for nodes in x])
        rss_std = np.array([np.std(
            [(iteration_data["memory_benchmark"]["rss"] / 1024 / 1024) for iteration_data in
             values[nodes].values()]) for nodes in x])

        vmsize = np.array([np.mean(
            [(iteration_data["memory_benchmark"]["vmsize"] / 1024 / 1024) for iteration_data in
             values[nodes].values()]) for nodes in x])
        vmsize_std = np.array([np.std(
            [(iteration_data["memory_benchmark"]["vmsize"] / 1024 / 1024) for iteration_data in
             values[nodes].values()]) for nodes in x])

        vmpeak = np.array([np.mean(
            [(iteration_data["memory_benchmark"]["vmpeak"] / 1024 / 1024) for iteration_data in
             values[nodes].values()]) for nodes in x])
        vmpeak_std = np.array([np.std(
            [(iteration_data["memory_benchmark"]["vmpeak"] / 1024 / 1024) for iteration_data in
             values[nodes].values()]) for nodes in x])

        print(rss, vmsize, vmpeak)

        x = np.array([int(val) for val in x], dtype=int)
        line1 = plt.errorbar(x, rss, yerr=rss_std, color=palette(colors[neuron]), linestyle=linestyles["rss"], label="rss",
                     ecolor='gray', capsize=2)
        line2 = plt.errorbar(x, vmsize, yerr=vmsize_std, color=palette(colors[neuron]), linestyle=linestyles["vmsize"], label="vmsize",
                     ecolor='gray', capsize=2)
        line3 = plt.errorbar(x, vmpeak, yerr=vmpeak_std, color=palette(colors[neuron]), linestyle=linestyles["vmpeak"], label="vmpeak",
                     ecolor='gray', capsize=2)

        plot_lines.append([line1, line2, line3])

    # Create a legend for the linestyles
    linestyle_legend = plt.legend(plot_lines[0], list(linestyles.keys()), loc='upper left')
    plt.gca().add_artist(linestyle_legend)

    # Create a legend for the neurons
    neuron_handles = [plt.Line2D([0], [0], color=palette(colors[key]), lw=2) for key in legend.keys()]
    plt.legend(neuron_handles, list(legend.values()), loc='upper right')
    if args.enable_mpi:
        plt.xlabel('Number of nodes')
    else:
        plt.xlabel('Number of threads')
    plt.ylabel('Memory (GB)')
    plt.xscale('log')
    plt.yscale('log')
    plt.tight_layout()
    plt.xticks(MPI_SCALES, MPI_SCALES)
    plt.gca().xaxis.set_minor_locator(matplotlib.ticker.NullLocator())

    plt.savefig(os.path.join(output_folder, file_prefix + '_memory.png'))
    plt.savefig(os.path.join(output_folder, file_prefix + '_memory.pdf'))



def process_data(dir_name: str, mode="MPI"):
    scaling_data = {}
    abs_dir_name = os.path.join(output_folder, dir_name)
    print("Reading data from directory: " + abs_dir_name)
    for filename in os.listdir(abs_dir_name):
        if filename.endswith(".json"):
            simulated_neuron = extract_value_from_filename(filename, "simulated_neuron")
            if args.enable_mpi:
                nodes = int(extract_value_from_filename(filename, "nodes"))
            else:
                nodes = int(extract_value_from_filename(filename, "threads"))
            iteration = int(extract_value_from_filename(filename, "iteration"))
            rank = int(extract_value_from_filename(filename, "rank"))
            with open(os.path.join(output_folder, dir_name, filename), "r") as f:
                data = f.read()
                json_data = clean_json_content(data)
                scaling_data.setdefault(simulated_neuron, {}).setdefault(nodes, {}).setdefault(iteration, {}).setdefault(rank, json_data)
                f.close()

    return scaling_data


def plot_strong_scaling_benchmark():
    strong_scaling_data = process_data(STRONGSCALINGFOLDERNAME)
    plot_scaling_data(strong_scaling_data, "strong_scaling")
    plot_memory_scaling_benchmark(strong_scaling_data, "strong_scaling")


def plot_weak_scaling_benchmark():
    weak_scaling_data = process_data(WEAKSCALINGFOLDERNAME)
    plot_scaling_data(weak_scaling_data, "weak_scaling")
    plot_memory_scaling_benchmark(weak_scaling_data, "weak_scaling")


def deleteDat():
    for filename in os.listdir("./"):
        if filename.endswith(".dat"):
            os.remove(f"./{filename}")


def deleteJson():
    for filename in os.listdir(os.path.join(output_folder, WEAKSCALINGFOLDERNAME)):
        if filename.endswith(".json"):
            os.remove(os.path.join(output_folder, WEAKSCALINGFOLDERNAME, filename))
    for filename in os.listdir(os.path.join(output_folder, STRONGSCALINGFOLDERNAME)):
        if filename.endswith(".json"):
            os.remove(os.path.join(output_folder, STRONGSCALINGFOLDERNAME, filename))


def setup_template_env():
    template_file = "sbatch_run.sh.jinja2"
    template_dir = os.path.realpath(os.path.join(os.path.dirname(__file__)))
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
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
        time.sleep(10.)


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


def read_isis_from_files(neuron_models):
    data = {}
    for neuron_model in neuron_models:
        data[neuron_model] = {"isis": []}  # list of lists: one element for each iteration, containing the list of ISIs for that iteration (across all ranks)

        if args.enable_mpi:
            threads = 128
            nodes = 2
        else:
            threads = 1
            nodes = 1

        # loop across iterations
        iteration = 0
        while True:

            # loop across ranks
            rank = 0
            while True:
                filename = "timings_strong_scaling_mpi/isi_distribution_[simulated_neuron=" + neuron_model + "]_[network_scale=" + str(MPI_WEAK_SCALE_NEURONS) + "]_[iteration=" + str(iteration) + "]_[nodes=" + str(nodes) + "]_[threads=" + str(threads) + "]_[rank=" + str(rank) + "]_isi_list.txt" # XXX update MPI_WEAK_SCALE_NEURONS
                print("Reading ISIs from: " + os.path.join(output_folder, filename))
                if not os.path.exists(os.path.join(output_folder, filename)):
                    break

                with open(os.path.join(output_folder, filename), 'r') as file:
                    isis = [float(line.strip()) for line in file]
                    if iteration >= len(data[neuron_model]["isis"]):
                        data[neuron_model]["isis"].append([])

                    data[neuron_model]["isis"][iteration].extend(isis)

                rank += 1

            iteration += 1

            if iteration > 99:
                break

    return data


def analyze_isi_data(data, bin_size):
    # Determine the range for the bins
    min_val = np.inf
    max_val = -np.inf
    for neuron_model in data.keys():
        isi_list = data[neuron_model]["isis"]
        if len(isi_list) == 0:
            raise Exception("ISI list is empty")
        for isi in isi_list:
            min_val = min(min_val, min(isi))
            max_val = max(max_val, max(isi))

    bins = np.arange(min_val, max_val + bin_size, bin_size)

    for neuron_model in data.keys():
        isi_list = data[neuron_model]["isis"]
        data[neuron_model]["counts"] = len(isi_list) * [None]
        for i, isi in enumerate(isi_list):
            counts, bin_edges = np.histogram(isi, bins=bins)
            n_datapoints = len(isi)
            data[neuron_model]["counts"][i] = counts / n_datapoints

        data[neuron_model]["counts_mean"] = np.mean(np.array(data[neuron_model]["counts"]), axis=0)
        data[neuron_model]["counts_std"] = np.std(np.array(data[neuron_model]["counts"]), axis=0)

    data["bin_edges"] = bin_edges
    data["bin_centers"] = (bin_edges[:-1] + bin_edges[1:]) / 2
    data["min_val"] = min_val
    data["max_val"] = max_val


def plot_isi_distributions(neuron_models, data):
    plt.figure(figsize=(6, 4))

    for neuron_model in neuron_models:
        plt.bar(data["bin_centers"], 100 * 2 * data[neuron_model]["counts_std"], data["bin_centers"][1] - data["bin_centers"][0], bottom=100 * (data[neuron_model]["counts_mean"] - data[neuron_model]["counts_std"]), alpha=.5)
        plt.step(data["bin_edges"][:-1], 100 * data[neuron_model]["counts_mean"], label=legend[neuron_model], linewidth=2, alpha=.5, where="post")
        #plt.errorbar(data["bin_centers"], data[neuron_model]["counts_mean"], yerr=data[neuron_model]["counts_std"], fmt='o', color='black', capsize=5)

    plt.xlabel('ISI [ms]')
    plt.ylabel('Frequency of occurrence [%]')
    plt.grid(True)
    plt.tight_layout()
    plt.legend()

    plt.savefig(os.path.join(output_folder, 'isi_distributions.png'))
    plt.savefig(os.path.join(output_folder, 'isi_distributions.pdf'))


if __name__ == "__main__":
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(os.path.join(output_folder, STRONGSCALINGFOLDERNAME), exist_ok=True)
    os.makedirs(os.path.join(output_folder, WEAKSCALINGFOLDERNAME), exist_ok=True)

    if args.enable_mpi:
        # create dirs for sbatch scripts
        os.makedirs(os.path.join(output_folder, STRONGSCALINGFOLDERNAME, "sbatch"), exist_ok=True)
        os.makedirs(os.path.join(output_folder, WEAKSCALINGFOLDERNAME, "sbatch"), exist_ok=True)

    if os.path.isfile(os.path.join(output_folder, "log.txt")):
        os.remove(os.path.join(output_folder, "log.txt"))

    # Run simulation
    if runSim:
        deleteJson()
        deleteDat()
        for i in range(ITERATIONS):
            if args.enable_mpi:
                start_strong_scaling_benchmark_mpi(i)
                start_weak_scaling_benchmark_mpi(i)
            else:
                start_strong_scaling_benchmark_threads(i)
                start_weak_scaling_benchmark_threads(i)

    if args.enable_mpi:
        check_for_completion()

    log("Finished")
    deleteDat()

    plot_strong_scaling_benchmark()
    plot_weak_scaling_benchmark()

    # plot ISI distributions
    bin_size = 5  # Adjust the bin size as needed
    data = read_isis_from_files(NEURONMODELS)
    analyze_isi_data(data, bin_size)
    plot_isi_distributions(NEURONMODELS, data)
