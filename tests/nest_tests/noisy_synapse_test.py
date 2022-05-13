# -*- coding: utf-8 -*-
#
# noisy_synapse_test.py
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
from pynestml.frontend.pynestml_frontend import generate_nest_target

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.ticker
    import matplotlib.pyplot as plt
    TEST_PLOTS = True
except Exception:
    TEST_PLOTS = False


class NoisySynapseTest(unittest.TestCase):

    neuron_model_name = "iaf_psc_delta"
    synapse_model_name = "noisy_synapse_nestml"

    def setUp(self):
        """Generate and build the model code"""
        generate_nest_target(input_path="models/synapses/noisy_synapse.nestml",
                             target_path="/tmp/nestml-noisy-synapse",
                             logging_level="INFO",
                             module_name="nestml_noisy_synapse_module",
                             suffix="_nestml")

    def test_noisy_noisy_synapse_synapse(self):

        fname_snip = "noisy_synapse_test"

        pre_spike_times = np.linspace(1., 100., 10)

        self.run_synapse_test(neuron_model_name=self.neuron_model_name,
                              synapse_model_name=self.synapse_model_name,
                              resolution=.1,  # [ms]
                              delay=1.,  # [ms]
                              pre_spike_times=pre_spike_times,
                              fname_snip=fname_snip)

    def run_synapse_test(self, neuron_model_name,
                         synapse_model_name,
                         resolution=.1,  # [ms]
                         delay=1.,  # [ms]
                         sim_time=None,  # if None, computed from pre and post spike times
                         pre_spike_times=None,
                         fname_snip=""):

        if pre_spike_times is None:
            pre_spike_times = []

        if sim_time is None:
            sim_time = np.amax(pre_spike_times) + 5 * delay

        nest.set_verbosity("M_ALL")
        nest.ResetKernel()
        nest.Install("nestml_noisy_synapse_module")

        print("Pre spike times: " + str(pre_spike_times))

        nest.set_verbosity("M_WARNING")

        post_weights = {'parrot': []}

        nest.ResetKernel()
        nest.SetKernelStatus({'resolution': resolution})

        wr = nest.Create('weight_recorder')
        nest.CopyModel(synapse_model_name, "noisy_synapse_nestml_rec",
                       {"weight_recorder": wr[0], "w": 1., "the_delay": 1., "receptor_type": 0})

        # create spike_generators with these times
        pre_sg = nest.Create("spike_generator",
                             params={"spike_times": pre_spike_times})

        # create parrot neurons and connect spike_generators
        pre_neuron = nest.Create("parrot_neuron")
        post_neuron = nest.Create(neuron_model_name, {"tau_m": 2.})

        spikedet_pre = nest.Create("spike_recorder")
        mm = nest.Create("multimeter", params={"record_from": ["V_m"]})

        nest.Connect(pre_sg, pre_neuron, "one_to_one", syn_spec={"delay": 1.})
        nest.Connect(pre_neuron, post_neuron, "all_to_all", syn_spec={'synapse_model': 'noisy_synapse_nestml_rec'})
        nest.Connect(mm, post_neuron)
        nest.Connect(pre_neuron, spikedet_pre)

        # get noisy_synapse synapse and weight before protocol
        syn = nest.GetConnections(source=pre_neuron, synapse_model="noisy_synapse_nestml_rec")

        n_steps = int(np.ceil(sim_time / resolution)) + 1
        t = 0.
        t_hist = []
        w_hist = []
        while t <= sim_time:
            nest.Simulate(resolution)
            t += resolution
            t_hist.append(t)
            w_hist.append(nest.GetStatus(syn)[0]['w'])

        # plot
        if TEST_PLOTS:
            fig, ax = plt.subplots(nrows=3)

            pre_spike_times_ = nest.GetStatus(spikedet_pre, "events")[0]["times"]
            print("Actual pre spike times: " + str(pre_spike_times_))

            n_spikes = len(pre_spike_times_)
            for i in range(n_spikes):
                if i == 0:
                    _lbl = "nestml"
                else:
                    _lbl = None
                ax[0].plot(2 * [pre_spike_times_[i] + delay], [0, 1], linewidth=2, color="blue", alpha=.4, label=_lbl)

            timevec = nest.GetStatus(mm, "events")[0]["times"]
            V_m = nest.GetStatus(mm, "events")[0]["V_m"]
            ax[1].plot(timevec, V_m, label="nestml", alpha=.7, linestyle=":")
            ax[1].set_ylabel("V_m")

            ax[2].plot(wr.get('events')['times'], wr.get('events')['weights'], marker="o", label="w")

            for _ax in ax:
                _ax.grid(which="major", axis="both")
                _ax.grid(which="minor", axis="x", linestyle=":", alpha=.4)
                # _ax.minorticks_on()
                _ax.set_xlim(0., sim_time)
                _ax.legend()

            fig.savefig("/tmp/noisy_synapse_synapse_test" + fname_snip + "_V_m.png", dpi=300)
