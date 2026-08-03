# -*- coding: utf-8 -*-
#
# test__compartmental_multi_synapse_codegen.py
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
import unittest

import nest
import pytest

from pynestml.frontend.pynestml_frontend import generate_nest_compartmental_target

TEST_PLOTS = True
try:
    import matplotlib.pyplot as plt
except BaseException:
    TEST_PLOTS = False


class TestCompartmentalMultiSynapseCodegen(unittest.TestCase):
    MODULE_NAME = "cm_multi_synapse_module"
    TARGET_DIR = "target_multi_synapse"
    SYNAPSE_CASES = {
        "stdp_synapse": {
            "nest_synapse": "stdp_synapse",
            "nestml_receptor": "AMPA_stdp_synapse_nestml",
            "plot_name": "compartmental_multi_synapse_stdp.png",
            "warmup_pre_spike": None,
        },
        "stdp_nn_symm_synapse": {
            "nest_synapse": "stdp_nn_symm_synapse",
            "nestml_receptor": "AMPA_stdp_nn_symm_synapse_nestml",
            "plot_name": "compartmental_multi_synapse_stdp_nn_symm.png",
            "warmup_pre_spike": 0.5,
        },
    }

    @pytest.fixture(scope="module", autouse=True)
    def setup(self):
        tests_path = os.path.realpath(os.path.dirname(__file__))
        resources_path = os.path.join(tests_path, "resources")
        target_path = os.path.join(tests_path, self.TARGET_DIR)

        if not os.path.exists(target_path):
            os.makedirs(target_path)

        nest.ResetKernel()
        nest.SetKernelStatus(dict(resolution=.1))

        generate_nest_compartmental_target(
            input_path=[
                os.path.join(resources_path, "concmech.nestml"),
                os.path.join(resources_path, "cm_default.nestml"),
                os.path.join(resources_path, "..", "..", "..", "models", "synapses", "stdp_synapse.nestml"),
                os.path.join(resources_path, "..", "..", "..", "models", "synapses", "stdp_nn_symm_synapse.nestml"),
            ],
            target_path=target_path,
            module_name=self.MODULE_NAME,
            suffix="_nestml",
            logging_level="DEBUG",
            codegen_opts={
                "neuron_synapse_pairs": [
                    {
                        "neuron": "multichannel_test_model",
                        "synapses": {
                            "stdp_synapse": {"post_ports": ["post_spikes"]},
                            "stdp_nn_symm_synapse": {"post_ports": ["post_spikes"]},
                        },
                    },
                    {
                        "neuron": "cm_default",
                        "synapses": {
                            "stdp_synapse": {"post_ports": ["post_spikes"]},
                            "stdp_nn_symm_synapse": {"post_ports": ["post_spikes"]},
                        },
                    },
                ],
                "weight_variable": {
                    "stdp_synapse": "w",
                    "stdp_nn_symm_synapse": "w",
                },
            },
        )

        nest.Install(self.MODULE_NAME + ".so")

    def test_create_two_neurons_with_two_synapse_receptor_variants(self):
        compartment_params = {"C_m": 10.0, "g_C": 0.0, "g_L": 1.5, "e_L": -70.0}
        receptor_params = {"w": 1.0, "delay": 0.1, "e_AMPA": -70.0}

        multichannel_neuron = nest.Create("multichannel_test_model_nestml")
        multichannel_neuron.compartments = [{"parent_idx": -1, "params": compartment_params}]
        multichannel_neuron.receptors = [
            {"comp_idx": 0, "receptor_type": "AMPA_stdp_synapse_nestml", "params": receptor_params},
            {"comp_idx": 0, "receptor_type": "AMPA_stdp_nn_symm_synapse_nestml", "params": receptor_params},
        ]

        cm_default_neuron = nest.Create("cm_default_nestml")
        cm_default_neuron.compartments = [{"parent_idx": -1, "params": compartment_params}]
        cm_default_neuron.receptors = [
            {"comp_idx": 0, "receptor_type": "AMPA_stdp_synapse_nestml", "params": receptor_params},
            {"comp_idx": 0, "receptor_type": "AMPA_stdp_nn_symm_synapse_nestml", "params": receptor_params},
        ]

    def run_model(self, synapse_case, model_case, pre_spike, post_spike, sim_time):
        nest.ResetKernel()
        nest.SetKernelStatus(dict(resolution=.1))
        nest.Install(self.MODULE_NAME + ".so")

        measuring_spike = sim_time + 1
        pre_spike_times = [pre_spike, measuring_spike]
        if synapse_case["warmup_pre_spike"] is not None:
            pre_spike_times.insert(0, synapse_case["warmup_pre_spike"])

        external_input_pre = nest.Create("spike_generator", params={"spike_times": pre_spike_times})
        pre_neuron = nest.Create("parrot_neuron")
        post_neuron = nest.Create("multichannel_test_model_nestml")

        compartment_params = {"C_m": 10.0, "g_C": 0.0, "g_L": 1.5, "e_L": -70.0}
        post_neuron.compartments = [{"parent_idx": -1, "params": compartment_params}]

        if model_case == "nestml":
            post_neuron.receptors = [
                {
                    "comp_idx": 0,
                    "receptor_type": synapse_case["nestml_receptor"],
                    "params": {"w": 10.0, "delay": 0.1, "e_AMPA": -70.0},
                }
            ]
            mm = nest.Create("multimeter", 1, {
                "record_from": [
                    "v_comp0",
                    "w0",
                    synapse_case["nestml_receptor"] + "0",
                    "pre_trace0",
                    "post_trace0",
                ],
                "interval": .1,
            })
        elif model_case == "nest":
            post_neuron.receptors = [
                {"comp_idx": 0, "receptor_type": "AMPA", "params": {"e_AMPA": -70.0}}
            ]
            mm = nest.Create("multimeter", 1, {
                "record_from": ["v_comp0", "AMPA0"], "interval": .1})

        nest.Connect(external_input_pre, pre_neuron, "one_to_one",
                     syn_spec={"synapse_model": "static_synapse", "weight": 2.0, "delay": 0.1})

        if model_case == "nestml":
            nest.Connect(pre_neuron, post_neuron, "one_to_one",
                         syn_spec={"synapse_model": "static_synapse", "weight": 1.0, "delay": 0.1, "receptor_type": 0})
        elif model_case == "nest":
            weight_recorder = nest.Create("weight_recorder")
            synapse_model_name = synapse_case["nest_synapse"] + "_rec"
            nest.CopyModel(
                synapse_case["nest_synapse"],
                synapse_model_name,
                {"weight_recorder": weight_recorder[0], "receptor_type": 0, "weight": 1.0},
            )
            nest.Connect(
                pre_neuron,
                post_neuron,
                "all_to_all",
                syn_spec={
                    "synapse_model": synapse_model_name,
                    "delay": 0.1,
                    "weight": 10.0,
                    "receptor_type": 0,
                },
            )

        nest.Connect(mm, post_neuron)

        spike_recorder_post = nest.Create("spike_recorder")
        spike_recorder_pre = nest.Create("spike_recorder")

        nest.Connect(post_neuron, spike_recorder_post)
        nest.Connect(pre_neuron, spike_recorder_pre)

        nest.Simulate(post_spike)
        nest.SetStatus(post_neuron, {"v_comp0": 0.0})
        nest.Simulate(sim_time - post_spike + 2)

        recorded = {"times": nest.GetStatus(mm, "events")[0]["times"]}
        if model_case == "nest":
            recorded["weight"] = nest.GetStatus(weight_recorder, "events")[0]["weights"]
        elif model_case == "nestml":
            recorded["weight"] = nest.GetStatus(mm, "events")[0]["w0"]

        recorded["pre_spikes"] = nest.GetStatus(spike_recorder_pre)[0]["events"]
        recorded["post_spikes"] = nest.GetStatus(spike_recorder_post)[0]["events"]

        return recorded

    def assert_generated_synapse_matches_nest(self, synapse_case):
        rec_nest_runs = []
        rec_nestml_runs = []

        sim_time = 30
        resolution = 20
        sim_time = int(sim_time / resolution) * resolution

        for i in range(1, resolution):
            pre_spike = i * sim_time / resolution
            post_spike = sim_time / 2
            sp_td = pre_spike - post_spike
            rec_nest_runs.append(self.run_model(synapse_case, "nest", pre_spike, post_spike, sim_time))
            rec_nestml_runs.append(self.run_model(synapse_case, "nestml", pre_spike, post_spike, sim_time))
            rec_nest_runs[-1]["sp_td"] = sp_td
            rec_nestml_runs[-1]["sp_td"] = sp_td

        nest_values = [recording["weight"][-1] for recording in rec_nest_runs]
        nestml_values = [recording["weight"][-1] for recording in rec_nestml_runs]
        signed_diff_values = [
            nestml_value - nest_value
            for nestml_value, nest_value in zip(nestml_values, nest_values)
        ]
        abs_diff_values = [
            abs(nestml_value - nest_value)
            for sp_td_value, nestml_value, nest_value in zip(
                [recording["sp_td"] for recording in rec_nest_runs],
                nestml_values,
                nest_values)
            if sp_td_value != 0
        ]

        if TEST_PLOTS:
            self.plot_comparison(synapse_case, rec_nest_runs, rec_nestml_runs, signed_diff_values)

        assert max(abs_diff_values) <= 0.005, (
            "the maximum weight difference is too large! ("
            + str(max(abs_diff_values))
            + " > 0.005)")

    def plot_comparison(self, synapse_case, rec_nest_runs, rec_nestml_runs, diff_values):
        fig, axs = plt.subplots(4)
        sp_td = [recording["sp_td"] for recording in rec_nest_runs]

        for i in range(len(rec_nest_runs)):
            if i == 0:
                nest_label = "nest"
                nestml_label = "nestml"
            else:
                nest_label = None
                nestml_label = None

            rec_nest_raw = rec_nest_runs[i]
            rec_nestml_raw = rec_nestml_runs[i]
            axs[0].plot([sp_td[i]], [rec_nest_raw["weight"][-1]], c="grey", marker="o",
                        label=nest_label, markersize=7)
            axs[0].plot([sp_td[i]], [rec_nestml_raw["weight"][-1]], c="orange", marker="X",
                        label=nestml_label, markersize=5)

            linewidth = 8
            markersize = 1.5
            for spike_index, spike_time in enumerate(rec_nest_raw["pre_spikes"]["times"]):
                label = "pre_spikes" if i == 0 and spike_index == 0 else None
                axs[2].plot([sp_td[i]], [spike_time], c="blue", marker="_", label=label,
                            markersize=linewidth + 10)
                axs[2].vlines(
                    x=sp_td[i],
                    ymin=spike_time - markersize,
                    ymax=spike_time,
                    color="blue",
                    linewidth=linewidth)

            for spike_index, spike_time in enumerate(rec_nest_raw["post_spikes"]["times"]):
                label = "post_spikes" if i == 0 and spike_index == 0 else None
                axs[2].plot([sp_td[i]], [spike_time], c="red", marker="_", label=label,
                            markersize=linewidth + 10)
                axs[2].vlines(
                    x=sp_td[i],
                    ymin=spike_time,
                    ymax=spike_time + markersize,
                    color="red",
                    linewidth=linewidth)

            for spike_index, spike_time in enumerate(rec_nestml_raw["pre_spikes"]["times"]):
                label = "pre_spikes" if i == 0 and spike_index == 0 else None
                axs[3].plot([sp_td[i]], [spike_time], c="blue", marker="_", label=label,
                            markersize=linewidth + 10)
                axs[3].vlines(
                    x=sp_td[i],
                    ymin=spike_time - markersize,
                    ymax=spike_time,
                    color="blue",
                    linewidth=linewidth)

            for spike_index, spike_time in enumerate(rec_nestml_raw["post_spikes"]["times"]):
                label = "post_spikes" if i == 0 and spike_index == 0 else None
                axs[3].plot([sp_td[i]], [spike_time], c="red", marker="_", label=label,
                            markersize=linewidth + 10)
                axs[3].vlines(
                    x=sp_td[i],
                    ymin=spike_time,
                    ymax=spike_time + markersize,
                    color="red",
                    linewidth=linewidth)

        axs[1].vlines(sp_td, 0, diff_values, color="red", label="diff", linewidth=3)

        axs[0].set_title("resulting weights: " + synapse_case["nest_synapse"])
        axs[1].set_title("weight difference")
        axs[2].set_title("nest spike times")
        axs[3].set_title("nestml spike times")

        axs[0].legend()
        axs[1].legend()
        axs[2].legend()
        axs[3].legend()

        plt.tight_layout()
        plt.savefig(synapse_case["plot_name"])
        plt.close(fig)

    def test__compartmental_stdp_synapse_matches_nest(self):
        self.assert_generated_synapse_matches_nest(self.SYNAPSE_CASES["stdp_synapse"])

    def test__compartmental_stdp_nn_symm_synapse_matches_nest(self):
        self.assert_generated_synapse_matches_nest(self.SYNAPSE_CASES["stdp_nn_symm_synapse"])
