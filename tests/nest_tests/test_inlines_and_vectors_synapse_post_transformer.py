# -*- coding: utf-8 -*-
#
# test_inlines_and_vectors_synapse_post_transformer.py
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
from tests.test_utils import get_trace_at

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.ticker
    import matplotlib.pyplot as plt
    TEST_PLOTS = True
except Exception:
    TEST_PLOTS = False


class TestInlinesAndVectorsSynapsePostTransformer:
    r"""Test that the SynapsePostTransformer works as expected when inline expressions and convolutions are present in the synapse"""

    neuron_model_name = "iaf_psc_exp_neuron_nestml__with_test_inlines_and_vectors_synapse_post_transformer_synapse_nestml"
    synapse_model_name = "test_inlines_and_vectors_synapse_post_transformer_synapse_nestml__with_iaf_psc_exp_neuron_nestml"

    @pytest.fixture(scope="module", autouse=True)
    def setUp(self):
        """Generate the model code"""

        codegen_opts = {"neuron_synapse_pairs": [{"neuron": "iaf_psc_exp_neuron",
                                                  "synapse": "test_inlines_and_vectors_synapse_post_transformer_synapse",
                                                  "post_ports": ["post_spikes"]}],
                        "weight_variable": {"test_inlines_and_vectors_synapse_post_transformer_synapse": "w"}}

        # generate the code for the co-generated neuron and synapse
        files = [os.path.join("models", "neurons", "iaf_psc_exp_neuron.nestml"),
                 os.path.join("tests", "nest_tests", "resources", "test_inlines_and_vectors_synapse_post_transformer_synapse.nestml")]
        input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, s))) for s in files]
        generate_nest_target(input_path=input_path,
                             target_path="test_inlines_and_vectors_synapse_post_transformer_synapse-target",
                             logging_level="DEBUG",
                             suffix="_nestml",
                             codegen_opts=codegen_opts)

    def test_inlines_and_vectors_synapse_post_transformer(self):
        fname_snip = ""

        delay = 1.   # [ms]
        resolution = 1.   # [ms]

        pre_spike_times = [1., 11., 21.]
        post_spike_times = [6., 16., 26.]
        print("Pre spike times: " + str(pre_spike_times))
        print("Post spike times: " + str(post_spike_times))

        sim_time = max(np.amax(pre_spike_times), np.amax(post_spike_times)) + 5 * delay

        nest.ResetKernel()
        nest.Install("nestmlmodule")
        nest.resolution = 1.

        # create spike_generators with these times
        pre_sg = nest.Create("spike_generator",
                             params={"spike_times": pre_spike_times})
        post_sg = nest.Create("spike_generator",
                              params={"spike_times": post_spike_times})

        # create parrot neurons and connect spike_generators
        pre_neuron = nest.Create("parrot_neuron")
        post_neuron = nest.Create(self.neuron_model_name)

        spikedet_pre = nest.Create("spike_recorder")
        spikedet_post = nest.Create("spike_recorder")
        mm = nest.Create("multimeter", params={"record_from": ["V_m"]})

        nest.Connect(pre_sg, pre_neuron, "one_to_one", syn_spec={"delay": 1.})
        nest.Connect(post_sg, post_neuron, "one_to_one", syn_spec={"delay": 1., "weight": 9999.})
        nest.Connect(pre_neuron, post_neuron, "all_to_all", syn_spec={"synapse_model": self.synapse_model_name})
        nest.Connect(mm, post_neuron)
        nest.Connect(pre_neuron, spikedet_pre)
        nest.Connect(post_neuron, spikedet_post)

        syn = nest.GetConnections(source=pre_neuron, synapse_model=self.synapse_model_name)

        # simulate
        syn_variables_to_record = ["foo", "K__X__pre_spikes", "K__X__post_spikes"]

        t = 0.
        t_hist = []
        hist = {}
        for key in syn_variables_to_record:
            hist[key] = []

        while t <= sim_time:
            nest.Simulate(resolution)
            t += resolution
            t_hist.append(t)
            for key in syn_variables_to_record:
                hist[key].append(nest.GetStatus(syn)[0][key])
        pre_spike_times_ = nest.GetStatus(spikedet_pre, "events")[0]["times"]
        print("Actual pre spike times: " + str(pre_spike_times_))

        post_spike_times_ = nest.GetStatus(spikedet_post, "events")[0]["times"]
        print("Actual post spike times: " + str(post_spike_times_))

        pre_tr_ref_hist = []
        post_tr_ref_hist = []
        for t in t_hist:
            pre_tr_ref_hist.append(get_trace_at(t - resolution, pre_spike_times_, syn.tau))
            post_tr_ref_hist.append(get_trace_at(t - 2 * resolution, post_spike_times_, syn.tau))

        # plot
        if TEST_PLOTS:
            fig, ax = plt.subplots(nrows=4)

            for i in range(len(pre_spike_times_)):
                if i == 0:
                    _lbl = "nestml"
                else:
                    _lbl = None
                ax[0].plot(2 * [pre_spike_times_[i]], [0, 1], linewidth=2, color="blue", alpha=.4, label=_lbl)
            ax[0].set_ylabel("Pre spikes")

            for i in range(len(post_spike_times_)):
                if i == 0:
                    _lbl = "nestml"
                else:
                    _lbl = None
                ax[1].plot(2 * [post_spike_times_[i]], [0, 1], linewidth=2, color="black", alpha=.4, label=_lbl)
            ax[1].set_ylabel("Post spikes")

            key = "K__X__pre_spikes"
            ax[2].plot(t_hist, hist[key], marker="o", label="nestml")
            ax[2].plot(t_hist, pre_tr_ref_hist, label="ref")
            ax[2].set_ylabel(key)

            key = "K__X__post_spikes"
            ax[3].plot(t_hist, hist[key], marker="o", label="nestml")
            ax[3].plot(t_hist, post_tr_ref_hist, label="ref")
            ax[3].set_ylabel(key)

            ax[-1].set_xlabel("Time [ms]")

            for _ax in ax:
                _ax.grid(which="major", axis="both")
                _ax.xaxis.set_major_locator(matplotlib.ticker.FixedLocator(np.arange(0, np.ceil(sim_time))))
                _ax.set_xlim(0., sim_time)
                _ax.legend()
            fig.savefig("/tmp/test_inlines_and_vectors_synapse_post_transformer" + fname_snip + ".png", dpi=300)

        # verify: trace values should be correct when they are updated by NEST (i.e. at the time of arrival of a presynaptic spike)
        for t_pre_sp in pre_spike_times_:
            tidx = np.where(t_hist == t_pre_sp + resolution)[0][0]
            pre_tr_nestml = hist["K__X__pre_spikes"][tidx]
            post_tr_nestml = hist["K__X__post_spikes"][tidx]
            pre_tr_ref = pre_tr_ref_hist[tidx]
            post_tr_ref = post_tr_ref_hist[tidx]
            np.testing.assert_allclose(pre_tr_nestml, pre_tr_ref)
            np.testing.assert_allclose(post_tr_nestml, post_tr_ref)
