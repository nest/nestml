# -*- coding: utf-8 -*-
#
# test_synapse_post_neuron_transformer_compound_blocks.py
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


def generate_regular_spike_train(rate, T, dt, start_t=0.):
    """
    Generates regular spike train as a Boolean array.

    Parameters:
    - rate: Firing rate in Hz.
    - T: Total simulation time in ms.
    - dt: Time step in ms.

    Returns:
    - spike_train: Boolean array of length len(time), where True indicates a spike.
    - spike_times: same data as spike time data
    """
    # Step 1: Generate spike times
    spikes = []
    t = start_t
    while t < T:
        isi = 1 / rate * 1000
        t += isi
        if t < T:
            spikes.append(t)

    spike_times = np.array(spikes)

    # Step 2: Create time array
    time = np.arange(0, T, dt)

    # Step 3: Initialize spike train array
    spike_train = np.zeros(len(time), dtype=bool)

    # Step 4: Map spike times to nearest indices in the time array
    # Ensure that spike times correspond to time steps in "time"
    indices = np.searchsorted(time, spike_times)

    # Handle edge cases where indices might be equal to len(time)
    indices = indices[indices < len(time)]

    # Step 5: Set corresponding indices in spike_train to True
    spike_train[indices] = True

    return spike_train, spike_times


@pytest.mark.skipif(NESTTools.detect_nest_version().startswith("v2"),
                    reason="This test does not support NEST 2")
class TestSynapsePostNeuronTransformerCompoundBlocks:
    r"""This test checks that variables inside compound blocks are properly identified by the transformer as "strictly synaptic" variables."""
    @pytest.fixture(autouse=True)
    def generate_model_code(self, request):
        r"""Generate the NEST C++ code for neuron and synapse models"""

        files = [os.path.join("models", "neurons", "iaf_psc_delta_neuron.nestml"),
                 os.path.join("tests", "resources", "double_postsyn_trace_synapse.nestml")]
        input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(os.pardir, os.pardir, s))) for s in files]

        codegen_opts = {"neuron_synapse_pairs": [{"neuron": "iaf_psc_delta_neuron",
                                                  "synapse": "double_postsyn_trace_synapse",
                                                  "post_ports": ["post_spikes"]}],
                        "delay_variable": {"double_postsyn_trace_synapse": "d"},
                        "weight_variable": {"double_postsyn_trace_synapse": "w"}}

        use_synapse_post_neuron_transformer = request.param

        print("Now generating code with ``use_synapse_post_neuron_transformer`` = " + str(use_synapse_post_neuron_transformer))

        if not use_synapse_post_neuron_transformer:
            codegen_opts["strictly_synaptic_vars"] = {"double_postsyn_trace_synapse": ["zp_trace", "zm_trace"]}

        generate_nest_target(input_path=input_path,
                             logging_level="DEBUG",
                             suffix="_nestml",
                             codegen_opts=codegen_opts)

    @pytest.mark.parametrize("generate_model_code", (False, True), indirect=True)
    @pytest.mark.parametrize("update_order_w_before_trace", [True, False])
    def test_double_postsyn_trace_synapse(self, update_order_w_before_trace: bool):
        neuron_model_name = "iaf_psc_delta_neuron_nestml__with_double_postsyn_trace_synapse_nestml"
        synapse_model_name = "double_postsyn_trace_synapse_nestml__with_iaf_psc_delta_neuron_nestml"

        nest.ResetKernel()
        nest.Install("nestmlmodule")
        nest.print_time = False
        nest.set_verbosity("M_ERROR")

        # define spike train
        rate = 20
        T = 500
        dt = 0.1
        syn_delay = dt
        nest.resolution = dt

        spike_train_pre_bool, spikes_pre = generate_regular_spike_train(rate, T, dt, start_t=15.)
        spike_train_post_bool, spikes_post = generate_regular_spike_train(rate * 2, T, dt, start_t=2.5)

        spikes_pre = np.round(spikes_pre, 1)
        spikes_post = np.round(spikes_post, 1)

        spikes_post -= syn_delay
        spikes_pre -= syn_delay

        p = {"Z": 0.4102089913,
             "Z2": 0.11584585200000001,
             "tau_post": 100,
             "tau_post2": 63.297325105}

        wr = nest.Create("weight_recorder")
        syn_model = "stdp_stp_synapse_rec"
        initial_w = 1.0
        nest.CopyModel(synapse_model_name, syn_model, {"weight_recorder": wr,
                                                       "w": initial_w,
                                                       "d": syn_delay,
                                                       "update_order_w_before_trace": update_order_w_before_trace,
                                                       "receptor_type": 0,
                                                       "Zp": p["Z2"],
                                                       "Zm": p["Z"],
                                                       "tau_zm": p["tau_post"],
                                                       "tau_zp": p["tau_post2"]})

        spikes_pre_gr = nest.Create("spike_generator", params={"spike_times": spikes_pre})
        spikes_post_gr = nest.Create("spike_generator", params={"spike_times": spikes_post})

        pre_neuron = nest.Create("parrot_neuron")
        post_neuron = nest.Create(neuron_model_name)

        # set postsynaptic parameters
        try:
            post_neuron.Zp__for_double_postsyn_trace_synapse_nestml = p["Z2"]
            post_neuron.Zm__for_double_postsyn_trace_synapse_nestml = p["Z"]
            post_neuron.tau_zm__for_double_postsyn_trace_synapse_nestml = p["tau_post"]
            post_neuron.tau_zp__for_double_postsyn_trace_synapse_nestml = p["tau_post2"]
        except BaseException:
            try:
                post_neuron.Zp__for_minimal_SLSTDP_old_synapse_nestml = p["Z2"]
                post_neuron.Zm__for_minimal_SLSTDP_old_synapse_nestml = p["Z"]
                post_neuron.tau_zm__for_minimal_SLSTDP_old_synapse_nestml = p["tau_post"]
                post_neuron.tau_zp__for_minimal_SLSTDP_old_synapse_nestml = p["tau_post2"]
            except BaseException:
                pass

        nest.Connect(spikes_pre_gr, pre_neuron, "one_to_one", syn_spec={"delay": syn_delay})
        nest.Connect(pre_neuron, post_neuron, "one_to_one", syn_spec={"synapse_model": syn_model})
        nest.Connect(spikes_post_gr, post_neuron, "one_to_one", syn_spec={"delay": syn_delay, "weight": 9999.})

        conn = nest.GetConnections(target=post_neuron, synapse_model=syn_model)
        try:
            conn.Zp = p["Z2"]
            conn.Zm = p["Z"]
        except BaseException:
            pass

        # spike detectors
        spikedet_pre = nest.Create("spike_recorder")
        spikedet_post = nest.Create("spike_recorder")
        nest.Connect(pre_neuron, spikedet_pre)
        nest.Connect(post_neuron, spikedet_post)

        n_steps = int(np.ceil(T / syn_delay))
        trace_nest = []
        trace_nest_t = []
        trace_nest_z2 = []

        t = nest.biological_time
        trace_nest_t.append(t)

        try:
            trace_nest.append(post_neuron.zm_trace__for_double_postsyn_trace_synapse_nestml)
            trace_nest_z2.append(post_neuron.zp_trace__for_double_postsyn_trace_synapse_nestml)
        except BaseException:
            try:
                trace_nest.append(post_neuron.zm_trace__for_minimal_SLSTDP_old_synapse_nestml)
                trace_nest_z2.append(post_neuron.zp_trace__for_minimal_SLSTDP_old_synapse_nestml)
            except BaseException:
                trace_nest.append(conn.get("zm_trace"))
                trace_nest_z2.append(conn.get("zp_trace"))

        w_trace = []

        w_trace.append(conn.get("weight"))
        for step in range(n_steps):
            nest.Simulate(syn_delay)
            t = nest.biological_time

            trace_nest_t.append(t)

            conn = nest.GetConnections(target=post_neuron, synapse_model=syn_model)
            # post
            try:
                trace_nest.append(post_neuron.zm_trace__for_double_postsyn_trace_synapse_nestml)
                trace_nest_z2.append(post_neuron.zp_trace__for_double_postsyn_trace_synapse_nestml)
            except BaseException:
                try:
                    trace_nest.append(post_neuron.zm_trace__for_minimal_SLSTDP_old_synapse_nestml)
                    trace_nest_z2.append(post_neuron.zp_trace__for_minimal_SLSTDP_old_synapse_nestml)
                except BaseException:
                    trace_nest.append(conn.get("zm_trace"))
                    trace_nest_z2.append(conn.get("zp_trace"))

            w_trace.append(conn.get("weight"))

        conn = nest.GetConnections(target=post_neuron, synapse_model=syn_model)

        if TEST_PLOTS:
            fig, axs = plt.subplots(3, 1)
            events = wr.get("events")

            axs[0].set_ylabel("w")
            axs[0].grid(True)
            axs[0].step(trace_nest_t, w_trace, color="black", where="post", label="NEST")

            axs[1].plot(trace_nest_t, trace_nest, label="z1 nestml", color="red")
            axs[1].plot(trace_nest_t, trace_nest_z2, label="z2 nestml", color="black")
            axs[1].legend()
            axs[1].grid(True)

            axs[-1].scatter(spikedet_post.events["times"], np.zeros_like(spikedet_post.events["times"]), label="post sp")
            axs[-1].scatter(spikedet_pre.events["times"], np.ones_like(spikedet_pre.events["times"]), label="pre sp")
            axs[-1].set_xlim(axs[0].get_xlim())
            axs[1].grid(True)

        def spike_times_to_bool_array(spike_times, T, dt):
            time = np.arange(0, T, dt)

            # Step 3: Initialize spike train array
            spike_train = np.zeros(len(time), dtype=bool)

            # Step 4: Map spike times to nearest indices in the time array
            # Ensure that spike times correspond to time steps in "time"
            indices = np.searchsorted(time, spike_times)

            # Handle edge cases where indices might be equal to len(time)
            indices = indices[indices < len(time)]

            # Step 5: Set corresponding indices in spike_train to True
            spike_train[indices] = True

            return spike_train

        spike_train_pre = spikedet_pre.events["times"]
        spike_train_post = spikedet_post.events["times"]

        spike_train_pre_bool = spike_times_to_bool_array(spike_train_pre, T, dt)
        spike_train_post_bool = spike_times_to_bool_array(spike_train_post, T, dt)

        # Lists to record variables for plotting
        w_history = []
        z_history = []
        z2_history = []

        w = initial_w  # Initial synaptic weight
        z = 0.0  # Post-synaptic trace
        z2 = 0.0

        time = np.arange(0, T, dt)
        for t in range(len(time)):
            z *= np.exp(-dt / p["tau_post"])
            z2 *= np.exp(-dt / p["tau_post2"])

            if spike_train_pre_bool[t] and spike_train_post_bool[t]:
                raise Exception()

            if spike_train_post_bool[t]:
                if update_order_w_before_trace:
                    w += z * z2  # Update synaptic weight
                    z += p["Z"] * (1 - z)  # Increment post-synaptic trace
                    z2 += p["Z2"] * (1 - z2)
                else:
                    z += p["Z"] * (1 - z)  # Increment post-synaptic trace
                    z2 += p["Z2"] * (1 - z2)
                    w += z * z2  # Update synaptic weight

            w_history.append(w)
            z_history.append(z)
            z2_history.append(z2)

        if TEST_PLOTS:
            axs[0].plot(time, w_history, "--", color="black", label="w python")
            axs[0].legend()

            axs[1].plot(time, z_history, "--", label=r"$z_1$ python", color="red")
            axs[1].plot(time, z2_history, "--", label=r"$z_2$ python", color="black")
            axs[1].legend()

            plt.savefig("/tmp/test_synapse_post_neuron_transformer.png")

        #
        #   testing
        #

        assert len(spike_train_pre) > 0
        for pre_spike_time in spike_train_pre:
            tidx_nest = np.argmin((pre_spike_time - trace_nest_t)**2)
            w_according_to_nest = w_trace[tidx_nest + 1]

            tidx_ref = np.argmin((pre_spike_time - time)**2)
            w_according_to_ref = w_history[tidx_ref]

            np.testing.assert_allclose(trace_nest_t[tidx_nest], time[tidx_ref])

            np.testing.assert_allclose(w_according_to_nest, w_according_to_ref)
