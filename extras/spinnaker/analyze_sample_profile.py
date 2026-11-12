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

# shared figure style, kept with the SpiNNaker tests
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tests" / "spinnaker_tests"))
from spinnaker_test_utils import apply_publication_style, figsize

apply_publication_style()

# whether to draw titles inside the figures; disabled for publication (the caption takes this role)
SHOW_TITLES = False


def set_title(ax, title):
    """Set the title of the axes ``ax``, if titles are enabled (see ``SHOW_TITLES``)."""
    if SHOW_TITLES:
        ax.set_title(title)



BASE_DIR = Path(__file__).resolve().parents[2]
REPORT_DIR = BASE_DIR / "reports"
PROFILE2_CSV = BASE_DIR / "benchmark_balanced_networks_profiling.csv"
PROFILE_CSV = BASE_DIR / "balanced_networks_profiling.csv"
ENERGY_CSV = BASE_DIR / "balanced_networks_energy.csv"

PROFILE_NAME = "sample_profile.json"
ENERGY_NAME = "energy_report.rpt"
METADATA_NAME = "metadata.json"


IMPLEMENTATION_LABELS = {
    "builtin": "Built-in",
    "nestml_exp_lut": "NESTML + exp LUT",
    "nestml_not_exp_lut": "NESTML + no exp LUT"
}



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


def plot_core_activity_range(cores, title, output_path):
    """Plot per-core min/max active time as a vertical range, with the mean as a marker."""
    labels = [f"{core['chip']}:{core['core']}" for core in cores]
    means = np.array([core["mean_percent_active"] for core in cores], dtype=float)
    mins = np.array([core.get("min_percent_active") if core.get("min_percent_active") is not None else core["mean_percent_active"] for core in cores], dtype=float)
    maxs = np.array([core.get("max_percent_active") if core.get("max_percent_active") is not None else core["mean_percent_active"] for core in cores], dtype=float)
    x = np.arange(len(cores))

    fig, ax = plt.subplots(figsize=figsize(6 / 12))
    ax.vlines(x, mins, maxs, color="tab:blue", alpha=0.35, linewidth=2, label="Min–max")
    ax.scatter(x, mins, marker="_", color="tab:blue", s=60)
    ax.scatter(x, maxs, marker="_", color="tab:blue", s=60)
    ax.scatter(x, means, marker="o", color="tab:orange", s=20, zorder=3, label="Mean")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=90)
    ax.set_xlim(-0.5, len(cores) - 0.5)
    ax.set_xlabel("Core")
    ax.set_ylabel("Active time [%]")
    set_title(ax, title)
    ax.grid(axis="y", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_path, dpi=300)
    plt.close(fig)



def plot_core_activity_bar(cores, title, output_path, implementation):
    """Plot per-core mean active time as a bar chart."""
    labels = [f"{core['chip']}:{core['core']}" for core in cores]
    values = [core["mean_percent_active"] for core in cores]

    plt.figure(figsize=figsize(6 / 12))
    plt.bar(labels, values)
    plt.xlabel("Core")
    plt.ylabel("Mean active time [%]")
    set_title(plt.gca(), title)
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()



def load_metadata(profile_path):
    """Load the ``metadata.json`` file living next to a sample profile, or return an empty dict if absent."""
    metadata_path = Path(profile_path).parent / METADATA_NAME

    if not metadata_path.exists():
        print(f"Warning: no {METADATA_NAME} found at {metadata_path}")
        return {}

    with open(metadata_path, "r", encoding="utf-8") as f:
        return json.load(f)


def format_metadata_for_title(metadata):
    """Format network size and exp LUT usage as a title suffix, e.g. " (N = 256, exp LUTs: True)"."""
    parts = []

    if metadata.get("N") is not None:
        parts.append(f"N = {metadata['N']}")

    if metadata.get("use_exp_luts") is not None:
        parts.append(f"exp LUTs: {metadata['use_exp_luts']}")

    return f" ({', '.join(parts)})" if parts else ""


def plot_core_activity(cores, profile_path, implementation):
    if not cores:
        print(f"No core profiling data found for {implementation}.")
        return

    title = f"{implementation} SpiNNaker Core Activity" + format_metadata_for_title(load_metadata(profile_path))

    output_path = Path(profile_path).parent / f"sample_profile_activity_{implementation.lower()}_range.png"
    plot_core_activity_range(cores, title, output_path)

    output_path = Path(profile_path).parent / f"sample_profile_activity_{implementation.lower()}.png"
    plot_core_activity_bar(cores, title, output_path, implementation)

    print(f"{implementation} core activity plot saved to: {output_path}")


def plot_comparison(reference, nestml, profile_path):
    """Plot summary activity metrics for reference and NESTML."""
    labels = ["Mean", "Median", "Maximum"]
    reference_values = [reference["mean"], reference["median"], reference["max"]]
    nestml_values = [nestml["mean"], nestml["median"], nestml["max"]]

    x = np.arange(len(labels))
    width = 0.35

    plt.figure(figsize=figsize(6 / 9))
    plt.bar(x - width / 2, reference_values, width, label="Reference")
    plt.bar(x + width / 2, nestml_values, width, label="NESTML")
    plt.xlabel("Core activity metric")
    plt.ylabel("Active time [%]")
    set_title(plt.gca(), "Reference vs NESTML Core Activity")
    plt.xticks(x, labels)
    plt.legend()
    plt.tight_layout()

    output_path = Path(profile_path).parent / "sample_profile_comparison.png"
    plt.savefig(output_path, dpi=300)
    plt.close()

    print(f"Comparison plot saved to: {output_path}")


def plot_distribution(reference_cores, nestml_cores, profile_path):
    """Plot transparent histograms with identical binning for both activity distributions."""
    reference_values = [core["mean_percent_active"] for core in reference_cores]
    nestml_values = [core["mean_percent_active"] for core in nestml_cores]

    if not reference_values or not nestml_values:
        print("No data available for histogram comparison.")
        return

    combined = reference_values + nestml_values
    bin_count = min(20, max(5, int(np.sqrt(len(combined)))))
    min_value = min(combined)
    max_value = max(combined)
    if np.isclose(min_value, max_value):
        min_value -= 0.5
        max_value += 0.5

    bins = np.linspace(min_value, max_value, bin_count + 1)

    plt.figure(figsize=figsize(6 / 8))
    plt.hist(
        reference_values,
        bins=bins,
        alpha=0.6,
        color="blue",
        label="Reference",
        edgecolor="black",
    )
    plt.hist(
        nestml_values,
        bins=bins,
        alpha=0.6,
        color="orange",
        label="NESTML",
        edgecolor="black",
    )

    plt.xlabel("Mean active time [%]")
    plt.ylabel("Number of cores")
    set_title(plt.gca(), "Distribution of Core Activity")
    plt.legend()
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

def load_profiling_data():
    """Load profiling data from CSV."""
    if not PROFILE2_CSV.exists():
        raise FileNotFoundError(f"Profiling CSV not found: {PROFILE2_CSV}")

    with open(PROFILE2_CSV, "r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_profile(path):
    """Load a sample profile JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_experiment_label(row):
    """Determine the experiment label from implementation and LUT setting."""

    implementation = row.get("implementation")
    use_exp_luts = row.get("use_exp_luts", "").lower() == "true"

    if implementation == "builtin":
        return "builtin"

    if implementation == "nestml":
        if use_exp_luts:
            return "nestml_exp_lut"

        return "nestml_not_exp_lut"

    return None


def plot_sum_core_activity(rows):
    """Plot sum of core activity against number of neurons."""

    data = {}

    for row in rows:
        implementation = get_experiment_label(row)

        if implementation not in IMPLEMENTATION_LABELS:
            continue

        try:
            neurons = int(row["N"])
            activity = float(row["sum_core_activity_percent"])
        except (ValueError, TypeError, KeyError):
            continue

        data.setdefault(implementation, []).append((neurons, activity))

    if not data:
        raise Exception("No profiling data available for plotting.")

    # mean and standard deviation across repeated runs, for each implementation and number of neurons
    stats = {}
    for implementation, values in data.items():
        grouped = {}
        for neurons, activity in values:
            grouped.setdefault(neurons, []).append(activity)

        stats[implementation] = {}
        for neurons_count in sorted(grouped):
            activities = grouped[neurons_count]
            stats[implementation][neurons_count] = (float(np.mean(activities)),
                                                    float(np.std(activities, ddof=1)) if len(activities) > 1 else 0.0)

    fig, (ax, ax_rel) = plt.subplots(2, 1, sharex=True, figsize=figsize(9 / 9), gridspec_kw={"height_ratios": [2, 1]})

    colors = {}
    for implementation, implementation_stats in stats.items():
        neurons = sorted(implementation_stats)
        means = [implementation_stats[n][0] for n in neurons]
        stds = [implementation_stats[n][1] for n in neurons]

        errorbar = ax.errorbar(
            neurons,
            means,
            yerr=stds,
            fmt="o-",
            capsize=4,
            label=IMPLEMENTATION_LABELS[implementation],
        )
        colors[implementation] = errorbar[0].get_color()

    ax.set_ylabel("Sum core activity [percentage-points]")
    set_title(ax, "SpiNNaker Core Activity vs Number of Neurons")
    ax.grid(True)
    ax.legend()

    # relative performance: activity of each implementation as a percentage of the built-in activity, at the numbers of neurons for which both are available
    if "builtin" in stats:
        baseline = stats["builtin"]
        # error bars in this panel show the run-to-run standard deviation of each implementation itself, expressed as a percentage of the built-in mean (so the variability of the baseline is shown on the baseline points, and is not also folded into the error bars of the other implementations)
        baseline_neurons = [n for n in sorted(baseline) if baseline[n][0] != 0.]
        ax_rel.errorbar(
            baseline_neurons,
            [100.] * len(baseline_neurons),
            yerr=[100. * baseline[n][1] / baseline[n][0] for n in baseline_neurons],
            fmt="o-",
            capsize=4,
            color=colors["builtin"],
            label=IMPLEMENTATION_LABELS["builtin"] + " (baseline)",
        )

        for implementation, implementation_stats in stats.items():
            if implementation == "builtin":
                continue

            neurons = [n for n in sorted(implementation_stats) if n in baseline and baseline[n][0] != 0.]
            if not neurons:
                continue

            ratios = []
            ratio_stds = []
            for n in neurons:
                mean, std = implementation_stats[n]
                baseline_mean = baseline[n][0]
                ratios.append(100. * mean / baseline_mean)
                ratio_stds.append(100. * std / baseline_mean)

            ax_rel.errorbar(
                neurons,
                ratios,
                yerr=ratio_stds,
                fmt="o-",
                capsize=4,
                color=colors[implementation],
                label=IMPLEMENTATION_LABELS[implementation],
            )

        # no legend: the colours are the same as in the top panel (whose legend identifies them), and a legend here tends to cover data points
    else:
        ax_rel.text(0.5, 0.5, "No built-in data available as baseline", ha="center", va="center", transform=ax_rel.transAxes)

    ax_rel.set_xlabel("Number of neurons")
    ax_rel.set_ylabel("Relative to built-in [%]")
    ax_rel.grid(True)

    fig.tight_layout()

    output_path = BASE_DIR / "sample_profile_sum_core_activity.png"
    fig.savefig(output_path, dpi=300)
    plt.close(fig)

    print(f"Sum core activity plot saved to: {output_path}")

# def plot_core_activity_by_neurons(rows):
#     """Plot core activity for different neuron counts."""

#     experiments = {}

#     for row in rows:
#         implementation = get_experiment_label(row)

#         if implementation not in IMPLEMENTATION_LABELS:
#             continue

#         timestamp = row.get("timestamp")

#         try:
#             neurons = int(row["N"])
#         except (ValueError, TypeError, KeyError):
#             continue

#         profile_path = (
#             BASE_DIR
#             / "reports_archive"
#             / timestamp
#             / "sample_profile.json"
#         )

#         if not profile_path.exists():
#             print(f"Profile file not found: {profile_path}")
#             continue

#         data = load_profile(profile_path)
#         cores = extract_core_activity(data)

#         experiments.setdefault(implementation, []).append(
#             (neurons, cores)
#         )

#     for implementation, runs in experiments.items():

#         core_data = {}

#         for neurons, cores in runs:
#             for core in cores:
#                 core_name = f"{core['chip']}:{core['core']}"

#                 core_data.setdefault(core_name, []).append(
#                     (neurons, core["mean_percent_active"])
#                 )

#         if not core_data:
#             continue

#         core_names = sorted(core_data.keys())

#         plt.figure(figsize=(14, 7))

#         for x, core_name in enumerate(core_names):

#             values = sorted(
#                 core_data[core_name],
#                 key=lambda value: value[0]
#             )

#             for neurons, activity in values:
#                 plt.scatter(
#                     x,
#                     activity,
#                     s=45
#                 )

#                 plt.annotate(
#                     f"N={neurons}",
#                     (x, activity),
#                     xytext=(5, 5),
#                     textcoords="offset points",
#                     fontsize=8
#                 )

#         plt.xticks(
#             range(len(core_names)),
#             core_names,
#             rotation=90
#         )

#         plt.xlabel("Core")
#         plt.ylabel("Mean active time [%]")
#         plt.title(
#             f"{IMPLEMENTATION_LABELS[implementation]} "
#             "Core Activity vs Number of Neurons"
#         )

#         plt.tight_layout()

#         output_path = (
#             BASE_DIR
#             / f"sample_profile_core_activity_vs_N_{implementation}.png"
#         )

#         plt.savefig(output_path, dpi=300)
#         plt.close()

#         print(f"Core activity vs N plot saved to: {output_path}")

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

    rows = load_profiling_data()
    plot_sum_core_activity(rows)
    # plot_core_activity_by_neurons(rows)


if __name__ == "__main__":
    main()
