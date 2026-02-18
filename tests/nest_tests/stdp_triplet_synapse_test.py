# -*- coding: utf-8 -*-
#
# stdp_triplet_synapse_test.py
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


@pytest.fixture(autouse=True,
                scope="module")
def nestml_generate_target():
    r"""Generate the neuron model code"""

    files = [os.path.join("models", "neurons", "iaf_psc_delta_fixed_timestep_neuron.nestml"),
             os.path.join("models", "synapses", "stdp_triplet_synapse.nestml")]
    input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
        os.pardir, os.pardir, s))) for s in files]
    generate_nest_target(input_path=input_path,
                         logging_level="DEBUG",
                         suffix="_nestml",
                         codegen_opts={"neuron_parent_class": "StructuralPlasticityNode",
                                       "neuron_parent_class_include": "structural_plasticity_node.h",
                                       "neuron_synapse_pairs": [{"neuron": "iaf_psc_delta_fixed_timestep_neuron",
                                                                 "synapse": "stdp_triplet_synapse",
                                                                 "post_ports": ["post_spikes"]}],
                                       "weight_variable": {"stdp_triplet_synapse": "w"}})


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


def run_reference_simulation(syn_opts,
                             sim_time=None,  # if None, computed from pre and post spike times
                             times_spikes_pre=None,
                             times_spikes_syn_persp=None,
                             times_spikes_post_syn_persp=None,
                             fname_snip=""):

    log = {}
    weight = syn_opts["w_init"]

    r1 = 0.
    r2 = 0.
    o1 = 0.
    o2 = 0.
    last_t_sp = 0.
    log[0.] = {"weight": weight,
               "r1": r1,
               "r2": r2
               }

    for spk_time in np.unique(times_spikes_syn_persp):
        if spk_time in times_spikes_post_syn_persp:
            print("\tgetting pre trace r1")
            r1 = get_trace_at(spk_time, times_spikes_pre,
                              syn_opts["tau_plus"], before_increment=False, extra_debug=True)
            print("\tgetting post trace o2")
            o2 = get_trace_at(spk_time, times_spikes_post_syn_persp,
                              syn_opts["tau_y"], before_increment=True, extra_debug=True)
            old_weight = weight
            weight = np.clip(weight + r1 * (syn_opts["A2_plus"] + syn_opts["A3_plus"]
                             * o2), a_min=syn_opts["w_min"], a_max=syn_opts["w_max"])
            print("[REF] t = " + str(spk_time) + ": facilitating from " + str(old_weight) + " to " + str(weight) + " with pre tr = " + str(r1) + ", post tr = " + str(o2))

        if spk_time in times_spikes_pre:
            # print("Pre spike --> depression")
            print("\tgetting post trace o1")
            o1 = get_trace_at(spk_time, times_spikes_post_syn_persp,
                              syn_opts["tau_minus"], before_increment=False, extra_debug=True)
            print("\tgetting pre trace r2")
            r2 = get_trace_at(spk_time, times_spikes_pre,
                              syn_opts["tau_x"], before_increment=True, extra_debug=True)
            old_weight = weight
            weight = np.clip(weight - o1 * (syn_opts["A2_minus"] + syn_opts["A3_minus"]
                             * r2), a_min=syn_opts["w_min"], a_max=syn_opts["w_max"])
            print("[REF] t = " + str(spk_time) + ": depressing from " + str(old_weight) + " to " + str(weight) + " with pre tr = " + str(r2) + ", post tr = " + str(o1))

        log[spk_time] = {"weight": weight}

        last_t_sp = spk_time

    timevec = np.sort(list(log.keys()))
    weight_reference = np.array([log[k]["weight"] for k in timevec])

    return timevec, weight_reference


def run_nest_simulation(neuron_model_name,
                        synapse_model_name,
                        neuron_opts,
                        syn_opts,
                        resolution=1.,  # [ms]
                        sim_time=None,  # if None, computed from pre and post spike times
                        pre_spike_times_req=None,
                        post_spike_times_req=None,
                        J_ext=10000.,
                        fname_snip=""):

    if pre_spike_times_req is None:
        pre_spike_times_req = []

    if post_spike_times_req is None:
        post_spike_times_req = []

    if sim_time is None:
        sim_time = max(np.amax(pre_spike_times_req), np.amax(post_spike_times_req)) + 10. + 3 * syn_opts["delay"]

    nest.set_verbosity("M_ALL")

    # Set parameters of the NEST simulation kernel
    nest.ResetKernel()

    try:
        nest.Install("nestmlmodule")
    except Exception:
        # ResetKernel() does not unload modules for NEST Simulator < v3.7; ignore exception if module is already loaded on earlier versions
        pass

    nest.SetKernelStatus({"print_time": False, "local_num_threads": 1})
    nest.SetKernelStatus({"resolution": resolution})

    nest.SetDefaults(neuron_model_name, neuron_opts)

    # Create nodes -------------------------------------------------

    neurons = nest.Create(neuron_model_name, 2)

    print("Requested pre times: " + str(pre_spike_times_req))
    print("Requested post times: " + str(post_spike_times_req))

    # one more pre spike to obtain updated values at end of simulation
    pre_spike_times_req = np.hstack((pre_spike_times_req, [sim_time - syn_opts["delay"]]))

    external_input = nest.Create("spike_generator", params={"spike_times": pre_spike_times_req})
    external_input1 = nest.Create("spike_generator", params={"spike_times": post_spike_times_req})

    if NESTTools.detect_nest_version().startswith("v2"):
        spikes = nest.Create("spike_detector")
    else:
        spikes = nest.Create("spike_recorder")
    weight_recorder_E = nest.Create("weight_recorder")

    # Set models default -------------------------------------------

    nest.CopyModel("static_synapse",
                   "excitatory_noise",
                   {"weight": J_ext,
                    "delay": syn_opts["delay"]})

    _syn_opts = syn_opts.copy()
    _syn_opts["Wmax"] = _syn_opts.pop("w_max")
    _syn_opts["Wmin"] = _syn_opts.pop("w_min")
    _syn_opts["w"] = _syn_opts.pop("w_init")
    nest.CopyModel(synapse_model_name,
                   synapse_model_name + "_rec",
                   {"weight_recorder": weight_recorder_E[0]})
    nest.SetDefaults(synapse_model_name + "_rec", _syn_opts)

    # Connect nodes ------------------------------------------------

    if NESTTools.detect_nest_version().startswith("v2"):
        nest.Connect([neurons[0]], [neurons[1]], syn_spec={"model": synapse_model_name + "_rec"})
        nest.Connect(external_input, [neurons[0]], syn_spec="excitatory_noise")
        nest.Connect(external_input1, [neurons[1]], syn_spec="excitatory_noise")
    else:
        nest.Connect(neurons[0], neurons[1], syn_spec={"synapse_model": synapse_model_name + "_rec"})
        nest.Connect(external_input, neurons[0], syn_spec="excitatory_noise")
        nest.Connect(external_input1, neurons[1], syn_spec="excitatory_noise")
    # spike_recorder ignores connection delay; recorded times are times of spike creation rather than spike arrival
    nest.Connect(neurons, spikes)

    # Simulate -----------------------------------------------------

    nest.Simulate(sim_time)

    connections = nest.GetConnections(neurons, neurons)
    gid_pre = nest.GetStatus(connections, "source")[0]
    gid_post = nest.GetStatus(connections, "target")[0]

    events = nest.GetStatus(spikes, "events")[0]
    times_spikes = np.array(events["times"])
    senders_spikes = events["senders"]

    events = nest.GetStatus(weight_recorder_E, "events")[0]
    times_weights = events["times"]
    weight_simulation = events["weights"]
    return times_weights, weight_simulation, gid_pre, gid_post, times_spikes, senders_spikes, sim_time


def compare_results(timevec, weight_reference, times_weights, weight_simulation):
    """
    Compare (timevec, weight_reference) and (times_weights, weight_simulation), where the former may contain more entries than the latter.
    """

    idx = [np.where(np.abs(timevec - i) < 1E-9)[0][0] for i in times_weights]
    timevec_pruned = timevec[idx]
    weight_reference_pruned = weight_reference[idx]

    np.testing.assert_allclose(timevec_pruned, times_weights)

    w_ref_vec = []
    for idx_w_sim, t_sim in enumerate(times_weights):
        w_sim = weight_simulation[idx_w_sim]
        idx_w_ref = np.where(timevec == t_sim)[0][0]
        w_ref = weight_reference[idx_w_ref]
        w_ref_vec.append(w_ref)

    np.testing.assert_allclose(weight_simulation, w_ref_vec, atol=1E-6, rtol=1E-6)
    print("Test passed!")


def plot_comparison(syn_opts, times_spikes_pre, times_spikes_post, times_spikes_post_syn_persp, timevec, weight_reference, times_weights, weight_simulation, sim_time):
    fig, ax = plt.subplots(nrows=4)
    fig.suptitle("Triplet STDP")

    _r1 = [get_trace_at(t, times_spikes_pre, syn_opts["tau_plus"]) for t in timevec]
    _r2 = [get_trace_at(t, times_spikes_pre, syn_opts["tau_x"]) for t in timevec]
    ax[0].plot(timevec, _r1, label="r1")
    ax[0].scatter(timevec, _r1, s=40, marker="o")
    ax[0].plot(timevec, _r2, label="r2")
    ax[0].scatter(timevec, _r2, s=40, marker="o")
    ax[0].set_ylabel("Soma & syn\ntrace (PRE)")
    _ylim = ax[0].get_ylim()
    for t_sp in times_spikes_pre:
        ax[0].plot([t_sp, t_sp], _ylim, linewidth=2, color=(.25, .5, 1.))
    ax[0].legend()

    _o1 = [get_trace_at(t, times_spikes_post, syn_opts["tau_minus"]) for t in timevec]
    _o2 = [get_trace_at(t, times_spikes_post, syn_opts["tau_y"]) for t in timevec]
    ax[1].plot(timevec, _o1, label="o1")
    ax[1].scatter(timevec, _o1, s=40, marker="o")
    ax[1].plot(timevec, _o2, label="o2")
    ax[1].scatter(timevec, _o2, s=40, marker="o")
    _ylim = ax[1].get_ylim()
    for t_sp in times_spikes_post:
        ax[1].plot([t_sp, t_sp], _ylim, linewidth=2, color=(.25, .5, 1.))
    ax[1].set_ylabel("Soma trace\n(POST)")
    ax[1].legend()

    _high_resolution_timevec = np.linspace(0, sim_time, 1000)
    _o1 = [get_trace_at(t, times_spikes_post_syn_persp, syn_opts["tau_minus"]) for t in _high_resolution_timevec]
    ax[2].plot(_high_resolution_timevec, _o1, label="o1", alpha=.333, color="blue")
    _o2 = [get_trace_at(t, times_spikes_post_syn_persp, syn_opts["tau_y"]) for t in _high_resolution_timevec]
    ax[2].plot(_high_resolution_timevec, _o2, label="o2", alpha=.333, color="orange")

    _o1 = [get_trace_at(t, times_spikes_post_syn_persp, syn_opts["tau_minus"]) for t in timevec]
    _o2 = [get_trace_at(t, times_spikes_post_syn_persp, syn_opts["tau_y"]) for t in timevec]
    ax[2].plot(timevec, _o1, label="o1", color="blue")
    ax[2].scatter(timevec, _o1, s=40, marker="o")
    ax[2].plot(timevec, _o2, label="o2", color="orange")
    ax[2].scatter(timevec, _o2, s=40, marker="o")
    _ylim = ax[2].get_ylim()
    for t_sp in times_spikes_post_syn_persp:
        ax[2].plot([t_sp, t_sp], _ylim, linewidth=2, color=(.25, .5, 1.))
    ax[2].set_ylabel("Syn trace\n(POST)")
    ax[2].legend()

    ax[-1].plot(timevec, weight_reference, label="Py ref")
    ax[-1].set_ylabel("Weight")

    ax[-1].scatter(times_weights, weight_simulation, s=40, marker="o",
                   label="NEST", facecolor="none", edgecolor="black")
    ax[-1].legend()

    for _ax in ax:
        _ax.grid(True)
        _ax.set_xlim(0., sim_time)
        _ax.xaxis.set_major_locator(mpl.ticker.FixedLocator(np.arange(0, np.ceil(sim_time))))
        if not _ax == ax[-1]:
            _ax.set_xticklabels([])

    ax[-1].set_xlabel("Time [ms]")

    plt.savefig("/tmp/stdp_triplets_[delay=" + "%.3f" % syn_opts["delay"] + "].png", dpi=150.)


def _test_stdp_triplet_synapse(delay, spike_times_len):
    print("Running test for delay = " + str(delay) + ", spike_times_len = " + str(spike_times_len))

    experiment = "test_nestml_pair_synapse"
    syn_opts = {
        "delay": delay,
        "tau_minus": 33.7,
        "tau_plus": 16.8,
        "tau_x": 101.,
        "tau_y": 125.,
        "A2_plus": 7.5e-10,
        "A3_plus": 9.3e-3,
        "A2_minus": 7e-3,
        "A3_minus": 2.3e-4,
        "w_max":  50.,
        "w_min": 0.,
        "w_init": 1.
    }

    if experiment == "test_nestml_pair_synapse":
        neuron_model_name = "iaf_psc_delta_fixed_timestep_neuron_nestml__with_stdp_triplet_synapse_nestml"
        neuron_opts = {"tau_minus__for_stdp_triplet_synapse_nestml": syn_opts["tau_minus"],
                       "tau_y__for_stdp_triplet_synapse_nestml": syn_opts["tau_y"]}

        synapse_model_name = "stdp_triplet_synapse_nestml__with_iaf_psc_delta_fixed_timestep_neuron_nestml"
        nest_syn_opts = {}
        nest_syn_opts.update(syn_opts)
        nest_syn_opts.pop("tau_minus")  # these have been moved to the neuron
        nest_syn_opts.pop("tau_y")
    elif experiment == "test_nest_triplet_synapse":
        tau_m = 40.0      # Membrane time constant (mV)
        V_th = 20.0      # Spike threshold (mV)
        C_m = 250.0     # Membrane capacitance (pF)
        t_ref = 2.0       # Refractory period (ms)
        E_L = 0.0       # Resting membrane potential (mV)
        V_reset = 10.0      # Reset potential after spike (mV)

        neuron_model_name = "iaf_psc_delta"
        neuron_opts = {"tau_m": tau_m,
                       "t_ref": t_ref,
                       "C_m": C_m,
                       "V_reset": V_reset,
                       "E_L": E_L,
                       "V_m": E_L,
                       "V_th": V_th,
                       "tau_minus": syn_opts["tau_minus"],
                       "tau_minus_triplet": syn_opts["tau_y"]}

        synapse_model_name = "stdp_triplet"
        nest_syn_opts = {"delay": delay,
                         "tau_plus": syn_opts["tau_plus"],
                         "tau_plus_triplet": syn_opts["tau_x"],
                         "Aplus": syn_opts["A2_plus"],
                         "Aplus_triplet": syn_opts["A3_plus"],
                         "Aminus": syn_opts["A2_minus"],
                         "Aminus_triplet": syn_opts["A3_minus"],
                         "Wmax": syn_opts["w_max"],
                         "weight": syn_opts["w_init"]}

    fname_snip = "_experiment=[" + experiment + "]"

    pre_spike_times = 1 + 10 * np.arange(spike_times_len).astype(float)
    post_spike_times = 5 + 10 * np.arange(spike_times_len).astype(float)

    nestml_timevec, nestml_w, gid_pre, gid_post, times_spikes, senders_spikes, sim_time = \
        run_nest_simulation(neuron_model_name=neuron_model_name,
                            synapse_model_name=synapse_model_name,
                            neuron_opts=neuron_opts,
                            syn_opts=nest_syn_opts,
                            resolution=.1,  # [ms]
                            sim_time=None,  # 20.,
                            pre_spike_times_req=pre_spike_times,
                            post_spike_times_req=post_spike_times,
                            fname_snip=fname_snip)

    # n.b. spike times here refer to the **somatic** spike time

    idx = np.argsort(times_spikes)
    senders_spikes = senders_spikes[idx]
    times_spikes = times_spikes[idx]

    times_spikes_pre = times_spikes[senders_spikes == gid_pre]
    times_spikes_post = times_spikes[senders_spikes == gid_post]

    print("Actual pre spike times: " + str(times_spikes_pre))
    print("Actual post spike times: " + str(times_spikes_post))

    assert len(times_spikes_pre) > 0, "No presynaptic spikes!"
    assert len(times_spikes_post) > 0, "No postsynaptic spikes!"

    # convert somatic spike times to synaptic perspective: add post dendritic delay

    times_spikes_syn_persp = np.copy(times_spikes)
    times_spikes_syn_persp[senders_spikes == gid_post] += syn_opts["delay"]

    times_spikes_post_syn_persp = times_spikes_syn_persp[senders_spikes == gid_post]
    times_spikes_syn_persp = np.sort(times_spikes_syn_persp)

    print("Actual post spike times (syn. pers.): " + str(times_spikes_post_syn_persp))

    ref_timevec, ref_w = \
        run_reference_simulation(syn_opts=syn_opts,
                                 sim_time=sim_time,
                                 times_spikes_pre=times_spikes_pre,
                                 times_spikes_syn_persp=times_spikes_syn_persp,
                                 times_spikes_post_syn_persp=times_spikes_post_syn_persp,
                                 fname_snip=fname_snip)

    if TEST_PLOTS:
        plot_comparison(syn_opts, times_spikes_pre, times_spikes_post, times_spikes_post_syn_persp,
                        ref_timevec, ref_w, nestml_timevec, nestml_w, sim_time)

    compare_results(ref_timevec, ref_w, nestml_timevec, nestml_w)


@pytest.mark.parametrize("delay", [1., 5., 10.])
@pytest.mark.parametrize("spike_times_len", [10])
def test_stdp_triplet_synapse_delay_1(spike_times_len, delay):
    _test_stdp_triplet_synapse(delay, spike_times_len)
