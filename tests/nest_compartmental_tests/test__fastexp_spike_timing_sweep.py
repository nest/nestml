# -*- coding: utf-8 -*-
#
# test__fastexp_spike_timing_sweep.py
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

import copy
import csv
import os

import nest
import numpy as np
import pytest

from pynestml.frontend.pynestml_frontend import generate_nest_compartmental_target

try:
    import matplotlib as mpl
    mpl.use("agg")
    import matplotlib.pyplot as plt
    TEST_PLOTS = True
except BaseException:
    TEST_PLOTS = False


DT = 0.1
BURST_START = 20.0
RECOVERY_WINDOW = 200.0
RECOVERY_STABILITY = 10.0
FREQUENCIES_HZ = [10, 20, 30, 50, 100, 200]
BURST_LENGTHS_MS = [10, 20, 30, 50, 100, 200]
INPUT_WEIGHT = 5.0
SPIKE_TIME_TOLERANCE = 0.5
RECOVERY_THRESHOLD = 1.0

RECORDABLES = ["v_comp0", "m_Na0", "h_Na0", "n_K0"]

SOMA_PARAMS = {
    "C_m": 89.245535,
    "g_C": 0.0,
    "g_L": 8.924572508,
    "e_L": -75.0,
    "v_comp": -75.0,
    "gbar_Na": 4608.698576715,
    "e_Na": 60.0,
    "gbar_K": 956.112772900,
    "e_K": -90.0,
}

VARIANTS = {
    "reference": {
        "module_name": "cm_fastexp_spike_sweep_reference_module",
        "suffix": "_fastexp_spike_sweep_reference_nestml",
        "model_name": "cm_default_fastexp_spike_sweep_reference_nestml",
        "codegen_opts": {"use_fastexp": False},
    },
    "fastexp": {
        "module_name": "cm_fastexp_spike_sweep_fastexp_module",
        "suffix": "_fastexp_spike_sweep_fastexp_nestml",
        "model_name": "cm_default_fastexp_spike_sweep_fastexp_nestml",
        "codegen_opts": {"use_fastexp": True},
    },
}


class TestFastExpSpikeTimingSweep:
    @pytest.fixture(scope="class", autouse=True)
    def setup_models(self, request):
        tests_path = os.path.realpath(os.path.dirname(__file__))
        input_path = os.path.join(tests_path, "resources", "cm_default.nestml")
        target_root = os.path.join(tests_path, "target", "fastexp_spike_timing_sweep")

        for variant_name, variant in VARIANTS.items():
            target_path = os.path.join(target_root, variant_name)
            install_path = os.path.join(target_path, "install")
            os.makedirs(target_path, exist_ok=True)
            os.makedirs(install_path, exist_ok=True)
            variant["target_path"] = target_path
            variant["module_path"] = os.path.join(install_path, variant["module_name"] + ".so")

            generate_nest_compartmental_target(
                input_path=input_path,
                target_path=target_path,
                install_path=install_path,
                module_name=variant["module_name"],
                suffix=variant["suffix"],
                logging_level="WARNING",
                codegen_opts=variant["codegen_opts"],
            )

        request.cls.VARIANTS = VARIANTS
        request.cls.target_root = target_root

    def test_spike_timing_sweep_against_standard_exponential(self):
        rows = []
        worst_recovery_case = None
        worst_mean_spike_error_case = None
        worst_max_spike_error_case = None
        reference_spiking_cases = 0
        spike_count_mismatches = []

        for frequency_hz in FREQUENCIES_HZ:
            for burst_length_ms in BURST_LENGTHS_MS:
                spike_times = self._input_spike_times(frequency_hz, burst_length_ms)
                sim_time = BURST_START + burst_length_ms + RECOVERY_WINDOW
                reference = self._run_variant("reference", spike_times, sim_time)
                fastexp = self._run_variant("fastexp", spike_times, sim_time)
                recovery_reference_time = self._recovery_reference_time(
                    reference["spike_times"],
                    fastexp["spike_times"],
                    spike_times,
                )

                assert np.allclose(reference["times"], fastexp["times"])
                for variable in RECORDABLES:
                    assert np.all(np.isfinite(reference[variable]))
                    assert np.all(np.isfinite(fastexp[variable]))

                metrics = self._case_metrics(reference, fastexp, recovery_reference_time)
                metrics.update({
                    "frequency_hz": frequency_hz,
                    "burst_length_ms": burst_length_ms,
                    "input_spike_count": len(spike_times),
                    "recovery_reference_time_ms": recovery_reference_time,
                    "reference_spike_count": len(reference["spike_times"]),
                    "fastexp_spike_count": len(fastexp["spike_times"]),
                })
                rows.append(metrics)
                case = {
                    "metrics": dict(metrics),
                    "reference": reference,
                    "fastexp": fastexp,
                    "input_spike_times": np.asarray(spike_times),
                    "recovery_reference_time": recovery_reference_time,
                }
                worst_recovery_case = self._select_worse_recovery_case(worst_recovery_case, case)
                worst_mean_spike_error_case = self._select_worse_spike_error_case(
                    worst_mean_spike_error_case,
                    case,
                    "normalized_spike_error_ms",
                )
                worst_max_spike_error_case = self._select_worse_spike_error_case(
                    worst_max_spike_error_case,
                    case,
                    "max_spike_error_ms",
                )

                if metrics["reference_spike_count"] > 0:
                    reference_spiking_cases += 1
                if metrics["reference_spike_count"] != metrics["fastexp_spike_count"]:
                    spike_count_mismatches.append(metrics)

        self._write_results(rows)
        self._plot_results(rows)
        self._plot_detailed_case(worst_recovery_case, "worst_recovery")
        self._plot_detailed_case(worst_mean_spike_error_case, "worst_mean_spike_error")
        self._plot_detailed_case(worst_max_spike_error_case, "worst_max_spike_error")
        self._plot_combined_results(
            rows,
            worst_recovery_case,
            worst_mean_spike_error_case,
            worst_max_spike_error_case,
        )

        assert reference_spiking_cases > 0
        assert not spike_count_mismatches

    def _run_variant(self, variant_name, spike_times, sim_time):
        variant = self.VARIANTS[variant_name]

        nest.ResetKernel()
        nest.SetKernelStatus({"resolution": DT})
        nest.Install(variant["module_path"])

        neuron = nest.Create(variant["model_name"])
        neuron.V_th = -50.0
        neuron.compartments = [{"parent_idx": -1, "params": copy.deepcopy(SOMA_PARAMS)}]
        neuron.receptors = [{"comp_idx": 0, "receptor_type": "AMPA_NMDA"}]

        spike_generator = nest.Create("spike_generator", 1, {"spike_times": spike_times})
        nest.Connect(
            spike_generator,
            neuron,
            syn_spec={
                "synapse_model": "static_synapse",
                "weight": INPUT_WEIGHT,
                "delay": DT,
                "receptor_type": 0,
            },
        )

        multimeter = nest.Create("multimeter", 1, {"record_from": RECORDABLES, "interval": DT})
        spike_recorder = nest.Create("spike_recorder")
        nest.Connect(multimeter, neuron)
        nest.Connect(neuron, spike_recorder)

        nest.Simulate(sim_time)
        multimeter_events = nest.GetStatus(multimeter, "events")[0]
        spike_events = nest.GetStatus(spike_recorder, "events")[0]

        result = {variable: np.asarray(multimeter_events[variable]) for variable in ["times"] + RECORDABLES}
        result["spike_times"] = np.asarray(spike_events["times"])
        return result

    @staticmethod
    def _input_spike_times(frequency_hz, burst_length_ms):
        isi = 1000.0 / frequency_hz
        spike_times = np.arange(BURST_START, BURST_START + burst_length_ms, isi)
        return list(np.unique(np.round(spike_times / DT) * DT))

    @staticmethod
    def _last_input_arrival_time(spike_times):
        assert len(spike_times) > 0
        return max(spike_times) + DT

    @staticmethod
    def _recovery_reference_time(reference_spikes, fastexp_spikes, input_spike_times):
        if len(reference_spikes) or len(fastexp_spikes):
            reference_anchor = reference_spikes[-1] if len(reference_spikes) else -np.inf
            fastexp_anchor = fastexp_spikes[-1] if len(fastexp_spikes) else -np.inf
            return max(reference_anchor, fastexp_anchor)

        return TestFastExpSpikeTimingSweep._last_input_arrival_time(input_spike_times)

    @staticmethod
    def _case_metrics(reference, fastexp, recovery_reference_time):
        reference_spikes = reference["spike_times"]
        fastexp_spikes = fastexp["spike_times"]
        spike_count_mismatch = len(reference_spikes) != len(fastexp_spikes)

        max_spike_error = np.nan
        if spike_count_mismatch:
            comparable_count = min(len(reference_spikes), len(fastexp_spikes))
            if comparable_count:
                spike_errors = np.abs(reference_spikes[:comparable_count] - fastexp_spikes[:comparable_count])
                matched_error = np.sum(spike_errors)
                max_spike_error = np.max(spike_errors)
            else:
                matched_error = 0.0
            missing_error = abs(len(reference_spikes) - len(fastexp_spikes)) * SPIKE_TIME_TOLERANCE
            normalized_spike_error = matched_error / comparable_count if comparable_count else np.nan
            accumulated_spike_error = matched_error + missing_error
        elif len(reference_spikes):
            spike_errors = np.abs(reference_spikes - fastexp_spikes)
            accumulated_spike_error = np.sum(spike_errors)
            normalized_spike_error = accumulated_spike_error / len(reference_spikes)
            max_spike_error = np.max(spike_errors)
        else:
            accumulated_spike_error = 0.0
            normalized_spike_error = 0.0
            max_spike_error = 0.0

        state_error = TestFastExpSpikeTimingSweep._state_error(reference, fastexp)
        recovery_time = TestFastExpSpikeTimingSweep._recovery_time(reference["times"], state_error, recovery_reference_time)

        return {
            "spike_count_mismatch": spike_count_mismatch,
            "accumulated_spike_error_ms": accumulated_spike_error,
            "normalized_spike_error_ms": normalized_spike_error,
            "max_spike_error_ms": max_spike_error,
            "recovery_time_ms": recovery_time,
            "max_state_error": np.nanmax(state_error),
        }

    @staticmethod
    def _state_error(reference, fastexp):
        voltage_error = np.abs(fastexp["v_comp0"] - reference["v_comp0"]) / 1.0
        gate_error = np.maximum.reduce([
            np.abs(fastexp["m_Na0"] - reference["m_Na0"]) / 0.01,
            np.abs(fastexp["h_Na0"] - reference["h_Na0"]) / 0.01,
            np.abs(fastexp["n_K0"] - reference["n_K0"]) / 0.01,
        ])
        return np.maximum(voltage_error, gate_error)

    @staticmethod
    def _recovery_time(times, state_error, recovery_reference_time):
        after_reference = np.flatnonzero(times >= recovery_reference_time)
        if not after_reference.size:
            return np.nan

        stable_samples = max(1, int(round(RECOVERY_STABILITY / DT)))
        for idx in after_reference:
            if idx + stable_samples > len(state_error):
                break
            if np.all(state_error[idx:idx + stable_samples] <= RECOVERY_THRESHOLD):
                return times[idx] - recovery_reference_time

        return np.nan

    def _write_results(self, rows):
        output_path = os.path.join(self.target_root, "fastexp_spike_timing_sweep.csv")
        fieldnames = [
            "frequency_hz",
            "burst_length_ms",
            "input_spike_count",
            "recovery_reference_time_ms",
            "reference_spike_count",
            "fastexp_spike_count",
            "spike_count_mismatch",
            "accumulated_spike_error_ms",
            "normalized_spike_error_ms",
            "max_spike_error_ms",
            "recovery_time_ms",
            "max_state_error",
        ]
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    @staticmethod
    def _select_worse_recovery_case(current, candidate):
        if current is None:
            return candidate

        candidate_score = TestFastExpSpikeTimingSweep._recovery_score(candidate["metrics"])
        current_score = TestFastExpSpikeTimingSweep._recovery_score(current["metrics"])
        return candidate if candidate_score > current_score else current

    @staticmethod
    def _recovery_score(metrics):
        recovery_time = metrics["recovery_time_ms"]
        no_recovery_penalty = 1.0e9 if not np.isfinite(recovery_time) else 0.0
        recovery_time = 0.0 if not np.isfinite(recovery_time) else recovery_time
        return no_recovery_penalty + recovery_time + metrics["max_state_error"] * 1.0e-6

    @staticmethod
    def _select_worse_spike_error_case(current, candidate, metric_name):
        if current is None:
            return candidate

        candidate_score = TestFastExpSpikeTimingSweep._spike_error_score(candidate["metrics"], metric_name)
        current_score = TestFastExpSpikeTimingSweep._spike_error_score(current["metrics"], metric_name)
        return candidate if candidate_score > current_score else current

    @staticmethod
    def _spike_error_score(metrics, metric_name):
        mismatch_penalty = 1.0e9 if metrics["spike_count_mismatch"] else 0.0
        spike_error = metrics[metric_name]
        spike_error = 0.0 if not np.isfinite(spike_error) else spike_error
        return mismatch_penalty + spike_error

    @staticmethod
    def _plot_results(rows):
        if not TEST_PLOTS:
            return

        tests_path = os.path.realpath(os.path.dirname(__file__))
        frequencies, burst_lengths, recovery_times, mean_spike_errors, max_spike_errors, mismatches = (
            TestFastExpSpikeTimingSweep._plot_arrays(rows)
        )

        TestFastExpSpikeTimingSweep._plot_surface_like_scatter(
            frequencies,
            burst_lengths,
            recovery_times,
            mismatches,
            "fastexp state recovery after output spike",
            "recovery time [ms]",
            os.path.join(tests_path, "fastexp_spike_timing_sweep_recovery_time.png"),
        )
        TestFastExpSpikeTimingSweep._plot_surface_like_scatter(
            frequencies,
            burst_lengths,
            mean_spike_errors,
            mismatches,
            "fastexp mean spike-time error",
            "mean spike error [ms/spike]",
            os.path.join(tests_path, "fastexp_spike_timing_sweep_spike_error.png"),
        )
        TestFastExpSpikeTimingSweep._plot_surface_like_scatter(
            frequencies,
            burst_lengths,
            max_spike_errors,
            mismatches,
            "fastexp max spike-time error",
            "max spike error [ms]",
            os.path.join(tests_path, "fastexp_spike_timing_sweep_max_spike_error.png"),
        )

    @staticmethod
    def _plot_arrays(rows):
        return (
            np.asarray([row["frequency_hz"] for row in rows]),
            np.asarray([row["burst_length_ms"] for row in rows]),
            np.asarray([row["recovery_time_ms"] for row in rows], dtype=float),
            np.asarray([row["normalized_spike_error_ms"] for row in rows], dtype=float),
            np.asarray([row["max_spike_error_ms"] for row in rows], dtype=float),
            np.asarray([row["spike_count_mismatch"] for row in rows], dtype=bool),
        )

    @staticmethod
    def _plot_detailed_case(case, case_name):
        if not TEST_PLOTS or case is None:
            return

        tests_path = os.path.realpath(os.path.dirname(__file__))
        reference = case["reference"]
        fastexp = case["fastexp"]
        metrics = case["metrics"]
        times = reference["times"]
        title_suffix = (
            f'{metrics["frequency_hz"]} Hz, {metrics["burst_length_ms"]} ms burst; '
            f'recovery={metrics["recovery_time_ms"]:.3g} ms, '
            f'mean spike error={metrics["normalized_spike_error_ms"]:.3g} ms/spike, '
            f'max spike error={metrics["max_spike_error_ms"]:.3g} ms'
        )
        plot_groups = [
            ("voltage", ["v_comp0"]),
            ("gating variables", ["m_Na0", "h_Na0", "n_K0"]),
        ]

        fig, axes = plt.subplots(len(plot_groups), 2, figsize=(12, 7), squeeze=False)
        TestFastExpSpikeTimingSweep._plot_detailed_case_on_axes(axes, case, case_name)
        fig.suptitle(title_suffix)
        fig.tight_layout()
        output_path = os.path.join(
            tests_path,
            f"fastexp_spike_timing_sweep_{case_name}_details.png",
        )
        fig.savefig(output_path)
        plt.close(fig)

    @staticmethod
    def _plot_detailed_case_on_axes(axes, case, case_name):
        reference = case["reference"]
        fastexp = case["fastexp"]
        times = reference["times"]
        plot_groups = [
            ("voltage", ["v_comp0"]),
            ("gating variables", ["m_Na0", "h_Na0", "n_K0"]),
        ]

        for row, (title, variables) in enumerate(plot_groups):
            trace_axis = axes[row][0]
            diff_axis = axes[row][1]

            for variable in variables:
                trace_axis.plot(times, reference[variable], label=f"{variable} reference")
                trace_axis.plot(times, fastexp[variable], linestyle="--", label=f"{variable} fastexp")
                diff_axis.plot(times, np.abs(fastexp[variable] - reference[variable]), label=variable)

            TestFastExpSpikeTimingSweep._annotate_case_times(trace_axis, case)
            TestFastExpSpikeTimingSweep._annotate_case_times(diff_axis, case)

            trace_axis.set_title(f"{case_name}: {title}")
            trace_axis.set_xlabel("time [ms]")
            trace_axis.grid(True, alpha=0.3)
            trace_axis.legend(fontsize="xx-small", ncol=2)

            diff_axis.set_title(f"{title} absolute difference")
            diff_axis.set_xlabel("time [ms]")
            diff_axis.grid(True, alpha=0.3)
            diff_axis.legend(fontsize="xx-small", ncol=2)

    @staticmethod
    def _plot_combined_results(rows, worst_recovery_case, worst_mean_spike_error_case, worst_max_spike_error_case):
        if (
                not TEST_PLOTS
                or worst_recovery_case is None
                or worst_mean_spike_error_case is None
                or worst_max_spike_error_case is None):
            return

        tests_path = os.path.realpath(os.path.dirname(__file__))
        frequencies, burst_lengths, recovery_times, mean_spike_errors, max_spike_errors, mismatches = (
            TestFastExpSpikeTimingSweep._plot_arrays(rows)
        )
        fig = plt.figure(figsize=(24, 14))
        grid = fig.add_gridspec(3, 6, height_ratios=[1.45, 1.0, 1.0], hspace=0.38, wspace=0.28)

        recovery_axis = fig.add_subplot(grid[0, 0:2], projection="3d")
        mean_spike_error_axis = fig.add_subplot(grid[0, 2:4], projection="3d")
        max_spike_error_axis = fig.add_subplot(grid[0, 4:6], projection="3d")
        TestFastExpSpikeTimingSweep._plot_surface_like_scatter(
            frequencies,
            burst_lengths,
            recovery_times,
            mismatches,
            "state recovery after output spike",
            "recovery time [ms]",
            axis=recovery_axis,
            fig=fig,
        )
        TestFastExpSpikeTimingSweep._plot_surface_like_scatter(
            frequencies,
            burst_lengths,
            mean_spike_errors,
            mismatches,
            "mean spike-time error",
            "mean spike error [ms/spike]",
            axis=mean_spike_error_axis,
            fig=fig,
        )
        TestFastExpSpikeTimingSweep._plot_surface_like_scatter(
            frequencies,
            burst_lengths,
            max_spike_errors,
            mismatches,
            "max spike-time error",
            "max spike error [ms]",
            axis=max_spike_error_axis,
            fig=fig,
        )

        recovery_detail_axes = np.asarray([
            [fig.add_subplot(grid[1, 0]), fig.add_subplot(grid[1, 1])],
            [fig.add_subplot(grid[2, 0]), fig.add_subplot(grid[2, 1])],
        ])
        mean_spike_detail_axes = np.asarray([
            [fig.add_subplot(grid[1, 2]), fig.add_subplot(grid[1, 3])],
            [fig.add_subplot(grid[2, 2]), fig.add_subplot(grid[2, 3])],
        ])
        max_spike_detail_axes = np.asarray([
            [fig.add_subplot(grid[1, 4]), fig.add_subplot(grid[1, 5])],
            [fig.add_subplot(grid[2, 4]), fig.add_subplot(grid[2, 5])],
        ])
        TestFastExpSpikeTimingSweep._plot_detailed_case_on_axes(
            recovery_detail_axes,
            worst_recovery_case,
            "worst recovery",
        )
        TestFastExpSpikeTimingSweep._plot_detailed_case_on_axes(
            mean_spike_detail_axes,
            worst_mean_spike_error_case,
            "worst mean spike error",
        )
        TestFastExpSpikeTimingSweep._plot_detailed_case_on_axes(
            max_spike_detail_axes,
            worst_max_spike_error_case,
            "worst max spike error",
        )

        fig.suptitle("fastexp spike timing sweep", fontsize=14)
        output_base = os.path.join(tests_path, "fastexp_spike_timing_sweep_overview")
        fig.savefig(output_base + ".png")
        fig.savefig(output_base + ".pdf")
        plt.close(fig)

    @staticmethod
    def _annotate_case_times(axis, case):
        for spike_idx, spike_time in enumerate(case["input_spike_times"]):
            axis.axvline(
                spike_time,
                color="tab:gray",
                linewidth=0.6,
                alpha=0.2,
                label="input spikes" if spike_idx == 0 else None,
            )
        for spike_idx, spike_time in enumerate(case["reference"]["spike_times"]):
            axis.axvline(
                spike_time,
                color="black",
                linewidth=0.8,
                alpha=0.5,
                label="reference output spikes" if spike_idx == 0 else None,
            )
        for spike_idx, spike_time in enumerate(case["fastexp"]["spike_times"]):
            axis.axvline(
                spike_time,
                color="tab:red",
                linestyle="--",
                linewidth=0.8,
                alpha=0.5,
                label="fastexp output spikes" if spike_idx == 0 else None,
            )
        axis.axvline(
            case["recovery_reference_time"],
            color="tab:blue",
            linestyle=":",
            linewidth=1.0,
            alpha=0.7,
            label="recovery anchor",
        )

    @staticmethod
    def _plot_surface_like_scatter(
            frequencies,
            burst_lengths,
            values,
            mismatches,
            title,
            z_label,
            output_path=None,
            axis=None,
            fig=None):
        own_figure = fig is None or axis is None
        if own_figure:
            fig = plt.figure(figsize=(8, 6))
            axis = fig.add_subplot(111, projection="3d")

        finite = np.isfinite(values)
        matched = finite & ~mismatches
        mismatch = finite & mismatches
        missing = ~finite

        if np.any(matched):
            TestFastExpSpikeTimingSweep._plot_stems_to_zero(
                axis,
                frequencies[matched],
                burst_lengths[matched],
                values[matched],
                "gray",
            )
            scatter = axis.scatter(
                frequencies[matched],
                burst_lengths[matched],
                values[matched],
                c=values[matched],
                cmap="viridis",
                s=45,
                label="matched spike count",
            )
            fig.colorbar(scatter, ax=axis, shrink=0.6, pad=0.12, label=z_label)
        if np.any(mismatch):
            TestFastExpSpikeTimingSweep._plot_stems_to_zero(
                axis,
                frequencies[mismatch],
                burst_lengths[mismatch],
                values[mismatch],
                "red",
            )
            axis.scatter(
                frequencies[mismatch],
                burst_lengths[mismatch],
                values[mismatch],
                color="red",
                s=65,
                marker="x",
                label="missed or extra spikes",
            )
        if np.any(missing):
            fallback_z = np.nanmax(values[finite]) if np.any(finite) else 0.0
            TestFastExpSpikeTimingSweep._plot_stems_to_zero(
                axis,
                frequencies[missing],
                burst_lengths[missing],
                np.full(np.sum(missing), fallback_z),
                "black",
            )
            axis.scatter(
                frequencies[missing],
                burst_lengths[missing],
                np.full(np.sum(missing), fallback_z),
                color="black",
                s=65,
                marker="^",
                label="no recovery within window",
            )

        axis.set_xlabel("input frequency [Hz]")
        axis.set_ylabel("burst length [ms]")
        axis.set_zlabel(z_label)
        axis.set_title(title)
        axis.legend(fontsize="x-small")
        if output_path is not None:
            fig.tight_layout()
            fig.savefig(output_path)
        if own_figure:
            plt.close(fig)

    @staticmethod
    def _plot_stems_to_zero(axis, frequencies, burst_lengths, values, color):
        for frequency, burst_length, value in zip(frequencies, burst_lengths, values):
            axis.plot(
                [frequency, frequency],
                [burst_length, burst_length],
                [0.0, value],
                color=color,
                linewidth=0.7,
                alpha=0.35,
            )
