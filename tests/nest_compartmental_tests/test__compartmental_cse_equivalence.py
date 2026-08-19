# -*- coding: utf-8 -*-
#
# test__compartmental_cse_equivalence.py
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


class TestCompartmentalCSEEquivalence:
    CASES = {
        "cse": {
            "module_name": "cm_cse_equivalence_cse_module",
            "suffix": "_cse_nestml",
            "model_name": "cm_default_cse_nestml",
            "receptor_type": "AMPA_stdp_synapse_cse_nestml",
            "codegen_opts": {},
        },
        "no_cse": {
            "module_name": "cm_cse_equivalence_no_cse_module",
            "suffix": "_no_cse_nestml",
            "model_name": "cm_default_no_cse_nestml",
            "receptor_type": "AMPA_stdp_synapse_no_cse_nestml",
            "codegen_opts": {"enable_cse": False},
        },
    }

    @pytest.fixture(scope="class", autouse=True)
    def setup_models(self, request):
        tests_path = os.path.realpath(os.path.dirname(__file__))
        resources_path = os.path.join(tests_path, "resources")
        synapse_path = os.path.join(tests_path, "..", "..", "models", "synapses", "stdp_synapse.nestml")

        for case_name, case in self.CASES.items():
            target_path = os.path.join(tests_path, "target", "cse_equivalence", case_name)
            install_path = os.path.join(target_path, "install")
            os.makedirs(target_path, exist_ok=True)
            os.makedirs(install_path, exist_ok=True)

            codegen_opts = {
                "neuron_synapse_pairs": [{
                    "neuron": "cm_default",
                    "synapses": {
                        "stdp_synapse": {"post_ports": ["post_spikes"]},
                    },
                }],
                "weight_variable": {"stdp_synapse": "w"},
                **case["codegen_opts"],
            }

            generate_nest_compartmental_target(
                input_path=[
                    os.path.join(resources_path, "cm_default.nestml"),
                    synapse_path,
                ],
                target_path=target_path,
                install_path=install_path,
                module_name=case["module_name"],
                suffix=case["suffix"],
                logging_level="WARNING",
                codegen_opts=codegen_opts,
            )

            case["target_path"] = target_path
            case["module_path"] = os.path.join(install_path, case["module_name"] + ".so")

        request.cls.CASES = self.CASES

    def run_model(self, case):
        nest.ResetKernel()
        nest.SetKernelStatus(dict(resolution=0.1))
        nest.Install(case["module_path"])

        neuron = nest.Create(case["model_name"])
        neuron.compartments = [{
            "parent_idx": -1,
            "params": {
                "C_m": 20.0,
                "g_C": 0.0,
                "g_L": 1.0,
                "e_L": -70.0,
                "v_comp": -70.0,
                "gbar_Na": 4608.698576715,
                "e_Na": 60.0,
                "gbar_K": 956.112772900,
                "e_K": -90.0,
            },
        }]
        neuron.V_th = -50.0
        neuron.receptors = [{
            "comp_idx": 0,
            "receptor_type": case["receptor_type"],
            "params": {
                "w": 20.0,
                "delay": 0.1,
                "e_AMPA": 60.0,
            },
        }]

        pre_spike_times = [5.0, 5.3, 5.6, 5.9, 6.2, 6.5, 6.8, 7.1, 7.4, 7.7]
        spike_generator = nest.Create("spike_generator", params={"spike_times": pre_spike_times})
        pre_neuron = nest.Create("parrot_neuron")
        nest.Connect(
            spike_generator,
            pre_neuron,
            "one_to_one",
            syn_spec={"synapse_model": "static_synapse", "weight": 25.0, "delay": 0.1},
        )
        nest.Connect(
            pre_neuron,
            neuron,
            "one_to_one",
            syn_spec={"synapse_model": "static_synapse", "weight": 1.0, "delay": 0.1, "receptor_type": 0},
        )

        recordables = [
            "v_comp0",
            "m_Na0",
            "h_Na0",
            "n_K0",
            "w0",
            "pre_trace0",
            "post_trace0",
            case["receptor_type"] + "0",
        ]
        multimeter = nest.Create("multimeter", 1, {"record_from": recordables, "interval": 0.1})
        pre_spike_recorder = nest.Create("spike_recorder")
        post_spike_recorder = nest.Create("spike_recorder")

        nest.Connect(multimeter, neuron)
        nest.Connect(pre_neuron, pre_spike_recorder)
        nest.Connect(neuron, post_spike_recorder)

        nest.Simulate(30.0)

        events = nest.GetStatus(multimeter, "events")[0]
        return {
            "times": events["times"],
            "v_comp": events["v_comp0"],
            "m_Na": events["m_Na0"],
            "h_Na": events["h_Na0"],
            "n_K": events["n_K0"],
            "weight": events["w0"],
            "pre_trace": events["pre_trace0"],
            "post_trace": events["post_trace0"],
            "receptor_current": events[case["receptor_type"] + "0"],
            "pre_spikes": nest.GetStatus(pre_spike_recorder, "events")[0]["times"],
            "post_spikes": nest.GetStatus(post_spike_recorder, "events")[0]["times"],
        }

    def test_cse_and_no_cse_generated_stdp_models_match(self):
        cse_result = self.run_model(self.CASES["cse"])
        no_cse_result = self.run_model(self.CASES["no_cse"])

        assert len(cse_result["post_spikes"]) > 0
        assert len(no_cse_result["post_spikes"]) > 0

        for key in cse_result:
            try:
                np.testing.assert_allclose(cse_result[key], no_cse_result[key], rtol=1e-7, atol=1e-7)
            except AssertionError:
                self._plot_comparison_failure(cse_result, no_cse_result, failing_key=key)
                raise

    @staticmethod
    def _plot_comparison_failure(cse_result, no_cse_result, failing_key):
        if not TEST_PLOTS:
            return

        trace_keys = [
            "v_comp",
            "m_Na",
            "h_Na",
            "n_K",
            "weight",
            "pre_trace",
            "post_trace",
            "receptor_current",
        ]
        times = cse_result["times"]
        fig, axes = plt.subplots(len(trace_keys), 2, figsize=(12, 2.2 * len(trace_keys)), squeeze=False)

        for row, key in enumerate(trace_keys):
            trace_axis = axes[row][0]
            diff_axis = axes[row][1]

            trace_axis.plot(times, cse_result[key], label=f"{key} cse")
            trace_axis.plot(times, no_cse_result[key], linestyle="--", label=f"{key} no_cse")
            trace_axis.set_title(key)
            trace_axis.set_xlabel("time [ms]")
            trace_axis.legend(fontsize="x-small")
            trace_axis.grid(True, alpha=0.3)

            diff_axis.plot(times, np.abs(cse_result[key] - no_cse_result[key]), label=f"|{key} cse - no_cse|")
            diff_axis.set_title(f"{key} absolute difference")
            diff_axis.set_xlabel("time [ms]")
            diff_axis.legend(fontsize="x-small")
            diff_axis.grid(True, alpha=0.3)

        fig.suptitle(f"CSE equivalence comparison failed for {failing_key}")
        fig.tight_layout()
        output_path = os.path.join(
            os.path.realpath(os.path.dirname(__file__)),
            "compartmental_cse_equivalence_failure.png",
        )
        fig.savefig(output_path)
        plt.close(fig)

    def test_cse_option_changes_generated_source(self):
        cse_source = os.path.join(
            self.CASES["cse"]["target_path"],
            "cm_neuroncurrents_cm_default_cse_nestml.cpp",
        )
        no_cse_source = os.path.join(
            self.CASES["no_cse"]["target_path"],
            "cm_neuroncurrents_cm_default_no_cse_nestml.cpp",
        )

        with open(cse_source, "r", encoding="utf-8") as f:
            assert "simd_cse_tmp_" in f.read()

        with open(no_cse_source, "r", encoding="utf-8") as f:
            assert "simd_cse_tmp_" not in f.read()
