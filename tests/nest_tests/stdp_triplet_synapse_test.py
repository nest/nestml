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
        _tr_prev = tr
        tr *= np.exp(-(t_sp - t_sp_prev) / tau)
        if t_sp == t and before_increment: # exact floating point match!
            if extra_debug:
                print("\t   [%] prev trace = " + str(_tr_prev) + " at t = " + str(t_sp_prev) + ", decayed by dt = " + str(t-t_sp_prev) + ", tau = " + str(tau) + " to t = " + str(t) + ": returning trace: " + str(tr))
            return tr
        tr += increment
        t_sp_prev = t_sp
    _tr_prev = tr # XXX REMOVE ME -- only for debug print below
    tr *= np.exp(-(t - t_sp_prev) / tau)
    if extra_debug:
        print("\t   [&] prev trace = " + str(_tr_prev) + " at t = " + str(t_sp_prev) + ", decayed by dt = " + str(t-t_sp_prev) + ", tau = " + str(tau) + " to t = " + str(t) + ": returning trace: " + str(tr))
    #import pdb;pdb.set_trace()
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

        if spk_time in times_spikes_post_syn_persp:
            #print("Post spike --> facilitation")
            r1 = get_trace_at(spk_time, times_spikes_pre, syn_opts["tau_plus"], before_increment=False)#F
            o2 = get_trace_at(spk_time, times_spikes_post_syn_persp, syn_opts["tau_y"], before_increment=True)
            #print("\tr1 = " + str(r1))
            #print("\to2 = " + str(o2))
            #print("\told weight = " + str(weight))
            old_weight = weight
            weight = np.clip(weight + r1*(syn_opts["A2_plus"]+syn_opts["A3_plus"]*o2), a_min=syn_opts["w_min"], a_max=syn_opts["w_max"])
            #print("\tnew weight = " + str(weight))
            print("[NESTML] stdp_connection: facilitating from " + str(old_weight) + " to " + str(weight) + " with pre tr = " + str(r1) + ", post tr = " + str(o2))

        if spk_time in times_spikes_pre:
            #print("Pre spike --> depression")
            o1 = get_trace_at(spk_time, times_spikes_post_syn_persp, syn_opts["tau_minus"], before_increment=False, extra_debug=True)#F
            r2 = get_trace_at(spk_time, times_spikes_pre, syn_opts["tau_x"], before_increment=True)
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
    import pdb;pdb.set_trace()
    return times_weights, weight_simulation, gid_pre, gid_post, times_spikes, senders_spikes, sim_time






    #nest.SetKernelStatus({'resolution': resolution})

    #wr = nest.Create('weight_recorder')
    #_syn_nestml_model_params = {"weight_recorder": wr[0], "w": 1., "receptor_type": 0}
    #_syn_nestml_model_params.update(nestml_syn_params)
    #nest.CopyModel(synapse_model_name, "stdp_nestml_rec", _syn_nestml_model_params)

    ## create spike_generators with these times
    #pre_sg = nest.Create("spike_generator",
                            #params={"spike_times": pre_spike_times})
    #post_sg = nest.Create("spike_generator",
                            #params={"spike_times": post_spike_times,
                                    #'allow_offgrid_times': True})

    ## create parrot neurons and connect spike_generators
    #pre_neuron = nest.Create("parrot_neuron")
    #post_neuron = nest.Create(neuron_model_name, params=nestml_neuron_params)
    #spikedet_pre = nest.Create("spike_recorder")
    #spikedet_post = nest.Create("spike_recorder")
    #mm = nest.Create("multimeter", params={"record_from" : ["V_m", "tr_o1_kernel__for_stdp_triplet_nestml__X__post_spikes__for_stdp_triplet_nestml", "tr_o2_kernel__for_stdp_triplet_nestml__X__post_spikes__for_stdp_triplet_nestml"],
                                            #"interval": resolution})
    #nest.Connect(pre_sg, pre_neuron, "one_to_one", syn_spec={"delay": 1.})
    #n\et(post_sg, post_neuron, "one_to_one", syn_spec={"delay": 1., "weight": 9999.})
    #nest.Connect(pre_neuron, post_neuron, "one_to_one", syn_spec={'synapse_model': 'stdp_nestml_rec'})
    #nest.Connect(mm, post_neuron)
    #nest.Connect(pre_neuron, spikedet_pre)
    #nest.Connect(post_neuron, spikedet_post)

    ## get STDP synapse and weight before protocol
    #syn = nest.GetConnections(source=pre_neuron, synapse_model="stdp_nestml_rec")

    #n_steps = int(np.ceil(sim_time / resolution)) + 1
    #t = 0.
    #t_hist = []
    #w_hist = []
    #while t <= sim_time:
        #nest.Simulate(resolution)
        #t += resolution
        #t_hist.append(t)
        #if nest.GetStatus(syn):
            #w_hist.append(nest.GetStatus(syn)[0]['w'])

    ## plot
    #if TEST_PLOTS:
        #fig, ax = plt.subplots(nrows=2)
        #ax1, ax2 = ax

        #timevec = nest.GetStatus(mm, "events")[0]["times"]
        #V_m = nest.GetStatus(mm, "events")[0]["V_m"]
        #ax2.plot(timevec, nest.GetStatus(mm, "events")[0]["tr_o1_kernel__for_stdp_triplet_nestml__X__post_spikes__for_stdp_triplet_nestml"], label="post_tr nestml")
        #ax2.plot(timevec, nest.GetStatus(mm, "events")[0]["tr_o2_kernel__for_stdp_triplet_nestml__X__post_spikes__for_stdp_triplet_nestml"], label="post_tr nestml")
        #ax1.plot(timevec, V_m, label="nestml")
        #ax1.set_ylabel("V_m")

        #for _ax in ax:
            #_ax.grid(which="major", axis="both")
            #_ax.grid(which="minor", axis="x", linestyle=":", alpha=.4)
            ##_ax.minorticks_on()
            #_ax.set_xlim(0., sim_time)
            #_ax.legend()
        #fig.savefig("/tmp/stdp_triplet_test" + fname_snip + "_V_m.png", dpi=300)

    ## plot
    #if TEST_PLOTS:
        #fig, ax = plt.subplots(nrows=3)
        #ax1, ax2, ax3 = ax

        #pre_spike_times_ = nest.GetStatus(spikedet_pre, "events")[0]["times"]
        #print("Actual pre spike times: "+ str(pre_spike_times_))

        #n_spikes = len(pre_spike_times_)
        #for i in range(n_spikes):
            #if i == 0:
            #_lbl = "nestml"
            #else:
            #_lbl = None
            #ax1.plot(2 * [pre_spike_times_[i] + delay], [0, 1], linewidth=2, color="blue", alpha=.4,label=_lbl)

        #post_spike_times_ = nest.GetStatus(spikedet_post, "events")[0]["times"]
        #print("Actual post spike times: "+ str(post_spike_times_))
        #n_spikes = len(post_spike_times_)
        #for i in range(n_spikes):
            #if i == 0:
            #_lbl = "nestml"
            #else:
            #_lbl = None
            #ax2.plot(2 * [post_spike_times_[i]], [0, 1], linewidth=2, color="black", alpha=.4, label=_lbl)
        #ax2.plot(timevec, nest.GetStatus(mm, "events")[0]["tr_o1_kernel__for_stdp_triplet_nestml__X__post_spikes__for_stdp_triplet_nestml"], label="nestml post tr")
        #ax2.set_ylabel("Post spikes")

        #if w_hist:
            #ax3.plot(t_hist, w_hist, marker="o", label="nestml")

        #ax3.set_xlabel("Time [ms]")
        #ax3.set_ylabel("w")
        #for _ax in ax:
            #_ax.grid(which="major", axis="both")
            #_ax.xaxis.set_major_locator(matplotlib.ticker.FixedLocator(np.arange(0, np.ceil(sim_time))))
            ##_ax.grid(which="minor", axis="x", linestyle=":", alpha=.4)
            ##_ax.minorticks_on()
            #_ax.set_xlim(0., sim_time)
            #_ax.legend()
        #fig.savefig("/tmp/stdp_triplet_test" + fname_snip + ".png", dpi=300)

    #return t_hist, w_hist



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

    _o1 = [get_trace_at(t, times_spikes_post_syn_persp, syn_opts["tau_minus"]) for t in timevec]
    _o2 = [get_trace_at(t, times_spikes_post_syn_persp, syn_opts["tau_y"]) for t in timevec]
    ax[2].plot(timevec, _o1, label="o1")
    ax[2].scatter(timevec, _o1, s=40, marker="o")
    ax[2].plot(timevec, _o2, label="o2")
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
        if not _ax == ax[-1]:
            _ax.set_xticklabels([])

    ax[-1].set_xlabel("Time [ms]")

    plt.savefig("/tmp/stdp_triplets_[delay=" + "%.3f" % syn_opts["delay"] + "].png", dpi=150.)


@pytest.mark.parametrize('delay', [1., 5., 14.3])
#@pytest.mark.parametrize('spike_times_len', [1, 10, 100])
@pytest.mark.parametrize('spike_times_len', [10])
def test_stdp_triplet_synapse(delay, spike_times_len):
    print("Running test for delay = " + str(delay) + ", spike_times_len = " + str(spike_times_len))

    experiment = "test_nestml_dyad_synapse"
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

    if experiment == "test_nestml_dyad_synapse":
        nest_modules_to_load = ["nestml_triplet_dyad_module"]

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
    #pre_spike_times=np.array([  2.,   3.,   7.,   8.,   9.,  10.,  12.,  17.,  19.,  21.,  22.,  24.,  25.,  26.,
        #28.,  30.,  36.,  37.,  38.,  40.,  43.,  46.,  47.,  48.,  49.,  50.,  51.,  52.,
        #53.,  55.,  58.,  59.,  60.,  62.,  64.,  65.,  66.,  67.,  68.,  69.,  71.,  72.,
            #76.,  77.,  78.,  82.,  83.,  84.,  85.,  86.,  87.,  88.,  92.,  96.,  99., 105.,
            #113., 114., 121., 122., 124., 129., 135., 140., 152., 161., 167., 170., 183., 186.,
            #192., 202., 218., 224., 303., 311.])
    #post_spike_times = np.array([  2.,   4.,   5.,   8.,   9.,  12.,  13.,  14.,  17.,  18.,  19.,  21.,  24.,  25.,
        #26.,  28.,  30.,  32.,  34.,  37.,  38.,  40.,  42.,  44.,  45.,  46.,  49.,  50.,
        #51.,  53.,  55.,  56.,  60.,  61.,  67.,  68.,  72.,  73.,  74.,  76.,  77.,  78.,
            #79.,  81.,  82.,  84.,  87.,  88.,  93.,  95.,  96.,  98.,  99., 100., 109., 110.,
            #111., 115., 116., 118., 120., 121., 124., 125., 127., 128., 140., 144., 149., 150.,
            #152., 155., 156., 157., 163., 164., 168., 172., 204., 206., 216., 239., 243.])



    pre_spike_times = 1 + 5 * np.arange(spike_times_len).astype(float)
    post_spike_times = 1 + 5 * np.arange(spike_times_len).astype(float)


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

    print("Actual post spike times (syn. pers.): " + str(times_spikes_syn_persp))

    times_spikes_post_syn_persp = times_spikes_syn_persp[senders_spikes==gid_post]
    times_spikes_syn_persp = np.sort(times_spikes_syn_persp)

    ref_timevec, ref_w = \
        run_reference_simulation(syn_opts=syn_opts,
                                sim_time=sim_time,
                                times_spikes_pre=times_spikes_pre,
                                times_spikes_syn_persp=times_spikes_syn_persp,
                                times_spikes_post_syn_persp=times_spikes_post_syn_persp,
                                fname_snip=fname_snip)

    compare_results(ref_timevec, ref_w, nestml_timevec, nestml_w)

    plot_comparison(syn_opts, times_spikes_pre, times_spikes_post, times_spikes_post_syn_persp, ref_timevec, ref_w, nestml_timevec, nestml_w, sim_time)
    
    import pdb;pdb.set_trace()