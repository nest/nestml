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
        neuron_model_name = "iaf_psc_exp_nestml__with_stdp_triplet_nestml"
        #neuron_model_name = "iaf_psc_exp"
        ref_neuron_model_name = "iaf_psc_exp"
        synapse_model_name = "stdp_triplet_nestml__with_iaf_psc_exp_nestml"
        #synapse_model_name = "stdp_nestml"
        ref_synapse_model_name = "stdp_triplet_synapse"
        fname_snip = "dyad_test"

        #post_spike_times = np.arange(1, 20).astype(np.float)
        #pre_spike_times = -2 + np.array([3., 13.])

        #post_spike_times = -2 + np.array([11. ,15., 32.])

        pre_spike_times = [1., 11., 21.]    # [ms]
        post_spike_times = [6., 16., 26.]  # [ms]

        #post_spike_times = np.sort(np.unique(1 + np.round(10 * np.sort(np.abs(np.random.randn(10))))))      # [ms]
        #pre_spike_times = np.sort(np.unique(1 + np.round(10 * np.sort(np.abs(np.random.randn(10))))))      # [ms]

        pre_spike_times = [4., 5., 6., 9., 12., 15., 16., 18.]
        post_spike_times = [6., 11., 14., 17., 20., 23., 27.]

#Actual pre spike times: [ 3.  4.  5.  6.  7.  8. 14. 15.]
#Actual post spike times: [ 4.  7. 10. 13. 16. 19.]

        '''pre_spike_times = np.array([ 14.])
        post_spike_times = np.array([3., 4., 9., 10., 11.])

        post_spike_times = np.sort(np.unique(1 + np.round(10 * np.sort(np.abs(np.random.randn(10))))))      # [ms]
        pre_spike_times = np.sort(np.unique(1 + np.round(10 * np.sort(np.abs(np.random.randn(10))))))      # [ms]

        post_spike_times = np.sort(np.unique(1 + np.round(100 * np.sort(np.abs(np.random.randn(100))))))      # [ms]
        pre_spike_times = np.sort(np.unique(1 + np.round(100 * np.sort(np.abs(np.random.randn(100))))))      # [ms]
        '''
        pre_spike_times=np.array([  2.,   3.,   7.,   8.,   9.,  10.,  12.,  17.,  19.,  21.,  22.,  24.,  25.,  26.,
          28.,  30.,  36.,  37.,  38.,  40.,  43.,  46.,  47.,  48.,  49.,  50.,  51.,  52.,
            53.,  55.,  58.,  59.,  60.,  62.,  64.,  65.,  66.,  67.,  68.,  69.,  71.,  72.,
              76.,  77.,  78.,  82.,  83.,  84.,  85.,  86.,  87.,  88.,  92.,  96.,  99., 105.,
               113., 114., 121., 122., 124., 129., 135., 140., 152., 161., 167., 170., 183., 186.,
                192., 202., 218., 224., 303., 311.])
        post_spike_times = np.array([  2.,   4.,   5.,   8.,   9.,  12.,  13.,  14.,  17.,  18.,  19.,  21.,  24.,  25.,
          26.,  28.,  30.,  32.,  34.,  37.,  38.,  40.,  42.,  44.,  45.,  46.,  49.,  50.,
            51.,  53.,  55.,  56.,  60.,  61.,  67.,  68.,  72.,  73.,  74.,  76.,  77.,  78.,
              79.,  81.,  82.,  84.,  87.,  88.,  93.,  95.,  96.,  98.,  99., 100., 109., 110.,
               111., 115., 116., 118., 120., 121., 124., 125., 127., 128., 140., 144., 149., 150.,
                152., 155., 156., 157., 163., 164., 168., 172., 204., 206., 216., 239., 243.])

        self.run_synapse_test(neuron_model_name=neuron_model_name,
                              ref_neuron_model_name=ref_neuron_model_name,
                              synapse_model_name=synapse_model_name,
                              ref_synapse_model_name=ref_synapse_model_name,
                              resolution=.1, # [ms]
                              delay=1., # [ms]
                              sim_time=20.,
                              pre_spike_times=pre_spike_times,
                              post_spike_times=post_spike_times,
                              fname_snip=fname_snip)

    def run_synapse_test(self, neuron_model_name,
                              ref_neuron_model_name,
                              synapse_model_name,
                              ref_synapse_model_name,
                              resolution=1., # [ms]
                              delay=1., # [ms]
                              sim_time=None,  # if None, computed from pre and post spike times
                              pre_spike_times=None,
                              post_spike_times=None,
                              fname_snip=""):

        syn_opts = {
        'delay': delay,
'tau_minus': 33.7,
'tau_plus': 16.8,
'tau_x': 101.,
'tau_y': 125.,
'A2_plus': 7.5e-10,
'A3_plus': 9.3e-3,
'A2_minus': 7e-3,
'A3_minus': 2.3e-4        }

        nest_syn_params = {'delay': delay,
                           'tau_plus': syn_opts['tau_plus'],
                           'tau_plus_triplet': syn_opts['tau_x'],
                           'Aplus': syn_opts['A2_plus'],
                           'Aplus_triplet': syn_opts['A3_plus'],
                           'Aminus': syn_opts['A2_minus'],
                           'Aminus_triplet': syn_opts['A3_minus']}

        nestml_syn_params = {'the_delay': delay}
        nestml_syn_params.update(syn_opts)
        nestml_syn_params.pop('tau_minus')  # these have been moved to the neuron
        nestml_syn_params.pop('tau_y')

        nestml_neuron_params = {'tau_minus__for_stdp_triplet_nestml': syn_opts['tau_minus'],
                                'tau_y__for_stdp_triplet_nestml': syn_opts['tau_y']}

        nest_neuron_params = {'tau_minus': syn_opts['tau_minus'],
                              'tau_minus_triplet': syn_opts['tau_y']}

        if pre_spike_times is None:
            pre_spike_times = []

        if post_spike_times is None:
            post_spike_times = []

        if sim_time is None:
            sim_time = max(np.amax(pre_spike_times), np.amax(post_spike_times)) + 5 * delay

        nest.set_verbosity("M_ALL")
        nest.ResetKernel()
        #nest.SetKernelStatus({"local_num_threads": 2})
        nest.Install("models_triplet_dyadmodule")

        print("Pre spike times: " + str(pre_spike_times))
        print("Post spike times: " + str(post_spike_times))

        nest.set_verbosity("M_WARNING")

        post_weights = {'parrot': []}

        nest.SetKernelStatus({'resolution': resolution})

        wr = nest.Create('weight_recorder')
        wr_ref = nest.Create('weight_recorder')
        _syn_nestml_model_params = {"weight_recorder": wr[0], "w": 1., "receptor_type": 0}
        _syn_nestml_model_params.update(nestml_syn_params)
        nest.CopyModel(synapse_model_name, "stdp_nestml_rec", _syn_nestml_model_params)

        _syn_nest_model_params = {"weight_recorder": wr_ref[0], "weight": 1., "receptor_type": 0}
        _syn_nest_model_params.update(nest_syn_params)
        nest.CopyModel(ref_synapse_model_name, "stdp_ref_rec", _syn_nest_model_params)

        # create spike_generators with these times
        pre_sg = nest.Create("spike_generator",
                             params={"spike_times": pre_spike_times})
        post_sg = nest.Create("spike_generator",
                              params={"spike_times": post_spike_times,
                                      'allow_offgrid_times': True})

        # create parrot neurons and connect spike_generators
        if sim_mdl:
         pre_neuron = nest.Create("parrot_neuron")
         post_neuron = nest.Create(neuron_model_name, params=nestml_neuron_params)

        if sim_ref:
         pre_neuron_ref = nest.Create("parrot_neuron")
         post_neuron_ref = nest.Create(ref_neuron_model_name, params=nest_neuron_params)

        if sim_mdl:
         spikedet_pre = nest.Create("spike_recorder")
         spikedet_post = nest.Create("spike_recorder")
         mm = nest.Create("multimeter", params={"record_from" : ["V_m", "tr_o1_kernel__for_stdp_triplet_nestml__X__post_spikes__for_stdp_triplet_nestml", "tr_o2_kernel__for_stdp_triplet_nestml__X__post_spikes__for_stdp_triplet_nestml"],
                                                "interval": resolution})
        if sim_ref:
         spikedet_pre_ref = nest.Create("spike_recorder")
         spikedet_post_ref = nest.Create("spike_recorder")
         mm_ref = nest.Create("multimeter", params={"record_from" : ["V_m"],
                                                    "interval": resolution})

        if sim_mdl:
         nest.Connect(pre_sg, pre_neuron, "one_to_one", syn_spec={"delay": 1.})
         nest.Connect(post_sg, post_neuron, "one_to_one", syn_spec={"delay": 1., "weight": 9999.})
         nest.Connect(pre_neuron, post_neuron, "one_to_one", syn_spec={'synapse_model': 'stdp_nestml_rec'})
         nest.Connect(mm, post_neuron)
         nest.Connect(pre_neuron, spikedet_pre)
         nest.Connect(post_neuron, spikedet_post)
        if sim_ref:
         nest.Connect(pre_sg, pre_neuron_ref, "one_to_one", syn_spec={"delay": 1.})
         nest.Connect(post_sg, post_neuron_ref, "one_to_one", syn_spec={"delay": 1., "weight": 9999.})
         nest.Connect(pre_neuron_ref, post_neuron_ref, "one_to_one", syn_spec={'synapse_model': 'stdp_ref_rec'})
         nest.Connect(pre_neuron_ref, spikedet_pre_ref)
         nest.Connect(post_neuron_ref, spikedet_post_ref)
         nest.Connect(mm_ref, post_neuron_ref)

        # get STDP synapse and weight before protocol
        if sim_mdl:
         syn = nest.GetConnections(source=pre_neuron, synapse_model="stdp_nestml_rec")
        if sim_ref:
         syn_ref = nest.GetConnections(source=pre_neuron_ref, synapse_model="stdp_ref_rec")

        n_steps = int(np.ceil(sim_time / resolution)) + 1
        t = 0.
        t_hist = []
        if sim_mdl:
         w_hist = []
        if sim_ref:
         w_hist_ref = []
        while t <= sim_time:
            nest.Simulate(resolution)
            t += resolution
            t_hist.append(t)
            if sim_ref and nest.GetStatus(syn_ref):
             w_hist_ref.append(nest.GetStatus(syn_ref)[0]['weight'])
            if sim_mdl and nest.GetStatus(syn):
             w_hist.append(nest.GetStatus(syn)[0]['w'])

        # plot
        if TEST_PLOTS:
            fig, ax = plt.subplots(nrows=2)
            ax1, ax2 = ax

            if sim_mdl:
             timevec = nest.GetStatus(mm, "events")[0]["times"]
             V_m = nest.GetStatus(mm, "events")[0]["V_m"]
             ax2.plot(timevec, nest.GetStatus(mm, "events")[0]["tr_o1_kernel__for_stdp_triplet_nestml__X__post_spikes__for_stdp_triplet_nestml"], label="post_tr nestml")
             ax2.plot(timevec, nest.GetStatus(mm, "events")[0]["tr_o2_kernel__for_stdp_triplet_nestml__X__post_spikes__for_stdp_triplet_nestml"], label="post_tr nestml")
             ax1.plot(timevec, V_m, label="nestml")
            if sim_ref:
             pre_ref_spike_times_ = nest.GetStatus(spikedet_pre_ref, "events")[0]["times"]
             timevec = nest.GetStatus(mm_ref, "events")[0]["times"]
             V_m = nest.GetStatus(mm_ref, "events")[0]["V_m"]
             ax1.plot(timevec, V_m, label="nest ref")
            ax1.set_ylabel("V_m")

            for _ax in ax:
                _ax.grid(which="major", axis="both")
                _ax.grid(which="minor", axis="x", linestyle=":", alpha=.4)
                #_ax.minorticks_on()
                _ax.set_xlim(0., sim_time)
                _ax.legend()
            fig.savefig("/tmp/stdp_triplet_test" + fname_snip + "_V_m.png", dpi=300)

        # plot
        if TEST_PLOTS:
            fig, ax = plt.subplots(nrows=3)
            ax1, ax2, ax3 = ax

            if sim_mdl:
             pre_spike_times_ = nest.GetStatus(spikedet_pre, "events")[0]["times"]
             print("Actual pre spike times: "+ str(pre_spike_times_))
            if sim_ref:
             pre_ref_spike_times_ = nest.GetStatus(spikedet_pre_ref, "events")[0]["times"]
             print("Actual pre ref spike times: "+ str(pre_ref_spike_times_))

            if sim_mdl:
             n_spikes = len(pre_spike_times_)
             for i in range(n_spikes):
                if i == 0:
                 _lbl = "nestml"
                else:
                 _lbl = None
                ax1.plot(2 * [pre_spike_times_[i] + delay], [0, 1], linewidth=2, color="blue", alpha=.4,label=_lbl)

            if sim_mdl:
             post_spike_times_ = nest.GetStatus(spikedet_post, "events")[0]["times"]
             print("Actual post spike times: "+ str(post_spike_times_))
            if sim_ref:
             post_ref_spike_times_ = nest.GetStatus(spikedet_post_ref, "events")[0]["times"]
             print("Actual post ref spike times: "+ str(post_ref_spike_times_))

            if sim_ref:
             n_spikes = len(pre_ref_spike_times_)
             for i in range(n_spikes):
                if i == 0:
                 _lbl = "nest ref"
                else:
                 _lbl = None
                ax1.plot(2 * [pre_ref_spike_times_[i] + delay], [0, 1], linewidth=2, color="cyan",label=_lbl, alpha=.4)
            ax1.set_ylabel("Pre spikes")

            if sim_mdl:
             n_spikes = len(post_spike_times_)
             for i in range(n_spikes):
                if i == 0:
                 _lbl = "nestml"
                else:
                 _lbl = None
                ax2.plot(2 * [post_spike_times_[i]], [0, 1], linewidth=2, color="black", alpha=.4, label=_lbl)
            if sim_ref:
             n_spikes = len(post_ref_spike_times_)
             for i in range(n_spikes):
                if i == 0:
                 _lbl = "nest ref"
                else:
                 _lbl = None
                ax2.plot(2 * [post_ref_spike_times_[i]], [0, 1], linewidth=2, color="red", alpha=.4, label=_lbl)
            ax2.plot(timevec, nest.GetStatus(mm, "events")[0]["tr_o1_kernel__for_stdp_triplet_nestml__X__post_spikes__for_stdp_triplet_nestml"], label="nestml post tr")
            ax2.set_ylabel("Post spikes")

            if sim_mdl and w_hist:
             ax3.plot(t_hist, w_hist, marker="o", label="nestml")
            if sim_ref and w_hist_ref:
             ax3.plot(t_hist, w_hist_ref, linestyle="--", marker="x", label="ref")

            ax3.set_xlabel("Time [ms]")
            ax3.set_ylabel("w")
            for _ax in ax:
                _ax.grid(which="major", axis="both")
                _ax.xaxis.set_major_locator(matplotlib.ticker.FixedLocator(np.arange(0, np.ceil(sim_time))))
                #_ax.grid(which="minor", axis="x", linestyle=":", alpha=.4)
                #_ax.minorticks_on()
                _ax.set_xlim(0., sim_time)
                _ax.legend()
            fig.savefig("/tmp/stdp_triplet_test" + fname_snip + ".png", dpi=300)


        # verify
        MAX_ABS_ERROR = 1E-6
        assert np.all(np.abs(np.array(w_hist) - np.array(w_hist_ref)) < MAX_ABS_ERROR)


