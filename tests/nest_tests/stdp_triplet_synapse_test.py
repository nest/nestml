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

import nest
import numpy as np
import pytest
from pynestml.frontend.pynestml_frontend import to_nest, install_nest

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.ticker
    import matplotlib.pyplot as plt
    TEST_PLOTS = True
except Exception:
    TEST_PLOTS = False

@pytest.fixture(autouse=True,
                scope="module")
def nestml_to_nest_extension_module():
    """Generate the neuron model code"""
    nest_path = nest.ll_api.sli_func("statusdict/prefix ::")

    to_nest(input_path=["models/neurons/iaf_psc_delta.nestml", "models/synapses/stdp_triplet_naive.nestml"],
            target_path="/tmp/nestml-triplet-stdp",
            logging_level="INFO",
            module_name="nestml_triplet_pair_module",
            suffix="_nestml",
            codegen_opts={"neuron_parent_class": "StructuralPlasticityNode",
                            "neuron_parent_class_include": "structural_plasticity_node.h",
                            "neuron_synapse_pairs": [{"neuron": "iaf_psc_delta",
                                                      "synapse": "stdp_triplet",
                                                      "post_ports": ["post_spikes"]}]})
    install_nest("/tmp/nestml-triplet-stdp", nest_path)


def get_trace_at(t, t_spikes, tau, initial=0., increment=1., before_increment=False, extra_debug=False):
    if extra_debug:
        print("\t-- obtaining trace at t = " +str(t))
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
        if t_sp == t: # exact floating point match!
            if before_increment:
                if extra_debug:
                    print("\t   [%] exact (before_increment = T), prev trace = " + str(_tr_prev) + " at t = " + str(t_sp_prev) + ", decayed by dt = " + str(t-t_sp_prev) + ", tau = " + str(tau) + " to t = " + str(t) + ": returning trace: " + str(tr))
                return tr
            else:
                if extra_debug:
                    print("\t   [%] exact (before_increment = F), prev trace = " + str(_tr_prev) + " at t = " + str(t_sp_prev) + ", decayed by dt = " + str(t-t_sp_prev) + ", tau = " + str(tau) + " to t = " + str(t) + ": returning trace: " + str(tr + increment))
                return tr + increment
        tr += increment
        t_sp_prev = t_sp
    if extra_debug:
        _tr_prev = tr
    tr *= np.exp(-(t - t_sp_prev) / tau)
    if extra_debug:
        print("\t   [&] prev trace = " + str(_tr_prev) + " at t = " + str(t_sp_prev) + ", decayed by dt = " + str(t-t_sp_prev) + ", tau = " + str(tau) + " to t = " + str(t) + ": returning trace: " + str(tr))
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
    #spike_idx = 0

    #min_dt = 1.  # XXX: bug still exists in minimum timestep code -- don't use for now
    for spk_time in np.unique(times_spikes_syn_persp):
    #while spike_idx < len(times_spikes_syn_persp):
    #    spk_time = times_spikes_syn_persp[spike_idx]
        #if spk_time - last_t_sp > min_dt:
            #spk_time = last_t_sp + min_dt
            #if spike_idx + 1 < len(times_spikes_syn_persp) \
            #and times_spikes_syn_persp[spike_idx + 1] == spk_time:
                #spike_idx += 1
        #else:
            #spike_idx += 1
        #spike_idx += 1

        #print("Jumping to spike at t = " + str(spk_time))
        import logging;logging.warning("XXX: TODO: before_increment values here are all wrong")

        if spk_time in times_spikes_post_syn_persp:
            #print("Post spike --> facilitation")
            print("\tgetting pre trace r1")
            r1 = get_trace_at(spk_time, times_spikes_pre, syn_opts["tau_plus"], before_increment=True, extra_debug=True)#F
            print("\tgetting post trace o2")
            o2 = get_trace_at(spk_time, times_spikes_post_syn_persp, syn_opts["tau_y"], before_increment=True, extra_debug=True)#T
            #print("\tr1 = " + str(r1))
            #print("\to2 = " + str(o2))
            #print("\told weight = " + str(weight))
            old_weight = weight
            weight = np.clip(weight + r1*(syn_opts["A2_plus"]+syn_opts["A3_plus"]*o2), a_min=syn_opts["w_min"], a_max=syn_opts["w_max"])
            #print("\tnew weight = " + str(weight))
            print("[NESTML] stdp_connection: facilitating from " + str(old_weight) + " to " + str(weight) + " with pre tr = " + str(r1) + ", post tr = " + str(o2))

        if spk_time in times_spikes_pre:
            #print("Pre spike --> depression")
            print("\tgetting post trace o1")
            o1 = get_trace_at(spk_time, times_spikes_post_syn_persp, syn_opts["tau_minus"], before_increment=True, extra_debug=True)#F
            print("\tgetting pre trace r2")
            r2 = get_trace_at(spk_time, times_spikes_pre, syn_opts["tau_x"], before_increment=True, extra_debug=True)#T
            #print("\to1 = " + str(o1))
            #print("\tr2 = " + str(r2))
            #print("\told weight = " + str(weight))
            old_weight = weight
            weight = np.clip(weight - o1*(syn_opts["A2_minus"]+syn_opts["A3_minus"]*r2), a_min=syn_opts["w_min"], a_max=syn_opts["w_max"])
            #print("\tnew weight = " + str(weight))
            print("[NESTML] stdp_connection: depressing from " + str(old_weight) + " to " + str(weight) + " with pre tr = " + str(r2) + ", post tr = " + str(o1))

        log[spk_time] = {"weight": weight}
        
        last_t_sp = spk_time

    timevec = np.sort(list(log.keys()))
    weight_reference = np.array([log[k]["weight"] for k in timevec])
    
    return timevec, weight_reference


def run_nest_simulation(neuron_model_name,
                        synapse_model_name,
                        neuron_opts,
                        syn_opts,
                        nest_modules_to_load=None,
                        resolution=1., # [ms]
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
        if nest_modules_to_load:
            for s in nest_modules_to_load:
                nest.Install(s)
    except:
        pass # will fail when run in a loop ("module is already loaded")

    
    nest.SetKernelStatus({'print_time': False,'local_num_threads': 1})
    nest.SetKernelStatus({'resolution': resolution})

    nest.SetDefaults(neuron_model_name, neuron_opts)

    # Create nodes -------------------------------------------------

    neurons           = nest.Create(neuron_model_name, 2)

    #external_input = nest.Create('poisson_generator', params={'rate': p_rate})
    #external_input1 = nest.Create('poisson_generator', params={'rate': p_rate})

    #external_input    = nest.Create('spike_generator', params={'spike_times': np.hstack((1+np.arange(10).astype(float), [sim_time - 10.]))})
    #external_input1    = nest.Create('spike_generator', params={'spike_times': 1+np.arange(10).astype(float)})

    print("Requested pre times: " + str(pre_spike_times_req))
    print("Requested post times: " + str(post_spike_times_req))

    pre_spike_times_req = np.hstack((pre_spike_times_req, [sim_time - syn_opts["delay"]]))  # one more pre spike to obtain updated values at end of simulation

    external_input    = nest.Create('spike_generator', params={'spike_times': pre_spike_times_req})
    external_input1    = nest.Create('spike_generator', params={'spike_times': post_spike_times_req})

    spikes            = nest.Create('spike_recorder')
    weight_recorder_E = nest.Create('weight_recorder')

    # Set models default -------------------------------------------

    nest.CopyModel('static_synapse',
                   'excitatory_noise',
                   {'weight': J_ext,
                    'delay' : syn_opts["delay"]})

    _syn_opts = syn_opts.copy()
    _syn_opts['Wmax'] = _syn_opts.pop('w_max')
    _syn_opts['Wmin'] = _syn_opts.pop('w_min')
    _syn_opts['w'] = _syn_opts.pop('w_init')
    _syn_opts.pop('delay')
    nest.CopyModel(synapse_model_name,
                   synapse_model_name + "_rec",
                   {'weight_recorder'   : weight_recorder_E[0]})
    nest.SetDefaults(synapse_model_name + "_rec", _syn_opts)

    # Connect nodes ------------------------------------------------

    nest.Connect(neurons[0], neurons[1], syn_spec={'synapse_model':synapse_model_name + "_rec"})
    nest.Connect(external_input, neurons[0], syn_spec='excitatory_noise')
    nest.Connect(external_input1, neurons[1], syn_spec='excitatory_noise')
    nest.Connect(neurons, spikes)   # spike_recorder ignores connection delay; recorded times are times of spike creation rather than spike arrival

    # Simulate -----------------------------------------------------

    nest.Simulate(sim_time)

    connections = nest.GetConnections(neurons, neurons)
    gid_pre         = nest.GetStatus(connections,'source')[0]
    gid_post        = nest.GetStatus(connections,'target')[0]

    events         = nest.GetStatus(spikes, 'events')[0]
    times_spikes   = np.array(events['times'])
    senders_spikes = events['senders']

    events            = nest.GetStatus(weight_recorder_E,'events')[0]
    times_weights     = events['times']
    weight_simulation = events['weights']
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

    ax[-1].scatter(times_weights, weight_simulation, s=40, marker="o", label="NEST", facecolor="none", edgecolor="black")
    ax[-1].legend()

    for _ax in ax:
        #_ax.set_xlim(-2*delay + min(np.amin(times_spikes_pre), np.amin(times_spikes_post)), np.amax(timevec) + 2*delay)
        _ax.grid(True)
        _ax.set_xlim(0., sim_time)
        _ax.xaxis.set_major_locator(matplotlib.ticker.FixedLocator(np.arange(0, np.ceil(sim_time))))
        if not _ax == ax[-1]:
            _ax.set_xticklabels([])

    ax[-1].set_xlabel("Time [ms]")

    plt.savefig("/tmp/stdp_triplets_[delay=" + "%.3f" % syn_opts["delay"] + "].png", dpi=150.)

#@pytest.mark.parametrize('delay', [1., 5., 14.3])
##@pytest.mark.parametrize('spike_times_len', [1, 10, 100])
#@pytest.mark.parametrize('spike_times_len', [10])
def _test_stdp_triplet_synapse(delay, spike_times_len):
    print("Running test for delay = " + str(delay) + ", spike_times_len = " + str(spike_times_len))

    experiment = "test_nestml_pair_synapse"
    syn_opts = {
        'delay': delay,
        'tau_minus': 33.7,
        'tau_plus': 16.8,
        'tau_x': 101.,
        'tau_y': 125.,
        'A2_plus': 7.5e-10,
        'A3_plus': 9.3e-3,
        'A2_minus': 7e-3,
        'A3_minus': 2.3e-4,
        'w_max':  50.,
        'w_min' : 0.,
        'w_init': 1.
    }

    if experiment == "test_nestml_pair_synapse":
        nest_modules_to_load = ["nestml_triplet_pair_module"]

        #neuron_model_name = "iaf_psc_exp_nestml__with_stdp_triplet_nestml"
        neuron_model_name = "iaf_psc_delta_nestml__with_stdp_triplet_nestml"
        neuron_opts = {'tau_minus__for_stdp_triplet_nestml': syn_opts['tau_minus'],
                        'tau_y__for_stdp_triplet_nestml': syn_opts['tau_y']}

        #synapse_model_name = "stdp_triplet_nestml__with_iaf_psc_exp_nestml"
        synapse_model_name = "stdp_triplet_nestml__with_iaf_psc_delta_nestml"
        nest_syn_opts = {'the_delay': delay}
        nest_syn_opts.update(syn_opts)
        nest_syn_opts.pop('tau_minus')  # these have been moved to the neuron
        nest_syn_opts.pop('tau_y')
    elif experiment == "test_nest_triplet_synapse":
        nest_modules_to_load = None

        #neuron_model_name = "iaf_psc_exp"
        #neuron_opts = {'tau_minus': syn_opts['tau_minus'],
                        #'tau_minus_triplet': syn_opts['tau_y']}
        tau_m    = 40.0      # Membrane time constant (mV)
        V_th     = 20.0      # Spike threshold (mV)
        C_m      = 250.0     # Membrane capacitance (pF)
        t_ref    = 2.0       # Refractory period (ms)
        E_L      = 0.0       # Resting membrane potential (mV)
        V_reset  = 10.0      # Reset potential after spike (mV)

        neuron_model_name = 'iaf_psc_delta'
        neuron_opts = {"tau_m"      : tau_m,
                        "t_ref"      : t_ref,
                        "C_m"        : C_m,
                        "V_reset"    : V_reset,
                        "E_L"        : E_L,
                        "V_m"        : E_L,
                        "V_th"       : V_th,
                        "tau_minus" : syn_opts['tau_minus'],
                        "tau_minus_triplet": syn_opts['tau_y']}
        
        synapse_model_name = "stdp_triplet"
        nest_syn_opts = {'delay': delay,
                    'tau_plus': syn_opts['tau_plus'],
                    'tau_plus_triplet': syn_opts['tau_x'],
                    'Aplus': syn_opts['A2_plus'],
                    'Aplus_triplet': syn_opts['A3_plus'],
                    'Aminus': syn_opts['A2_minus'],
                    'Aminus_triplet': syn_opts['A3_minus'],
                    'Wmax'              : syn_opts["w_max"],
                    'weight'            : syn_opts["w_init"]}

    fname_snip = "_experiment=[" + experiment + "]"

    #post_spike_times = np.arange(1, 20).astype(np.float)
    #pre_spike_times = -2 + np.array([3., 13.])

    #post_spike_times = -2 + np.array([11. ,15., 32.])

    #pre_spike_times = [1., 11., 21.]    # [ms]
    #post_spike_times = [6., 16., 26.]  # [ms]

    #post_spike_times = np.sort(np.unique(1 + np.round(10 * np.sort(np.abs(np.random.randn(10))))))      # [ms]
    #pre_spike_times = np.sort(np.unique(1 + np.round(10 * np.sort(np.abs(np.random.randn(10))))))      # [ms]

    #pre_spike_times = [4., 5., 6., 9., 12., 15., 16., 18.]
    #post_spike_times = [6., 11., 14., 17., 20., 23., 27.]

    '''pre_spike_times = np.array([ 14.])
    post_spike_times = np.array([3., 4., 9., 10., 11.])

    post_spike_times = np.sort(np.unique(1 + np.round(10 * np.sort(np.abs(np.random.randn(10))))))      # [ms]
    pre_spike_times = np.sort(np.unique(1 + np.round(10 * np.sort(np.abs(np.random.randn(10))))))      # [ms]

    post_spike_times = np.sort(np.unique(1 + np.round(100 * np.sort(np.abs(np.random.randn(100))))))      # [ms]
    pre_spike_times = np.sort(np.unique(1 + np.round(100 * np.sort(np.abs(np.random.randn(100))))))      # [ms]
    '''
    pre_spike_times=np.array([  2.,   3.,   7.,   8.,   9.,  10.,  12.,  17.,  19.,  21.,  22.,  24.,  25.,  26.,
        28.,  30.,  36.,  37.,  38.,  40.,  43.,  46.,  47.,  48.,  49.,  50.,  51.,  52.,
        53.,  55.,  58.,  59.,  60.,  62.,  64.,  65.,  66.,  67.,  68.,  69.,  71.,  72.,
            76.,  77.,  78.,  82.,  83.,  84.,  85.,  86.,  87.,  88.,  92.,  96.,  99., 105.,
            113., 114., 121., 122., 124., 129., 135., 140., 152., 161., 167., 170., 183., 186.,
            192., 202., 218., 224., 303., 311.])
    post_spike_times = np.array([  2.,   4.,   5.,   8.,   9.,  12.,  13.,  14.,  17.,  18.,  19.,  21.,  24.,  25.,
        26.,  28.,  30.,  32.,  34.,  37.,  38.,  40.,  42.,  44.,  45.,  46.,  49.,  50.,
        51.,  53.,  55.,  56.,  60.,  61.,  67.,  68.,  72.,  73.,  74.,  76.,  77.,  78.,
            79.,  81.,  82.,  84.,  87.,  88.,  93.,  95.,  96.,  98.,  99., 100., 109., 110.,
            111., 115., 116., 118., 120., 121., 124., 125., 127., 128., 140., 144., 149., 150.,
            152., 155., 156., 157., 163., 164., 168., 172., 204., 206., 216., 239., 243.])

    # pre_spike_times = 1 + 5 * np.arange(spike_times_len).astype(float)
    # post_spike_times = 1 + 5 * np.arange(spike_times_len).astype(float)

    nestml_timevec, nestml_w, gid_pre, gid_post, times_spikes, senders_spikes, sim_time = \
        run_nest_simulation(neuron_model_name=neuron_model_name,
                                synapse_model_name=synapse_model_name,
                                neuron_opts=neuron_opts,
                                syn_opts=nest_syn_opts,
                                nest_modules_to_load=nest_modules_to_load,
                                resolution=.1, # [ms]
                                sim_time=None, #20.,
                                pre_spike_times_req=pre_spike_times,
                                post_spike_times_req=post_spike_times,
                                fname_snip=fname_snip)

    # n.b. spike times here refer to the **somatic** spike time

    idx            = np.argsort(times_spikes)
    senders_spikes = senders_spikes[idx]
    times_spikes   = times_spikes[idx]

    times_spikes_pre  = times_spikes[senders_spikes==gid_pre]
    times_spikes_post = times_spikes[senders_spikes==gid_post]

    print("Actual pre spike times: " + str(times_spikes_pre))
    print("Actual post spike times: " + str(times_spikes_post))

    # convert somatic spike times to synaptic perspective: add post dendritic delay

    times_spikes_syn_persp = np.copy(times_spikes)
    times_spikes_syn_persp[senders_spikes==gid_post] += syn_opts["delay"]

    times_spikes_post_syn_persp = times_spikes_syn_persp[senders_spikes==gid_post]
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
        plot_comparison(syn_opts, times_spikes_pre, times_spikes_post, times_spikes_post_syn_persp, ref_timevec, ref_w, nestml_timevec, nestml_w, sim_time)

    compare_results(ref_timevec, ref_w, nestml_timevec, nestml_w)


#@pytest.mark.parametrize('spike_times_len', [1, 10, 100])
@pytest.mark.parametrize('spike_times_len', [10])
def test_stdp_triplet_synapse_delay_1(spike_times_len):
    delay = 1.
    _test_stdp_triplet_synapse(delay, spike_times_len)

# import logging;logging.warning("XXX: TODO: xfail test due to https://github.com/nest/nestml/issues/661")
# @pytest.mark.xfail(strict=True, raises=Exception)
#@pytest.mark.parametrize('spike_times_len', [1, 10, 100])
@pytest.mark.parametrize('spike_times_len', [10])
def test_stdp_triplet_synapse_delay_5(spike_times_len):
    delay = 5.
    _test_stdp_triplet_synapse(delay, spike_times_len)

# import logging;logging.warning("XXX: TODO: xfail test due to https://github.com/nest/nestml/issues/661")
# @pytest.mark.xfail(strict=True, raises=Exception)
#@pytest.mark.parametrize('spike_times_len', [1, 10, 100])
@pytest.mark.parametrize('spike_times_len', [10])
def test_stdp_triplet_synapse_delay_10(spike_times_len):
    delay = 10.
    _test_stdp_triplet_synapse(delay, spike_times_len)
