# -*- coding: utf-8 -*-
#
# analyze_profiling_data.py
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

"""
Analyze SpiNNaker sample profiling data.

Usage:
    python analyze_profiling_data.py
        Compare the two latest profiles.
        Older profile = built-in, newer profile = NESTML.

    python analyze_profiling_data.py <builtin.json> <nestml.json>
        Compare two explicitly selected profiles.



To use this script, make sure that 

.. code::

   [Reports]
   write_energy_report = True
   write_sample_profile_report = True

in ``.spynnaker.cfg``.
"""

import csv
import json
import sys
from pathlib import Path
import shutil

import matplotlib.pyplot as plt
import numpy as np

# Enable grid lines globally for all plots
plt.rcParams['axes.grid'] = True

# Optional: Set grid aesthetic defaults (style, opacity, line width)
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.alpha'] = 0.7
plt.rcParams['grid.linewidth'] = 0.8



REPORT_DIR = Path(__file__).resolve().parents[2] / "reports"    
ARCHIVE_DIR = Path(__file__).resolve().parents[2] / "reports_archive"
PROFILE_NAME = "sample_profile.json"
ENERGY_NAME = "energy_report.rpt"
BENCHMARK_CSV = Path(__file__).resolve().parents[2] / "benchmark_balanced_networks_results.csv"
PROFILE_CSV = Path(__file__).resolve().parents[2] / "benchmark_balanced_networks_profiling.csv"
ENERGY_CSV = Path(__file__).resolve().parents[2] / "benchmark_balanced_networks_energy.csv"


ENERGY_FIELDS = {
    "Simulation execution time": "execution_time_s",
    "Simulation execution energy": "execution_energy_J",
    "Simulation execution energy (active chips and cores only)": "execution_energy_active_only_J",
    "Simulation execution energy (ignoring frame power)": "execution_energy_ignoring_frame_J",
    "Mapping time": "mapping_time_s",
    "Mapping energy": "mapping_energy_J",
    "Data Spec time": "data_spec_time_s",
    "Data Spec energy": "data_spec_energy_J",
    "Saving time": "saving_time_s",
    "Saving energy": "saving_energy_J",
    "Other time": "other_time_s",
    "Other energy": "other_energy_J",
    "Total energy": "total_energy_J"
}

def find_profile_to_run():

    profiles = list(REPORT_DIR.rglob("*/run_*/sample_profile.json" ))

    if not profiles:
        raise FileNotFoundError(
            f"No sample_profile.json files found in {REPORT_DIR}"
        )
    
    return max(profiles, key=lambda p: p.stat().st_mtime)


def load_json(path):
    """Load a sample profile JSON file."""
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Profile file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_core_activity(data):
    """Extract core activity values from Andrew's JSON format."""
    cores = []

    for chip_name, chip_data in data.items():
        if not chip_name.startswith("chip_"):
            continue

        for core_name, core_data in chip_data.items():
            if not core_name.startswith("core_"):
                continue

            if core_data.get("mean_percent_active") is None:
                continue

            cores.append({
                "chip": chip_name,
                "core": core_name,
                "vertex": core_data.get("vertex"),
                "vertex_slice": core_data.get("vertex_slice"),
                "vertex_label": core_data.get("vertex_label"),
                "min_percent_active": core_data.get("min_percent_active"),
                "max_percent_active": core_data.get("max_percent_active"),
                "mean_percent_active": core_data.get("mean_percent_active")
            })

    return cores

def calculate_sum_core_activity(cores):
    """
    Calculate the sum of core active fraction across cores.
    """
    sum_core_activity = 0.0

    for core in cores:
        if core["mean_percent_active"] is None:
            raise ValueError(f"Core {core['chip']}:{core['core']} has no mean_percent_active value.")
        else:
            sum_core_activity += core["mean_percent_active"]

    return sum_core_activity


def calculate_mean_core_activity(cores):
    """
    Calculate the mean of active fraction across cores.
    """
    if not cores:
        return np.nan

    values = [core["mean_percent_active"] for core in cores if core["mean_percent_active"] is not None]

    if not values:
        return np.nan

    return float(np.mean(values))


def load_energy_report(profile_path):
    """Load the energy report corresponding to a sample profile."""
    energy_path = Path(profile_path).parent / ENERGY_NAME

    if not energy_path.exists():
        raise FileNotFoundError(f"Energy report not found: {energy_path}")

    energy = {}

    with open(energy_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if line.startswith("Simulation cores used:"):
                parts = line.split()
                energy["cores_used"] = int(parts[3])
                energy["active_cores"] = int(parts[6])
                continue

            for report_field, key in ENERGY_FIELDS.items():
                if line.startswith(f"{report_field}:"):
                    value = line.split(":", 1)[1].strip()
                    energy[key] = float(value.split()[0])  # Convert to float
                    break

    return energy   


def archive_run(profile_path, result):
    """Archive profiling and energy reports together with run metadata."""

    profile_path = Path(profile_path)
    energy_path = profile_path.parent / ENERGY_NAME

    if not profile_path.exists():
        raise FileNotFoundError(f"Profile file not found: {profile_path}")

    if not energy_path.exists():
        raise FileNotFoundError(f"Energy report not found: {energy_path}")


    run_dir = ARCHIVE_DIR / result["timestamp"]
    run_dir.mkdir(parents=True, exist_ok=True)

    shutil.copy2(profile_path, run_dir / PROFILE_NAME)
    shutil.copy2(energy_path, run_dir / ENERGY_NAME)

    metadata = {
        "timestamp": result["timestamp"],
        "implementation": result["implementation"],
        "use_static_synapses": result["use_static_synapses"],
        "use_exp_luts": result["use_exp_luts"] if "use_exp_luts" in result.keys() else None,
        "N": result["n_neurons"],
        "g": result["g"],
        "rate_ext_input": result["rate_ext_input"],
        "neurons_per_core": result["neurons_per_core"],
        "poisson_generators_per_core": result["poisson_generators_per_core"],
        "t_sim": result["t_sim"],
        "source_report_directory": str(profile_path.parent),
        "files": {
            "profile": PROFILE_NAME,
            "energy": ENERGY_NAME
        }
    }

    with open(run_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)

    print(f"Run archived to: {run_dir}")

    return run_dir


def save_profiling_to_csv(result, core_count, mean_activity, sum_activity):
    row = {
        "timestamp": result["timestamp"],
        "implementation": result["implementation"],
        "seed": result["seed"],
        "use_static_synapses": result["use_static_synapses"],
        "use_exp_luts": result["use_exp_luts"] if "use_exp_luts" in result.keys() else None,
        "N": result["n_neurons"],
        "g": result["g"],
        "rate_ext_input": result["rate_ext_input"],
        "neurons_per_core": result["neurons_per_core"],
        "poisson_generators_per_core": result["poisson_generators_per_core"],
        "t_sim": result["t_sim"],
        "core_count": core_count,
        "mean_core_activity_percent": mean_activity,
        "sum_core_activity_percent": sum_activity
    }

    file_exists = PROFILE_CSV.exists()

    with open(PROFILE_CSV, "a", newline="", encoding="utf-8") as file:

        writer = csv.DictWriter(file, fieldnames=row.keys())

        if not file_exists:
            writer.writeheader()

        writer.writerow(row)

def save_energy_to_csv(result, energy):

    row = {
        "timestamp": result["timestamp"],
        "implementation": result["implementation"],
        "seed": result["seed"],
        "use_static_synapses": result["use_static_synapses"],
        "use_exp_luts": result["use_exp_luts"] if "use_exp_luts" in result.keys() else None,
        "N": result["n_neurons"],
        "g": result["g"],
        "rate_ext_input": result["rate_ext_input"],
        "neurons_per_core": result["neurons_per_core"],
        "poisson_generators_per_core": result["poisson_generators_per_core"],
        "t_sim": result["t_sim"],
        "cores_used": energy["cores_used"],
        "active_cores": energy["active_cores"],
        "execution_time_s": energy["execution_time_s"],
        "execution_energy_J": energy["execution_energy_J"],
        "execution_energy_active_only_J": energy["execution_energy_active_only_J"],
        "execution_energy_ignoring_frame_J": energy["execution_energy_ignoring_frame_J"],
        "mapping_time_s": energy["mapping_time_s"],
        "mapping_energy_J": energy["mapping_energy_J"],
        "data_spec_time_s": energy["data_spec_time_s"],
        "data_spec_energy_J": energy["data_spec_energy_J"],
        "saving_time_s": energy["saving_time_s"],
        "saving_energy_J": energy["saving_energy_J"],
        "other_time_s": energy["other_time_s"],
        "other_energy_J": energy["other_energy_J"],
        "total_energy_J": energy["total_energy_J"]
    }

    file_exists = ENERGY_CSV.exists()

    with open(ENERGY_CSV, "a", newline="", encoding="utf-8") as file:

        writer = csv.DictWriter(file, fieldnames=row.keys())

        if not file_exists:
            writer.writeheader()

        writer.writerow(row)


def plot_core_activity(cores, run_dir, implementation):
    if not cores:
        print(f"No core profiling data found for {implementation}.")
        return

    labels = [f"{core['chip']}:{core['core']}" for core in cores]
    values = [core["mean_percent_active"] for core in cores]

    plt.figure(figsize=(12, 6))
    plt.bar(labels, values)
    plt.xlabel("Core")
    plt.ylabel("Mean active time [%]")
    plt.title(f"{implementation} SpiNNaker Core Activity")
    plt.xticks(rotation=90)
    plt.tight_layout()

    output_path = (run_dir / f"sample_profile_activity_{implementation.lower()}.png")
    plt.savefig(output_path, dpi=300)
    plt.close()

    print(f"{implementation} core activity plot saved to: {output_path}")


def analyze_run(result):

    profile_path = find_profile_to_run()

    data = load_json(profile_path)
    cores = extract_core_activity(data)

    core_count = len(cores)
    mean_activity = calculate_mean_core_activity(cores)
    sum_activity = calculate_sum_core_activity(cores)

    energy = load_energy_report(profile_path)

    print("\n===================================")
    print("SPINNAKER RUN ANALYSIS")
    print("===================================")

    print(f"Implementation: {result['implementation']}")
    print(f"N: {result['n_neurons']}")
    if "use_exp_luts" in result.keys():
        print(f"Use exp LUTs: {result['use_exp_luts']}")

    print("\nCore activity")
    print(f"Core count: {core_count}")
    print(f"Mean activity: {mean_activity:.4f}%")
    print(f"Sum activity: {sum_activity:.4f}%")

    print("\nEnergy")
    print(f"Cores used: {energy['cores_used']}")
    print(f"Active cores: {energy['active_cores']}")
    print(f"Execution energy: {energy['execution_energy_J']:.6f} J")
    print(f"Total energy: {energy['total_energy_J']:.6f} J")

    run_dir = archive_run(profile_path, result)

    plot_core_activity(cores, run_dir, result["implementation"])

    save_profiling_to_csv(
        result,
        core_count,
        mean_activity,
        sum_activity
    )

    save_energy_to_csv(result, energy)

