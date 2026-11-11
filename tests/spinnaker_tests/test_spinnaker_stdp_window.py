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

from tests.test_utils import get_trace_at


# results of the STDP window test, keyed by ``use_exp_luts``; collected across the parametrized runs so that they can be plotted together
_stdp_window_results = {}

# results of the repeated-pairing drift test, keyed by ``use_exp_luts``
_stdp_drift_results = {}


class TestSpiNNakerSTDPWindow:
    """Test that STDP synapse produces correct STDP window"""

    @pytest.fixture
    def generate_code(self, request):
        use_exp_luts: bool = request.param
        print(f"\nGenerating code with use_exp_luts = {use_exp_luts}")

        codegen_opts = {"neuron_synapse_pairs": [{"neuron": "iaf_psc_exp_neuron",
                                                  "synapses": {"stdp_synapse": {"post_ports": ["post_spikes"]}}}],
                        "weight_variable": {"stdp_synapse": "w"},
                        "use_exp_luts": use_exp_luts}

        files = [
            os.path.join("models", "neurons", "iaf_psc_exp_with_ignore_neuron.nestml"),
            os.path.join("models", "synapses", "stdp_additive_synapse.nestml")
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

        yield use_exp_luts

    def run_reference_simulation(self,
                                 syn_opts,
                                 sim_time=None,  # if None, computed from pre and post spike times
                                 times_spikes_pre=None,
                                 times_spikes_post_syn_persp=None,
                                 initial_weight=1.,
                                 fname_snip="",
                                 debug=True):

        log = {}

        log[0.] = {"weight": initial_weight,
                   "pre_trace": 0.,
                   "post_trace": 0.}

        weight = initial_weight
        last_t_sp = 0.
        for spk_time in np.unique(np.sort(np.hstack([times_spikes_pre, times_spikes_post_syn_persp]))):
            pre_trace = get_trace_at(spk_time, times_spikes_pre, syn_opts["tau_pre_trace"], before_increment=False, extra_debug=debug)
            post_trace = get_trace_at(spk_time, times_spikes_post_syn_persp, syn_opts["tau_post_trace"], before_increment=False, extra_debug=debug)

            # process post spike?
            if spk_time in times_spikes_post_syn_persp:
                old_weight = weight
                weight = old_weight + syn_opts["lambda"] * pre_trace
                if debug:
                    print("[REF] t = " + str(spk_time) + ": facilitating from " + str(old_weight) + " to " + str(weight) + " with pre tr = " + str(pre_trace))

            # process pre spike?
            if spk_time in times_spikes_pre:
                old_weight = weight
                weight = old_weight - syn_opts["lambda"] * post_trace
                if debug:
                    print("[REF] t = " + str(spk_time) + ": depressing from " + str(old_weight) + " to " + str(weight) + " with post tr = " + str(post_trace))

            log[spk_time] = {"weight": weight,
                             "pre_trace": pre_trace,
                             "post_trace": post_trace}

            last_t_sp = spk_time

        timevec = np.sort(list(log.keys()))
        weight_reference = np.array([log[t]["weight"] for t in timevec])

        return weight_reference[-1] - initial_weight    # return the final weight minus the initial weight


    def run_sim(self, pre_spike_times, post_spike_times, syn_opts, sim_time=1100, initial_weight=1., n_pre_neurons=1, n_post_neurons=1):
        import pyNN.spiNNaker as p

        from python_models8.neuron.builds.iaf_psc_exp_neuron_nestml import iaf_psc_exp_neuron_nestml as iaf_psc_exp_neuron_nestml
        from python_models8.neuron.implementations.stdp_synapse_nestml_impl import stdp_synapse_nestmlDynamics as stdp_synapse_nestml

        assert len(pre_spike_times) == n_pre_neurons
        assert len(post_spike_times) == n_post_neurons

        use_NESTML = True

        p.setup(timestep=1.0)
        if use_NESTML:
            exc_input = "exc_spikes"
        else:
            exc_input = "excitatory"

        # inputs for pre and post synaptic neurons
        pre_input = p.Population(n_pre_neurons, p.SpikeSourceArray(pre_spike_times), label="pre_input")
        post_input = p.Population(n_post_neurons, p.SpikeSourceArray(post_spike_times), label="post_input")

        # pre and post synaptic spiking neuron populations
        if use_NESTML:
            pre_spiking = p.Population(n_pre_neurons, iaf_psc_exp_neuron_nestml(), label="pre_spiking")
            post_spiking = p.Population(n_post_neurons, iaf_psc_exp_neuron_nestml(), label="post_spiking")
        else:
            pre_spiking = p.Population(n_pre_neurons, p.IF_curr_exp(), label="pre_spiking")
            post_spiking = p.Population(n_post_neurons, p.IF_curr_exp(), label="post_spiking")

        weight_pre = 5000
        weight_post = 5000

        p.Projection(pre_input, pre_spiking, p.OneToOneConnector(), receptor_type=exc_input, synapse_type=p.StaticSynapse(weight=weight_pre))
        p.Projection(post_input, post_spiking, p.OneToOneConnector(), receptor_type=exc_input, synapse_type=p.StaticSynapse(weight=weight_post))

        #stdp_model._nestml_model_variables["tau_tr_pre"] = 20.
        #stdp_model._nestml_model_variables["tau_tr_post"] = 20.
        if use_NESTML:
            stdp_model = stdp_synapse_nestml(weight=initial_weight)
            stdp_model._nestml_model_variables["lambda"] = syn_opts["lambda"]
            stdp_projection = p.Projection(pre_spiking, post_spiking, p.AllToAllConnector(), synapse_type=stdp_model, receptor_type="ignore_spikes")   # connect to a port where incoming spikes are ignored, so the STDP synapse itself does not change the postsynaptic spike timing
        else:
            stdp_model = p.Projection(pre_spiking, post_spiking, p.AllToAllConnector(), synapse_type=stdp_model, receptor_type="excitatory")   # connect to a port where incoming spikes are ignored, so the STDP synapse itself doe>
            stdp_projection = p.Projection(pre_spiking, post_spiking, p.AllToAllConnector(), synapse_type=stdp_model, receptor_type="excitatory")   # connect to a port where incoming spikes are ignored, so the STDP synapse itself does not change the postsynaptic spike timing
        print("[NESTML synapse] Synapse parameters: " + str(stdp_model._nestml_model_variables))
            #for k, v in syn_opts.items():
            #    stdp_projection[i].set(k, v)
#        stdp_projection = p.Projection(pre_spiking, post_spiking, p.AllToAllConnector(), synapse_type=stdp_model, receptor_type="exc_spikes")   # connect to a port where incoming spikes are ignored, so the STDP synapse itself does not change the postsynaptic spike timing

        pre_spiking.record(["spikes"])
        post_spiking.record(["spikes"])

        p.run(sim_time)

        pre_neo = pre_spiking.get_data("spikes")
        post_neo = post_spiking.get_data("spikes")

        actual_pre_spike_times = pre_neo.segments[0].spiketrains
        actual_post_spike_times = post_neo.segments[0].spiketrains

        w_final = stdp_projection.get("weight", format="float")    # get the weight at the end of the simulation

        p.end()

        return w_final, actual_pre_spike_times, actual_post_spike_times


    def compute_continuous_reference(self, syn_opts, pre_spike_times, dt_min, dt_max, initial_weight=1., n_points=501):
        r"""Evaluate the reference STDP window on a dense grid of (post - pre) spike time differences, for plotting"""
        pre_spike_times = np.array(pre_spike_times)
        dt_axis = np.linspace(dt_min, dt_max, n_points)
        dw_axis = np.empty_like(dt_axis)
        for i, dt in enumerate(dt_axis):
            dw_axis[i] = self.run_reference_simulation(syn_opts,
                                                       times_spikes_pre=pre_spike_times,
                                                       times_spikes_post_syn_persp=np.array([pre_spike_times[0] + dt]) + syn_opts["delay"],
                                                       initial_weight=initial_weight,
                                                       debug=False)

        return dt_axis, dw_axis

    def plot_stdp_window(self, syn_opts, initial_weight=1.):
        r"""Plot the STDP window for all runs (exp LUTs on/off) collected so far, together with the reference"""
        if not _stdp_window_results:
            return

        # the ideal reference is taken from the first available run
        first_result = next(iter(_stdp_window_results.values()))
        all_dt = np.hstack([r["spike_time_axis"] for r in _stdp_window_results.values()])
        dt_cont, dw_cont = self.compute_continuous_reference(syn_opts,
                                                             first_result["pre_spike_times"],
                                                             dt_min=np.amin(all_dt),
                                                             dt_max=np.amax(all_dt),
                                                             initial_weight=initial_weight)

        run_styles = {True: {"color": "tab:orange", "marker": "o", "label": "NESTML (exp LUTs)"},
                      False: {"color": "tab:green", "marker": "s", "label": "NESTML (no exp LUTs)"}}

        fig, (ax, ax_err) = plt.subplots(2, 1, sharex=True, figsize=(6.4, 6.), gridspec_kw={"height_ratios": [3, 1]})

        ax.plot(dt_cont, dw_cont, '-', color="grey", alpha=.4, linewidth=1., zorder=0)
        ax.plot(first_result["spike_time_axis"], first_result["ref_weights"], 'x', color="tab:blue", markersize=8, label="ref")
        for use_exp_luts, result in _stdp_window_results.items():
            style = run_styles[use_exp_luts]
            ax.plot(result["spike_time_axis"], result["sim_weights"], linestyle="none", marker=style["marker"], markerfacecolor="none", color=style["color"], label=style["label"])
            ax_err.plot(result["spike_time_axis"], result["sim_weights"] - result["ref_weights"], linestyle="none", marker=style["marker"], markerfacecolor="none", color=style["color"], label=style["label"])

        ax.set_ylabel(r"$\Delta w$")
        ax.set_title("STDP-Window")
        ax.grid(True)
        ax.legend()

        ax_err.axhline(0., color="grey", alpha=.4, linewidth=1., zorder=0)
        ax_err.set_xlabel(r"$t_\mathrm{post} - t_\mathrm{pre}$ [ms]")
        ax_err.set_ylabel(r"$\Delta w - \Delta w_\mathrm{ref}$")
        ax_err.grid(True)

        fig.tight_layout()
        fig.savefig("nestml_stdp_window.png")
        plt.close(fig)

    @pytest.mark.parametrize("generate_code", [True, False], indirect=True)
    def test_stdp_window(self, generate_code):
        r"""Test that the STDP window matches that of a reference simulation"""
        use_exp_luts = generate_code
        assert use_exp_luts in [True, False]

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

#       for t_post in np.linspace(200, 300, 7):#[:1]:
        for t_post in np.linspace(200, 300, 7): #XX: was 19
                w_final, actual_pre_spike_times, actual_post_spike_times = self.run_sim([pre_spike_times],
                                                                                        [[t_post]],
                                                                                        syn_opts,
                                                                                        initial_weight=initial_weight)
                dw = w_final[0][0] - initial_weight

                sim_weights.append(dw)

                dw_ref = self.run_reference_simulation(syn_opts,
                                                       times_spikes_pre=np.array(actual_pre_spike_times)[0],
                                                       times_spikes_post_syn_persp=np.array(actual_post_spike_times)[0] + syn_opts["delay"],
                                                       initial_weight=initial_weight)
                ref_weights.append(dw_ref)

                spike_time_axis.append(float(actual_post_spike_times[0][0]) - float(actual_pre_spike_times[0][0]))

                print("actual pre_spikes: " + str(actual_pre_spike_times))
                print("actual post_spikes: " + str(actual_post_spike_times))
                print("delta weight after simulation: " + str(dw))
                print("delta weight after simulation (ref): " + str(dw_ref))

        ref_weights = np.array(ref_weights)
        sim_weights = np.array(sim_weights)

        print("Simulation results")
        print("------------------")
        print("post - pre spike times = " + str(spike_time_axis))
        print("delta weights after sim = " + str(sim_weights))
        print("delta weights after ref sim = " + str(ref_weights))

        _stdp_window_results[use_exp_luts] = {"spike_time_axis": np.array(spike_time_axis),
                                              "sim_weights": sim_weights,
                                              "ref_weights": ref_weights,
                                              "pre_spike_times": np.array(actual_pre_spike_times[0]).astype(float)}

        self.plot_stdp_window(syn_opts, initial_weight=initial_weight)

        # testing

        atol = 2 / 2**16    # twice LSB tolerance of S1516 format
        np.testing.assert_allclose(sim_weights, ref_weights, atol=atol, rtol=np.inf)

    def run_sim_with_weight_readout(self, pre_spike_times, post_spike_times, syn_opts, readout_times, initial_weight=1.):
        r"""Run a single pre/post neuron pair, and read out the weight of the STDP synapse at each of the times in ``readout_times`` by running the simulation in chunks"""
        import pyNN.spiNNaker as p

        from python_models8.neuron.builds.iaf_psc_exp_neuron_nestml import iaf_psc_exp_neuron_nestml as iaf_psc_exp_neuron_nestml
        from python_models8.neuron.implementations.stdp_synapse_nestml_impl import stdp_synapse_nestmlDynamics as stdp_synapse_nestml

        p.setup(timestep=1.0)

        pre_input = p.Population(1, p.SpikeSourceArray(pre_spike_times), label="pre_input")
        post_input = p.Population(1, p.SpikeSourceArray(post_spike_times), label="post_input")

        pre_spiking = p.Population(1, iaf_psc_exp_neuron_nestml(), label="pre_spiking")
        post_spiking = p.Population(1, iaf_psc_exp_neuron_nestml(), label="post_spiking")

        p.Projection(pre_input, pre_spiking, p.OneToOneConnector(), receptor_type="exc_spikes", synapse_type=p.StaticSynapse(weight=5000))
        p.Projection(post_input, post_spiking, p.OneToOneConnector(), receptor_type="exc_spikes", synapse_type=p.StaticSynapse(weight=5000))

        stdp_model = stdp_synapse_nestml(weight=initial_weight)
        stdp_model._nestml_model_variables["lambda"] = syn_opts["lambda"]
        stdp_projection = p.Projection(pre_spiking, post_spiking, p.AllToAllConnector(), synapse_type=stdp_model, receptor_type="ignore_spikes")   # connect to a port where incoming spikes are ignored, so the STDP synapse itself does not change the postsynaptic spike timing

        pre_spiking.record(["spikes"])
        post_spiking.record(["spikes"])

        weights = []
        t = 0.
        for t_readout in readout_times:
            p.run(t_readout - t)
            t = t_readout
            weights.append(stdp_projection.get("weight", format="float")[0][0])

        actual_pre_spike_times = np.array(pre_spiking.get_data("spikes").segments[0].spiketrains[0]).astype(float)
        actual_post_spike_times = np.array(post_spiking.get_data("spikes").segments[0].spiketrains[0]).astype(float)

        p.end()

        return np.array(weights), actual_pre_spike_times, actual_post_spike_times

    def compute_reference_weight_at(self, syn_opts, t, pre_spike_times, post_spike_times, initial_weight=1.):
        r"""Compute the reference weight as it would be read out from SpiNNaker at time ``t``.

        On SpiNNaker, postsynaptic spikes are only buffered when they occur; the corresponding weight updates are deferred until the next presynaptic spike is processed. The weight read out at time ``t`` therefore reflects all presynaptic spikes up to ``t``, but only those postsynaptic spikes that arrived (in the synaptic perspective, i.e. including the dendritic delay) up to the last of those presynaptic spikes."""
        pre_spike_times = pre_spike_times[pre_spike_times <= t]
        if len(pre_spike_times) == 0:
            return initial_weight

        post_spike_times_syn_persp = post_spike_times + syn_opts["delay"]
        post_spike_times_syn_persp = post_spike_times_syn_persp[post_spike_times_syn_persp <= pre_spike_times[-1]]

        return initial_weight + self.run_reference_simulation(syn_opts,
                                                              times_spikes_pre=pre_spike_times,
                                                              times_spikes_post_syn_persp=post_spike_times_syn_persp,
                                                              initial_weight=initial_weight,
                                                              debug=False)

    def plot_stdp_drift(self, syn_opts):
        r"""Plot the weight over time for all runs (exp LUTs on/off) collected so far, together with the reference"""
        if not _stdp_drift_results:
            return

        lsb = 2**-16    # LSB of S1516 format

        run_styles = {True: {"color": "tab:orange", "marker": "o", "label": "NESTML (exp LUTs)"},
                      False: {"color": "tab:green", "marker": "s", "label": "NESTML (no exp LUTs)"}}

        fig, (ax, ax_err) = plt.subplots(2, 1, sharex=True, figsize=(6.4, 6.), gridspec_kw={"height_ratios": [2, 2]})

        first_result = next(iter(_stdp_drift_results.values()))
        ax.plot(first_result["readout_times"], first_result["ref_weights"], 'x-', color="tab:blue", markersize=8, label="ref")
        for use_exp_luts, result in _stdp_drift_results.items():
            style = run_styles[use_exp_luts]
            ax.plot(result["readout_times"], result["sim_weights"], linestyle="none", marker=style["marker"], markerfacecolor="none", color=style["color"], label=style["label"])
            ax_err.plot(result["readout_times"], (result["sim_weights"] - result["ref_weights"]) / lsb, linestyle="-", marker=style["marker"], markerfacecolor="none", color=style["color"], label=style["label"])

        ax.set_ylabel("$w$")
        ax.set_title(r"Repeated pairings ($\lambda$ = " + str(syn_opts["lambda"]) + ")")
        ax.grid(True)
        ax.legend()

        ax_err.axhline(0., color="grey", alpha=.4, linewidth=1., zorder=0)
        ax_err.set_xlabel("Time [ms]")
        ax_err.set_ylabel(r"$w - w_\mathrm{ref}$ [S1516 LSB]")
        ax_err.grid(True)
        ax_err.legend()

        fig.tight_layout()
        fig.savefig("nestml_stdp_drift.png")
        plt.close(fig)

    @pytest.mark.parametrize("generate_code", [True, False], indirect=True)
    def test_stdp_drift_repeated_pairings(self, generate_code):
        r"""Show the accumulation of weight error over many repeated, identical pre/post spike pairings.

        The exp() look-up table stores ``floor(exp(-k / tau) * 2048)``, so every lookup underestimates the decay factor by up to 1/2048. Because this error is a bias (always of the same sign) rather than noise, it accumulates linearly over repeated pairings.

        The pairing period is chosen much longer than the LUT length (about 7.6 tau), so that each pairing is isolated: the traces are exactly reset between pairings and the depression term from the previous postsynaptic spike is negligible. Each pairing thus contributes the same potentiation error (``lambda`` times the LUT error at the given spike time difference)."""
        use_exp_luts = generate_code
        assert use_exp_luts in [True, False]

        syn_opts = {
            "delay": 1.,  # dendritic delay [ms]
            "tau_pre_trace": 20.,
            "tau_post_trace": 20.,
            "lambda": .1}

        initial_weight = 1.
        t_start = 50.               # time of the first pairing [ms]
        pairing_period = 250.       # [ms]; should be longer than the LUT (~154 ms for tau = 20 ms)
        pairing_dt = 3.             # post minus pre input spike time [ms]; with dendritic delay, this gives a synaptic perspective dt of 4 ms, where the LUT error is large (~0.76/2048), and also large at +/- 1 ms
        n_pairings = 40
        pairings_per_readout = 4

        pre_spike_times = t_start + pairing_period * np.arange(n_pairings)
        post_spike_times = pre_spike_times + pairing_dt

        # read out halfway between pairings, so that the last presynaptic spike has been processed
        readout_times = t_start + pairing_period * (pairings_per_readout * np.arange(1, n_pairings // pairings_per_readout + 1) - .5)

        sim_weights, actual_pre_spike_times, actual_post_spike_times = self.run_sim_with_weight_readout(list(pre_spike_times),
                                                                                                        list(post_spike_times),
                                                                                                        syn_opts,
                                                                                                        readout_times,
                                                                                                        initial_weight=initial_weight)

        ref_weights = np.array([self.compute_reference_weight_at(syn_opts,
                                                                 t,
                                                                 actual_pre_spike_times,
                                                                 actual_post_spike_times,
                                                                 initial_weight=initial_weight) for t in readout_times])

        print("Simulation results")
        print("------------------")
        print("actual pre spikes: " + str(actual_pre_spike_times))
        print("actual post spikes: " + str(actual_post_spike_times))
        print("readout times = " + str(readout_times))
        print("weights after sim = " + str(sim_weights))
        print("weights after ref sim = " + str(ref_weights))
        print("difference [S1516 LSB] = " + str((sim_weights - ref_weights) * 2**16))

        _stdp_drift_results[use_exp_luts] = {"readout_times": readout_times,
                                             "sim_weights": sim_weights,
                                             "ref_weights": ref_weights}

        self.plot_stdp_drift(syn_opts)

        # testing: allow for one LSB of weight rounding per weight update (one potentiation and one depression per pairing), plus (if LUTs are used) the worst-case LUT error per lookup
        lsb = 2**-16    # LSB of S1516 format
        n_pairings_processed = np.array([np.sum(actual_pre_spike_times <= t) for t in readout_times])
        atol_per_pairing = 2 * lsb
        if use_exp_luts:
            atol_per_pairing += 2 * syn_opts["lambda"] / 2048
        atol = 2 * lsb + n_pairings_processed * atol_per_pairing
        assert np.all(np.abs(sim_weights - ref_weights) <= atol)


    """def run_reference_simulation(self,syn_opts,
                                 times_spikes_pre=None,
                                 times_spikes_post=None,
                                 fname_snip=""):

        log = {}
        weight = syn_opts["w_init"]

        last_t_sp = 0.
        log[0.] = {"weight": weight}

        for spk_time in np.unique(times_spikes_syn_persp):
            if spk_time in times_spikes_post_syn_persp:
                pre_tr = get_trace_at(spk_time, times_spikes_pre,
                                   syn_opts["tau_plus"], before_increment=False, extra_debug=True)
                old_weight = weight
                weight = weight + pre_tr * syn_opts["lambda"]
                print("[REF] t = " + str(spk_time) + ": facilitating from " + str(old_weight) + " to " + str(weight) + " with pre tr = " + str(pre_tr))

            if spk_time in times_spikes_pre:
                post_tr = get_trace_at(spk_time, times_spikes_post_syn_persp,
                                  syn_opts["tau_minus"], before_increment=False, extra_debug=True)
                old_weight = weight
                weight = weight - post_tr * syn_opts["lambda"]
                print("[REF] t = " + str(spk_time) + ": depressing from " + str(old_weight) + " to " + str(weight) + " with post tr = " + str(post_tr))

            log[spk_time] = {"weight": weight}

            last_t_sp = spk_time

        timevec = np.sort(list(log.keys()))
        weight_reference = np.array([log[k]["weight"] for k in timevec])

        return timevec, weight_reference"""

    def compute_weight_from_spike_trains(self, syn_opts, pre_spike_times, post_spike_times):
        dw = self.run_reference_simulation(syn_opts,
                                                                  times_spikes_pre=pre_spike_times,
                                                                  times_spikes_post_syn_persp=np.array(post_spike_times) + syn_opts["delay"],
                                                                  initial_weight=1.)
        return dw

    '''def test_multiple_stdp_synapses(self):
        r"""Check that multiple STDP synapses onto the same postsynaptic neuron do not influence one another."""

        # XXX: TODO: add static synapses too!!!!!! and check that they don´t change or change anything else!

        n_pre_neurons = 3
        n_post_neurons = 4

        syn_opts = {
            "delay": 1.,  # dendritic delay [ms]
            "tau_pre_trace": 20.,
            "tau_post_trace": 20.,
            "lambda": .01}

        sim_weights = []
        spike_time_axis = []
        initial_weight = 1.

        #pre_spike_times = [250, 1000]
        n_pre_spike_times = 10
        n_post_spike_times = 10
        pre_spike_times = [list(10. + np.cumsum(np.random.randint(low=2, high=50, size=n_pre_spike_times))) for _ in range(n_pre_neurons)]
        post_spike_times = [list(10. + np.cumsum(np.random.randint(low=2, high=50, size=n_post_spike_times))) for _ in range(n_post_neurons)]
        assert len([t_sp for t_sp in pre_spike_times + post_spike_times if t_sp in pre_spike_times and t_sp in post_spike_times]) == 0

        sim_time = max(np.max(pre_spike_times), np.max(post_spike_times))

        for pre_spike_times_ in pre_spike_times:
            pre_spike_times_.append(sim_time + 10)

        sim_time += 20

        w, actual_pre_spike_times, actual_post_spike_times = self.run_sim(pre_spike_times,
                                                                          post_spike_times,
                                                                          n_pre_neurons=n_pre_neurons,
                                                                          n_post_neurons=n_post_neurons,
                                                                          sim_time=sim_time)

        atol = 2 / 2**16    # twice LSB tolerance of S1516 format
        for pre_idx in range(n_pre_neurons):
            assert len(actual_pre_spike_times[pre_idx]) > n_pre_spike_times // 2
            for post_idx in range(n_post_neurons):
                assert len(actual_post_spike_times[post_idx]) > n_post_spike_times // 2
                np.testing.assert_allclose(w[pre_idx, post_idx],
                                           initial_weight + self.compute_weight_from_spike_trains(syn_opts, np.array(actual_pre_spike_times[pre_idx]), np.array(actual_post_spike_times[post_idx])),
                                           atol=atol, rtol=np.inf)
'''
