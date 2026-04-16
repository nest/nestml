# -*- coding: utf-8 -*-
#
# test__basic_integration.py
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

import os

import numpy as np
import pytest

import nest

from pynestml.codegeneration.nest_tools import NESTTools
from pynestml.frontend.pynestml_frontend import generate_nest_compartmental_target


SP = {"C_m": 1.00, "g_C": 0.00, "g_L": 0.100, "e_L": -70.0, "v_comp": -70.0}
DP = [
    {"C_m": 0.10, "g_C": 0.10, "g_L": 0.010, "e_L": -70.0, "v_comp": -70.0},
    {"C_m": 0.08, "g_C": 0.11, "g_L": 0.007, "e_L": -70.0, "v_comp": -70.0},
    {"C_m": 0.09, "g_C": 0.07, "g_L": 0.011, "e_L": -70.0, "v_comp": -70.0},
    {"C_m": 0.15, "g_C": 0.12, "g_L": 0.014, "e_L": -70.0, "v_comp": -70.0},
    {"C_m": 0.20, "g_C": 0.32, "g_L": 0.022, "e_L": -55.0, "v_comp": -55.0},
    {"C_m": 0.12, "g_C": 0.12, "g_L": 0.010, "e_L": -23.0, "v_comp": -23.0},
    {"C_m": 0.32, "g_C": 0.09, "g_L": 0.032, "e_L": -32.0, "v_comp": -32.0},
    {"C_m": 0.01, "g_C": 0.05, "g_L": 0.001, "e_L": -88.0, "v_comp": -88.0},
]


def _comp(parent_idx, params):
    return {"parent_idx": parent_idx, "params": dict(params)}


def primitive_1dend_1comp():
    return [_comp(-1, SP), _comp(0, DP[0])]


def primitive_2dend_1comp():
    return [_comp(-1, SP), _comp(0, DP[0]), _comp(0, DP[1])]


def primitive_1dend_2comp():
    return [_comp(-1, SP), _comp(0, DP[0]), _comp(1, DP[1])]


def primitive_tdend_4comp():
    return [
        _comp(-1, SP),
        _comp(0, DP[0]),
        _comp(1, DP[1]),
        _comp(2, DP[2]),
        _comp(2, DP[3]),
    ]


def primitive_2tdend_4comp():
    return [
        _comp(-1, SP),
        _comp(0, DP[0]),
        _comp(1, DP[1]),
        _comp(2, DP[2]),
        _comp(2, DP[3]),
        _comp(0, DP[4]),
        _comp(5, DP[5]),
        _comp(6, DP[6]),
        _comp(6, DP[7]),
    ]


def build_linear_system_full_step(compartments, dt):
    """Build A, b for the generated compartmental solver scheme.

    The generated cm_tree uses full conductance terms in A and
    b_i = C_i/dt * e_L_i + g_L_i * e_L_i (+ injected current).
    """
    n_comp = len(compartments)
    aa = np.zeros((n_comp, n_comp), dtype=float)
    bb = np.zeros(n_comp, dtype=float)

    children = [[] for _ in range(n_comp)]
    for idx, c in enumerate(compartments):
        p_idx = c["parent_idx"]
        if p_idx >= 0:
            children[p_idx].append(idx)

    for idx, c in enumerate(compartments):
        p = c["params"]

        diag = p["C_m"] / dt + p["g_L"]

        parent_idx = c["parent_idx"]
        if parent_idx >= 0:
            gc = p["g_C"]
            diag += gc
            aa[idx, parent_idx] = -gc
            aa[parent_idx, idx] = -gc

        for child_idx in children[idx]:
            diag += compartments[child_idx]["params"]["g_C"]

        aa[idx, idx] = diag
        bb[idx] = p["C_m"] / dt * p["e_L"] + p["g_L"] * p["e_L"]

    return aa, bb


class TestBasicIntegration:
    MODULE_NAME = "cm_default_basic_integration_module"
    MODEL_NAME = "cm_default_basic_nestml"

    @pytest.fixture(scope="class", autouse=True)
    def setup_model(self):
        tests_path = os.path.realpath(os.path.dirname(__file__))
        input_path = os.path.join(tests_path, "resources", "cm_default.nestml")
        target_path = os.path.join(tests_path, "target/")

        if not os.path.exists(target_path):
            os.makedirs(target_path)

        generate_nest_compartmental_target(
            input_path=input_path,
            target_path=target_path,
            module_name=self.MODULE_NAME,
            suffix="_basic_nestml",
            logging_level="INFO",
        )

    def _run_and_compare(self, compartments, dt, injected_currents=None, sample_index=-1):
        nest.ResetKernel()
        nest.SetKernelStatus({"resolution": dt})
        nest.Install(self.MODULE_NAME)

        neuron = nest.Create(self.MODEL_NAME)
        neuron.V_th = 100.0
        neuron.compartments = compartments
        neuron.receptors = [{
                "comp_idx": idx, "receptor_type": "inp"
            } for idx in range(len(compartments))
        ]

        n_comp = len(compartments)
        mm = nest.Create(
            "multimeter",
            1,
            {"record_from": [f"v_comp{i}" for i in range(n_comp)], "interval": dt},
        )
        nest.Connect(mm, neuron)

        aa, bb = build_linear_system_full_step(compartments, dt)

        if injected_currents is not None:
            for idx, amp in enumerate(injected_currents):
                nest.Connect(
                    nest.Create("dc_generator", {"amplitude": float(amp)}),
                    neuron,
                    syn_spec={
                        "synapse_model": "static_synapse",
                        "weight": 1.0,
                        "delay": dt,
                        "receptor_type": idx,
                    },
                )
                bb[idx] += float(amp)

            # with delay=dt, current affects the second integration step
            nest.Simulate(3.0 * dt)
        else:
            # Keep explicit zero-current input connections so the model is
            # integrated and multimeter data is produced (mirrors NEST test).
            for idx in range(n_comp):
                nest.Connect(
                    nest.Create("dc_generator", {"amplitude": 0.0}),
                    neuron,
                    syn_spec={
                        "synapse_model": "static_synapse",
                        "weight": 1.0,
                        "delay": dt,
                        "receptor_type": idx,
                    },
                )
            # For no-input inversion check, compare the first integration step.
            nest.Simulate(2.0 * dt)

        events = nest.GetStatus(mm, "events")[0]
        v_neuron = np.array([events[f"v_comp{i}"][sample_index] for i in range(n_comp)])
        v_expected = np.linalg.solve(aa, bb)

        print(f"------- n_comp = {len(compartments)} -------")
        print("v_neuron:", v_neuron)
        print("v_expected:", v_expected)
        try:
            assert np.allclose(v_neuron, v_expected)
        except AssertionError:
            raise AssertionError(f"Neuron voltages {v_neuron} do not match expected values {v_expected}.")

    @pytest.mark.skipif(NESTTools.detect_nest_version().startswith("v2"),
                        reason="This test does not support NEST 2")
    @pytest.mark.parametrize(
        "primitive_fn",
        [
            primitive_1dend_1comp,
            primitive_2dend_1comp,
            primitive_1dend_2comp,
            primitive_tdend_4comp,
        ],
    )
    def test_inversion_primitives_with_input(self, primitive_fn):
        dt = 0.1
        compartments = primitive_fn()
        n_comp = len(compartments)
        i_in = 0.1 * np.arange(1, n_comp + 1)
        self._run_and_compare(compartments, dt=dt, injected_currents=i_in, sample_index=-1)

    @pytest.mark.skipif(NESTTools.detect_nest_version().startswith("v2"),
                        reason="This test does not support NEST 2")
    def test_inversion_heterogeneous_primitive_no_input(self):
        dt = 0.1
        compartments = primitive_2tdend_4comp()
        self._run_and_compare(compartments, dt=dt, injected_currents=None, sample_index=0)
