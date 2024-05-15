# -*- coding: utf-8 -*-
#
# stdp_neuromod_test.py
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

import numpy as np
import os
import pytest
import unittest

import nest

from pynestml.codegeneration.nest_tools import NESTTools
from pynestml.frontend.pynestml_frontend import generate_nest_target

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.ticker
    import matplotlib.pyplot as plt
    TEST_PLOTS = True
except Exception:
    TEST_PLOTS = False

sim_mdl = True
sim_ref = True


class NestSTDPNeuromodTest(unittest.TestCase):
    r"""
    Test the neuromodulated (for instance, dopamine-modulated) synapse, by numerically comparing it to the NEST "stdp_dopamine" synapse in a representative simulation run.
    """

    neuron_model_name = "iaf_psc_exp_neuron_nestml__with_neuromodulated_stdp_synapse_nestml"
    synapse_model_name = "neuromodulated_stdp_synapse_nestml__with_iaf_psc_exp_neuron_nestml"

    ref_neuron_model_name = "iaf_psc_exp_neuron_nestml_non_jit"
    ref_synapse_model_name = "stdp_dopamine_synapse"

    def setUp(self):
        r"""generate code for neuron and synapse and build NEST user module"""
        files = [os.path.join("models", "neurons", "iaf_psc_exp_neuron.nestml"),
                 os.path.join("models", "synapses", "neuromodulated_stdp_synapse.nestml")]
        input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, s))) for s in files]
        generate_nest_target(input_path=input_path,
                             target_path="/tmp/nestml-jit",
                             logging_level="INFO",
                             module_name="nestml_jit_module",
                             suffix="_nestml",
                             codegen_opts={"neuron_parent_class": "StructuralPlasticityNode",
                                           "neuron_parent_class_include": "structural_plasticity_node.h",
                                           "neuron_synapse_pairs": [{"neuron": "iaf_psc_exp_neuron",
                                                                     "synapse": "neuromodulated_stdp_synapse",
                                                                     "post_ports": ["post_spikes"],
                                                                     "vt_ports": ["mod_spikes"]}]})

        generate_nest_target(input_path=os.path.realpath(os.path.join(os.path.dirname(__file__),
                                                                      os.path.join(os.pardir, os.pardir, "models", "neurons", "iaf_psc_exp_neuron.nestml"))),
                             target_path="/tmp/nestml-non-jit",
                             logging_level="INFO",
                             module_name="nestml_non_jit_module",
                             suffix="_nestml_non_jit",
                             codegen_opts={"neuron_parent_class": "ArchivingNode",
                                           "neuron_parent_class_include": "archiving_node.h"})

    @pytest.mark.skipif(NESTTools.detect_nest_version().startswith("v2"),
                        reason="This test does not support NEST 2")
    def test_nest_stdp_synapse(self):

        fname_snip = ""

        pre_spike_times = [1., 11., 21.]    # [ms]
        post_spike_times = [6., 16., 26.]  # [ms]

        vt_spike_times = [14., 23.]    # [ms]

        self.run_synapse_test(neuron_model_name=self.neuron_model_name,
                              ref_neuron_model_name=self.ref_neuron_model_name,
                              synapse_model_name=self.synapse_model_name,
                              ref_synapse_model_name=self.ref_synapse_model_name,
                              resolution=.1,  # [ms]
                              delay=1.,  # [ms]
                              pre_spike_times=pre_spike_times,
                              post_spike_times=post_spike_times,
                              vt_spike_times=vt_spike_times,
                              fname_snip=fname_snip)

    def run_synapse_test(self, neuron_model_name,
                         ref_neuron_model_name,
                         synapse_model_name,
                         ref_synapse_model_name,
                         resolution=1.,  # [ms]
                         delay=1.,  # [ms]
                         sim_time=None,  # if None, computed from pre and post spike times
                         pre_spike_times=None,
                         post_spike_times=None,
                         vt_spike_times=None,
                         fname_snip=""):

        if pre_spike_times is None:
            pre_spike_times = []

        if post_spike_times is None:
            post_spike_times = []

        if vt_spike_times is None:
            vt_spike_times = []

        if sim_time is None:
            sim_time = max(np.amax(pre_spike_times, initial=0.), np.amax(
                post_spike_times, initial=0.), np.amax(vt_spike_times, initial=0.)) + 5 * delay

        nest.ResetKernel()
        # nest.set_verbosity("M_ALL")
        nest.set_verbosity("M_ERROR")
        nest.SetKernelStatus({"resolution": resolution})
        nest.Install("nestml_jit_module")
        nest.Install("nestml_non_jit_module")

        print("Pre spike times: " + str(pre_spike_times))
        print("Post spike times: " + str(post_spike_times))
        print("VT spike times: " + str(vt_spike_times))

        # create spike_generators with these times
        pre_sg = nest.Create("spike_generator",
                             params={"spike_times": pre_spike_times})
        post_sg = nest.Create("spike_generator",
                              params={"spike_times": post_spike_times,
                                      "allow_offgrid_times": True})
        vt_sg = nest.Create("spike_generator",
                            params={"spike_times": vt_spike_times,
                                    "allow_offgrid_times": True})

        # create  volume transmitter
        vt = nest.Create("volume_transmitter")
        vt_parrot = nest.Create("parrot_neuron")
        nest.Connect(vt_sg, vt_parrot)
        nest.Connect(vt_parrot, vt, syn_spec={"synapse_model": "static_synapse",
                                              "weight": 1.,
                                              "delay": 1.})   # delay is ignored?!

        # set up custom synapse models
        wr = nest.Create("weight_recorder")
        wr_ref = nest.Create('weight_recorder')
        nest.CopyModel(synapse_model_name, "stdp_nestml_rec",
                       {"weight_recorder": wr[0], "w": 1., "d": delay, "receptor_type": 0,
                        "volume_transmitter": vt})
        nest.CopyModel(ref_synapse_model_name, "stdp_ref_rec",
                       {"weight_recorder": wr_ref[0], "weight": 1., "delay": delay, "receptor_type": 0,
                        "volume_transmitter": vt})

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
            spikedet_vt = nest.Create("spike_recorder")
            mm = nest.Create("multimeter", params={"record_from": ["V_m", "post_tr__for_neuromodulated_stdp_synapse_nestml"]})

        if sim_ref:
            spikedet_pre_ref = nest.Create("spike_recorder")
            spikedet_post_ref = nest.Create("spike_recorder")
            mm_ref = nest.Create("multimeter", params={"record_from": ["V_m"]})

        if sim_mdl:
            nest.Connect(pre_sg, pre_neuron, "one_to_one", syn_spec={"delay": 1.})
            nest.Connect(post_sg, post_neuron, "one_to_one", syn_spec={"delay": 1., "weight": 9999.})
            nest.Connect(pre_neuron, post_neuron, "all_to_all", syn_spec={"synapse_model": "stdp_nestml_rec"})
            nest.Connect(mm, post_neuron)
            nest.Connect(pre_neuron, spikedet_pre)
            nest.Connect(post_neuron, spikedet_post)
            nest.Connect(vt_parrot, spikedet_vt)
        if sim_ref:
            nest.Connect(pre_sg, pre_neuron_ref, "one_to_one", syn_spec={"delay": 1.})
            nest.Connect(post_sg, post_neuron_ref, "one_to_one", syn_spec={"delay": 1., "weight": 9999.})
            nest.Connect(pre_neuron_ref, post_neuron_ref, "all_to_all", syn_spec={"synapse_model": "stdp_ref_rec"})
            nest.Connect(mm_ref, post_neuron_ref)
            nest.Connect(pre_neuron_ref, spikedet_pre_ref)
            nest.Connect(post_neuron_ref, spikedet_post_ref)

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
            if sim_ref:
                w_hist_ref.append(nest.GetStatus(syn_ref)[0]["weight"])
            if sim_mdl:
                w_hist.append(nest.GetStatus(syn)[0]["w"])

        # plot
        if TEST_PLOTS:
            fig, ax = plt.subplots(nrows=2)
            ax1, ax2 = ax

            if sim_mdl:
                timevec = nest.GetStatus(mm, "events")[0]["times"]
                V_m = nest.GetStatus(mm, "events")[0]["V_m"]
                ax2.plot(timevec, nest.GetStatus(mm, "events")[
                         0]["post_tr__for_neuromodulated_stdp_synapse_nestml"], label="post_tr nestml")
                ax1.plot(timevec, V_m, label="nestml", alpha=.7, linestyle=":")
            if sim_ref:
                pre_ref_spike_times_ = nest.GetStatus(spikedet_pre_ref, "events")[0]["times"]
                timevec = nest.GetStatus(mm_ref, "events")[0]["times"]
                V_m = nest.GetStatus(mm_ref, "events")[0]["V_m"]
                ax1.plot(timevec, V_m, label="nest ref", alpha=.7)
            ax1.set_ylabel("V_m")

            for _ax in ax:
                _ax.grid(which="major", axis="both")
                _ax.grid(which="minor", axis="x", linestyle=":", alpha=.4)
                # _ax.minorticks_on()
                _ax.set_xlim(0., sim_time)
                _ax.legend()
            fig.savefig("/tmp/stdp_synapse_test" + fname_snip + "_V_m.png", dpi=300)

        # plot
        if TEST_PLOTS:
            fig, ax = plt.subplots(nrows=4)
            ax1, ax2, ax3, ax4 = ax

            if sim_mdl:
                pre_spike_times_ = nest.GetStatus(spikedet_pre, "events")[0]["times"]
                print("Actual pre spike times: " + str(pre_spike_times_))
            if sim_ref:
                pre_ref_spike_times_ = nest.GetStatus(spikedet_pre_ref, "events")[0]["times"]
                print("Actual pre ref spike times: " + str(pre_ref_spike_times_))

            if sim_mdl:
                n_spikes = len(pre_spike_times_)
                for i in range(n_spikes):
                    if i == 0:
                        _lbl = "nestml"
                    else:
                        _lbl = None
                    ax1.plot(2 * [pre_spike_times_[i] + delay], [0, 1], linewidth=2, color="blue", alpha=.4, label=_lbl)

            if sim_mdl:
                post_spike_times_ = nest.GetStatus(spikedet_post, "events")[0]["times"]
                print("Actual post spike times: " + str(post_spike_times_))
            if sim_ref:
                post_ref_spike_times_ = nest.GetStatus(spikedet_post_ref, "events")[0]["times"]
                print("Actual post ref spike times: " + str(post_ref_spike_times_))

            if sim_ref:
                n_spikes = len(pre_ref_spike_times_)
                for i in range(n_spikes):
                    if i == 0:
                        _lbl = "nest ref"
                    else:
                        _lbl = None
                    ax1.plot(2 * [pre_ref_spike_times_[i] + delay], [0, 1],
                             linewidth=2, color="cyan", label=_lbl, alpha=.4)
            ax1.set_ylabel("Pre spikes")

            ax2.plot(timevec, nest.GetStatus(mm, "events")[
                     0]["post_tr__for_neuromodulated_stdp_synapse_nestml"], label="nestml post tr")
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
            ax2.set_ylabel("Post spikes")

            if sim_mdl:
                vt_spike_times_ = nest.GetStatus(spikedet_vt, "events")[0]["times"]
                print("Actual vt spike times: " + str(vt_spike_times_))

            if sim_mdl:
                n_spikes = len(vt_spike_times_)
                for i in range(n_spikes):
                    ax3.plot(2 * [vt_spike_times_[i]], [0, 1], linewidth=2, color="black", alpha=.4)
            ax3.set_ylabel("VT spikes")

            if sim_mdl:
                ax4.plot(t_hist, w_hist, marker="o", label="nestml")
            if sim_ref:
                ax4.plot(t_hist, w_hist_ref, linestyle="--", marker="x", label="ref")
            ax4.set_xlabel("Time [ms]")
            ax4.set_ylabel("w")

            for _ax in ax:
                _ax.grid(which="major", axis="both")
                _ax.xaxis.set_major_locator(matplotlib.ticker.FixedLocator(np.arange(0, np.ceil(sim_time))))
                _ax.set_xlim(0., sim_time)
                _ax.legend()
            fig.savefig("/tmp/stdp_dopa_synapse_test" + fname_snip + ".png", dpi=300)

        # verify
        MAX_ABS_ERROR = 1E-6
        assert np.all(np.abs(np.array(w_hist) - np.array(w_hist_ref)) < MAX_ABS_ERROR)
