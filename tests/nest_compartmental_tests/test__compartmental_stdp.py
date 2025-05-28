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
            "stdp_synapse.nestml"
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
        if False:
            generate_nest_compartmental_target(
                input_path=[neuron_input_path, synapse_input_path],
                target_path=target_path,
                module_name="cm_stdp_module",
                suffix="_nestml",
                logging_level="DEBUG",
                codegen_opts={"neuron_synapse_pairs": [{"neuron": "multichannel_test_model",
                                                        "synapse": "stdp_synapse",
                                                        "post_ports": ["post_spikes"]}],
                              "delay_variable": {"stdp_synapse": "d"},
                              "weight_variable": {"stdp_synapse": "w"}
                              }
            )

        nest.Install("cm_stdp_module.so")

    def run_model(self, model_case, pre_spike, post_spike, measuring_spike):
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

        pre_spike_times = [pre_spike, measuring_spike]
        post_spike_times = [post_spike]
        sim_time = 30

        external_input_pre = nest.Create("spike_generator", params={"spike_times": pre_spike_times})
        external_input_post = nest.Create("spike_generator", params={"spike_times": post_spike_times})
        pre_neuron = nest.Create("parrot_neuron")
        post_neuron = nest.Create('multichannel_test_model_nestml', params={"tau_minus": 20.0})
        print("created")

        params = {'C_m': 10.0, 'g_C': 0.0, 'g_L': 1.5, 'e_L': -70.0}
        post_neuron.compartments = [
            {"parent_idx": -1, "params": params}
        ]
        print("comps")
        if model_case == "nestml":
            post_neuron.receptors = [
                {"comp_idx": 0, "receptor_type": "AMPA"},
                {"comp_idx": 0, "receptor_type": "AMPA_stdp_synapse_nestml", "params": {'w': 0.1, "tau_tr_post": 10.0}}
            ]
            mm = nest.Create('multimeter', 1, {
                'record_from': ['v_comp0', 'w1', 'AMPA0', 'AMPA_stdp_synapse_nestml1', 'pre_trace1',
                                'post_trace1'], 'interval': .1})
        elif model_case == "nest":
            post_neuron.receptors = [
                {"comp_idx": 0, "receptor_type": "AMPA"},
                {"comp_idx": 0, "receptor_type": "AMPA"}
            ]
            mm = nest.Create('multimeter', 1, {
                'record_from': ['v_comp0', 'AMPA0', 'AMPA1'], 'interval': .1})

        spikedet_pre = nest.Create("spike_recorder")
        spikedet_post = nest.Create("spike_recorder")

        nest.Connect(external_input_pre, pre_neuron, "one_to_one",
                     syn_spec={'synapse_model': 'static_synapse', 'weight': 2.0, 'delay': 0.1})
        nest.Connect(external_input_post, post_neuron, "one_to_one",
                     syn_spec={'synapse_model': 'static_synapse', 'weight': 5.0, 'delay': 0.1, 'receptor_type': 0})
        if model_case == "nestml":
            nest.Connect(pre_neuron, post_neuron, "one_to_one",
                         syn_spec={'synapse_model': 'static_synapse', 'weight': 0.1, 'delay': 0.1, 'receptor_type': 1})
        elif model_case == "nest":
            wr = nest.Create("weight_recorder")
            nest.CopyModel(
                "stdp_synapse",
                "stdp_synapse_rec",
                {"weight_recorder": wr[0], "receptor_type": 1},
            )
            nest.Connect(
                pre_neuron,
                post_neuron,
                "all_to_all",
                syn_spec={
                    "synapse_model": "stdp_synapse_rec",
                    "delay": 0.1,
                    "weight": 0.1,
                    "receptor_type": 1,
                    #"tau_minus": 10.0,
                },
            )
        nest.Connect(mm, post_neuron)

        nest.Connect(pre_neuron, spikedet_pre)
        nest.Connect(post_neuron, spikedet_post)

        chunk_size = 0.1
        if model_case == "nest":
            pre_trace_nest = list()
            post_trace_nest = list()
            weight_nest = list()
            conns = nest.GetConnections(source=pre_neuron, target=post_neuron)

            for t in range(int(sim_time / chunk_size)):
                nest.Simulate(chunk_size)
                if t < sim_time / chunk_size - 1:
                    conn_status = nest.GetStatus(conns)
                    neuron_status = nest.GetStatus(post_neuron)
                    pre_trace_nest.append(conn_status[0]["Kplus"])
                    weight_nest.append(conn_status[0]["weight"])
                    post_trace_nest.append(neuron_status[0]["post_trace"])

        elif model_case == "nestml":
            for t in range(int(sim_time / chunk_size)):
                nest.Simulate(chunk_size)
        res = nest.GetStatus(mm, 'events')[0]
        pre_spikes_rec = nest.GetStatus(spikedet_pre, 'events')[0]
        post_spikes_rec = nest.GetStatus(spikedet_post, 'events')[0]
        recorded = dict()
        if model_case == "nest":
            recorded["weight"] = nest.GetStatus(wr, "events")[0]["weights"]
            recorded["post_trace"] = post_trace_nest
            recorded["pre_trace"] = pre_trace_nest
        elif model_case == "nestml":
            recorded["weight"] = res['w1']
            recorded["pre_trace"] = res['pre_trace1']
            recorded["post_trace"] = res['post_trace1']

        recorded["v_comp"] = res['v_comp0']
        recorded["times"] = res['times']

        return recorded

    def test__compartmental_stdp(self):
        rec_nest_runs = list()
        rec_nestml_runs = list()
        for ms in range(11, 31):
            rec_nest_runs.append(self.run_model("nest", 2, 10, ms))
            rec_nestml_runs.append(self.run_model("nestml", 2, 10, ms))

        fig, axs = plt.subplots(4)

        ax_bg = (0.3, 0.3, 0.3)
        fig_bg = (0.45, 0.45, 0.45)

        fig.set_facecolor(fig_bg)
        for ax in axs:
            ax.set_facecolor(ax_bg)

        for i in range(len(rec_nest_runs)):
            increasing = 0+(1/len(rec_nestml_runs))*i
            decreasing = 1.0-(1/len(rec_nestml_runs))*i
            nest_color=(increasing, 1-increasing/5, 0)
            nestml_color=(increasing, 0, decreasing)

            rec_nest_raw = rec_nest_runs[i]
            rec_nestml_raw = rec_nestml_runs[i]

            rec_nest = dict()
            rec_nestml = dict()

            cut_off_index=(11+i)*10
            for entry_name, entry in rec_nest_raw.items():
                rec_nest[entry_name] = entry[cut_off_index+1:cut_off_index+2]

            for entry_name, entry in rec_nestml_raw.items():
                rec_nestml[entry_name] = entry[cut_off_index+1:cut_off_index+2]

            axs[0].plot(rec_nest['times'], rec_nest['v_comp'], color=nest_color, marker='o', label='nest')
            axs[0].plot(rec_nestml['times'], rec_nestml['v_comp'], color=nestml_color, marker='o', label="nestml")

            axs[1].plot(rec_nest['times'], rec_nest['post_trace'], color=nest_color, marker='o', label='nest')
            axs[1].plot(rec_nestml['times'], rec_nestml['post_trace'], color=nestml_color, marker='o', label="nestml")

            axs[2].plot(rec_nest['times'], rec_nest['pre_trace'], color=nest_color, marker='o', label='nest')
            axs[2].plot(rec_nestml['times'], rec_nestml['pre_trace'], color=nestml_color, marker='o', label="nestml")

        # axs[3].plot(rec_nest['times'], rec_nest['weight'], c='r', label='nest')
        # axs[3].plot(rec_nestml['times'], rec_nestml['weight'], c='g', label="nestml")

        axs[0].set_title('v_comp')
        axs[1].set_title('post_trace')
        axs[2].set_title('pre_trace')
        # axs[3].set_title('weight')

        # axs[0].legend()
        # axs[1].legend()
        # axs[2].legend()
        # axs[3].legend()

        plt.show()
