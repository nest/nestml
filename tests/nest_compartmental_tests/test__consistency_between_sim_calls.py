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

from pynestml.frontend.pynestml_frontend import generate_nest_compartmental_target

# set to `True` to plot simulation traces
TEST_PLOTS = True
try:
    import matplotlib
    import matplotlib.pyplot as plt
except BaseException as e:
    # always set TEST_PLOTS to False if matplotlib can not be imported
    TEST_PLOTS = False

class TestConsistencyBetweenSimCalls(unittest.TestCase):
    @pytest.fixture(scope="module", autouse=True)
    def setup(self):
        tests_path = os.path.realpath(os.path.dirname(__file__))
        neuron_input_path = os.path.join(
            tests_path,
            "resources",
            "cm_default.nestml"
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
                input_path=[neuron_input_path],
                target_path=target_path,
                module_name="cm_module",
                suffix="_nestml",
                logging_level="DEBUG",
                codegen_opts={}
            )

        nest.Install("cm_module.so")

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
        spike_times = [10, 20]

        sim_time = 100
        repeats = 10

        spike_times_tm1 = spike_times
        for i in range(repeats):
            spike_times_t = [n+sim_time for n in spike_times_tm1]
            spike_times_tm1 = spike_times_t

            spike_times = spike_times + spike_times_t


        external_input_pre = nest.Create("spike_generator", params={"spike_times": spike_times})

        neuron = nest.Create('cm_default_nestml')
        print("created")

        params = {'C_m': 10.0, 'g_C': 0.0, 'g_L': 1.5, 'e_L': -70.0, 'gbar_Na': 1.0}
        neuron.compartments = [
            {"parent_idx": -1, "params": params},
            {"parent_idx": 0, "params": {}},
            {"parent_idx": 1, "params": params}
        ]
        print("comps")
        neuron.receptors = [
            {"comp_idx": 0, "receptor_type": "AMPA"},
        ]
        print("syns")
        mm = nest.Create('multimeter', 1, {
            'record_from': ['v_comp0', 'Na0', 'AMPA0'], 'interval': .1})

        nest.Connect(external_input_pre, neuron, "one_to_one", syn_spec={'synapse_model': 'static_synapse', 'weight': 5.0, 'delay': 0.1})
        nest.Connect(mm, neuron)
        print("pre sim")
        nest.Simulate(sim_time)
        for i in range(repeats):
            nest.SetStatus(neuron, {'v_comp0': -70.0, 'm_Na0': 0.01696863, 'h_Na0': 0.83381407, 'Na0': 0.0, 'AMPA0': 0.0, 'g_AMPA0': 0.0})
            nest.Simulate(sim_time)
        res = nest.GetStatus(mm, 'events')[0]

        run_len = list(res['times']).index(sim_time - 0.1) + 1
        res['times'] = np.insert(res['times'], 0, 0.0)
        res['v_comp0'] = np.insert(res['v_comp0'], 0, res['v_comp0'][run_len])
        res['Na0'] = np.insert(res['Na0'], 0, res['Na0'][run_len])
        res['AMPA0'] = np.insert(res['AMPA0'], 0, res['AMPA0'][run_len])

        run_len += 1
        max_deviation = 0.0
        deviations = []

        for i in range(repeats+1):
            for ii in range(run_len):
                deviation = abs(res['v_comp0'][ii+(i*run_len)]-res['v_comp0'][ii])
                deviations.append(deviation)
                if deviation > max_deviation:
                    max_deviation = deviation

        print("max_deviation", max_deviation)

        fig, axs = plt.subplots(4)

        axs[0].plot(res['times'], res['v_comp0'], c='r', label='V_m')
        axs[1].plot(res['times'], res['Na0'], c='b', label="Na")
        axs[2].plot(res['times'], res['AMPA0'], c='b', label="AMPA")
        axs[3].plot(list(res['times']), deviations, c='orange', label="dev")



        axs[0].set_title('V_m')
        axs[1].set_title('Na')
        axs[2].set_title('AMPA')
        axs[3].set_title('dev')

        axs[0].legend()
        axs[1].legend()
        axs[2].legend()
        axs[3].legend()

        plt.savefig("consistency sim calls test.png")

        assert max_deviation < 0.0001, ("There should be no deviation between simulation calls! The maximum deviation in this run is ("+str(max_deviation)+").")
