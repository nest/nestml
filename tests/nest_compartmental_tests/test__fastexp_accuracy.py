# -*- coding: utf-8 -*-
#
# test__fastexp_accuracy.py
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
import os

import numpy as np
import pytest

import nest

from pynestml.codegeneration.nest_compartmental_code_generator import NESTCompartmentalCodeGenerator
from pynestml.frontend.pynestml_frontend import generate_nest_compartmental_target

try:
    import matplotlib as mpl
    mpl.use("agg")
    import matplotlib.pyplot as plt
    TEST_PLOTS = True
except BaseException:
    TEST_PLOTS = False


def _scaled_params(base_params, scales=None, updates=None):
    params = copy.deepcopy(base_params)
    for name, scale in (scales or {}).items():
        params[name] *= scale
    params.update(updates or {})
    return params


class TestFastExpAccuracy:
    DT = 0.1
    SIM_TIME = 45.0

    RECORDABLES = [
        "v_comp0",
        "v_comp1",
        "v_comp2",
        "m_Na0",
        "h_Na0",
        "n_K0",
        "m_Na1",
        "h_Na1",
        "n_K1",
        "m_Na2",
        "h_Na2",
        "n_K2",
        "g_AN_AMPA0",
        "g_AN_NMDA0",
        "g_AN_AMPA1",
        "g_AN_NMDA1",
        "g_AN_AMPA2",
        "g_AN_NMDA2",
    ]

    BASE_SOMA_PARAMS = {
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

    BASE_DEND_PARAMS = {
        "C_m": 1.929929,
        "g_C": 1.255439494,
        "g_L": 0.192992878,
        "e_L": -75.0,
        "v_comp": -75.0,
        "gbar_Na": 17.203212493,
        "e_Na": 60.0,
        "gbar_K": 11.887347450,
        "e_K": -90.0,
    }

    SOMA_CAPACITANCE_SCALE = 0.75
    DEND_COUPLING_SCALE = 1.8
    PROXIMAL_DEND_CHANNEL_SCALE = 12.0
    DISTAL_DEND_CHANNEL_SCALE = 8.0
    DISTAL_DEND_CAPACITANCE_SCALE = 0.75
    AMPA_TAU_SCALE = 0.6
    NMDA_TAU_SCALE = 1.0 / 3.0

    COMPARTMENTS = [
        {
            "parent_idx": -1,
            "params": _scaled_params(BASE_SOMA_PARAMS, {"C_m": SOMA_CAPACITANCE_SCALE}),
        },
        {
            "parent_idx": 0,
            "params": _scaled_params(
                BASE_DEND_PARAMS,
                {
                    "g_C": DEND_COUPLING_SCALE,
                    "gbar_Na": PROXIMAL_DEND_CHANNEL_SCALE,
                    "gbar_K": PROXIMAL_DEND_CHANNEL_SCALE,
                },
                {"e_L": -74.0, "v_comp": -74.0},
            ),
        },
        {
            "parent_idx": 1,
            "params": _scaled_params(
                BASE_DEND_PARAMS,
                {
                    "C_m": DISTAL_DEND_CAPACITANCE_SCALE,
                    "g_C": DEND_COUPLING_SCALE,
                    "gbar_Na": DISTAL_DEND_CHANNEL_SCALE,
                    "gbar_K": DISTAL_DEND_CHANNEL_SCALE,
                },
                {"e_L": -73.0, "v_comp": -73.0},
            ),
        },
    ]

    RECEPTOR_PARAMS = {
        "tau_r_AN_AMPA": 0.2 * AMPA_TAU_SCALE,
        "tau_d_AN_AMPA": 3.0 * AMPA_TAU_SCALE,
        "tau_r_AN_NMDA": 0.2 / AMPA_TAU_SCALE,
        "tau_d_AN_NMDA": 43.0 * NMDA_TAU_SCALE,
        "NMDA_ratio": 2.0,
    }

    VARIANTS = {
        "reference": {
            "module_name": "cm_accuracy_double_module",
            "suffix": "_accuracy_double_nestml",
            "model_name": "cm_default_accuracy_double_nestml",
            "codegen_opts": {"use_fastexp": False},
        },
        "double_fastexp": {
            "module_name": "cm_accuracy_double_fastexp_module",
            "suffix": "_accuracy_double_fastexp_nestml",
            "model_name": "cm_default_accuracy_double_fastexp_nestml",
            "codegen_opts": {"use_fastexp": True},
        },
    }

    @pytest.fixture(scope="class", autouse=True)
    def setup_models(self):
        tests_path = os.path.realpath(os.path.dirname(__file__))
        input_path = os.path.join(tests_path, "resources", "cm_default.nestml")

        for variant_name, variant in self.VARIANTS.items():
            target_path = os.path.join(tests_path, "target", "fastexp_accuracy", variant_name)
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
                logging_level="INFO",
                codegen_opts=variant["codegen_opts"],
            )

    @pytest.fixture(scope="class")
    def reference_trace(self):
        return self._run_variant("reference")

    @pytest.mark.parametrize("variant_name", ["double_fastexp"])
    def test_stressful_multicompartment_states(self, variant_name, reference_trace):
        result = self._run_variant(variant_name)

        np.testing.assert_allclose(result["times"], reference_trace["times"])
        self._plot_comparison(reference_trace, result, variant_name)

        for variable in self.RECORDABLES:
            assert np.all(np.isfinite(reference_trace[variable]))
            assert np.all(np.isfinite(result[variable]))

    def test_stressful_multicompartment_spike_times(self, reference_trace):
        result = self._run_variant("double_fastexp")

        assert len(reference_trace["spike_times"]) > 0
        assert len(result["spike_times"]) == len(reference_trace["spike_times"])
        np.testing.assert_allclose(result["spike_times"], reference_trace["spike_times"], atol=0.5, rtol=0.0)

    def test_fastexp_variant_uses_fast_propagator_function(self):
        variant = self.VARIANTS["double_fastexp"]
        source_path = os.path.join(
            variant["target_path"],
            "cm_neuroncurrents_" + variant["model_name"] + ".cpp",
        )

        with open(source_path, "r", encoding="utf-8") as f:
            source = f.read()

        assert "cm_fast_propagator_exp(" in source

    @staticmethod
    def _run_variant(variant_name):
        variant = TestFastExpAccuracy.VARIANTS[variant_name]

        nest.ResetKernel()
        nest.SetKernelStatus({"resolution": TestFastExpAccuracy.DT})
        nest.Install(variant["module_path"])

        neuron = nest.Create(variant["model_name"])
        neuron.V_th = -50.0
        neuron.compartments = copy.deepcopy(TestFastExpAccuracy.COMPARTMENTS)
        neuron.receptors = [
            {"comp_idx": 0, "receptor_type": "AMPA_NMDA", "params": copy.deepcopy(TestFastExpAccuracy.RECEPTOR_PARAMS)},
            {"comp_idx": 1, "receptor_type": "AMPA_NMDA", "params": copy.deepcopy(TestFastExpAccuracy.RECEPTOR_PARAMS)},
            {"comp_idx": 2, "receptor_type": "AMPA_NMDA", "params": copy.deepcopy(TestFastExpAccuracy.RECEPTOR_PARAMS)},
        ]

        # The small dendritic capacitances, active conductances in all
        # compartments, fast AMPA time constants, and spatially separated bursts
        # make both cable variables and exponential mechanism propagators move
        # appreciably at the standard 0.1 ms resolution.
        spike_trains = [
            ([5.0, 5.4, 5.8, 22.0, 22.4], 5.0),
            ([7.0, 7.4, 7.8, 24.0, 24.4], 4.5),
            ([9.0, 9.3, 9.6, 26.0, 26.3], 4.0),
        ]
        for receptor_idx, (spike_times, weight) in enumerate(spike_trains):
            spike_generator = nest.Create("spike_generator", 1, {"spike_times": spike_times})
            nest.Connect(
                spike_generator,
                neuron,
                syn_spec={
                    "synapse_model": "static_synapse",
                    "weight": weight,
                    "delay": TestFastExpAccuracy.DT,
                    "receptor_type": receptor_idx,
                },
            )

        multimeter = nest.Create(
            "multimeter",
            1,
            {"record_from": TestFastExpAccuracy.RECORDABLES, "interval": TestFastExpAccuracy.DT},
        )
        nest.Connect(multimeter, neuron)
        spike_recorder = nest.Create("spike_recorder")
        nest.Connect(neuron, spike_recorder)

        nest.Simulate(TestFastExpAccuracy.SIM_TIME)
        multimeter_events = nest.GetStatus(multimeter, "events")[0]
        spike_events = nest.GetStatus(spike_recorder, "events")[0]

        result = {
            variable: np.asarray(multimeter_events[variable])
            for variable in ["times"] + TestFastExpAccuracy.RECORDABLES
        }
        result["spike_times"] = np.asarray(spike_events["times"])
        return result

    @staticmethod
    def _plot_comparison(reference, result, variant_name):
        if not TEST_PLOTS:
            return

        plot_groups = [
            ("compartment voltages", ["v_comp0", "v_comp1", "v_comp2"]),
            ("soma channel states", ["m_Na0", "h_Na0", "n_K0"]),
        ]

        fig, axes = plt.subplots(len(plot_groups) + 1, 2, figsize=(12, 9), squeeze=False)
        times = reference["times"]

        for row, (title, variables) in enumerate(plot_groups):
            trace_ax = axes[row][0]
            diff_ax = axes[row][1]

            for variable in variables:
                trace_ax.plot(times, reference[variable], label=f"{variable} reference")
                trace_ax.plot(times, result[variable], linestyle="--", label=f"{variable} {variant_name}")
                diff_ax.plot(times, np.abs(result[variable] - reference[variable]), label=variable)

            TestFastExpAccuracy._plot_spike_times(trace_ax, reference, result, variant_name)
            TestFastExpAccuracy._plot_spike_times(diff_ax, reference, result, variant_name)

            trace_ax.set_title(title)
            trace_ax.set_xlabel("time [ms]")
            trace_ax.legend(fontsize="x-small", ncol=2)

            diff_ax.set_title(f"{title} absolute difference")
            diff_ax.set_xlabel("time [ms]")
            diff_ax.legend(fontsize="x-small", ncol=2)

        TestFastExpAccuracy._plot_tau_comparison(axes[len(plot_groups)])

        fig.tight_layout()
        output_path = os.path.join(
            os.path.realpath(os.path.dirname(__file__)),
            f"fastexp_accuracy_comparison_{variant_name}.png",
        )
        fig.savefig(output_path)
        plt.close(fig)

    @staticmethod
    def _plot_spike_times(axis, reference, result, variant_name):
        for spike_idx, spike_time in enumerate(reference["spike_times"]):
            axis.axvline(
                spike_time,
                color="black",
                linewidth=0.8,
                alpha=0.45,
                label="reference spikes" if spike_idx == 0 else None,
            )
        for spike_idx, spike_time in enumerate(result["spike_times"]):
            axis.axvline(
                spike_time,
                color="tab:red",
                linestyle="--",
                linewidth=0.8,
                alpha=0.45,
                label=f"{variant_name} spikes" if spike_idx == 0 else None,
            )

    @staticmethod
    def _plot_tau_comparison(axes):
        voltages = np.linspace(-100.0, 80.0, 1801)
        tau_values = {
            "m_Na": TestFastExpAccuracy._positive_finite_tau(TestFastExpAccuracy._tau_m_Na(voltages)),
            "h_Na": TestFastExpAccuracy._positive_finite_tau(TestFastExpAccuracy._tau_h_Na(voltages)),
            "n_K": TestFastExpAccuracy._positive_finite_tau(TestFastExpAccuracy._tau_n_K(voltages)),
        }

        tau_ax = axes[0]
        propagator_ax = axes[1]

        for name, tau in tau_values.items():
            tau_ax.plot(voltages, tau, label=f"tau_{name}")
            exact = TestFastExpAccuracy._exact_propagator(tau)
            fastexp = TestFastExpAccuracy._bounded_fast_propagator(tau)
            propagator_ax.plot(voltages, exact, label=f"{name} std::exp")
            propagator_ax.plot(voltages, fastexp, linestyle="--", label=f"{name} fastexp")

        tau_ax.axhline(
            TestFastExpAccuracy.DT / 2.0,
            linestyle="--",
            color="black",
            linewidth=1.0,
            label="fastexp lower bound: tau = h / 2",
        )
        tau_ax.set_xlabel("v_comp [mV]")
        tau_ax.set_ylabel("tau [ms]")
        tau_ax.set_yscale("log")
        tau_ax.set_title("propagator tau ranges")
        tau_ax.grid(True, which="both", alpha=0.3)
        tau_ax.legend(fontsize="x-small", ncol=2)

        propagator_ax.set_xlabel("v_comp [mV]")
        propagator_ax.set_ylabel("exp(-h / tau)")
        propagator_ax.set_title("fastexp disabled vs bounded fastexp")
        propagator_ax.grid(True, alpha=0.3)
        propagator_ax.legend(fontsize="x-small", ncol=2)

    @staticmethod
    def _tau_m_Na(v_comp):
        with np.errstate(divide="ignore", invalid="ignore"):
            simd_cse_tmp_Na0 = 0.111111111 * v_comp
            simd_cse_tmp_Na1 = (0.182 * v_comp + 6.372366) / (
                1.0 - 0.0204385321 * np.exp(-simd_cse_tmp_Na0)
            )
            simd_cse_tmp_Na2 = 1.0 / (
                simd_cse_tmp_Na1
                + ((-0.124) * v_comp - 4.341612) / (1.0 - 48.9271929 * np.exp(simd_cse_tmp_Na0))
            )
            return 0.31152648 * simd_cse_tmp_Na2

    @staticmethod
    def _tau_h_Na(v_comp):
        with np.errstate(divide="ignore", invalid="ignore"):
            simd_cse_tmp_Na3 = 0.2 * v_comp
            return 0.31152648 / (
                ((-0.0091) * v_comp - 0.6826183) / (1.0 - 3277527.88 * np.exp(simd_cse_tmp_Na3))
                + (0.024 * v_comp + 1.200312) / (1.0 - 4.52820433e-05 * np.exp(-simd_cse_tmp_Na3))
            )

    @staticmethod
    def _tau_n_K(v_comp):
        with np.errstate(divide="ignore", invalid="ignore"):
            simd_cse_tmp_K0 = 0.111111111 * v_comp
            simd_cse_tmp_K1 = 1.0 / (1.0 - 16.0832406 * np.exp(-simd_cse_tmp_K0))
            simd_cse_tmp_K2 = 1.0 / (
                simd_cse_tmp_K1 * (0.02 * v_comp - 0.5)
                + (0.05 - 0.002 * v_comp) / (1.0 - 0.0621765242 * np.exp(simd_cse_tmp_K0))
            )
            return 0.31152648 * simd_cse_tmp_K2

    @staticmethod
    def _positive_finite_tau(tau_values):
        return np.where(np.isfinite(tau_values) & (tau_values > 0.0), tau_values, np.nan)

    @staticmethod
    def _exact_propagator(tau_values):
        with np.errstate(divide="ignore", invalid="ignore"):
            return np.exp(-TestFastExpAccuracy.DT / tau_values)

    @staticmethod
    def _bounded_fast_propagator(tau_values):
        with np.errstate(divide="ignore", invalid="ignore"):
            x = -TestFastExpAccuracy.DT / tau_values
            xc = np.minimum(-1.0e-12, np.maximum(-2.0, x))
            return 0.9999833698215348 + xc * (
                0.9993709968710967 + xc * (
                    0.4961277470116421 + xc * (
                        0.15781341991629894 + xc * (
                            0.03218380466140601 + xc * 0.003214600822495845
                        )
                    )
                )
            )


def test_fastexp_option_is_accepted():
    code_generator = NESTCompartmentalCodeGenerator()
    code_generator.set_options({"use_fastexp": True})
