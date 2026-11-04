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
        Older profile = reference, newer profile = NESTML.

    python analyze_profiling_data.py <reference.json> <nestml.json>
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

import matplotlib.pyplot as plt
import numpy as np

# Enable grid lines globally for all plots
plt.rcParams['axes.grid'] = True

# Optional: Set grid aesthetic defaults (style, opacity, line width)
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.alpha'] = 0.7
plt.rcParams['grid.linewidth'] = 0.8




REPORT_DIR = Path(__file__).resolve().parents[2] / "reports"
PROFILE_NAME = "sample_profile.json"
ENERGY_NAME = "energy_report.rpt"
PROFILE_CSV = Path(__file__).resolve().parents[2] / "balanced_networks_profiling.csv"
ENERGY_CSV = Path(__file__).resolve().parents[2] / "balanced_networks_energy.csv"


def find_latest_profiles():
    """Find the two newest sample profile files."""
    profiles = sorted(
        REPORT_DIR.rglob(PROFILE_NAME),
        key=lambda path: path.stat().st_mtime
    )

    if len(profiles) < 2:
        raise FileNotFoundError(
            f"At least two {PROFILE_NAME} files are required under {REPORT_DIR}"
        )

    return profiles[-2], profiles[-1]


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


def summarize_activity(cores):
    """Calculate summary statistics for profiled cores."""
    values = np.array([core["mean_percent_active"] for core in cores], dtype=float)

    return {
        "core_count": len(values),
        "mean": np.mean(values),
        "median": np.median(values),
        "max": np.max(values)
    }


def analyze_profiles(reference_path, nestml_path):
    """Analyze and compare reference and NESTML profiles."""
    reference = load_json(reference_path)
    nestml = load_json(nestml_path)

    reference_cores = extract_core_activity(reference)
    nestml_cores = extract_core_activity(nestml)

    reference_summary = summarize_activity(reference_cores)
    nestml_summary = summarize_activity(nestml_cores)

    mean_difference = nestml_summary["mean"] - reference_summary["mean"]
    median_difference = nestml_summary["median"] - reference_summary["median"]
    max_difference = nestml_summary["max"] - reference_summary["max"]

    mean_relative_difference = mean_difference / reference_summary["mean"] * 100 if reference_summary["mean"] != 0 else np.nan

    print("\n===================================")
    print("SPINNAKER PROFILE COMPARISON")
    print("===================================")

    print(f"Reference: {reference_path}")
    print(f"NESTML:    {nestml_path}")

    print("\n-----------------------------------")
    print("Core activity")
    print("-----------------------------------")

    print(f"Reference profiled cores: {reference_summary['core_count']}")
    print(f"NESTML profiled cores:    {nestml_summary['core_count']}")

    print(f"\nReference mean activity: {reference_summary['mean']:.4f}%")
    print(f"NESTML mean activity:    {nestml_summary['mean']:.4f}%")
    print(f"Mean difference:          {mean_difference:.4f} percentage points")
    print(f"Mean relative difference: {mean_relative_difference:.2f}%")

    print(f"\nReference median activity: {reference_summary['median']:.4f}%")
    print(f"NESTML median activity:    {nestml_summary['median']:.4f}%")
    print(f"Median difference:          {median_difference:.4f} percentage points")

    print(f"\nReference maximum activity: {reference_summary['max']:.4f}%")
    print(f"NESTML maximum activity:    {nestml_summary['max']:.4f}%")
    print(f"Maximum difference:          {max_difference:.4f} percentage points")

    plot_core_activity(reference_cores, reference_path, "Reference")
    plot_core_activity(nestml_cores, nestml_path, "NESTML")
    plot_comparison(reference_summary, nestml_summary, nestml_path)
    plot_distribution(reference_cores, nestml_cores, nestml_path)
    save_comparison_to_csv(reference_path, nestml_path, reference_summary, nestml_summary, mean_difference, mean_relative_difference)




def plot_core_activity(cores, profile_path, implementation):
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

    output_path = Path(profile_path).parent / f"sample_profile_activity_{implementation.lower()}.png"
    plt.savefig(output_path, dpi=300)
    plt.close()

    print(f"{implementation} core activity plot saved to: {output_path}")

def plot_comparison(reference, nestml, profile_path):
    """Plot summary activity metrics for reference and NESTML."""
    labels = ["Mean", "Median", "Maximum"]
    reference_values = [reference["mean"], reference["median"], reference["max"]]
    nestml_values = [nestml["mean"], nestml["median"], nestml["max"]]

    x = np.arange(len(labels))
    width = 0.35

    plt.figure(figsize=(9, 6))
    plt.bar(x - width / 2, reference_values, width, label="Reference")
    plt.bar(x + width / 2, nestml_values, width, label="NESTML")
    plt.xlabel("Core activity metric")
    plt.ylabel("Active time [%]")
    plt.title("Reference vs NESTML Core Activity")
    plt.xticks(x, labels)
    plt.legend()
    plt.tight_layout()

    output_path = Path(profile_path).parent / "sample_profile_comparison.png"
    plt.savefig(output_path, dpi=300)
    plt.close()

    print(f"Comparison plot saved to: {output_path}")


def plot_distribution(reference_cores, nestml_cores, profile_path):
    """Plot the distribution of mean core activity."""
    reference_values = [core["mean_percent_active"] for core in reference_cores]
    nestml_values = [core["mean_percent_active"] for core in nestml_cores]

    plt.figure(figsize=(8, 6))
    plt.boxplot([reference_values, nestml_values], tick_labels=["Reference", "NESTML"])
    plt.ylabel("Mean active time [%]")
    plt.title("Distribution of Core Activity")
    plt.tight_layout()

    output_path = Path(profile_path).parent / "sample_profile_activity_distribution.png"
    plt.savefig(output_path, dpi=300)
    plt.close()

    print(f"Distribution plot saved to: {output_path}")


def save_comparison_to_csv(reference_path, nestml_path, reference, nestml, mean_difference, mean_relative_difference):
    """Save the reference vs NESTML profiling comparison."""
    csv_path = Path(__file__).resolve().parents[2] / "balanced_networks_profiling.csv"

    row = {
        "reference_profile": str(reference_path),
        "nestml_profile": str(nestml_path),
        "reference_core_count": reference["core_count"],
        "nestml_core_count": nestml["core_count"],
        "reference_mean_activity_percent": reference["mean"],
        "nestml_mean_activity_percent": nestml["mean"],
        "mean_difference_percentage_points": mean_difference,
        "mean_relative_difference_percent": mean_relative_difference,
        "reference_median_activity_percent": reference["median"],
        "nestml_median_activity_percent": nestml["median"],
        "reference_max_activity_percent": reference["max"],
        "nestml_max_activity_percent": nestml["max"]
    }

    file_exists = csv_path.exists()

    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())

        if not file_exists:
            writer.writeheader()

        writer.writerow(row)

    print(f"CSV saved to: {csv_path}")


# Energy analysis
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


def parse_energy_value(value):
    """Convert the numeric part of an energy-report value to float."""
    return float(value.split()[0])


def load_energy_report(profile_path):
    """Parse the energy report belonging to a profile."""
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
                    energy[key] = parse_energy_value(value)
                    break

    return energy

def analyze_energy(reference_path, nestml_path):
    """Analyze and compare reference and NESTML energy reports."""
    reference = load_energy_report(reference_path)
    nestml = load_energy_report(nestml_path)

    print_energy_comparison(reference, nestml)

    save_energy_comparison_to_csv(
        reference_path,
        nestml_path,
        reference,
        nestml
    )


def print_energy_comparison(reference, nestml):
    """Print Reference vs NESTML energy results."""
    execution_difference = (
        nestml["execution_energy_J"] -
        reference["execution_energy_J"]
    )

    execution_relative_difference = (
        abs(execution_difference) /
        reference["execution_energy_J"] * 100
        if reference["execution_energy_J"] != 0 else np.nan
    )

    print("\n===================================")
    print("ENERGY COMPARISON")
    print("===================================")

    print(f"Reference cores used: {reference['cores_used']}")
    print(f"NESTML cores used:    {nestml['cores_used']}")

    print(f"Reference active cores: {reference['active_cores']}")
    print(f"NESTML active cores:    {nestml['active_cores']}")

    print(f"\nReference execution time: {reference['execution_time_s']:.6f} s")
    print(f"NESTML execution time:    {nestml['execution_time_s']:.6f} s")

    print(f"\nReference execution energy: {reference['execution_energy_J']:.6f} J")
    print(f"NESTML execution energy:    {nestml['execution_energy_J']:.6f} J")
    print(f"Execution energy difference: {execution_difference:.6f} J")
    print(f"Execution energy relative difference: {execution_relative_difference:.2f}%")

    print(
        f"\nReference active-only execution energy: "
        f"{reference['execution_energy_active_only_J']:.6f} J"
    )

    print(
        f"NESTML active-only execution energy:    "
        f"{nestml['execution_energy_active_only_J']:.6f} J"
    )

    print(f"\nReference total energy: {reference['total_energy_J']:.6f} J")
    print(f"NESTML total energy:    {nestml['total_energy_J']:.6f} J")


def save_energy_comparison_to_csv(
    reference_path,
    nestml_path,
    reference,
    nestml
):
    """Save the Reference vs NESTML energy comparison."""
    execution_difference = (
        nestml["execution_energy_J"] -
        reference["execution_energy_J"]
    )

    execution_relative_difference = (
        abs(execution_difference) /
        reference["execution_energy_J"] * 100
        if reference["execution_energy_J"] != 0 else np.nan
    )

    row = {
        "reference_profile": str(reference_path),
        "nestml_profile": str(nestml_path),
        "reference_cores_used": reference["cores_used"],
        "nestml_cores_used": nestml["cores_used"],
        "reference_active_cores": reference["active_cores"],
        "nestml_active_cores": nestml["active_cores"],
        "reference_execution_time_s": reference["execution_time_s"],
        "nestml_execution_time_s": nestml["execution_time_s"],
        "reference_execution_energy_J": reference["execution_energy_J"],
        "nestml_execution_energy_J": nestml["execution_energy_J"],
        "execution_energy_difference_J": execution_difference,
        "execution_energy_relative_difference_percent": execution_relative_difference,
        "reference_active_only_energy_J": reference["execution_energy_active_only_J"],
        "nestml_active_only_energy_J": nestml["execution_energy_active_only_J"],
        "reference_total_energy_J": reference["total_energy_J"],
        "nestml_total_energy_J": nestml["total_energy_J"]
    }

    file_exists = ENERGY_CSV.exists()

    with open(ENERGY_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())

        if not file_exists:
            writer.writeheader()

        writer.writerow(row)

    print(f"Energy CSV saved to: {ENERGY_CSV}")


def analyze_latest_profiles():
    """Analyze the two latest profiles: reference first, NESTML second."""
    reference_path, nestml_path = find_latest_profiles()

    analyze_profiles(reference_path, nestml_path)
    analyze_energy(reference_path, nestml_path)


def main():
    if len(sys.argv) == 1:
        analyze_latest_profiles()
    elif len(sys.argv) == 3:
        analyze_profiles(sys.argv[1], sys.argv[2])
        analyze_energy(sys.argv[1], sys.argv[2])
    else:
        raise SystemExit(
            "Usage:\n"
            "  python analyze_profiling_data.py\n"
            "  python analyze_profiling_data.py <reference.json> <nestml.json>"
        )


if __name__ == "__main__":
    main()
