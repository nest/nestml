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

def get_trace_at(t, t_spikes, tau, initial=0., increment=1., before_increment=False, extra_debug=False):
    if extra_debug:
        print("\t-- obtaining trace at t = " + str(t))
    if len(t_spikes) == 0:
        return initial
    tr = initial
    t_sp_prev = 0.
    for t_sp in t_spikes:
        if t_sp > t:
            break
        if extra_debug:
            _tr_prev = tr
        tr *= np.exp(-(t_sp - t_sp_prev) / tau)
        if t_sp == t:  # exact floating point match!
            if before_increment:
                if extra_debug:
                    print("\t   [%] exact (before_increment = T), prev trace = " + str(_tr_prev) + " at t = " + str(t_sp_prev)
                          + ", decayed by dt = " + str(t - t_sp_prev) + ", tau = " + str(tau) + " to t = " + str(t) + ": returning trace: " + str(tr))
                return tr
            else:
                if extra_debug:
                    print("\t   [%] exact (before_increment = F), prev trace = " + str(_tr_prev) + " at t = " + str(t_sp_prev) + ", decayed by dt = " + str(
                        t - t_sp_prev) + ", tau = " + str(tau) + " to t = " + str(t) + ": returning trace: " + str(tr + increment))
                return tr + increment
        tr += increment
        t_sp_prev = t_sp
    if extra_debug:
        _tr_prev = tr
    tr *= np.exp(-(t - t_sp_prev) / tau)
    if extra_debug:
        print("\t   [&] prev trace = " + str(_tr_prev) + " at t = " + str(t_sp_prev) + ", decayed by dt = "
              + str(t - t_sp_prev) + ", tau = " + str(tau) + " to t = " + str(t) + ": returning trace: " + str(tr))
    return tr

@pytest.mark.skipif(NESTTools.detect_nest_version().startswith("v2"),
                    reason="This test does not support NEST 2")
class TestSynapsePostNeuronTransformerUpdateOrder:
    r"""This test checks that postsynaptic update statements inside a synaptic on-post event handler result in updates in the expected order when transformed by the SynapsePostNeuronTransformer.

    Note that when the SynapsePostNeuronTransformer is used, the numerical value obtained for the moved variables at a time of a spike is always the value "just before" the update due to the spike. This is why the test with ``update_order_w_before_traces=False`` is marked as expected to fail.
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
                        "delay_variable": {"postsyn_trace_synapse": "d"},
                        "weight_variable": {"postsyn_trace_synapse": "w"}}

        # generate_nest_target(input_path=input_path,
        #                      logging_level="DEBUG",
        #                      suffix="_nestml",
        #                      codegen_opts=codegen_opts)

    # @pytest.mark.xfail(strict=True)
    # def test_postsyn_trace_synapse(self):
    #     self.run_test_postsyn_trace_synapse(update_order_w_before_traces=True)


    def _run_nest_simulation(self, initial_w, neuron_model_name, synapse_model_name, T, dt, spike_train_pre, spike_train_post, syn_delay, p):

        # weight recorder
        wr = nest.Create("weight_recorder")
        syn_model = "stdp_stp_synapse_rec"
        nest.CopyModel(synapse_model_name, syn_model, {"weight_recorder": wr,
                                                       "w": initial_w,
                                                       "d": syn_delay,
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

    def _run_ref_simulation(self, initial_w, T, dt, spike_train_pre, spike_train_post, p, before_increment):
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
            # if t in spike_train_pre:
            #     print("\tgetting pre trace r1")
            #     r1 = get_trace_at(spk_time, times_spikes_pre,
            #                     syn_opts["tau_plus"], before_increment=False, extra_debug=True)
            #     print("\tgetting post trace o2")
            #     o2 = get_trace_at(spk_time, times_spikes_post_syn_persp,
            #                     syn_opts["tau_y"], before_increment=True, extra_debug=True)
            #     old_weight = weight
            #     weight = np.clip(weight + r1 * (syn_opts["A2_plus"] + syn_opts["A3_plus"]
            #                     * o2), a_min=syn_opts["w_min"], a_max=syn_opts["w_max"])
            #     print("[REF] t = " + str(spk_time) + ": facilitating from " + str(old_weight) + " to " + str(weight) + " with pre tr = " + str(r1) + ", post tr = " + str(o2))

            #if t in spike_train_post:
            tr = get_trace_at(t, spike_train_post + .1, p["tau_post2"], before_increment=before_increment, extra_debug=True)

            if np.any([np.isclose(t, t_sp) for t_sp in spike_train_post]):
                old_weight = w
                w += p["learning_rate"] * tr
                print("[REF] t = " + str(t) + ": depressing from " + str(old_weight) + " to " + str(w) + " with tr = " + str(tr))

            w_history.append(w)
            z2_history.append(tr)

            # last_t_sp = spk_time


        # #for tidx, t in enumerate(range(len(timevec))[1:]):
        #     z2 *= np.exp(-dt / p["tau_post2"])

        #     if spike_train_pre[t] and spike_train_post_bool[t]:
        #         raise Exception()

        #     if spike_train_post_bool[t]:
        #         print("Processing post spike at time t = " + str(time[t]))
        #         if update_order_w_before_traces:
        #             print("Updating w = " + str(w) + " (z2 = " + str(z2) + ") new weight = " + str(w + p["learning_rate"] * z2))
        #             w += p["learning_rate"] * z2   # Update synaptic weight
        #             # z += p["Z"] * (1 - z)  # Increment post-synaptic trace
        #             # print("Updating z2: old z2 = " + str(z2) + ", new z2 = " + str(z2 + p["Z2"] * (1 - z2)))
        #             print("Updating z2: old z2 = " + str(z2) + ", new z2 = " + str(z2 + 1))
        #             z2 += 1#p["Z2"] * (1 - z2)
        #         else:
        #             # z += p["Z"] * (1 - z)  # Increment post-synaptic trace
        #             print("Updating z2: old z2 = " + str(z2) + ", new z2 = " + str(z2 + 1))
        #             # print("Updating z2: old z2 = " + str(z2) + ", new z2 = " + str(z2 + p["Z2"] * (1 - z2)))
        #             z2 += 1#p["Z2"] * (1 - z2)
        #             print("Updating w = " + str(w) + " (z2 = " + str(z2) + ") new weight = " + str(w + p["learning_rate"] * z2))
        #             w += p["learning_rate"] * z2  # Update synaptic weight

        #     w_history.append(w)
        #     # z_history.append(z)
        #     z2_history.append(z2)

        assert len(timevec) == len(z2_history)
        assert len(timevec) == len(w_history)

        return timevec, z2_history, w_history


    def test_postsyn_trace_synapse_alternate_order(self):
        self.run_test_postsyn_trace_synapse(update_order_w_before_traces=False)

    def run_test_postsyn_trace_synapse(self, update_order_w_before_traces: bool):
        self.generate_model_code(update_order_w_before_traces)

        neuron_model_name = "iaf_psc_delta_neuron_nestml__with_postsyn_trace_synapse_nestml"
        synapse_model_name = "postsyn_trace_synapse_nestml__with_iaf_psc_delta_neuron_nestml"

        nest.ResetKernel()
        nest.Install("nestmlmodule")
        nest.print_time = False
        nest.set_verbosity("M_ERROR")

        initial_w = 1.0
        T = 150.
        dt = 0.1
        syn_delay = dt
        nest.resolution = dt

        spike_train_pre = np.array([ 65., 115.])
        spike_train_post = np.array([  7.2,  12.2,  17.2,  22.2,  27.2,  32.2,  37.2,  42.2,  47.2, 52.2,  57.2,  62.2,  67.2,  72.2,  77.2,  82.2,  87.2,  92.2, 97.2, 102.2, 107.2, 112.2, 117.2, 122.2, 127.2, 132.2, 137.2, 142.2, 147.2])

        p = {"Z2": 0.2,
             "tau_post2": 50.,
             "learning_rate": 1E-3}

        timevec_nest, trace_nest, w_nest, spike_train_pre_nest, spike_train_post_nest = self._run_nest_simulation(initial_w, neuron_model_name, synapse_model_name, T, dt, spike_train_pre, spike_train_post, syn_delay, p)
        np.testing.assert_allclose(spike_train_pre, spike_train_pre_nest)

        timevec_ref, trace_ref, w_ref = self._run_ref_simulation(initial_w, T, dt, spike_train_post_nest, spike_train_post, p, before_increment=update_order_w_before_traces)


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

            # axs[1].plot(time, z_history, "--", label=r"$z_1$ python", color="red")
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

        np.testing.assert_allclose(w_nest, w_ref)

        # for pre_spike_time in spike_train_pre:
        #     tidx_nest = np.argmin((pre_spike_time - timevec_nest)**2)
        #     w_according_to_nest = w_nest[tidx_nest + 1]

        #     tidx_ref = np.argmin((pre_spike_time - time)**2)
        #     w_according_to_ref = w_history[tidx_ref]

        #     np.testing.assert_allclose(timevec_nest[tidx_nest], time[tidx_ref])

        #     np.testing.assert_allclose(w_according_to_nest, w_according_to_ref)
