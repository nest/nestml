# -*- coding: utf-8 -*-
#
# test__compartmental_stdp.py
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

import pytest

import nest

from pynestml.frontend.pynestml_frontend import generate_nest_compartmental_target

# set to `True` to plot simulation traces
TEST_PLOTS = True
try:
    import matplotlib
    import matplotlib.pyplot as plt
except BaseException as e:
    # always set TEST_PLOTS to False if matplotlib can not be imported
    TEST_PLOTS = False


class TestCompartmentalConcmech(unittest.TestCase):
    @pytest.fixture(scope="module", autouse=True)
    def setup(self):
        tests_path = os.path.realpath(os.path.dirname(__file__))
        neuron_input_path = os.path.join(
            tests_path,
            "resources",
            "concmech.nestml"
        )
        synapse_input_path = os.path.join(
            tests_path,
            "resources",
            "cm_stdp_synapse.nestml"
        )
        target_path = os.path.join(
            tests_path,
            "target/"
        )

        if not os.path.exists(target_path):
            os.makedirs(target_path)

        print(
            f"Compiled nestml model 'cm_main_cm_default_nestml' not found, installing in:"
            f"    {target_path}"
        )

        nest.ResetKernel()
        nest.SetKernelStatus(dict(resolution=.1))

        generate_nest_compartmental_target(
            input_path=[neuron_input_path, synapse_input_path],
            target_path=target_path,
            module_name="cm_stdp_module",
            suffix="_nestml",
            logging_level="INFO",
            codegen_opts={"neuron_synapse_pairs": [{"neuron": "multichannel_test_model",
                                                    "synapse": "stdp_synapse",
                                                    "post_ports": ["post_spikes"]}],
                          "delay_variable": {"stdp_synapse": "d"},
                          "weight_variable": {"stdp_synapse": "w"}
                          }
        )

        nest.Install("cm_stdp_module.so")

    def run_model(self, model_case, pre_spike, post_spike, sim_time):
        """
        Test the interaction between the pre- and post-synaptic spikes using STDP (Spike-Timing-Dependent Plasticity).

        This function sets up a simulation environment using NEST Simulator to demonstrate synaptic dynamics with pre-defined spike times for pre- and post-synaptic neurons. The function creates neuron models, assigns parameters, sets up connections, and records data from the simulation. It then plots the results for voltage, synaptic weight, spike timing, and pre- and post-synaptic traces.

        Simulation Procedure:
        1. Define pre- and post-synaptic spike timings and calculate simulation duration.
        2. Set up neuron models:
           a. `spike_generator` to provide external spike input.
           b. `parrot_neuron` for relaying spikes.
           c. Custom `multichannel_test_model_nestml` neuron for the postsynaptic side, with compartments and receptor configurations specified.
        3. Create recording devices:
           a. `multimeter` to record voltage, synaptic weights, currents, and traces.
           b. `spike_recorder` to record spikes from pre- and post-synaptic neurons.
        4. Establish connections:
           a. Connect spike generators to pre and post-neurons with static synaptic configurations.
           b. Connect pre-neuron to post-neuron using a configured STDP synapse.
           c. Connect recording devices to the respective neurons.
        5. Simulate the network for the specified time duration.
        6. Retrieve data from the multimeter and spike recorders.
        7. Plot the recorded data:
           a. Membrane voltage of the post-synaptic neuron.
           b. Synaptic weight change.
           c. Pre- and post-spike timings marked with vertical lines.
           d. Pre- and post-synaptic traces.

        Results:
        The plots generated illustrate the effects of spike timing on various properties of the post-synaptic neuron, highlighting STDP-driven synaptic weight changes and trace dynamics.
        """
        nest.ResetKernel()
        nest.SetKernelStatus(dict(resolution=.1))
        nest.Install("cm_stdp_module.so")

        measuring_spike = sim_time - 1
        if measuring_spike > pre_spike:
            pre_spike_times = [pre_spike, measuring_spike]
        else:
            pre_spike_times = [measuring_spike, pre_spike]
        post_spike_times = [post_spike]

        external_input_pre = nest.Create("spike_generator", params={"spike_times": pre_spike_times})
        external_input_post = nest.Create("spike_generator", params={"spike_times": post_spike_times})
        pre_neuron = nest.Create("parrot_neuron")
        post_neuron = nest.Create('multichannel_test_model_nestml')

        params = {'C_m': 10.0, 'g_C': 0.0, 'g_L': 1.5, 'e_L': -70.0}
        post_neuron.compartments = [
            {"parent_idx": -1, "params": params}
        ]

        if model_case == "nestml":
            post_neuron.receptors = [
                {"comp_idx": 0, "receptor_type": "AMPA_stdp_synapse_nestml", "params": {'w': 10.0, "d": 0.1, "tau_tr_pre": 40, "tau_tr_post": 40}}
            ]
            mm = nest.Create('multimeter', 1, {
                'record_from': ['v_comp0', 'w0', 'AMPA_stdp_synapse_nestml0', 'pre_trace0',
                                'post_trace0'], 'interval': .1})
        elif model_case == "nest":
            post_neuron.receptors = [
                {"comp_idx": 0, "receptor_type": "AMPA", "params": {}}
            ]
            mm = nest.Create('multimeter', 1, {
                'record_from': ['v_comp0', 'AMPA0'], 'interval': .1})

        nest.Connect(external_input_pre, pre_neuron, "one_to_one",
                     syn_spec={'synapse_model': 'static_synapse', 'weight': 2.0, 'delay': 0.1})
        if model_case == "nestml":
            nest.Connect(pre_neuron, post_neuron, "one_to_one",
                         syn_spec={'synapse_model': 'static_synapse', 'weight': 1.0, 'delay': 0.1, 'receptor_type': 0})
        elif model_case == "nest":
            wr = nest.Create("weight_recorder")
            nest.CopyModel(
                "stdp_synapse",
                "stdp_synapse_rec",
                {"weight_recorder": wr[0], "receptor_type": 0, 'weight': 1.0},
            )
            nest.Connect(
                pre_neuron,
                post_neuron,
                "all_to_all",
                syn_spec={
                    "synapse_model": "stdp_synapse_rec",
                    "delay": 0.1,
                    "weight": 10.0,
                    "receptor_type": 0
                },
            )
        nest.Connect(mm, post_neuron)

        nest.Simulate(sim_time)

        res = nest.GetStatus(mm, 'events')[0]
        recorded = dict()
        if model_case == "nest":
            recorded["weight"] = nest.GetStatus(wr, "events")[0]["weights"]
            recorded["w_times"] = nest.GetStatus(wr, "events")[0]["times"]
        elif model_case == "nestml":
            recorded["weight"] = res['w0']
            recorded["pre_trace"] = res['pre_trace0']
            recorded["post_trace"] = res['post_trace0']

        recorded["times"] = res['times']
        recorded["v_comp"] = res['v_comp0']

        return recorded

    def test__compartmental_stdp(self):
        rec_nest_runs = list()
        rec_nestml_runs = list()

        sim_time = 40
        resolution = 20
        sim_time = int(sim_time / resolution) * resolution

        sp_td = []
        for i in range(1, resolution):
            pre_spike = i * sim_time / resolution
            post_spike = sim_time / 2
            sp_td.append(pre_spike - post_spike)
            rec_nest_runs.append(self.run_model("nest", pre_spike, post_spike, sim_time))
            rec_nestml_runs.append(self.run_model("nestml", pre_spike, post_spike, sim_time))

        fig, axs = plt.subplots(2)

        for i in range(len(rec_nest_runs)):
            if i == 0:
                nest_l = "nest"
                nestml_l = "nestml"
            else:
                nest_l = None
                nestml_l = None

            rec_nest_raw = rec_nest_runs[i]
            rec_nestml_raw = rec_nestml_runs[i]
            axs[0].plot([sp_td[i]], [rec_nest_raw['weight'][-1]], c='grey', marker='o', label=nest_l, markersize=7)
            axs[0].plot([sp_td[i]], [rec_nestml_raw['weight'][-1]], c='orange', marker='X', label=nestml_l, markersize=5)

        nest_values = [rec_nest_runs[i]['weight'][-1] for i in range(len(rec_nest_runs))]
        nestml_values = [rec_nestml_runs[i]['weight'][-1] for i in range(len(rec_nestml_runs))]
        diff_values = [nestml_values[i] - nest_values[i] for i in range(len(rec_nest_runs))]

        axs[1].vlines(sp_td, 0, diff_values, color='red', label='diff', linewidth=3)

        axs[0].set_title('resulting weights')
        axs[1].set_title('weight difference')

        axs[0].legend()
        axs[1].legend()

        plt.tight_layout()

        plt.savefig("compartmental_stdp.png")
        plt.show()

        assert abs(max(diff_values)) <= 0.005, ("the maximum weight difference is too large! (" + str(max(diff_values)) + " > 0.005)")
