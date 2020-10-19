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
    import matplotlib.pyplot as plt
    TEST_PLOTS = True
except:
    TEST_PLOTS = False



class NestSTDPSynapseTest(unittest.TestCase):

    def test_nest_stdp_synapse(self):

        neuron_model_name = "iaf_psc_exp_nestml__with_stdp_nestml"
        synapse_model_name = "stdp_nestml__with_iaf_psc_exp_nestml"
        fname_snip = "dyad_test"

        nest.set_verbosity("M_ALL")

        nest.ResetKernel()
        nest.Install("models_for_dyadmodule")

        # simulation parameters
        resolution = 1.	 # [ms]
        delay = 1.  # [ms]

        pre_spike_times = [3., 5., 7., 11., 15., 17., 20., 21., 22., 23., 26., 28.]       # [ms]
        post_spike_times = [6., 8., 10., 13.]
        post_spike_times = np.sort(np.unique(1 + np.round(10 * np.sort(np.abs(np.random.randn(10))))))      # [ms]

        print("Pre spike times: " + str(pre_spike_times))
        print("Post spike times: " + str(post_spike_times))

        nest.set_verbosity("M_WARNING")

        post_weights = {'parrot': []}

        nest.ResetKernel()
        nest.SetKernelStatus({'resolution': resolution})

        wr = nest.Create('weight_recorder')
        wr_ref = nest.Create('weight_recorder')
        nest.CopyModel(synapse_model_name, "stdp_nestml_rec",
                    {"weight_recorder": wr[0], "w": 1., "the_delay" : 1., "receptor_type" : 0})

        # create spike_generators with these times
        pre_sg = nest.Create("spike_generator",
                            params={"spike_times": pre_spike_times})
        post_sg = nest.Create("spike_generator",
                            params={"spike_times": post_spike_times,
                                    'allow_offgrid_times': True})

        # create parrot neurons and connect spike_generators
        pre_neuron = nest.Create("parrot_neuron")
        post_neuron = nest.Create(neuron_model_name)
        #mm = nest.Create("multimeter", params={"record_from" : ["V_m"], 'interval' : .1, 'withtime': True })
        spikedet_pre = nest.Create("spike_recorder")
        spikedet_post = nest.Create("spike_recorder")

        nest.Connect(pre_sg, pre_neuron, "one_to_one", syn_spec={"delay": 1.})
        nest.Connect(post_sg, post_neuron, "one_to_one", syn_spec={"delay": 1., "weight": 9999.})
        nest.Connect(pre_neuron, post_neuron, "all_to_all", syn_spec={'synapse_model': 'stdp_nestml_rec'})

        nest.Connect(pre_neuron, spikedet_pre)
        nest.Connect(post_neuron, spikedet_post)

        # get STDP synapse and weight before protocol
        syn = nest.GetConnections(source=pre_neuron, synapse_model="stdp_nestml_rec")

        sim_time = 20. #np.amax(pre_spike_times) + 5 * delay
        n_steps = int(np.ceil(sim_time / resolution)) + 1
        t = 0.
        t_hist = []
        w_hist = []
        w_hist_ref = []
        while t <= sim_time:
            nest.Simulate(resolution)
            t += resolution
            t_hist.append(t)
            #w_hist_ref.append(nest.GetStatus(syn_ref)[0]['weight'])
            #w_hist_ref.append(nest.GetStatus(syn)[0]['weight'])
            w_hist.append(nest.GetStatus(syn)[0]['w'])
            w_hist_ref.append(nest.GetStatus(syn)[0]['w'])      # XXX


        # verify

        MAX_ABS_ERROR = 1E-6
        #assert np.all(np.abs(np.array(w_hist) - np.array(w_hist_ref)) < MAX_ABS_ERROR)


        # plot

        if TEST_PLOTS:
            fig, ax = plt.subplots(nrows=3)
            ax1, ax3, ax2 = ax

            pre_spike_times_ = nest.GetStatus(spikedet_pre, "events")[0]["times"]
            n_spikes = len(pre_spike_times_)
            for i in range(n_spikes):
                ax1.plot(2 * [pre_spike_times_[i] + delay], [0, 1], linewidth=2, color="blue", alpha=.4)

            post_spike_times_ = nest.GetStatus(spikedet_post, "events")[0]["times"]
            n_spikes = len(post_spike_times_)
            for i in range(n_spikes):
                ax3.plot(2 * [post_spike_times_[i]], [0, 1], linewidth=2, color="red", alpha=.4)

            ax2.plot(t_hist, w_hist, marker="o", label="nestml")
            ax2.plot(t_hist, w_hist_ref, linestyle="--", marker="x", label="ref")
            #ax2.plot(wr_weights)

            ax2.set_xlabel("Time [ms]")
            ax1.set_ylabel("Pre spikes")
            ax3.set_ylabel("Post spikes")
            ax2.set_ylabel("w")
            ax2.legend()
            for _ax in ax:
                _ax.grid(which="major", axis="both")
                _ax.grid(which="minor", axis="x", linestyle=":", alpha=.4)
                _ax.minorticks_on()
                _ax.set_xlim(0., sim_time)
            fig.savefig("/tmp/stdp_synapse_test" + fname_snip + ".png", dpi=300)



