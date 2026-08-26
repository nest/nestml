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

from pynestml.frontend.pynestml_frontend import generate_nest_compartmental_target

try:
    import matplotlib as mpl
    mpl.use("agg")
    import matplotlib.pyplot as plt
    TEST_PLOTS = True
except BaseException:
    TEST_PLOTS = False


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

SOMA_CAPACITANCE_SCALE = 0.75           # Shortens the somatic membrane time constant while staying close to the baseline.
DEND_COUPLING_SCALE = 1.8               # Makes voltage changes propagate through the cable during the short burst windows.
PROXIMAL_DEND_CHANNEL_SCALE = 12.0      # Makes dendritic Na/K currents clearly visible at 0.1 ms resolution.
DISTAL_DEND_CHANNEL_SCALE = 8.0         # Keeps distal dynamics active but weaker than the proximal compartment.
DISTAL_DEND_CAPACITANCE_SCALE = 0.75    # Makes the distal voltage respond within a few 0.1 ms steps.
AMPA_TAU_SCALE = 0.6                    # Puts the AMPA rise time near one 0.1 ms step, stressing exponential propagators.
NMDA_TAU_SCALE = 1.0 / 3.0              # Keeps NMDA slower than AMPA but short enough to change over this 45 ms test.


def _scaled_params(base_params, scales=None, updates=None):
    params = copy.deepcopy(base_params)
    for name, scale in (scales or {}).items():
        params[name] *= scale
    params.update(updates or {})
    return params


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


class TestFastExpAccuracy:
    @pytest.fixture(scope="class", autouse=True)
    def setup_models(self):
        tests_path = os.path.realpath(os.path.dirname(__file__))
        input_path = os.path.join(tests_path, "resources", "cm_default.nestml")

        for variant_name, variant in VARIANTS.items():
            target_path = os.path.join(tests_path, "target", "fastexp_accuracy", variant_name)
            os.makedirs(target_path, exist_ok=True)

            generate_nest_compartmental_target(
                input_path=input_path,
                target_path=target_path,
                module_name=variant["module_name"],
                suffix=variant["suffix"],
                logging_level="INFO",
                codegen_opts=variant["codegen_opts"],
            )

    @pytest.fixture(scope="class")
    def reference_trace(self):
        return self._run_variant("reference")

    @pytest.mark.parametrize("variant_name", ["double_fastexp"])
    def test_stressful_multicompartment_accuracy_against_double_reference(self, variant_name, reference_trace):
        result = self._run_variant(variant_name)

        np.testing.assert_allclose(result["times"], reference_trace["times"])
        self._plot_comparison(reference_trace, result, variant_name)

        for variable in RECORDABLES:
            max_abs = np.max(np.abs(result[variable] - reference_trace[variable]))
            assert max_abs <= self._absolute_tolerance(variable), (
                f"{variant_name} deviates from double precision reference for {variable}: "
                f"max abs diff {max_abs} > {self._absolute_tolerance(variable)}"
            )

        assert np.ptp(reference_trace["v_comp0"]) > 5.0
        assert np.ptp(reference_trace["v_comp1"]) > 5.0
        assert np.ptp(reference_trace["v_comp2"]) > 5.0
        assert np.ptp(reference_trace["m_Na0"]) > 0.05
        assert np.ptp(reference_trace["h_Na0"]) > 0.05
        assert np.ptp(reference_trace["n_K0"]) > 0.05
        assert np.max(reference_trace["g_AN_AMPA2"]) > 0.5

    @staticmethod
    def _run_variant(variant_name):
        variant = VARIANTS[variant_name]

        nest.ResetKernel()
        nest.SetKernelStatus({"resolution": DT})
        nest.Install(variant["module_name"] + ".so")

        neuron = nest.Create(variant["model_name"])
        neuron.compartments = copy.deepcopy(COMPARTMENTS)
        neuron.receptors = [
            {"comp_idx": 0, "receptor_type": "AMPA_NMDA", "params": copy.deepcopy(RECEPTOR_PARAMS)},
            {"comp_idx": 1, "receptor_type": "AMPA_NMDA", "params": copy.deepcopy(RECEPTOR_PARAMS)},
            {"comp_idx": 2, "receptor_type": "AMPA_NMDA", "params": copy.deepcopy(RECEPTOR_PARAMS)},
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
                    "delay": DT,
                    "receptor_type": receptor_idx,
                },
            )

        multimeter = nest.Create("multimeter", 1, {"record_from": RECORDABLES, "interval": DT})
        nest.Connect(multimeter, neuron)

        nest.Simulate(SIM_TIME)
        events = nest.GetStatus(multimeter, "events")[0]

        return {variable: np.asarray(events[variable]) for variable in ["times"] + RECORDABLES}

    @staticmethod
    def _absolute_tolerance(variable):
        if variable.startswith("v_comp"):
            return 0.75
        if variable.startswith(("m_Na", "h_Na", "n_K")):
            return 0.03
        if variable.startswith(("g_AN_AMPA", "g_AN_NMDA")):
            return 0.08
        raise AssertionError(f"No tolerance configured for {variable}.")

    @staticmethod
    def _plot_comparison(reference, result, variant_name):
        if not TEST_PLOTS:
            return

        plot_groups = [
            ("compartment voltages", ["v_comp0", "v_comp1", "v_comp2"]),
            ("soma channel states", ["m_Na0", "h_Na0", "n_K0"]),
            (
                "receptor conductances",
                ["g_AN_AMPA0", "g_AN_NMDA0", "g_AN_AMPA1", "g_AN_NMDA1", "g_AN_AMPA2", "g_AN_NMDA2"],
            ),
        ]

        fig, axes = plt.subplots(len(plot_groups), 2, figsize=(12, 9), squeeze=False)
        times = reference["times"]

        for row, (title, variables) in enumerate(plot_groups):
            trace_ax = axes[row][0]
            diff_ax = axes[row][1]

            for variable in variables:
                trace_ax.plot(times, reference[variable], label=f"{variable} reference")
                trace_ax.plot(times, result[variable], linestyle="--", label=f"{variable} {variant_name}")
                diff_ax.plot(times, np.abs(result[variable] - reference[variable]), label=variable)

            trace_ax.set_title(title)
            trace_ax.set_xlabel("time [ms]")
            trace_ax.legend(fontsize="x-small", ncol=2)

            diff_ax.set_title(f"{title} absolute difference")
            diff_ax.set_xlabel("time [ms]")
            diff_ax.legend(fontsize="x-small", ncol=2)

        fig.tight_layout()
        output_path = os.path.join(
            os.path.realpath(os.path.dirname(__file__)),
            f"fastexp_accuracy_comparison_{variant_name}.png",
        )
        fig.savefig(output_path)
        plt.close(fig)
