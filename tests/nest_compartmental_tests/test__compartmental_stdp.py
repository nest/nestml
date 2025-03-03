# -*- coding: utf-8 -*-
#
# compartmental_stdp_test.py
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

import numpy as np
import pytest

import nest

from pynestml.codegeneration.nest_tools import NESTTools
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
            "third_factor_stdp_synapse.nestml"
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
        if True:
            generate_nest_compartmental_target(
                input_path=[neuron_input_path, synapse_input_path],
                target_path=target_path,
                module_name="cm_stdp_module",
                suffix="_nestml",
                logging_level="DEBUG",
                codegen_opts={"neuron_synapse_pairs": [{"neuron": "multichannel_test_model",
                                                        "synapse": "third_factor_stdp_synapse",
                                                        "post_ports": ["post_spikes"]}],
                              "delay_variable": {"stdp_synapse": "d"},
                              "weight_variable": {"stdp_synapse": "w"}
                              }
            )

        nest.Install("cm_stdp_module.so")

    def test_cm_stdp(self):
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
        pre_spike_times = [11, 50]
        post_spike_times = [12, 45]
        sim_time = max(np.amax(pre_spike_times), np.amax(post_spike_times)) + 20
        #wr = nest.Create("weight_recorder")
        #nest.CopyModel("stdp_synapse_nestml__with_multichannel_test_model_nestml", "stdp_nestml_rec",
        #               {"weight_recorder": wr[0], "w": 1., "d": 1., "receptor_type": 0})
        external_input_pre = nest.Create("spike_generator", params={"spike_times": pre_spike_times})
        external_input_post = nest.Create("spike_generator", params={"spike_times": post_spike_times})
        pre_neuron = nest.Create("parrot_neuron")
        post_neuron = nest.Create('multichannel_test_model_nestml')
        print("created")

        params = {'C_m': 10.0, 'g_C': 0.0, 'g_L': 1.5, 'e_L': -70.0, 'gbar_Ca_HVA': 1.0, 'gbar_SK_E2': 1.0}
        post_neuron.compartments = [
            {"parent_idx": -1, "params": params}
        ]
        print("comps")
        post_neuron.receptors = [
            {"comp_idx": 0, "receptor_type": "AMPA"},
            {"comp_idx": 0, "receptor_type": "AMPA_third_factor_stdp_synapse_nestml", "params": {'w': 50.0}}
        ]
        print("syns")
        mm = nest.Create('multimeter', 1, {
            'record_from': ['v_comp0', 'w_input1', 'i_tot_input0', 'i_tot_input1', 'pre_trace_input1', 'post_trace_input1'], 'interval': .1})
        spikedet_pre = nest.Create("spike_recorder")
        spikedet_post = nest.Create("spike_recorder")

        nest.Connect(external_input_pre, pre_neuron, "one_to_one", syn_spec={'synapse_model': 'static_synapse', 'weight': 2.0, 'delay': 0.1})
        nest.Connect(external_input_post, post_neuron, "one_to_one", syn_spec={'synapse_model': 'static_synapse', 'weight': 5.0, 'delay': 0.1, 'receptor_type': 0})
        nest.Connect(pre_neuron, post_neuron, "one_to_one", syn_spec={'synapse_model': 'static_synapse', 'weight': 1.0, 'delay': 0.1, 'receptor_type': 1})
        nest.Connect(mm, post_neuron)
        nest.Connect(pre_neuron, spikedet_pre)
        nest.Connect(post_neuron, spikedet_post)
        print("pre sim")
        nest.Simulate(sim_time)
        res = nest.GetStatus(mm, 'events')[0]
        pre_spikes_rec = nest.GetStatus(spikedet_pre, 'events')[0]
        post_spikes_rec = nest.GetStatus(spikedet_post, 'events')[0]

        fig, axs = plt.subplots(4)

        axs[0].plot(res['times'], res['v_comp0'], c='r', label='V_m_0')
        axs[1].plot(res['times'], res['w_input1'], c='r', label="weight")
        #axs[1].plot(res['times'], res['pre_trace_input1'], c='b', label="pre_trace")
        #axs[1].plot(res['times'], res['post_trace_input1'], c='g', label="post_trace")
        axs[2].plot(res['times'], res['i_tot_input0'], c='b', label="AMPA")
        axs[2].plot(res['times'], res['i_tot_input1'], c='g', label="AMPA STDP")
        label_set = False
        for spike in pre_spikes_rec['times']:
            if(label_set):
                axs[2].axvline(x=spike, color='purple', linestyle='--', linewidth=1)
            else:
                axs[2].axvline(x=spike, color='purple', linestyle='--', linewidth=1, label="pre syn spikes")
                label_set = True

        label_set = False
        for spike in post_spikes_rec['times']:
            if(label_set):
                axs[2].axvline(x=spike, color='orange', linestyle='--', linewidth=1)
            else:
                axs[2].axvline(x=spike, color='orange', linestyle='--', linewidth=1, label="post syn spikes")
                label_set = True

        axs[3].plot(res['times'], res['pre_trace_input1'], c='b', label="pre_trace")
        axs[3].plot(res['times'], res['post_trace_input1'], c='g', label="post_trace")


        axs[0].set_title('V_m_0')
        axs[1].set_title('weight')
        axs[2].set_title('spikes')
        axs[3].set_title('traces')

        axs[0].legend()
        axs[1].legend()
        axs[2].legend()
        axs[3].legend()

        plt.show()
