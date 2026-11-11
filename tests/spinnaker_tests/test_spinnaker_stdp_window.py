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


# results of the STDP window test, keyed by ``use_exp_luts`` (or "builtin" for the sPyNNaker built-in models); collected across the parametrized runs so that they can be plotted together
_stdp_window_results = {}

# results of the repeated-pairing drift test, keyed by ``use_exp_luts`` (or "builtin" for the sPyNNaker built-in models)
_stdp_drift_results = {}

# plotting styles for each of the result keys
_run_styles = {True: {"color": "tab:orange", "marker": "o", "label": "NESTML (exp LUTs)"},
               False: {"color": "tab:green", "marker": "s", "label": "NESTML (no exp LUTs)"},
               "builtin": {"color": "tab:purple", "marker": "^", "label": "sPyNNaker built-in"}}

# maximum weight for the sPyNNaker built-in STDP synapse. Just under a power of two, as this determines the weight resolution: the stored weights are 16-bit, scaled such that weights up to 2**ceil(log2(BUILTIN_W_MAX)) can be represented
BUILTIN_W_MAX = 7.9

# publication-ready figure style
plt.rcParams.update({
    # grid lines for all plots
    "axes.grid": True,
    "grid.linestyle": "--",
    "grid.alpha": 0.7,
    "grid.linewidth": 0.8,

    # font sizes
    "font.size": 14,
    "axes.labelsize": 16,
    "xtick.labelsize": 14,
    "ytick.labelsize": 14,
    "legend.fontsize": 13,
    "axes.titlesize": 16,

    # lines and markers
    "lines.linewidth": 2.,
    "lines.markersize": 8.,
    "errorbar.capsize": 4.,
    "axes.linewidth": 1.2,
    "xtick.major.width": 1.2,
    "ytick.major.width": 1.2,
    "xtick.major.size": 5.,
    "ytick.major.size": 5.,

    # output
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "pdf.fonttype": 42,    # embed TrueType fonts (rather than Type 3) in PDF/PS output, as required by many publishers
    "ps.fonttype": 42,
})


def builtin_weight_resolution():
    r"""Weight resolution of the sPyNNaker built-in STDP synapse (see ``PopulationVertex.get_ring_buffer_shifts()`` and ``__get_weight_scale()`` in sPyNNaker)"""
    ring_buffer_shift = int(np.ceil(np.log2(BUILTIN_W_MAX)))
    return 2.**(ring_buffer_shift + 1 - 16)


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


    def create_network(self, p, pre_spike_times, post_spike_times, syn_opts, initial_weight=1., n_pre_neurons=1, n_post_neurons=1, use_builtin=False):
        r"""Create the pre- and postsynaptic neurons (each driven to spike at the given times by a spike source), connected by an STDP synapse.

        If ``use_builtin`` is True, the sPyNNaker built-in ``IF_curr_exp`` neuron and ``STDPMechanism`` (``SpikePairRule`` with ``AdditiveWeightDependence``) are used instead of the NESTML-generated models; these implement the same additive STDP rule as the reference (``A_plus = A_minus = lambda``)."""
        assert len(pre_spike_times) == n_pre_neurons
        assert len(post_spike_times) == n_post_neurons

        # inputs for pre and post synaptic neurons
        pre_input = p.Population(n_pre_neurons, p.SpikeSourceArray(pre_spike_times), label="pre_input")
        post_input = p.Population(n_post_neurons, p.SpikeSourceArray(post_spike_times), label="post_input")

        if use_builtin:
            # short synaptic time constant and long refractory period so that each input spike elicits exactly one spike
            neuron_params = {"tau_syn_E": 1., "tau_refrac": 5.}
            drive_weight = 50.    # [nA]
            pre_spiking = p.Population(n_pre_neurons, p.IF_curr_exp(**neuron_params), label="pre_spiking")
            # fix the ring buffer shift of the inhibitory synapse type, which determines the weight resolution of the STDP synapse (``2**(ceil(log2(BUILTIN_W_MAX)) + 1 - 16)``)
            post_spiking = p.Population(n_post_neurons, p.IF_curr_exp(**neuron_params), label="post_spiking",
                                        additional_parameters={"max_expected_summed_weight": [drive_weight, BUILTIN_W_MAX]})

            p.Projection(pre_input, pre_spiking, p.OneToOneConnector(), receptor_type="excitatory", synapse_type=p.StaticSynapse(weight=drive_weight))
            p.Projection(post_input, post_spiking, p.OneToOneConnector(), receptor_type="excitatory", synapse_type=p.StaticSynapse(weight=drive_weight))

            stdp_model = p.STDPMechanism(timing_dependence=p.SpikePairRule(tau_plus=syn_opts["tau_pre_trace"],
                                                                           tau_minus=syn_opts["tau_post_trace"],
                                                                           A_plus=syn_opts["lambda"],
                                                                           A_minus=syn_opts["lambda"]),
                                         weight_dependence=p.AdditiveWeightDependence(w_min=0., w_max=BUILTIN_W_MAX),
                                         weight=initial_weight,
                                         delay=syn_opts["delay"])
            # connect to the inhibitory port: the strong excitatory drive still determines the postsynaptic spike timing, and the STDP synapse cannot cause additional postsynaptic spikes
            stdp_projection = p.Projection(pre_spiking, post_spiking, p.AllToAllConnector(), synapse_type=stdp_model, receptor_type="inhibitory")
        else:
            from python_models8.neuron.builds.iaf_psc_exp_neuron_nestml import iaf_psc_exp_neuron_nestml as iaf_psc_exp_neuron_nestml
            from python_models8.neuron.implementations.stdp_synapse_nestml_impl import stdp_synapse_nestmlDynamics as stdp_synapse_nestml

            pre_spiking = p.Population(n_pre_neurons, iaf_psc_exp_neuron_nestml(), label="pre_spiking")
            post_spiking = p.Population(n_post_neurons, iaf_psc_exp_neuron_nestml(), label="post_spiking")

            p.Projection(pre_input, pre_spiking, p.OneToOneConnector(), receptor_type="exc_spikes", synapse_type=p.StaticSynapse(weight=5000))
            p.Projection(post_input, post_spiking, p.OneToOneConnector(), receptor_type="exc_spikes", synapse_type=p.StaticSynapse(weight=5000))

            stdp_model = stdp_synapse_nestml(weight=initial_weight)
            stdp_model._nestml_model_variables["lambda"] = syn_opts["lambda"]
            stdp_projection = p.Projection(pre_spiking, post_spiking, p.AllToAllConnector(), synapse_type=stdp_model, receptor_type="ignore_spikes")   # connect to a port where incoming spikes are ignored, so the STDP synapse itself does not change the postsynaptic spike timing
            print("[NESTML synapse] Synapse parameters: " + str(stdp_model._nestml_model_variables))

        return pre_spiking, post_spiking, stdp_projection

    def run_sim(self, pre_spike_times, post_spike_times, syn_opts, sim_time=1100, initial_weight=1., n_pre_neurons=1, n_post_neurons=1, use_builtin=False):
        import pyNN.spiNNaker as p

        p.setup(timestep=1.0)

        pre_spiking, post_spiking, stdp_projection = self.create_network(p, pre_spike_times, post_spike_times, syn_opts,
                                                                         initial_weight=initial_weight,
                                                                         n_pre_neurons=n_pre_neurons,
                                                                         n_post_neurons=n_post_neurons,
                                                                         use_builtin=use_builtin)

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

        fig, (ax, ax_err) = plt.subplots(2, 1, sharex=True, figsize=(6.4, 6.), gridspec_kw={"height_ratios": [3, 1]})

        ax.plot(dt_cont, dw_cont, '-', color="grey", alpha=.4, linewidth=1., zorder=0)
        ax.plot(first_result["spike_time_axis"], first_result["ref_weights"], 'x', color="tab:blue", markersize=8, label="ref")
        for key, result in _stdp_window_results.items():
            style = _run_styles[key]
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

        self._run_stdp_window(results_key=use_exp_luts, use_builtin=False)

    def test_stdp_window_builtin(self):
        r"""Run the STDP window test with the sPyNNaker built-in ``IF_curr_exp`` neuron and ``STDPMechanism``, for comparison"""
        self._run_stdp_window(results_key="builtin", use_builtin=True)

    def _run_stdp_window(self, results_key, use_builtin: bool):
        syn_opts = {
            "delay": 1.,  # dendritic delay [ms]
            "tau_pre_trace": 20.,
            "tau_post_trace": 20.,
            "lambda": .1}

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
                                                                                        initial_weight=initial_weight,
                                                                                        use_builtin=use_builtin)
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

        _stdp_window_results[results_key] = {"spike_time_axis": np.array(spike_time_axis),
                                             "sim_weights": sim_weights,
                                             "ref_weights": ref_weights,
                                             "pre_spike_times": np.array(actual_pre_spike_times[0]).astype(float)}

        self.plot_stdp_window(syn_opts, initial_weight=initial_weight)

        # testing

        if use_builtin:
            # the built-in synapse truncates the weight to its (coarser) resolution after each presynaptic spike, and uses Q11 LUTs and Q11 traces
            atol = len(pre_spike_times) * builtin_weight_resolution() + 3 * syn_opts["lambda"] / 2048
        else:
            atol = 2**-15    # one LSB of the S16.15 (accum) format in which NESTML weights are stored
        np.testing.assert_allclose(sim_weights, ref_weights, atol=atol, rtol=np.inf)

    def run_sim_with_weight_readout(self, pre_spike_times, post_spike_times, syn_opts, readout_times, initial_weight=1., use_builtin=False):
        r"""Run a single pre/post neuron pair, and read out the weight of the STDP synapse at each of the times in ``readout_times`` by running the simulation in chunks"""
        import pyNN.spiNNaker as p

        p.setup(timestep=1.0)

        pre_spiking, post_spiking, stdp_projection = self.create_network(p, [pre_spike_times], [post_spike_times], syn_opts,
                                                                         initial_weight=initial_weight,
                                                                         use_builtin=use_builtin)

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
        r"""Plot the weight as a function of the number of pairings, for all runs (exp LUTs on/off) collected so far, together with the reference"""
        if not _stdp_drift_results:
            return

        lsb = 2**-15    # LSB of the S16.15 (accum) format in which NESTML weights are stored

        fig, (ax, ax_err) = plt.subplots(2, 1, sharex=True, figsize=(6.4, 6.), gridspec_kw={"height_ratios": [2, 2]})

        first_result = next(iter(_stdp_drift_results.values()))
        ax.plot(first_result["n_pairings_applied"], first_result["ref_weights"], 'x-', color="tab:blue", markersize=8, label="ref")
        for key, result in _stdp_drift_results.items():
            style = _run_styles[key]
            ax.plot(result["n_pairings_applied"], result["sim_weights"], linestyle="none", marker=style["marker"], markerfacecolor="none", color=style["color"], label=style["label"])
            ax_err.plot(result["n_pairings_applied"], (result["sim_weights"] - result["ref_weights"]) / lsb, linestyle="-", marker=style["marker"], markerfacecolor="none", color=style["color"], label=style["label"])

        ax.set_ylabel("$w$")
        ax.set_title(r"Repeated pairings ($\lambda$ = " + str(syn_opts["lambda"]) + ")")
        ax.grid(True)
        ax.legend()

        ax_err.axhline(0., color="grey", alpha=.4, linewidth=1., zorder=0)
        ax_err.set_yscale("symlog", linthresh=1.)    # logarithmic for |error| > 1 LSB (keeping the sign), linear within +/- 1 LSB so that zero error can be shown
        ax_err.set_xlabel("Number of pairings")
        ax_err.set_ylabel(r"$w - w_\mathrm{ref}$ [S16.15 LSB]")
        ax_err.grid(True)
        ax_err.legend()

        fig.tight_layout()
        fig.savefig("nestml_stdp_drift.png")
        plt.close(fig)

    @pytest.mark.parametrize("generate_code", [True, False], indirect=True)
    def test_stdp_drift_repeated_pairings(self, generate_code):
        r"""Show the accumulation of weight error over many repeated, identical pre/post spike pairings.

        The exp() look-up tables store the decay factor in Q11 fixed-point format. The NESTML-generated LUTs store ``round(exp(-k / tau) * 2048)`` (error up to 0.5/2048 of either sign); the sPyNNaker built-in LUTs store ``floor(exp(-k / tau) * 2048)`` (every lookup underestimates the decay factor by up to 1/2048). As all pairings are identical, each one looks up the same LUT entry, so the error has the same sign for every pairing and accumulates linearly.

        The pairing period is chosen much longer than the LUT length (about 7.6 tau for sPyNNaker's floored LUTs, 8.3 tau for NESTML's rounded LUTs), so that each pairing is isolated: the traces are exactly reset between pairings and the depression term from the previous postsynaptic spike is negligible. Each pairing thus contributes the same potentiation error (``lambda`` times the LUT error at the given spike time difference)."""
        use_exp_luts = generate_code
        assert use_exp_luts in [True, False]

        self._run_stdp_drift(results_key=use_exp_luts, use_builtin=False, use_exp_luts=use_exp_luts)

    def test_stdp_drift_repeated_pairings_builtin(self):
        r"""Run the repeated-pairing drift test with the sPyNNaker built-in ``IF_curr_exp`` neuron and ``STDPMechanism``, for comparison. Note that the built-in synapse always uses exp() LUTs."""
        self._run_stdp_drift(results_key="builtin", use_builtin=True, use_exp_luts=True)

    def _run_stdp_drift(self, results_key, use_builtin: bool, use_exp_luts: bool):
        syn_opts = {
            "delay": 1.,  # dendritic delay [ms]
            "tau_pre_trace": 20.,
            "tau_post_trace": 20.,
            "lambda": .1}

        initial_weight = 1.
        t_start = 50.               # time of the first pairing [ms]
        pairing_period = 250.       # [ms]; should be longer than the LUT (154 entries for sPyNNaker, 168 for NESTML, for tau = 20 ms and 1 ms time step)
        pairing_dt = 3.             # post minus pre input spike time [ms]; with dendritic delay, this gives a synaptic perspective dt of 4 ms, where the floored (sPyNNaker) LUT error is large (-0.76/2048), and also large at +/- 1 ms; the rounded (NESTML) LUT error there is +0.24/2048
        n_pairings = 40
        pairings_per_readout = 1    # increase to reduce the number of ``p.run()`` calls (and hence the run time), at the expense of fewer data points

        # one extra presynaptic spike at the end (without a postsynaptic partner) to flush the deferred weight update for the last postsynaptic spike
        pre_spike_times = t_start + pairing_period * np.arange(n_pairings + 1)
        post_spike_times = pre_spike_times[:-1] + pairing_dt

        # read out halfway between pairings, so that the last presynaptic spike has been processed
        readout_times = t_start + pairing_period * (np.arange(0, n_pairings + 1, pairings_per_readout) + .5)

        sim_weights, actual_pre_spike_times, actual_post_spike_times = self.run_sim_with_weight_readout(list(pre_spike_times),
                                                                                                        list(post_spike_times),
                                                                                                        syn_opts,
                                                                                                        readout_times,
                                                                                                        initial_weight=initial_weight,
                                                                                                        use_builtin=use_builtin)

        ref_weights = np.array([self.compute_reference_weight_at(syn_opts,
                                                                 t,
                                                                 actual_pre_spike_times,
                                                                 actual_post_spike_times,
                                                                 initial_weight=initial_weight) for t in readout_times])

        # number of pairings for which the (deferred) weight update has been applied at each readout time, i.e. the number of postsynaptic spikes (in the synaptic perspective) up to the last presynaptic spike before the readout
        n_pairings_applied = np.array([np.sum(actual_post_spike_times + syn_opts["delay"] <= np.amax(actual_pre_spike_times[actual_pre_spike_times <= t], initial=-np.inf)) for t in readout_times])

        print("Simulation results")
        print("------------------")
        print("actual pre spikes: " + str(actual_pre_spike_times))
        print("actual post spikes: " + str(actual_post_spike_times))
        print("readout times = " + str(readout_times))
        print("number of pairings applied = " + str(n_pairings_applied))
        print("weights after sim = " + str(sim_weights))
        print("weights after ref sim = " + str(ref_weights))
        print("difference [S16.15 LSB] = " + str((sim_weights - ref_weights) * 2**15))

        _stdp_drift_results[results_key] = {"n_pairings_applied": n_pairings_applied,
                                            "sim_weights": sim_weights,
                                            "ref_weights": ref_weights}

        self.plot_stdp_drift(syn_opts)

        # testing: allow for one LSB of weight rounding per pairing, plus (if LUTs are used) the worst-case LUT error per lookup
        lsb = 2**-15    # LSB of the S16.15 (accum) format in which NESTML weights are stored
        n_pairings_processed = np.array([np.sum(actual_pre_spike_times <= t) for t in readout_times])
        if use_builtin:
            # the built-in synapse truncates the weight to its (coarser) resolution after each presynaptic spike, and additionally stores the traces in Q11 format
            atol_per_pairing = builtin_weight_resolution() + syn_opts["lambda"] / 2048
        else:
            atol_per_pairing = lsb
        if use_exp_luts:
            atol_per_pairing += 2 * syn_opts["lambda"] / 2048
        atol = lsb + n_pairings_processed * atol_per_pairing
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

        atol = 2**-15    # one LSB of the S16.15 (accum) format in which NESTML weights are stored
        for pre_idx in range(n_pre_neurons):
            assert len(actual_pre_spike_times[pre_idx]) > n_pre_spike_times // 2
            for post_idx in range(n_post_neurons):
                assert len(actual_post_spike_times[post_idx]) > n_post_spike_times // 2
                np.testing.assert_allclose(w[pre_idx, post_idx],
                                           initial_weight + self.compute_weight_from_spike_trains(syn_opts, np.array(actual_pre_spike_times[pre_idx]), np.array(actual_post_spike_times[post_idx])),
                                           atol=atol, rtol=np.inf)
'''
