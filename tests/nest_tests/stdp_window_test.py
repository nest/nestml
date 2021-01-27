# -*- coding: utf-8 -*-
#
# stdp_synapse_test.py
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

import nest
import numpy as np
import os
import unittest
from pynestml.frontend.pynestml_frontend import to_nest, install_nest

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.ticker
    import matplotlib.pyplot as plt
    TEST_PLOTS = True
except Exception:
    TEST_PLOTS = False


sim_mdl = True
sim_ref = True

class NestSTDPSynapseTest(unittest.TestCase):

    def test_nest_stdp_synapse(self):
        #neuron_model_name = "iaf_psc_exp_nestml__with_stdp_nestml"
        neuron_model_name = "iaf_psc_exp"
        #synapse_model_name = "stdp_nestml__with_iaf_psc_exp_nestml"
        synapse_model_name = "stdp_synapse"
        fname_snip = "stdp_window_test"

        sim_time = 1000.  # [ms]
        pre_spike_time = 100. #sim_time / 2  # [ms]

        # plot
        if TEST_PLOTS:
            fig, ax = plt.subplots()

        dt_vec = []
        dw_vec = []
        for post_spike_time in np.linspace(1 + .05 * 2 * pre_spike_time, .95 * 2 * pre_spike_time - 1, 111):
            dt, dw = self.run_stdp_network(pre_spike_time, post_spike_time,
                              neuron_model_name,
                              synapse_model_name,
                              resolution=1., # [ms]
                              delay=10., # [ms]
                              sim_time=sim_time,  # if None, computed from pre and post spike times
                              fname_snip=fname_snip)
            dt_vec.append(dt)
            dw_vec.append(dw)


        # plot
        if TEST_PLOTS:
            ax.scatter(dt_vec, dw_vec)
            ax.set_xlabel(r"t_post - t_pre")
            ax.set_ylabel(r"$\Delta w$")

            for _ax in [ax]:
                _ax.grid(which="major", axis="both")
                _ax.grid(which="minor", axis="x", linestyle=":", alpha=.4)
                #_ax.minorticks_on()
                #_ax.set_xlim(0., sim_time)
            fig.savefig("/tmp/stdp_synapse_test" + fname_snip + "_window.png", dpi=300)


    def run_stdp_network(self, pre_spike_time, post_spike_time,
                              neuron_model_name,
                              synapse_model_name,
                              resolution=1., # [ms]
                              delay=1., # [ms]
                              sim_time=None,  # if None, computed from pre and post spike times
                              fname_snip=""):
        nest.ResetKernel()

        print("Pre spike time: " + str(pre_spike_time))
        print("Post spike time: " + str(post_spike_time))

        #nest.set_verbosity("M_WARNING")
        nest.set_verbosity("M_ALL")
        #nest.Install("models_for_dyadmodule")

        nest.ResetKernel()
        nest.SetKernelStatus({'resolution': resolution})

        wr = nest.Create('weight_recorder')
        nest.CopyModel(synapse_model_name, "stdp_nestml_rec",
                       {"weight_recorder": wr[0], "weight": 1., "delay": delay, "receptor_type": 0, "mu_minus": 0., "mu_plus": 0.})

        # create spike_generators with these times
        pre_sg = nest.Create("spike_generator",
                             params={"spike_times": [pre_spike_time, sim_time - 10.]})
        post_sg = nest.Create("spike_generator",
                              params={"spike_times": [post_spike_time],
                                      'allow_offgrid_times': True})

        # create parrot neurons and connect spike_generators
        pre_neuron = nest.Create("parrot_neuron")
        post_neuron = nest.Create(neuron_model_name)

        spikedet_pre = nest.Create("spike_recorder")
        spikedet_post = nest.Create("spike_recorder")
        #mm = nest.Create("multimeter", params={"record_from" : ["V_m"]})

        nest.Connect(pre_sg, pre_neuron, "one_to_one", syn_spec={"delay": 1.})
        nest.Connect(post_sg, post_neuron, "one_to_one", syn_spec={"delay": 1., "weight": 9999.})
        nest.Connect(pre_neuron, post_neuron, "all_to_all", syn_spec={'synapse_model': 'stdp_nestml_rec'})
        #nest.Connect(mm, post_neuron)

        nest.Connect(pre_neuron, spikedet_pre)
        nest.Connect(post_neuron, spikedet_post)

        # get STDP synapse and weight before protocol
        syn = nest.GetConnections(source=pre_neuron, synapse_model="stdp_nestml_rec")

        initial_weight = nest.GetStatus(syn)[0]['weight']
        nest.Simulate(sim_time)
        updated_weight = nest.GetStatus(syn)[0]['weight']

        actual_t_pre_sp = nest.GetStatus(spikedet_pre)[0]["events"]["times"][0]
        actual_t_post_sp = nest.GetStatus(spikedet_post)[0]["events"]["times"][0]

        dt = actual_t_post_sp - actual_t_pre_sp
        dw = updated_weight - initial_weight
        print("Returning " + str((dt, dw)))

        return dt, dw


