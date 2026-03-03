# -*- coding: utf-8 -*-
#
# test_tsodyks_synapse.py
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


@pytest.mark.skipif(NESTTools.detect_nest_version().startswith("v2"),
                    reason="This test does not support NEST 2")
class TestNESTTsodyksSynapse:

    neuron_model_name = "iaf_psc_exp_neuron_nestml__with_tsodyks_synapse_nestml"
    ref_neuron_model_name = "iaf_psc_exp_neuron_nestml_non_jit"

    synapse_model_name = "tsodyks_synapse_nestml__with_iaf_psc_exp_neuron_nestml"
    ref_synapse_model_name = "tsodyks_synapse"

    @pytest.fixture(scope="module", autouse=True)
    def setUp(self):
        """Generate the model code"""

        jit_codegen_opts = {"neuron_synapse_pairs": [{"neuron": "iaf_psc_exp_neuron",
                                                      "synapse": "tsodyks_synapse"}],
                            "delay_variable": {"tsodyks_synapse": "d"},
                            "weight_variable": {"tsodyks_synapse": "w"}}

        jit_codegen_opts["neuron_parent_class"] = "StructuralPlasticityNode"
        jit_codegen_opts["neuron_parent_class_include"] = "structural_plasticity_node.h"

        # generate the "jit" model (co-generated neuron and synapse), that does not rely on ArchivingNode
        files = [os.path.join("models", "neurons", "iaf_psc_exp_neuron.nestml"),
                 os.path.join("models", "synapses", "tsodyks_synapse.nestml")]
        input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, s))) for s in files]
        generate_nest_target(input_path=input_path,
                             target_path="/tmp/nestml-jit",
                             logging_level="DEBUG",
                             module_name="nestml_jit_module",
                             suffix="_nestml",
                             codegen_opts=jit_codegen_opts)

        non_jit_codegen_opts = {"neuron_parent_class": "ArchivingNode",
                                "neuron_parent_class_include": "archiving_node.h",
                                "delay_variable": {"tsodyks_synapse": "d"},
                                "weight_variable": {"tsodyks_synapse": "w"}}

        # generate the "non-jit" model, that relies on ArchivingNode
        generate_nest_target(input_path=os.path.realpath(os.path.join(os.path.dirname(__file__),
                                                                      os.path.join(os.pardir, os.pardir, "models", "neurons", "iaf_psc_exp_neuron.nestml"))),
                             target_path="/tmp/nestml-non-jit",
                             logging_level="DEBUG",
                             module_name="nestml_non_jit_module",
                             suffix="_nestml_non_jit",
                             codegen_opts=non_jit_codegen_opts)

    def test_nest_tsodyks_synapse(self):
        fname_snip = ""

        pre_spike_times = [1., 11., 21.]    # [ms]
        post_spike_times = [6., 16., 26.]  # [ms]

        post_spike_times = np.sort(np.unique(1 + np.round(10 * np.sort(np.abs(np.random.randn(10))))))      # [ms]
        pre_spike_times = np.sort(np.unique(1 + np.round(10 * np.sort(np.abs(np.random.randn(10))))))      # [ms]

        self.run_synapse_test(neuron_model_name=self.neuron_model_name,
                              ref_neuron_model_name=self.ref_neuron_model_name,
                              synapse_model_name=self.synapse_model_name,
                              ref_synapse_model_name=self.ref_synapse_model_name,
                              resolution=.5,  # [ms]
                              delay=1.,  # [ms]
                              pre_spike_times=pre_spike_times,
                              post_spike_times=post_spike_times,
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
                         fname_snip=""):

        if pre_spike_times is None:
            pre_spike_times = []

        if post_spike_times is None:
            post_spike_times = []

        if sim_time is None:
            sim_time = max(np.amax(pre_spike_times), np.amax(post_spike_times)) + 5 * delay

        nest.ResetKernel()
        nest.set_verbosity("M_ALL")
        nest.Install("nestml_jit_module")
        nest.Install("nestml_non_jit_module")
        nest.SetKernelStatus({"resolution": resolution})

        print("Pre spike times: " + str(pre_spike_times))
        print("Post spike times: " + str(post_spike_times))

        wr = nest.Create("weight_recorder")
        wr_ref = nest.Create("weight_recorder")
        nest.CopyModel(synapse_model_name, "tsodyks_nestml_rec",
                       {"weight_recorder": wr[0], "w": 1., "d": 1., "receptor_type": 0})
        nest.CopyModel(ref_synapse_model_name, "tsodyks_ref_rec",
                       {"weight_recorder": wr_ref[0], "weight": 1., "delay": 1., "receptor_type": 0})

        # create spike_generators with these times
        pre_sg = nest.Create("spike_generator",
                             params={"spike_times": pre_spike_times})
        post_sg = nest.Create("spike_generator",
                              params={"spike_times": post_spike_times,
                                      "allow_offgrid_times": True})

        # create parrot neurons and connect spike_generators
        pre_neuron = nest.Create("parrot_neuron")
        post_neuron = nest.Create(neuron_model_name)

        pre_neuron_ref = nest.Create("parrot_neuron")
        post_neuron_ref = nest.Create(ref_neuron_model_name)

        spikedet_pre = nest.Create("spike_recorder")
        spikedet_post = nest.Create("spike_recorder")
        mm = nest.Create("multimeter", params={"record_from": ["V_m"]})

        spikedet_pre_ref = nest.Create("spike_recorder")
        spikedet_post_ref = nest.Create("spike_recorder")
        mm_ref = nest.Create("multimeter", params={"record_from": ["V_m"]})

        nest.Connect(pre_sg, pre_neuron, "one_to_one", syn_spec={"delay": 1.})
        nest.Connect(post_sg, post_neuron, "one_to_one", syn_spec={"delay": 1., "weight": 9999.})
        nest.Connect(pre_neuron, post_neuron, "all_to_all", syn_spec={"synapse_model": "tsodyks_nestml_rec"})
        nest.Connect(mm, post_neuron)
        nest.Connect(pre_neuron, spikedet_pre)
        nest.Connect(post_neuron, spikedet_post)

        nest.Connect(pre_sg, pre_neuron_ref, "one_to_one", syn_spec={"delay": 1.})
        nest.Connect(post_sg, post_neuron_ref, "one_to_one", syn_spec={"delay": 1., "weight": 9999.})
        nest.Connect(pre_neuron_ref, post_neuron_ref, "all_to_all", syn_spec={"synapse_model": ref_synapse_model_name})
        nest.Connect(mm_ref, post_neuron_ref)
        nest.Connect(pre_neuron_ref, spikedet_pre_ref)
        nest.Connect(post_neuron_ref, spikedet_post_ref)

        # get tsodyks synapse and weight before protocol
        syn = nest.GetConnections(source=pre_neuron, synapse_model="tsodyks_nestml_rec")
        syn_ref = nest.GetConnections(source=pre_neuron_ref, synapse_model=ref_synapse_model_name)

        # simulate
        t = 0.
        t_hist = []
        hist = {}
        hist_ref = {}
        for key in ["x", "y", "u"]:
            hist[key] = []
            hist_ref[key] = []

        while t <= sim_time:
            nest.Simulate(resolution)
            t += resolution
            t_hist.append(t)
            for key in ["x", "y", "u"]:
                hist_ref[key].append(nest.GetStatus(syn_ref)[0][key])
                hist[key].append(nest.GetStatus(syn)[0][key])

        # data collection
        V_m = nest.GetStatus(mm, "events")[0]["V_m"]
        V_m_ref = nest.GetStatus(mm_ref, "events")[0]["V_m"]

        # plot
        if TEST_PLOTS:
            fig, ax1 = plt.subplots(nrows=1)

            timevec = nest.GetStatus(mm, "events")[0]["times"]
            ax1.plot(timevec, V_m, label="nestml", alpha=.7, linestyle=":")

            pre_ref_spike_times_ = nest.GetStatus(spikedet_pre_ref, "events")[0]["times"]
            timevec = nest.GetStatus(mm_ref, "events")[0]["times"]
            ax1.plot(timevec, V_m_ref, label="nest ref", alpha=.7)

            ax1.set_ylabel("V_m")
            ax1.grid(which="major", axis="both")
            ax1.grid(which="minor", axis="x", linestyle=":", alpha=.4)
            ax1.set_xlim(0., sim_time)
            ax1.legend()

            fig.savefig("/tmp/tsodyks_synapse_test" + fname_snip + "_V_m.png", dpi=300)

        # plot
        if TEST_PLOTS:
            fig, ax = plt.subplots(nrows=5)
            ax1, ax2, ax3, ax4, ax5 = ax

            pre_spike_times_ = nest.GetStatus(spikedet_pre, "events")[0]["times"]
            print("Actual pre spike times: " + str(pre_spike_times_))
            pre_ref_spike_times_ = nest.GetStatus(spikedet_pre_ref, "events")[0]["times"]
            print("Actual pre ref spike times: " + str(pre_ref_spike_times_))

            n_spikes = len(pre_spike_times_)
            for i in range(n_spikes):
                if i == 0:
                    _lbl = "nestml"
                else:
                    _lbl = None
                ax1.plot(2 * [pre_spike_times_[i] + delay], [0, 1], linewidth=2, color="blue", alpha=.4, label=_lbl)

            post_spike_times_ = nest.GetStatus(spikedet_post, "events")[0]["times"]
            print("Actual post spike times: " + str(post_spike_times_))
            post_ref_spike_times_ = nest.GetStatus(spikedet_post_ref, "events")[0]["times"]
            print("Actual post ref spike times: " + str(post_ref_spike_times_))

            if True:
                n_spikes = len(pre_ref_spike_times_)
                for i in range(n_spikes):
                    if i == 0:
                        _lbl = "nest ref"
                    else:
                        _lbl = None
                    ax1.plot(2 * [pre_ref_spike_times_[i] + delay], [0, 1],
                             linewidth=2, color="cyan", label=_lbl, alpha=.4)
            ax1.set_ylabel("Pre spikes")

            if True:
                n_spikes = len(post_spike_times_)
                for i in range(n_spikes):
                    if i == 0:
                        _lbl = "nestml"
                    else:
                        _lbl = None
                    ax2.plot(2 * [post_spike_times_[i]], [0, 1], linewidth=2, color="black", alpha=.4, label=_lbl)

                n_spikes = len(post_ref_spike_times_)
                for i in range(n_spikes):
                    if i == 0:
                        _lbl = "nest ref"
                    else:
                        _lbl = None
                    ax2.plot(2 * [post_ref_spike_times_[i]], [0, 1], linewidth=2, color="red", alpha=.4, label=_lbl)
            ax2.set_ylabel("Post spikes")

            for i, key in enumerate(["x", "y", "u"]):
                ax[2 + i].plot(t_hist, hist[key], marker="o", label="nestml")
                ax[2 + i].plot(t_hist, hist_ref[key], linestyle="--", marker="x", label="ref")
                ax[2 + i].set_ylabel(key)

            ax[-1].set_xlabel("Time [ms]")

            for _ax in ax:
                _ax.grid(which="major", axis="both")
                _ax.xaxis.set_major_locator(matplotlib.ticker.FixedLocator(np.arange(0, np.ceil(sim_time))))
                _ax.set_xlim(0., sim_time)
                _ax.legend()
            fig.savefig("/tmp/tsodyks_synapse_test" + fname_snip + ".png", dpi=300)

        # verify
        np.testing.assert_allclose(V_m, V_m_ref)
