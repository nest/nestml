# -*- coding: utf-8 -*-
#
# test_spinnaker_stdp_window.py
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

import os
import matplotlib.pyplot as plt
import numpy as np
import pytest

from pynestml.frontend.pynestml_frontend import generate_spinnaker_target


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



class TestSpiNNakerSTDPWindow:
    """Test that STDP synapse produces correct STDP window"""

    @pytest.fixture(autouse=True,
                    scope="module")
    def generate_code(self):
        codegen_opts = {"neuron_synapse_pairs": [{"neuron": "iaf_psc_exp_neuron",
                                                  "synapse": "stdp_synapse",
                                                  "post_ports": ["post_spikes"]}],
                        "delay_variable":{"stdp_synapse":"d"},
                        "weight_variable":{"stdp_synapse":"w"}}

        files = [
            os.path.join("models", "neurons", "iaf_psc_exp_neuron.nestml"),
            os.path.join("models", "synapses", "stdp_synapse.nestml")
        ]
        input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, s))) for s in files]
        target_path = "spinnaker-target"
        install_path = "spinnaker-install"
        logging_level = "DEBUG"
        suffix = "_nestml"
        generate_spinnaker_target(input_path,
                                  target_path=target_path,
                                  install_path=install_path,
                                  logging_level=logging_level,
                                  suffix=suffix,
                                  codegen_opts=codegen_opts)


    def run_reference_simulation(self,
                                 syn_opts,
                                 sim_time=None,  # if None, computed from pre and post spike times
                                 times_spikes_pre=None,
                                 times_spikes_post_syn_persp=None,
                                 initial_weight=1.,
                                 fname_snip=""):

        log = {}

        log[0.] = {"weight": initial_weight,
                   "pre_trace": 0.,
                   "post_trace": 0.}

        weight = initial_weight
        last_t_sp = 0.
        for spk_time in np.unique(np.sort(np.hstack([times_spikes_pre, times_spikes_post_syn_persp]))):
            pre_trace = get_trace_at(spk_time, times_spikes_pre, syn_opts["tau_pre_trace"], before_increment=False, extra_debug=True)
            post_trace = get_trace_at(spk_time, times_spikes_post_syn_persp, syn_opts["tau_post_trace"], before_increment=False, extra_debug=True)

            # process post spike?
            if spk_time in times_spikes_post_syn_persp:
                old_weight = weight
                weight = old_weight + syn_opts["lambda"] * pre_trace
                print("[REF] t = " + str(spk_time) + ": facilitating from " + str(old_weight) + " to " + str(weight) + " with pre tr = " + str(pre_trace))

            # process pre spike?
            if spk_time in times_spikes_pre:
                old_weight = weight
                weight = old_weight - syn_opts["lambda"] * post_trace
                print("[REF] t = " + str(spk_time) + ": depressing from " + str(old_weight) + " to " + str(weight) + " with post tr = " + str(post_trace))

            log[spk_time] = {"weight": weight,
                             "pre_trace": pre_trace,
                             "post_trace": post_trace}

            last_t_sp = spk_time

        timevec = np.sort(list(log.keys()))
        weight_reference = np.array([log[t]["weight"] for t in timevec])

        return weight_reference[-1] - initial_weight    # return the final weight minus the initial weight


    def run_sim(self, pre_spike_times, post_spike_times, simtime=1100, initial_weight=1.):
        import pyNN.spiNNaker as p
        from pyNN.utility.plotting import Figure, Panel

        from python_models8.neuron.builds.iaf_psc_exp_neuron_nestml import iaf_psc_exp_neuron_nestml as iaf_psc_exp_neuron_nestml
        from python_models8.neuron.implementations.stdp_synapse_nestml_impl import stdp_synapse_nestmlDynamics as stdp_synapse_nestml

        n_synapses = 3    # test with more than one synapse at a time (check that synapses with different dynamics do not interfere with one another)

#        p.reset()
        p.setup(timestep=1.0)
        exc_input = "exc_spikes"

        #inputs for pre and post synaptic neurons
        pre_input = p.Population(1, p.SpikeSourceArray(spike_times=[0]), label="pre_input")
        post_input = p.Population(1, p.SpikeSourceArray(spike_times=[0]), label="post_input")

        #pre and post synaptic spiking neuron populations
        pre_spiking = p.Population(1, iaf_psc_exp_neuron_nestml(), label="pre_spiking")
        post_spiking = p.Population(1, iaf_psc_exp_neuron_nestml(), label="post_spiking")

        weight_pre = 3000
        weight_post = 3000

        p.Projection(pre_input, pre_spiking, p.OneToOneConnector(), receptor_type=exc_input, synapse_type=p.StaticSynapse(weight=weight_pre))
        p.Projection(post_input, post_spiking, p.OneToOneConnector(), receptor_type=exc_input, synapse_type=p.StaticSynapse(weight=weight_post))

        stdp_projection = n_synapses * [None]
        for i in range(n_synapses):
            stdp_model = stdp_synapse_nestml(weight=initial_weight)
            if i == 0:
                print("0")
                stdp_model._nestml_model_variables["tau_tr_pre"] = 10.
                stdp_model._nestml_model_variables["tau_tr_post"] = 10.
            elif i == 1:
                stdp_model._nestml_model_variables["tau_tr_pre"] = 20.
                print("1")
                stdp_model._nestml_model_variables["tau_tr_post"] = 20.
            elif i == 2:
                print("2")
                stdp_model._nestml_model_variables["tau_tr_pre"] = 40.
                stdp_model._nestml_model_variables["tau_tr_post"] = 40.
            stdp_projection[i] = p.Projection(pre_spiking, post_spiking, p.AllToAllConnector(), synapse_type=stdp_model, receptor_type="ignore_spikes")   # connect to a port where incoming spikes are ignored, so the STDP synapse itself does not change the postsynaptic spike timing
            print(stdp_model._nestml_model_variables)
            #for k, v in syn_opts.items():
            #    stdp_projection[i].set(k, v)
#        stdp_projection = p.Projection(pre_spiking, post_spiking, p.AllToAllConnector(), synapse_type=stdp_model, receptor_type="exc_spikes")   # connect to a port where incoming spikes are ignored, so the STDP synapse itself does not change the postsynaptic spike timing

        pre_spiking.record(["spikes"])
        post_spiking.record(["spikes"])

        pre_input.set(spike_times=pre_spike_times)
        post_input.set(spike_times=post_spike_times)

        p.run(simtime)

        pre_neo = pre_spiking.get_data("spikes")
        post_neo = post_spiking.get_data("spikes")

        pre_spike_times = pre_neo.segments[0].spiketrains
        post_spike_times = post_neo.segments[0].spiketrains

        w_final = np.empty((n_synapses, ))
        for i in range(n_synapses):
            w_final[i] = stdp_projection[i].get("weight", format="float")[0][0]    # get the weight at the end of the simulation

        dw = w_final - initial_weight

        p.end()

        import pdb;pdb.set_trace()

        return dw, pre_spike_times, post_spike_times


    def test_stdp(self):

        syn_opts = {
            "delay": 1.,  # dendritic delay [ms]
            "tau_pre_trace": 20.,
            "tau_post_trace": 20.,
            "lambda": .01}

        ref_weights = []
        sim_weights = []
        spike_time_axis = []
        initial_weight = 1.

        pre_spike_times = [250, 1000]

        for t_post in np.linspace(200, 300, 7):  # XXX Should be 19
                dw, actual_pre_spike_times, actual_post_spike_times = self.run_sim(pre_spike_times, [t_post])
                sim_weights.append(dw)

                dw_ref = np.empty((3))
                for i in range(3):
                    if i == 0:
                        syn_opts["tau_pre_trace"] = 10.
                        syn_opts["tau_post_trace"] = 10.
                    elif i == 1:
                        syn_opts["tau_pre_trace"] = 20.
                        syn_opts["tau_post_trace"] = 20.
                    elif i == 2:
                        syn_opts["tau_pre_trace"] = 40.
                        syn_opts["tau_post_trace"] = 40.
                    dw_ref[i] = self.run_reference_simulation(
                                 syn_opts,
                                 times_spikes_pre=np.array(actual_pre_spike_times)[0],
                                 times_spikes_post_syn_persp=np.array(actual_post_spike_times)[0] + syn_opts["delay"],
                                 initial_weight=1.)
                ref_weights.append(dw_ref)

                spike_time_axis.append(float(actual_post_spike_times[0][0]) - float(actual_pre_spike_times[0][0]))

                print("actual pre_spikes: " + str(actual_pre_spike_times))
                print("actual post_spikes: " + str(actual_post_spike_times))
                print("weight after simulation: " + str(dw))
                print("weight after simulation (ref): " + str(dw_ref))

        ref_weights = np.array(ref_weights)
        sim_weights = np.array(sim_weights)

        print("Simulation results")
        print("------------------")
        print("post - pre spike times = " + str(spike_time_axis))
        print("weights after sim = " + str(sim_weights))
        print("weights after ref sim = " + str(ref_weights))

        fig, ax = plt.subplots()
        ax.plot(spike_time_axis, 2 * sim_weights, '.', color="orange")
        ax.plot(spike_time_axis, ref_weights, 'x', color="blue")
        ax.set_xlabel(r"$t_\mathrm{pre} - t_\mathrm{post} [ms]$")
        ax.set_ylabel(r"$\Delta w$")
        ax.set_title("STDP-Window")
        ax.set_ylim(-syn_opts["lambda"], syn_opts["lambda"])
        ax.grid(True)
        fig.savefig("nestml_stdp_window.png")
