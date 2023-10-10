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
import numpy as np
import os
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


class NestThirdFactorSTDPSynapseTest(unittest.TestCase):

    neuron_model_name = "iaf_psc_exp_dend__with_third_factor_stdp_synapse"
    synapse_model_name = "third_factor_stdp_synapse__with_iaf_psc_exp_dend"

    post_trace_var = "I_dend"

    def setUp(self):
        r"""Generate the neuron model code"""

        codegen_opts = {"neuron_synapse_pairs": [{"neuron": "iaf_psc_exp_dend",
                                                  "synapse": "third_factor_stdp_synapse",
                                                  "post_ports": ["post_spikes",
                                                                 ["I_post_dend", "I_dend"]]}]}

        if not NESTTools.detect_nest_version().startswith("v2"):
            codegen_opts["neuron_parent_class"] = "StructuralPlasticityNode"
            codegen_opts["neuron_parent_class_include"] = "structural_plasticity_node.h"

        # generate the "jit" model (co-generated neuron and synapse), that does not rely on ArchivingNode
        files = [os.path.join("models", "neurons", "iaf_psc_exp_dend_neuron.nestml"),
                 os.path.join("models", "synapses", "third_factor_stdp_synapse.nestml")]
        input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, s))) for s in files]
        generate_nest_target(input_path=input_path,
                             target_path="/tmp/nestml-jit",
                             logging_level="INFO",
                             module_name="nestml_jit_module",
                             codegen_opts=codegen_opts)

    def test_nest_stdp_synapse(self):

        fname_snip = ""

        post_spike_times = np.sort(np.unique(1 + np.round(500 * np.sort(np.abs(np.random.randn(500))))))      # [ms]
        pre_spike_times = np.sort(np.unique(1 + np.round(500 * np.sort(np.abs(np.random.randn(500))))))      # [ms]

        self.run_synapse_test(neuron_model_name=self.neuron_model_name,
                              synapse_model_name=self.synapse_model_name,
                              resolution=.5,  # [ms]
                              delay=1.5,  # [ms]
                              pre_spike_times=pre_spike_times,
                              post_spike_times=post_spike_times,
                              sim_time=400.,
                              fname_snip=fname_snip)

    def run_synapse_test(self, neuron_model_name,
                         synapse_model_name,
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

        nest_version = NESTTools.detect_nest_version()

        nest.set_verbosity("M_ALL")
        nest.ResetKernel()
        nest.Install("nestml_jit_module")

        print("Pre spike times: " + str(pre_spike_times))
        print("Post spike times: " + str(post_spike_times))

        nest.set_verbosity("M_WARNING")

        nest.ResetKernel()
        nest.SetKernelStatus({"resolution": resolution})

        wr = nest.Create("weight_recorder")
        nest.CopyModel(synapse_model_name, "stdp_nestml_rec",
                       {"weight_recorder": wr[0], "w": 1., "d": 1., "receptor_type": 0, "lambda": .001})

        # create spike_generators with these times
        pre_sg = nest.Create("spike_generator",
                             params={"spike_times": pre_spike_times})
        post_sg = nest.Create("spike_generator",
                              params={"spike_times": post_spike_times,
                                      "allow_offgrid_times": True})

        # create parrot neurons and connect spike_generators
        pre_neuron = nest.Create("parrot_neuron")
        post_neuron = nest.Create(neuron_model_name)

        if nest_version.startswith("v2"):
            spikedet_pre = nest.Create("spike_detector")
            spikedet_post = nest.Create("spike_detector")
        else:
            spikedet_pre = nest.Create("spike_recorder")
            spikedet_post = nest.Create("spike_recorder")
        mm = nest.Create("multimeter", params={"record_from": ["V_m", self.post_trace_var]})

        nest.Connect(pre_sg, pre_neuron, "one_to_one", syn_spec={"delay": 1.})
        nest.Connect(post_sg, post_neuron, "one_to_one", syn_spec={"delay": 1., "weight": 9999.})
        if nest_version.startswith("v2"):
            nest.Connect(pre_neuron, post_neuron, "all_to_all", syn_spec={"model": "stdp_nestml_rec"})
        else:
            nest.Connect(pre_neuron, post_neuron, "all_to_all", syn_spec={"synapse_model": "stdp_nestml_rec"})
        nest.Connect(mm, post_neuron)
        nest.Connect(pre_neuron, spikedet_pre)
        nest.Connect(post_neuron, spikedet_post)

        # get STDP synapse and weight before protocol
        syn = nest.GetConnections(source=pre_neuron, synapse_model="stdp_nestml_rec")

        t = 0.
        t_hist = []
        w_hist = []
        state = 0
        while t <= sim_time:
            if t > sim_time / 6. and state == 0:
                nest.SetStatus(post_neuron, {"I_dend": 1.})
                state = 1
            if t > 2 * sim_time / 6 and state == 1:
                nest.SetStatus(post_neuron, {"I_dend": 1.})
            if t > 3 * sim_time / 6. and state == 1:
                state = 2
            if t > 5 * sim_time / 6. and state == 2:
                nest.SetStatus(post_neuron, {"I_dend": 0.})
                state = 3
            nest.Simulate(resolution)
            t += resolution
            t_hist.append(t)
            w_hist.append(nest.GetStatus(syn)[0]["w"])

        third_factor_trace = nest.GetStatus(mm, "events")[0][self.post_trace_var]
        timevec = nest.GetStatus(mm, "events")[0]["times"]

        if TEST_PLOTS:
            fig, ax = plt.subplots(nrows=2)
            ax1, ax2 = ax

            V_m = nest.GetStatus(mm, "events")[0]["V_m"]
            ax2.plot(timevec, third_factor_trace, label="I_dend_post")
            ax1.plot(timevec, V_m, alpha=.7, linestyle=":")
            ax1.set_ylabel("V_m")

            for _ax in ax:
                _ax.grid(which="major", axis="both")
                _ax.grid(which="minor", axis="x", linestyle=":", alpha=.4)
                _ax.set_xlim(0., sim_time)
                _ax.legend()
            fig.savefig("/tmp/stdp_triplet_synapse_test" + fname_snip + "_V_m.png", dpi=300)

        if TEST_PLOTS:
            fig, ax = plt.subplots(nrows=5)
            ax1, ax2, ax3, ax4, ax5 = ax

            pre_spike_times_ = nest.GetStatus(spikedet_pre, "events")[0]["times"]
            print("Actual pre spike times: " + str(pre_spike_times_))

            n_spikes = len(pre_spike_times_)
            for i in range(n_spikes):
                ax1.plot(2 * [pre_spike_times_[i] + delay], [0, 1], linewidth=2, color="blue", alpha=.4)

            post_spike_times_ = nest.GetStatus(spikedet_post, "events")[0]["times"]
            print("Actual post spike times: " + str(post_spike_times_))
            ax1.set_ylabel("Pre spikes")

            n_spikes = len(post_spike_times_)
            for i in range(n_spikes):
                if i == 0:
                    _lbl = "nestml"
                else:
                    _lbl = None
                ax[-4].plot(2 * [post_spike_times_[i]], [0, 1], linewidth=2, color="black", alpha=.4, label=_lbl)
            ax[-4].set_ylabel("Post spikes")

            ax[-3].plot(timevec, third_factor_trace)
            ax[-3].set_ylabel("3rd factor")

            ax[-2].plot(t_hist[:-1], np.diff(w_hist), marker="o", label=u"Δw")
            ax[-2].set_ylabel(u"Δw")

            ax[-1].plot(t_hist, w_hist, marker="o")
            ax[-1].set_ylabel("w")
            ax[-1].set_xlabel("Time [ms]")
            for _ax in ax:
                if not _ax == ax[-1]:
                    _ax.set_xticklabels([])
                _ax.grid(True)
                _ax.set_xlim(0., sim_time)

            fig.savefig("/tmp/stdp_third_factor_synapse_test" + fname_snip + ".png", dpi=300)

        # verify
        idx = np.where(np.abs(third_factor_trace) < 1E-12)[0]  # find where third_factor_trace is (almost) zero
        times_dw_should_be_zero = timevec[idx]
        assert len(times_dw_should_be_zero) > 0  # make sure we have > 0 datapoints to check
        for time_dw_should_be_zero in times_dw_should_be_zero[1:]:
            _idx = np.argmin((time_dw_should_be_zero - np.array(t_hist))**2)
            np.testing.assert_allclose(t_hist[_idx], time_dw_should_be_zero)
            np.testing.assert_allclose(0., np.abs(w_hist[_idx - 1] - w_hist[_idx]))   # make sure that weight does not change appreciably

        assert np.any(np.abs(np.array(w_hist) - 1) > 0.), "No change in the weight!"
