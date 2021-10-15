# -*- coding: utf-8 -*-
#
# third_factor_stdp_synapse_test.py
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
sim_ref = False

class NestThirdFactorSTDPSynapseTest(unittest.TestCase):

    neuron_model_name = "iaf_psc_exp_dend_nestml__with_third_factor_stdp_nestml"
    ref_neuron_model_name = "iaf_psc_exp_nestml_non_jit"

    synapse_model_name = "third_factor_stdp_nestml__with_iaf_psc_exp_dend_nestml"
    ref_synapse_model_name = "third_factor_stdp_synapse"

    post_trace_var = "I_dend"#"post_trace_kernel__for_stdp_nestml__X__post_spikes__for_stdp_nestml"

    def setUp(self):
        """Generate the neuron model code"""
        nest_path = nest.ll_api.sli_func("statusdict/prefix ::")

        # generate the "jit" model (co-generated neuron and synapse), that does not rely on ArchivingNode
        to_nest(input_path=["models/neurons/iaf_psc_exp_dend.nestml", "models/synapses/third_factor_stdp_synapse.nestml"],
                target_path="/tmp/nestml-jit",
                logging_level="INFO",
                module_name="nestml_jit_module",
                suffix="_nestml",
                codegen_opts={"neuron_parent_class": "StructuralPlasticityNode",
                              "neuron_parent_class_include": "structural_plasticity_node.h",
                              "neuron_synapse_pairs": [{"neuron": "iaf_psc_exp_dend",
                                                        "synapse": "third_factor_stdp",
                                                        "post_ports": ["post_spikes",
                                                                      ["I_post_dend", "I_dend"]]}]})
        install_nest("/tmp/nestml-jit", nest_path)

    def test_nest_stdp_synapse(self):

        fname_snip = ""

        pre_spike_times = [1., 11., 21.]    # [ms]
        post_spike_times = [6., 16., 26.]  # [ms]

        post_spike_times = np.sort(np.unique(1 + np.round(10 * np.sort(np.abs(np.random.randn(10))))))      # [ms]
        pre_spike_times = np.sort(np.unique(1 + np.round(10 * np.sort(np.abs(np.random.randn(10))))))      # [ms]

        post_spike_times = np.sort(np.unique(1 + np.round(500 * np.sort(np.abs(np.random.randn(500))))))      # [ms]
        pre_spike_times = np.sort(np.unique(1 + np.round(500 * np.sort(np.abs(np.random.randn(500))))))      # [ms]

        self.run_synapse_test(neuron_model_name=self.neuron_model_name,
                              ref_neuron_model_name=self.ref_neuron_model_name,
                              synapse_model_name=self.synapse_model_name,
                              ref_synapse_model_name=self.ref_synapse_model_name,
                              resolution=.5, # [ms]
                              delay=1.5, # [ms]
                              pre_spike_times=pre_spike_times,
                              post_spike_times=post_spike_times,
                              sim_time=400.,
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
        nest.Install("nestml_jit_module")
        nest.Install("nestml_non_jit_module")

        print("Pre spike times: " + str(pre_spike_times))
        print("Post spike times: " + str(post_spike_times))

        nest.set_verbosity("M_WARNING")

        nest.ResetKernel()
        nest.SetKernelStatus({'resolution': resolution})

        wr = nest.Create('weight_recorder')
        wr_ref = nest.Create('weight_recorder')
        nest.CopyModel(synapse_model_name, "stdp_nestml_rec",
                       {"weight_recorder": wr[0], "w": 1., "the_delay": 1., "receptor_type": 0, "lambda": .001})
        if sim_ref:
         nest.CopyModel(ref_synapse_model_name, "stdp_ref_rec",
                       {"weight_recorder": wr_ref[0], "weight": 1., "delay": 1., "receptor_type": 0, "lambda": .001})

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
         mm = nest.Create("multimeter", params={"record_from" : ["V_m", self.post_trace_var]})
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

        t = 0.
        t_hist = []
        if sim_mdl:
         w_hist = []
        if sim_ref:
         w_hist_ref = []
        state = 0
        while t <= sim_time:
            if t > sim_time / 6. and state == 0:
                post_neuron.set({"I_dend": 1.})
                state = 1
            if t > 2 * sim_time / 6 and state == 1:
                post_neuron.set({"I_dend": 1.})
            if t > 2 * sim_time / 3. and state == 1:
                state = 2
            nest.Simulate(resolution)
            t += resolution
            t_hist.append(t)
            if sim_ref:
             w_hist_ref.append(nest.GetStatus(syn_ref)[0]['weight'])
            if sim_mdl:
             w_hist.append(nest.GetStatus(syn)[0]['w'])

        third_factor_trace = nest.GetStatus(mm, "events")[0][self.post_trace_var]
        timevec = nest.GetStatus(mm, "events")[0]["times"]

        if TEST_PLOTS:
            fig, ax = plt.subplots(nrows=2)
            ax1, ax2 = ax

            if sim_mdl:
             V_m = nest.GetStatus(mm, "events")[0]["V_m"]
             ax2.plot(timevec, third_factor_trace, label="I_dend_post")
             ax1.plot(timevec, V_m, alpha=.7, linestyle=":")
            if sim_ref:
             pre_ref_spike_times_ = nest.GetStatus(spikedet_pre_ref, "events")[0]["times"]
             timevec_ = nest.GetStatus(mm_ref, "events")[0]["times"]
             V_m_ = nest.GetStatus(mm_ref, "events")[0]["V_m"]
             ax1.plot(timevec_, V_m_, label="nest ref", alpha=.7)
            ax1.set_ylabel("V_m")

            for _ax in ax:
                _ax.grid(which="major", axis="both")
                _ax.grid(which="minor", axis="x", linestyle=":", alpha=.4)
                #_ax.minorticks_on()
                _ax.set_xlim(0., sim_time)
                _ax.legend()
            fig.savefig("/tmp/stdp_triplet_synapse_test" + fname_snip + "_V_m.png", dpi=300)

        if TEST_PLOTS:
            fig, ax = plt.subplots(nrows=5)
            ax1, ax2, ax3, ax4, ax5 = ax

            if sim_mdl:
             pre_spike_times_ = nest.GetStatus(spikedet_pre, "events")[0]["times"]
             print("Actual pre spike times: "+ str(pre_spike_times_))
            if sim_ref:
             pre_ref_spike_times_ = nest.GetStatus(spikedet_pre_ref, "events")[0]["times"]
             print("Actual pre ref spike times: "+ str(pre_ref_spike_times_))

            if sim_mdl:
             n_spikes = len(pre_spike_times_)
             for i in range(n_spikes):
                ax1.plot(2 * [pre_spike_times_[i] + delay], [0, 1], linewidth=2, color="blue", alpha=.4)

            if sim_mdl:
             post_spike_times_ = nest.GetStatus(spikedet_post, "events")[0]["times"]
             print("Actual post spike times: "+ str(post_spike_times_))
            if sim_ref:
             post_ref_spike_times_ = nest.GetStatus(spikedet_post_ref, "events")[0]["times"]
             print("Actual post ref spike times: "+ str(post_ref_spike_times_))

            if sim_ref:
             n_spikes = len(pre_ref_spike_times_)
             for i in range(n_spikes):
                ax1.plot(2 * [pre_ref_spike_times_[i] + delay], [0, 1], linewidth=2, color="cyan", alpha=.4)
            ax1.set_ylabel("Pre spikes")

            if sim_mdl:
             n_spikes = len(post_spike_times_)
             for i in range(n_spikes):
                if i == 0:
                 _lbl = "nestml"
                else:
                 _lbl = None
                ax[-4].plot(2 * [post_spike_times_[i]], [0, 1], linewidth=2, color="black", alpha=.4, label=_lbl)
            if sim_ref:
             n_spikes = len(post_ref_spike_times_)
             for i in range(n_spikes):
                if i == 0:
                 _lbl = "nest ref"
                else:
                 _lbl = None
                ax[-4].plot(2 * [post_ref_spike_times_[i]], [0, 1], linewidth=2, color="red", alpha=.4, label=_lbl)
            ax[-4].set_ylabel("Post spikes")

            ax[-3].plot(timevec, third_factor_trace)
            ax[-3].set_ylabel("3rd factor")

            ax[-2].plot(t_hist[:-1], np.diff(w_hist), marker="o", label=u"Δw")
            ax[-2].set_ylabel(u"Δw")

            ax[-1].plot(t_hist, w_hist, marker="o")
            if sim_ref:
              ax[-1].plot(t_hist, w_hist_ref, linestyle="--", marker="x", label="ref")
            ax[-1].set_ylabel("w")

            ax[-1].set_xlabel("Time [ms]")
            for _ax in ax:
                if not _ax == ax[-1]:
                    _ax.set_xticklabels([])
                _ax.grid(which="major", axis="both")
                _ax.xaxis.set_major_locator(matplotlib.ticker.FixedLocator(np.arange(0, np.ceil(sim_time))))
                _ax.set_xlim(0., sim_time)
            fig.savefig("/tmp/stdp_third_factor_synapse_test" + fname_snip + ".png", dpi=300)

        # verify
        MAX_ABS_ERROR = 1E-6
        idx = np.where(np.abs(third_factor_trace) < 1E-3)[0]  # find where third_factor_place is (almost) zero
        times_dw_should_be_zero = timevec[idx]
        for time_dw_should_be_zero in times_dw_should_be_zero:
            _idx = np.argmin((time_dw_should_be_zero - np.array(t_hist))**2)
            assert np.abs(np.diff(w_hist)[_idx]) < MAX_ABS_ERROR

        assert np.any(np.abs(np.array(w_hist) - 1) > MAX_ABS_ERROR), "No change in the weight!"
