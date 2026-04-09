# -*- coding: utf-8 -*-
#
# test_synapse_post_neuron_transformer_update_order.py
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

# try to import matplotlib; set the result in the flag TEST_PLOTS
try:
    import matplotlib as mpl
    mpl.use("agg")
    import matplotlib.pyplot as plt
    TEST_PLOTS = True
except BaseException:
    TEST_PLOTS = False

import nest

from pynestml.codegeneration.nest_tools import NESTTools
from pynestml.frontend.pynestml_frontend import generate_nest_target


@pytest.mark.skipif(NESTTools.detect_nest_version().startswith("v2"),
                    reason="This test does not support NEST 2")
class TestSynapsePostNeuronTransformerUpdateOrder:
    r"""This test checks that postsynaptic update statements inside a synaptic on-post event handler result in updates in the expected order when transformed by the SynapsePostNeuronTransformer.

    Note that the SynapsePostNeuronTransformer is not used in this test by setting ``strictly_synaptic_vars``.
    """

    def generate_model_code(self, update_order_w_before_traces: bool = False):
        r"""Generate the NEST C++ code for neuron and synapse models"""

        files = [os.path.join("models", "neurons", "iaf_psc_delta_neuron.nestml")]

        if update_order_w_before_traces:
            files.append(os.path.join("tests", "resources", "postsyn_trace_update_w_before_traces_synapse.nestml"))
        else:
            files.append(os.path.join("tests", "resources", "postsyn_trace_update_traces_before_w_synapse.nestml"))

        input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(os.pardir, os.pardir, s))) for s in files]

        codegen_opts = {"neuron_synapse_pairs": [{"neuron": "iaf_psc_delta_neuron",
                                                  "synapse": "postsyn_trace_synapse",
                                                  "post_ports": ["post_spikes"]}],
                        "weight_variable": {"postsyn_trace_synapse": "w"},
                        "strictly_synaptic_vars": {"postsyn_trace_synapse": ["zp_trace"]}}

        generate_nest_target(input_path=input_path,
                             logging_level="DEBUG",
                             suffix="_nestml",
                             codegen_opts=codegen_opts)

    def test_postsyn_trace_synapse(self):
        self.run_test_postsyn_trace_synapse(update_order_w_before_traces=True)

    def test_postsyn_trace_synapse_alternate_order(self):
        self.run_test_postsyn_trace_synapse(update_order_w_before_traces=False)

    def _run_nest_simulation(self, initial_w, neuron_model_name, synapse_model_name, T, dt, spike_train_pre, spike_train_post, syn_delay, p):
        # weight recorder
        wr = nest.Create("weight_recorder")
        syn_model = "stdp_stp_synapse_rec"
        nest.CopyModel(synapse_model_name, syn_model, {"weight_recorder": wr,
                                                       "w": initial_w,
                                                       "delay": syn_delay,
                                                       "receptor_type": 0,
                                                       "Zp": p["Z2"],
                                                       "tau_zp": p["tau_post2"],
                                                       "learning_rate": p["learning_rate"]})

        spikes_pre_gr = nest.Create("spike_generator", params={"spike_times": spike_train_pre - syn_delay})
        spikes_post_gr = nest.Create("spike_generator", params={"spike_times": spike_train_post - syn_delay})

        pre_neuron = nest.Create("parrot_neuron")
        post_neuron = nest.Create(neuron_model_name)

        # set postsynaptic parameters
        try:
            post_neuron.Zp__for_postsyn_trace_synapse_nestml = p["Z2"]
            post_neuron.tau_zp__for_postsyn_trace_synapse_nestml = p["tau_post2"]
        except BaseException:
            try:
                post_neuron.Zp__for_minimal_SLSTDP_old_synapse_nestml = p["Z2"]
                post_neuron.tau_zp__for_minimal_SLSTDP_old_synapse_nestml = p["tau_post2"]
            except BaseException:
                pass

        nest.Connect(spikes_pre_gr, pre_neuron, "one_to_one", syn_spec={"delay": syn_delay})
        nest.Connect(pre_neuron, post_neuron, "one_to_one", syn_spec={"synapse_model": syn_model})
        nest.Connect(spikes_post_gr, post_neuron, "one_to_one", syn_spec={"delay": syn_delay, "weight": 9999.})

        conn = nest.GetConnections(target=post_neuron, synapse_model=syn_model)
        try:
            conn.Zp = p["Z2"]
        except BaseException:
            pass

        # spike detectors
        spikedet_pre = nest.Create("spike_recorder")
        spikedet_post = nest.Create("spike_recorder")
        nest.Connect(pre_neuron, spikedet_pre)
        nest.Connect(post_neuron, spikedet_post)

        n_steps = int(np.ceil(T / syn_delay))
        timevec_nest = []
        trace_nest = []

        t = nest.biological_time
        timevec_nest.append(t)

        try:
            trace_nest.append(post_neuron.zp_trace__for_postsyn_trace_synapse_nestml)
        except BaseException:
            try:
                trace_nest.append(post_neuron.zp_trace__for_minimal_SLSTDP_old_synapse_nestml)
            except BaseException:
                trace_nest.append(conn.get("zp_trace"))

        w_nest = []

        w_nest.append(conn.get("weight"))
        for step in range(n_steps):
            nest.Simulate(syn_delay)
            t = nest.biological_time

            timevec_nest.append(t)

            conn = nest.GetConnections(target=post_neuron, synapse_model=syn_model)
            # post
            try:
                trace_nest.append(post_neuron.zp_trace__for_postsyn_trace_synapse_nestml)
            except BaseException:
                try:
                    trace_nest.append(post_neuron.zp_trace__for_minimal_SLSTDP_old_synapse_nestml)
                except BaseException:
                    trace_nest.append(conn.get("zp_trace"))

            w_nest.append(conn.get("weight"))

        spike_train_pre_nest = spikedet_pre.events["times"]
        spike_train_post_nest = spikedet_post.events["times"]

        return timevec_nest, trace_nest, w_nest, spike_train_pre_nest, spike_train_post_nest

    def _run_ref_simulation(self, initial_w, T, dt, spike_train_pre, spike_train_post, p, update_order_w_before_traces):
        # state and initial values
        w = initial_w  # Initial synaptic weight
        tr = 0.

        # Lists to record variables for plotting
        w_history = []
        z2_history = []

        timevec = np.arange(0, T + dt, dt)
        assert all(np.any(np.isclose(t_sp, timevec)) for t_sp in spike_train_pre)
        assert all(np.any(np.isclose(t_sp, timevec)) for t_sp in spike_train_post)
        for t in timevec:
            tr *= np.exp(-dt / p["tau_post2"])

            if np.any([np.isclose(t, t_sp) for t_sp in spike_train_post]):
                old_weight = w
                if update_order_w_before_traces:
                    w += p["learning_rate"] * tr
                    tr += .2 * (1 - tr)
                else:
                    tr += .2 * (1 - tr)
                    w += p["learning_rate"] * tr

                print("[REF] t = " + str(t) + ": depressing from " + str(old_weight) + " to " + str(w) + " with tr = " + str(tr))

            w_history.append(w)
            z2_history.append(tr)

        assert len(timevec) == len(z2_history)
        assert len(timevec) == len(w_history)

        return timevec, z2_history, w_history

    def run_test_postsyn_trace_synapse(self, update_order_w_before_traces: bool):
        self.generate_model_code(update_order_w_before_traces)

        neuron_model_name = "iaf_psc_delta_neuron_nestml__with_postsyn_trace_synapse_nestml"
        synapse_model_name = "postsyn_trace_synapse_nestml__with_iaf_psc_delta_neuron_nestml"

        nest.ResetKernel()
        if not NESTTools.detect_nest_version().startswith("main"):
            nest.set_verbosity("M_ALL")
        else:
            nest.verbosity = nest.VerbosityLevel.ALL
        nest.Install("nestmlmodule")
        nest.print_time = False

        initial_w = 1.0
        T = 150.
        dt = 0.1
        syn_delay = dt
        nest.resolution = dt

        spike_train_pre = np.array([50., 80., 100.])
        spike_train_post = np.array([10., 20., 30., 40., 80. - dt])

        p = {"Z2": 0.2,
             "tau_post2": 50.,
             "learning_rate": 1E-3}

        timevec_nest, trace_nest, w_nest, spike_train_pre_nest, spike_train_post_nest = self._run_nest_simulation(initial_w, neuron_model_name, synapse_model_name, T, dt, spike_train_pre, spike_train_post, syn_delay, p)
        np.testing.assert_allclose(spike_train_pre, spike_train_pre_nest)

        timevec_ref, trace_ref, w_ref = self._run_ref_simulation(initial_w, T, dt, spike_train_post_nest + .1, spike_train_post, p, update_order_w_before_traces=update_order_w_before_traces)

        if TEST_PLOTS:
            fig, axs = plt.subplots(3, 1)
            # events = wr.get("events")

            axs[0].set_ylabel("w")
            axs[0].step(timevec_nest, w_nest, color="black", where="post", label="NEST")

            axs[1].plot(timevec_nest, trace_nest, label="z2 nestml", color="black")

            axs[-1].scatter(spike_train_post_nest, np.zeros_like(spike_train_post_nest), label="post sp")
            axs[-1].scatter(spike_train_pre_nest, np.ones_like(spike_train_pre_nest), label="pre sp")
            axs[-1].set_xlim(axs[0].get_xlim())

            axs[0].plot(timevec_ref, w_ref, "--", color="black", label="w python")

            axs[1].plot(timevec_ref, trace_ref, "--", label=r"$z_2$ python", color="black")

            for ax in axs:
                ax.set_xlim(0., T)
                ax.legend()
                ax.grid(True)

            plt.savefig("/tmp/test_synapse_post_neuron_transformer_[update_order_w_before_traces=" + str(update_order_w_before_traces) + "].png", dpi=600)

        #
        #   testing
        #

        assert len(spike_train_pre) > 0
        np.testing.assert_allclose(timevec_nest, timevec_ref)
        np.testing.assert_allclose(w_nest[-1], w_ref[-1])    # final weight should be the same
