# -*- coding: utf-8 -*-
#
# stdp_nn_restr_symm_test.py
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

class NestSTDPNNRestrSymmSynapseTest(unittest.TestCase):

    neuron_model_name = "iaf_psc_exp_nestml__with_stdp_nn_restr_symm_nestml"
    ref_neuron_model_name = "iaf_psc_exp_nestml_non_jit"

    synapse_model_name = "stdp_nn_restr_symm_nestml__with_iaf_psc_exp_nestml"
    ref_synapse_model_name = "stdp_nn_restr_synapse"

    def setUp(self):
        """Generate the neuron model code"""
        nest_path = nest.ll_api.sli_func("statusdict/prefix ::")

        # generate the "jit" model (co-generated neuron and synapse), that does not rely on ArchivingNode
        to_nest(input_path=["models/iaf_psc_exp.nestml", "models/stdp_nn_restr_symm.nestml"],
                target_path="/tmp/nestml-jit",
                logging_level="INFO",
                module_name="nestml_jit_module",
                suffix="_nestml",
                codegen_opts={"neuron_parent_class": "StructuralPlasticityNode",
                              "neuron_parent_class_include": "structural_plasticity_node.h",
                              "neuron_synapse_pairs": [{"neuron": "iaf_psc_exp",
                                                        "synapse": "stdp_nn_restr_symm",
                                                        "post_ports": ["post_spikes"]}]})
        install_nest("/tmp/nestml-jit", nest_path)

        # generate the "non-jit" model, that relies on ArchivingNode
        to_nest(input_path="models/iaf_psc_exp.nestml",
                target_path="/tmp/nestml-non-jit",
                logging_level="INFO",
                module_name="nestml_non_jit_module",
                suffix="_nestml_non_jit",
                codegen_opts={"neuron_parent_class": "ArchivingNode",
                              "neuron_parent_class_include": "archiving_node.h"})
        install_nest("/tmp/nestml-non-jit", nest_path)


    def test_stdp_nn_synapse(self):

        fname_snip = ""

        pre_spike_times = [1., 11., 21.]    # [ms]
        post_spike_times = [6., 16., 26.]  # [ms]

        post_spike_times = np.sort(np.unique(1 + np.round(10 * np.sort(np.abs(np.random.randn(10))))))      # [ms]
        pre_spike_times = np.sort(np.unique(1 + np.round(10 * np.sort(np.abs(np.random.randn(10))))))      # [ms]

        post_spike_times = np.sort(np.unique(1 + np.round(100 * np.sort(np.abs(np.random.randn(100))))))      # [ms]
        pre_spike_times = np.sort(np.unique(1 + np.round(100 * np.sort(np.abs(np.random.randn(100))))))      # [ms]

        pre_spike_times = np.array([  2.,   4.,   7.,   8.,  12.,  13.,  19.,  23.,  24.,  28.,  29.,  30.,  33.,  34.,
  35.,  36.,  38.,  40.,  42.,  46.,  51.,  53.,  54.,  55.,  56.,  59.,  63.,  64.,
  65.,  66.,  68.,  72.,  73.,  76.,  79.,  80.,  83.,  84.,  86.,  87.,  90.,  95.,
  99., 100., 103., 104., 105., 111., 112., 126., 131., 133., 134., 139., 147., 150.,
 152., 155., 172., 175., 176., 181., 196., 197., 199., 202., 213., 215., 217., 265.])
        post_spike_times = np.array([  4.,   5.,   6.,   7.,  10.,  11.,  12.,  16.,  17.,  18.,  19.,  20.,  22.,  23.,
  25.,  27.,  29.,  30.,  31.,  32.,  34.,  36.,  37.,  38.,  39.,  42.,  44.,  46.,
  48.,  49.,  50.,  54.,  56.,  57.,  59.,  60.,  61.,  62.,  67.,  74.,  76.,  79.,
  80.,  81.,  83.,  88.,  93.,  94.,  97.,  99., 100., 105., 111., 113., 114., 115.,
 116., 119., 123., 130., 132., 134., 135., 145., 152., 155., 158., 166., 172., 174.,
 188., 194., 202., 245., 249., 289., 454.])

        self.run_synapse_test(neuron_model_name=self.neuron_model_name,
                              ref_neuron_model_name=self.ref_neuron_model_name,
                              synapse_model_name=self.synapse_model_name,
                              ref_synapse_model_name=self.ref_synapse_model_name,
                              resolution=1., # [ms]
                              delay=1., # [ms]
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

        if pre_spike_times is None:
            pre_spike_times = []

        if post_spike_times is None:
            post_spike_times = []

        if sim_time is None:
            sim_time = max(np.amax(pre_spike_times), np.amax(post_spike_times)) + 5 * delay

        nest.set_verbosity("M_ALL")
        nest.ResetKernel()
        if sim_mdl:
         nest.Install("nestml_jit_module")
        if sim_ref:
         nest.Install("nestml_non_jit_module")

        print("Pre spike times: " + str(pre_spike_times))
        print("Post spike times: " + str(post_spike_times))

        nest.set_verbosity("M_WARNING")

        post_weights = {'parrot': []}

        nest.ResetKernel()
        nest.SetKernelStatus({'resolution': resolution})

        wr = nest.Create('weight_recorder')
        wr_ref = nest.Create('weight_recorder')
        if sim_mdl:
         nest.CopyModel(synapse_model_name, "stdp_nestml_rec",
                       {"weight_recorder": wr[0], "w": 1., "the_delay": 1., "receptor_type": 0})
        if sim_ref:
         nest.CopyModel(ref_synapse_model_name, "stdp_ref_rec",
                       {"weight_recorder": wr_ref[0], "weight": 1., "delay": 1., "receptor_type": 0})

        # create spike_generators with these times
        pre_sg = nest.Create("spike_generator",
                             params={"spike_times": pre_spike_times})
        post_sg = nest.Create("spike_generator",
                              params={"spike_times": post_spike_times,
                                      'allow_offgrid_times': True})

        # create parrot neurons and connect spike_generators
        if sim_mdl:
         pre_neuron = nest.Create("parrot_neuron")
         post_neuron = nest.Create(neuron_model_name)

        if sim_ref:
         pre_neuron_ref = nest.Create("parrot_neuron")
         post_neuron_ref = nest.Create(ref_neuron_model_name)

        if sim_mdl:
         spikedet_pre = nest.Create("spike_recorder")
         spikedet_post = nest.Create("spike_recorder")
         mm = nest.Create("multimeter", params={"record_from" : ["V_m", "post_trace__for_stdp_nn_restr_symm_nestml"]})
        if sim_ref:
         spikedet_pre_ref = nest.Create("spike_recorder")
         spikedet_post_ref = nest.Create("spike_recorder")
         mm_ref = nest.Create("multimeter", params={"record_from" : ["V_m"]})


        if sim_mdl:
         nest.Connect(pre_sg, pre_neuron, "one_to_one", syn_spec={"delay": 1.})
         nest.Connect(post_sg, post_neuron, "one_to_one", syn_spec={"delay": 1., "weight": 9999.})
         nest.Connect(pre_neuron, post_neuron, "all_to_all", syn_spec={'synapse_model': 'stdp_nestml_rec'})
         nest.Connect(mm, post_neuron)
         nest.Connect(pre_neuron, spikedet_pre)
         nest.Connect(post_neuron, spikedet_post)
        if sim_ref:
         nest.Connect(pre_sg, pre_neuron_ref, "one_to_one", syn_spec={"delay": 1.})
         nest.Connect(post_sg, post_neuron_ref, "one_to_one", syn_spec={"delay": 1., "weight": 9999.})
         nest.Connect(pre_neuron_ref, post_neuron_ref, "all_to_all", syn_spec={'synapse_model': ref_synapse_model_name})
         nest.Connect(mm_ref, post_neuron_ref)
         nest.Connect(pre_neuron_ref, spikedet_pre_ref)
         nest.Connect(post_neuron_ref, spikedet_post_ref)

        # get STDP synapse and weight before protocol
        if sim_mdl:
         syn = nest.GetConnections(source=pre_neuron, synapse_model="stdp_nestml_rec")
        if sim_ref:
         syn_ref = nest.GetConnections(source=pre_neuron_ref, synapse_model=ref_synapse_model_name)

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
            if sim_ref:
             w_hist_ref.append(nest.GetStatus(syn_ref)[0]['weight'])
            if sim_mdl:
             w_hist.append(nest.GetStatus(syn)[0]['w'])

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
            if sim_mdl:
             ax2.plot(nest.GetStatus(mm, "events")[0]["times"], nest.GetStatus(mm, "events")[0]["post_trace__for_stdp_nn_restr_symm_nestml"], label="nestml post tr")
            ax2.set_ylabel("Post spikes")

            if sim_mdl:
             ax3.plot(t_hist, w_hist, marker="o", label="nestml")
            if sim_ref:
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
            fig.savefig("/tmp/stdp_nn_restr_symm_test" + fname_snip + ".png", dpi=300)

        # verify
        MAX_ABS_ERROR = 1E-6
        assert np.all(np.abs(np.array(w_hist) - np.array(w_hist_ref)) < MAX_ABS_ERROR)
