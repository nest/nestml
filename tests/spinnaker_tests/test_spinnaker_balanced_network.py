# -*- coding: utf-8 -*-

# test_spinnaker_balanced_network.py

# This file is part of NEST.

# Copyright (C) 2004 The NEST Initiative

# NEST is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.

# NEST is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with NEST.  If not, see <http://www.gnu.org/licenses/>.

from typing import List

import argparse
import csv
import datetime
import hashlib
import matplotlib.pyplot as plt
import numpy as np
import os
import time
import pytest

import pyNN.spiNNaker as p
from pyNN.random import RandomDistribution
from pyNN.random import NumpyRNG

from pynestml.frontend.pynestml_frontend import generate_spinnaker_target

from spinnaker_test_utils import analyze_run, figsize, plot_analog_signal, plot_spike_raster


#
#   options for saving benchmark results to file
#

csv_results_filename = "benchmark_balanced_networks_results.csv"


#
#   options for saving connections and constructing network using saved connections
#

USE_SAVED_CONNECTIONS = False


#
#   if True, initialise membrane potentials uniformly at random between E_L and V_th (instead of all at -60 mV), to avoid a synchronous volley of spikes at the start of the simulation
#

RANDOMIZE_INITIAL_V_M = True

CONNECTION_DIR = "."

EE_CONNECTION_FILE = os.path.join(CONNECTION_DIR, "ee.csv")
EI_CONNECTION_FILE = os.path.join(CONNECTION_DIR, "ei.csv")
II_CONNECTION_FILE = os.path.join(CONNECTION_DIR, "ii.csv")
IE_CONNECTION_FILE = os.path.join(CONNECTION_DIR, "ie.csv")


def spike_fingerprint(spike_trains):
    data = []

    for train in spike_trains:
        data.extend(np.asarray(train, dtype=np.float64))

    return hashlib.sha256(
        np.asarray(data, dtype=np.float64).tobytes()
    ).hexdigest()


def save_projection_connections(filename, projection):
    connections = projection.get("weight", format="list",
        with_address=True
    )

    with open(filename, "w", newline="") as csv_file:

        writer = csv.writer(csv_file)

        writer.writerow([
            "source",
            "target"
        ])

        for source, target, weight in connections:

            writer.writerow([
                int(source),
                int(target),
            ])

    print(f"Saved {len(connections)} connections to {filename}")


def load_projection_connections(filename):
    connections = []

    with open(filename, "r", newline="") as csv_file:

        reader = csv.DictReader(csv_file)

        for row in reader:

            connections.append([
                int(row["source"]),
                int(row["target"])
            ])

    return np.asarray(
        connections,
        dtype=np.float64
    )


def make_shared_input_connector(n_targets: int, q: int):
    """
    Connect each target to exactly one source, with blocks of ``q`` consecutive targets sharing the same source
    (target ``i`` receives input from source ``i // q``; there are ``ceil(n_targets / q)`` sources). For ``q == 1`` this
    is equivalent to a OneToOneConnector.

    Consecutive targets are grouped (rather than e.g. ``i % n_sources``) so that targets sharing a source end up on the
    same SpiNNaker core: each source spike then arrives as a single packet that delivers a synaptic row of length ``q``,
    which reduces the number of incoming packets per neuron core by a factor of ``q``. For this to work best, ``q``
    should divide the number of neurons per core.
    """
    if q == 1:
        return p.OneToOneConnector()

    connections = [[i // q, i] for i in range(n_targets)]

    return p.FromListConnector(connections)


def compute_cv(spike_train):
    """
    Compute the coefficient of variation (CV) for a single spike train.

    Parameters:
    spike_train (list or numpy array): Timestamps of spikes in the spike train.

    Returns:
    float: Coefficient of variation (CV) of the inter-spike intervals.
    """
    # Calculate inter-spike intervals (ISI)
    if len(spike_train) < 3:
        return np.nan

    isi = np.diff(spike_train)

    # Calculate mean and standard deviation of ISI
    mean_isi = np.mean(isi)

    if mean_isi == 0:
        return np.nan  # Avoid division by zero

    std_isi = np.std(isi)

    # Calculate coefficient of variation
    cv = std_isi / mean_isi

    return cv


def compute_cv_for_neurons(spike_trains):
    """
    Compute the average coefficient of variation (CV) for a population of neurons.
    """
    cvs = []

    for spike_train in spike_trains:

        cv = compute_cv(spike_train)

        if not np.isnan(cv):
            cvs.append(cv)

    if not cvs:
        return np.nan

    return np.mean(cvs)


def compute_average_firing_rate(spike_trains, n_neurons, t_sim):
    """
    Compute the population-average firing rate in Hz.
    """
    # Calculate the number of spikes
    total_spikes = sum(len(spike_train) for spike_train in spike_trains)

    # Convert ms to seconds
    sim_time_seconds = t_sim / 1000.0

    # Calculate average firing rate
    avg_firing_rate = total_spikes / (n_neurons * sim_time_seconds)

    return avg_firing_rate


def compare_results(builtin, results):
    """
    Compare NESTML results with the builtin implementation.
    """
    comparisons={}

    for name, result in results.items():
        if name == "builtin":
            continue

        if result is None:
            continue

        comparisons[name] = {
            "exc_relative_difference": (abs(result["exc_firing_rate"] - builtin["exc_firing_rate"]) / builtin["exc_firing_rate"]),
            "inh_relative_difference": (abs(result["inh_firing_rate"] - builtin["inh_firing_rate"]) / builtin["inh_firing_rate"]),
            "cv_absolute_difference": abs(result["cv"] - builtin["cv"]),
            "execution_time_difference": abs(result["execution_time"] - builtin["execution_time"])
        }


    return comparisons


def print_results(results, comparisons):

    print("\n===================================")
    print("RESULTS")
    print("===================================")

    for name, result in results.items():

        if result is None:
            print(f"\n{name}: SKIPPED")
            continue

        print(f"\n{name}")

        print(f"Exc. firing rate = {result['exc_firing_rate']:.3f} Hz")
        print(f"Inh. firing rate = {result['inh_firing_rate']:.3f} Hz")
        print(f"CV = {result['cv']:.3f}")

        print(f"Execution time = {result['execution_time']:.3f} s")

    if comparisons:
        print("\n===================================")
        print("REFERENCE COMPARISON")
        print("===================================")

        for name, comparison in comparisons.items():

            print(f"\nreference vs {name}")

            print(f"Exc. relative difference = {comparison['exc_relative_difference']:.2%}")
            print(f"Inh. relative difference = {comparison['inh_relative_difference']:.2%}")
            print(f"  CV absolute difference = {comparison['cv_absolute_difference']:.3f}")

            print(f"  Execution time difference = {comparison['execution_time_difference']:.3f} s")


def save_results_to_csv(results, filename):

    fieldnames = ["timestamp", "implementation", "seed", "use_static_synapses", "use_exp_luts","N", "g", "rate_ext_input", "neurons_per_core", "poisson_generators_per_core", "t_sim",
        "exc_firing_rate", "inh_firing_rate", "cv", "execution_time", "poisson_reduction_factor", "n_poisson_generators"]

    file_exists = os.path.isfile(filename)

    with open(filename, "a", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        for name, result in results.items():

            if result is None:
                continue

            row = {
                "timestamp": result["timestamp"],
                "implementation": result["implementation"],
                "seed": result["seed"],
                "use_static_synapses": result["use_static_synapses"],
                "use_exp_luts": str(result["use_exp_luts"]) if "use_exp_luts" in result.keys() else "",
                "N": result["n_neurons"],
                "g": result["g"],
                "rate_ext_input": result["rate_ext_input"],
                "neurons_per_core": result["neurons_per_core"],
                "poisson_generators_per_core": result["poisson_generators_per_core"],
                "t_sim": result["t_sim"],
                "exc_firing_rate": result["exc_firing_rate"],
                "inh_firing_rate": result["inh_firing_rate"],
                "cv": result["cv"],
                "execution_time": result["execution_time"],
                "poisson_reduction_factor": result["poisson_reduction_factor"],
                "n_poisson_generators": result["n_poisson_generators"],
            }

            writer.writerow(row)


def plot_membrane_potential(results):
    """
    Plot the membrane potential of a neuron and save the figure.
    """
    fig, ax = plt.subplots(nrows=1, figsize=figsize(4.8 / 6.4))

    ax.set_xlabel("Time [ms]")
    ax.set_ylabel("Membrane potential [mV]")
    ax.set_title(f"\nBalanced Network - {results['implementation']} | N={results['n_neurons']}, g={results['g']}, neurons/core={results['neurons_per_core']} \n"
                 f"input={results['rate_ext_input']} Hz, q={results['poisson_reduction_factor']} |\n")

    plot_analog_signal(ax, results['v_neuron'].segments[0].filter(name=results['membranePot'])[0])

    plt.savefig(
        f"spinnaker_bal_net_V_m__{results['implementation']}_{results['timestamp']}.png"
    )
    plt.close("all")


def plot_raster(results):
    """
    Plot the raster of spikes for excitatory and inhibitory populations and save the figure.
    """

    fig, ax = plt.subplots(2, 1, sharex=True, figsize=figsize(5.2 / 6))
    plot_spike_raster(ax[0], results['pop_exc_spikes'].segments[0].spiketrains, label="exc", marker=".", markersize=2, markeredgewidth=0)
    plot_spike_raster(ax[1], results['pop_inh_spikes'].segments[0].spiketrains, label="inh", marker=".", markersize=2, markeredgewidth=0)
    ax[-1].set_xlim(0, results["t_sim"])
    ax[-1].set_xlabel("Time [ms]")
    fig.suptitle(f"Balanced Network - {results['implementation']} | N={results['n_neurons']}, g={results['g']}, "
                 f"neurons/core={results['neurons_per_core']}\n"
                 f"input={results['rate_ext_input']} Hz, q={results['poisson_reduction_factor']} | "
                 f"CV={results['cv']:.3f}, "
                 f"Exc={results['exc_firing_rate']:.2f} Hz, "
                 f"Inh={results['inh_firing_rate']:.2f} Hz \n")
    fig.tight_layout()

    plt.savefig(
        f"bal_net_N{results['n_neurons']}_g{results['g']}_core{results['neurons_per_core']}_q{results['poisson_reduction_factor']}_"
        f"impl_{results['implementation']}_{results['timestamp']}.png"
    )

    plt.savefig(
        f"bal_net_N{results['n_neurons']}_g{results['g']}_core{results['neurons_per_core']}_q{results['poisson_reduction_factor']}_"
        f"impl_{results['implementation']}_{results['timestamp']}.pdf"
    )
    plt.close("all")


def plot_packets_per_timestep(results):
    """
    Plot the number of incoming spike packets per timestep for each core of the excitatory population (top), together with the total number of spikes emitted by the network per timestep (bottom), so that bursts of incoming packets can be related to bursts of network activity.
    """
    packets = results.get("packets_per_timestep")
    if packets is None:
        return

    packets_times = results["packets_times"]
    n_cores = packets.shape[1]

    # network activity: total number of exc + inh spikes per timestep (1 ms bins)
    spike_times = np.concatenate([np.asarray(st, dtype=float)
                                  for block in (results["pop_exc_spikes"], results["pop_inh_spikes"])
                                  for st in block.segments[0].spiketrains] + [np.zeros(0)])
    bin_edges = np.arange(0., results["t_sim"] + 1., 1.)
    spike_counts, _ = np.histogram(spike_times, bins=bin_edges)

    fig, ax = plt.subplots(2, 1, sharex=True, figsize=figsize(5.2 / 6))

    ax[0].plot(packets_times, packets, color="0.7", linewidth=.5)    # one line per core
    ax[0].plot([], [], color="0.7", linewidth=.5, label="per core")    # single legend entry for all cores
    ax[0].plot(packets_times, np.max(packets, axis=1), color="C0", linewidth=1., label="max over cores")
    ax[0].set_ylabel("Packets per timestep")
    ax[0].legend(loc="upper right")

    ax[1].plot(bin_edges[:-1], spike_counts, color="C0", linewidth=1.)
    ax[1].set_ylabel("Network spikes\nper timestep")
    ax[-1].set_xlim(0, results["t_sim"])
    ax[-1].set_xlabel("Time [ms]")

    for _ax in ax:
        _ax.set_ylim(bottom=0)

    fig.suptitle(f"Incoming packets (exc. pop.) - {results['implementation']} | N={results['n_neurons']}, "
                 f"neurons/core={results['neurons_per_core']} ({n_cores} cores), q={results['poisson_reduction_factor']}, "
                 f"random V_m init={results['randomize_initial_V_m']}\n"
                 f"packets/timestep/core: mean={np.mean(packets):.1f}, max={np.max(packets):.0f}")
    fig.tight_layout()

    for ext in ["png", "pdf"]:
        plt.savefig(
            f"bal_net_packets_N{results['n_neurons']}_g{results['g']}_core{results['neurons_per_core']}_q{results['poisson_reduction_factor']}_"
            f"impl_{results['implementation']}_{results['timestamp']}.{ext}"
        )

    plt.close("all")


def plot_results(results):

    for name, result in results.items():

        if result is None:
            continue

        plot_membrane_potential(result)

        plot_raster(result)

        plot_packets_per_timestep(result)


class TestSpiNNakerBalancedNetwork:
    """SpiNNaker code generation tests"""

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

    def run_balanced_network(self, n_neurons, neurons_per_core, poisson_generators_per_core, use_nestml_neuron, use_nestml_synapse, use_static_synapses: bool, poisson_reduction_factor: int = 1, randomize_initial_V_m: bool = RANDOMIZE_INITIAL_V_M):
        assert int(poisson_reduction_factor) == poisson_reduction_factor and poisson_reduction_factor >= 1, "poisson_reduction_factor must be a positive integer"
        poisson_reduction_factor = int(poisson_reduction_factor)

        from python_models8.neuron.implementations.stdp_synapse_nestml_impl import stdp_synapse_nestmlDynamics as stdp_synapse_nestml
        from python_models8.neuron.builds.iaf_psc_exp_neuron_nestml import iaf_psc_exp_neuron_nestml

        # network parameters
        eta = 0.9    # the ratio between external rate and threshold rate
        g = 10.    # the ratio between excitation and inhibition

        # simulation parameters
        t_sim = 1000    # total time to simulator for [ms]

        # neuron parameters
        V_th = -55
        E_L = -70
        C_m = 250
        tau_syn = 2
        tau_m = 10

        # population sizes
        n_exc = int(round(n_neurons * 0.8))
        n_inh = int(round(n_neurons * 0.2))

        # connectivity parameters
        K_exc = 40    # fixed
        K_inh = K_exc // 4    # fixed 4:1 E:I ratio
        K_ext = K_exc    # balance between external and recurrent drive

        # synaptic weights
        weight_exc = 1E3 * .1
        weight_inh = -g * weight_exc
        weight_input = weight_exc   # balance between the external and recurrent drive

        nu_thr = 1e3 * (V_th - E_L) * C_m / (weight_input * tau_syn * tau_m * K_ext)   # [Hz]
        print("nu_thr = " + str(nu_thr) + " Hz")
        rate_ext_input = eta * K_ext * nu_thr    # external input rate (eta parameter) [s⁻¹]


        if use_nestml_neuron:
            neuron_model = iaf_psc_exp_neuron_nestml

            receptor_name_exc = "exc_spikes"
            receptor_name_inh = "inh_spikes"
            membranePot = "V_m"

            neuron_parameters = {
                "C_m": C_m,
                "tau_m": tau_m,
                "tau_syn_inh": tau_syn,
                "tau_syn_exc": tau_syn,
                "refr_T": 2,
                "E_L": E_L,
                "V_reset": E_L,
                "V_th": V_th
            }
        else:
            neuron_model = p.IF_curr_exp

            receptor_name_exc = "excitatory"
            receptor_name_inh = "inhibitory"
            membranePot = "v"

            neuron_parameters = {
                "tau_m": tau_m,
                "cm": 1E-3 * C_m,
                "v_rest": E_L,
                "v_reset": E_L,
                "v_thresh": V_th,
                "tau_syn_E": tau_syn,
                "tau_syn_I": tau_syn,
                "tau_refrac": 2
            }

        p.setup(timestep=1.0, time_scale_factor=10)
        p.reset()
        p.set_number_of_neurons_per_core(neuron_model, neurons_per_core)
        p.set_number_of_neurons_per_core(p.SpikeSourcePoisson, poisson_generators_per_core)

        if not use_nestml_neuron:
            weight_exc *= 1E-3
            weight_inh *= 1E-3
            weight_input *= 1E-3

        # STDP Parameters
        learning_rate = 0.0
        tau_pre_trace = 20.0
        tau_post_trace = 20.0
        alpha = 1.0
        mu_plus = 1.0
        mu_minus = 1.0

        Wmin_exc = 0.0
        Wmax_exc = weight_exc * 2.0

        Wmin_inh = 0.0
        Wmax_inh = abs(weight_inh) * 2.0

        delays_exc = 1.
        weights_exc = weight_exc  # / (np.sqrt(n_neurons) / 16)

        delays_inh = 1.
        weights_inh = weight_inh # / (np.sqrt(n_neurons) / 16)

        weights_input = weight_input # / (np.sqrt(n_neurons) / 16)

        seed = 123

        # excitatory and inhibitory populations
        implementation = "nestml" if use_nestml_neuron or use_nestml_synapse else "builtin"

        # include the implementation in the population labels, so that SpiNNaker provenance warnings (dropped/late spikes etc.) can be attributed to the right run
        pop_exc = p.Population(n_exc, neuron_model, label=f"Excitatory_{implementation}", seed=seed)
        pop_inh = p.Population(n_inh, neuron_model, label=f"Inhibitory_{implementation}", seed=seed + 1)

        pop_exc.set(**neuron_parameters)
        pop_inh.set(**neuron_parameters)

        # external stimulus to exc and inh populations
        #
        # Each neuron receives input from exactly one Poisson generator with rate ``rate_ext_input`` and weight
        # ``weights_input``, independent of ``poisson_reduction_factor`` (q). For q > 1, only ceil(n / q) generators
        # are instantiated per population and each generator drives (up to) q neurons, so that the total external
        # input per neuron (rate x weight x in-degree) is unchanged; only the out-degree of the generators changes.
        # Neurons that share a generator receive identical (fully correlated) external input.
        n_stim_exc = int(np.ceil(n_exc / poisson_reduction_factor))
        n_stim_inh = int(np.ceil(n_inh / poisson_reduction_factor))
        print(f"Using {n_stim_exc} + {n_stim_inh} Poisson generators (reduction factor q = {poisson_reduction_factor})")

        pop_stim_exc = p.Population(n_stim_exc, p.SpikeSourcePoisson(rate=rate_ext_input), label=f"Stim_Exc_{implementation}", additional_parameters={"seed": seed + 2})
        p.Projection(pop_stim_exc, pop_exc, make_shared_input_connector(n_exc, poisson_reduction_factor), p.StaticSynapse(weight=weights_input, delay=1.), receptor_type=receptor_name_exc)
        pop_stim_inh = p.Population(n_stim_inh, p.SpikeSourcePoisson(rate=rate_ext_input), label=f"Stim_Inh_{implementation}", additional_parameters={"seed": seed + 3})
        p.Projection(pop_stim_inh, pop_inh, make_shared_input_connector(n_inh, poisson_reduction_factor), p.StaticSynapse(weight=weights_input, delay=1.), receptor_type=receptor_name_exc)

        # recurrent connections
        if (
            USE_SAVED_CONNECTIONS
            and os.path.exists(EE_CONNECTION_FILE)
            and os.path.exists(EI_CONNECTION_FILE)
            and os.path.exists(II_CONNECTION_FILE)
            and os.path.exists(IE_CONNECTION_FILE)
        ):

            ee_connections = load_projection_connections(
                EE_CONNECTION_FILE
            )

            ei_connections = load_projection_connections(
                EI_CONNECTION_FILE
            )

            ii_connections = load_projection_connections(
                II_CONNECTION_FILE
            )

            ie_connections = load_projection_connections(
                IE_CONNECTION_FILE
            )

            connector_ee = p.FromListConnector(
                ee_connections
            )

            connector_ei = p.FromListConnector(
                ei_connections
            )

            connector_ii = p.FromListConnector(
                ii_connections
            )

            connector_ie = p.FromListConnector(
                ie_connections
            )

            print("Loaded saved connections:")
            print("EE:", len(ee_connections))
            print("EI:", len(ei_connections))
            print("II:", len(ii_connections))
            print("IE:", len(ie_connections))

        else:
            connector_ee = p.FixedNumberPreConnector(K_exc)
            connector_ei = p.FixedNumberPreConnector(K_exc)
            connector_ii = p.FixedNumberPreConnector(K_inh)
            connector_ie = p.FixedNumberPreConnector(K_inh)
            #connector_ee = p.FixedProbabilityConnector(p_conn)
            #connector_ei = p.FixedProbabilityConnector(p_conn)
            #connector_ii = p.FixedProbabilityConnector(p_conn)
            #connector_ie = p.FixedProbabilityConnector(p_conn)
            print("Generated connections")

        # inhibitory projections: always static and always with positive weight (because they go to a dedicated input port ``receptor_name_inh``)
        syn_ie = p.StaticSynapse(weight=np.abs(weights_inh), delay=delays_inh)
        syn_ii = p.StaticSynapse(weight=np.abs(weights_inh), delay=delays_inh)

        # excitatory projections (static or STDP)
        if use_nestml_synapse:
            if use_static_synapses:
                syn_ee = p.StaticSynapse(weight=weights_exc, delay=delays_exc)
                syn_ei = p.StaticSynapse(weight=weights_exc, delay=delays_exc)
            else:
                syn_ee = stdp_synapse_nestml(weight=weights_exc, delay=delays_exc)
                syn_ei = stdp_synapse_nestml(weight=weights_exc, delay=delays_exc)

                print("STDP VARIABLES:")
                print(syn_ee._nestml_model_variables)
                print(syn_ei._nestml_model_variables)

                syn_ee._nestml_model_variables["lambda"] = learning_rate
                syn_ei._nestml_model_variables["lambda"] = learning_rate

                # for stdp_model in [syn_ee, syn_ei, stdp_ie, stdp_ii]:
                #     stdp_model._nestml_model_variables["lambda"] = learning_rate
                #     stdp_model._nestml_model_variables["tau_tr_pre"] = tau_pre_trace
                #     stdp_model._nestml_model_variables["tau_tr_post"] = tau_post_trace
                #     stdp_model._nestml_model_variables["Wmin"] = Wmin_exc
                #     stdp_model._nestml_model_variables["Wmax"] = Wmax_exc
        else:
            # Built-in additive STDP
            if use_static_synapses:
               syn_ee = p.StaticSynapse(weight=weights_exc, delay=delays_exc)
               syn_ei = p.StaticSynapse(weight=weights_exc, delay=delays_exc)
            else:
                timing_rule = p.SpikePairRule(
                    tau_plus=tau_pre_trace,
                    tau_minus=tau_post_trace,
                    A_plus=learning_rate,
                    A_minus=learning_rate
                )

                weight_rule_exc = p.AdditiveWeightDependence(
                    w_min=Wmin_exc,
                    w_max=Wmax_exc
                )

                weight_rule_inh = p.AdditiveWeightDependence(
                    w_min=Wmin_inh,
                    w_max=Wmax_inh
                )

                syn_ee = p.STDPMechanism(
                    timing_dependence=timing_rule,
                    weight_dependence=weight_rule_exc,
                    weight=weights_exc,
                    delay=delays_exc
                )

                timing_rule = p.SpikePairRule(
                    tau_plus=tau_pre_trace,
                    tau_minus=tau_post_trace,
                    A_plus=learning_rate,
                    A_minus=learning_rate
                )

                weight_rule_exc = p.AdditiveWeightDependence(
                    w_min=Wmin_exc,
                    w_max=Wmax_exc
                )

                weight_rule_inh = p.AdditiveWeightDependence(
                    w_min=Wmin_inh,
                    w_max=Wmax_inh
                )

                syn_ei = p.STDPMechanism(
                    timing_dependence=timing_rule,
                    weight_dependence=weight_rule_exc,
                    weight=weights_exc,
                    delay=delays_exc
                )

        # Recurrent projections
        projection_ee = p.Projection(pop_exc, pop_exc, connector_ee, synapse_type=syn_ee, receptor_type=receptor_name_exc)
        projection_ei = p.Projection(pop_exc, pop_inh, connector_ei, synapse_type=syn_ei, receptor_type=receptor_name_exc)
        projection_ii = p.Projection(pop_inh, pop_inh, connector_ii, synapse_type=syn_ii, receptor_type=receptor_name_inh)
        projection_ie = p.Projection(pop_inh, pop_exc, connector_ie, synapse_type=syn_ie, receptor_type=receptor_name_inh)

        # Initial membrane potentials
        if randomize_initial_V_m:
            # draw from a uniform distribution between resting potential and threshold, to avoid a synchronous volley of spikes at the start of the simulation. Use a dedicated, seeded RNG, so that the builtin and NESTML runs start from identical initial conditions.
            V_m_init_rng = np.random.default_rng(seed + 4)
            V_m_init_exc = V_m_init_rng.uniform(E_L, V_th, size=n_exc)
            V_m_init_inh = V_m_init_rng.uniform(E_L, V_th, size=n_inh)
        else:
            V_m_init_exc = -60.0
            V_m_init_inh = -60.0

        pop_exc.initialize(**{membranePot: V_m_init_exc})
        pop_inh.initialize(**{membranePot: V_m_init_inh})

        # Recording
        pop_exc[:5].record([membranePot])    # record only from the first 5 neurons
        pop_inh.record("spikes")
        pop_exc.record("spikes")
        pop_exc.record("packets-per-timestep")    # number of incoming spike packets per timestep, one column per core

        pop_stim_exc.record("spikes")
        pop_stim_inh.record("spikes")

        w_ref = projection_ee.get("weight", format="float")

        start_time = time.perf_counter()
        p.run(t_sim)
        execution_time = time.perf_counter() - start_time

        if not (
            os.path.exists(EE_CONNECTION_FILE)
            and os.path.exists(EI_CONNECTION_FILE)
            and os.path.exists(II_CONNECTION_FILE)
            and os.path.exists(IE_CONNECTION_FILE)
        ):

            save_projection_connections(
                EE_CONNECTION_FILE,
                projection_ee
            )

            save_projection_connections(
                EI_CONNECTION_FILE,
                projection_ei
            )

            save_projection_connections(
                II_CONNECTION_FILE,
                projection_ii
            )

            save_projection_connections(
                IE_CONNECTION_FILE,
                projection_ie
            )

        print("\n=== CHECK CONNECTIVITY  ===")

        for name, projection in [
            ("EE", projection_ee),
            ("EI", projection_ei),
            ("II", projection_ii),
            ("IE", projection_ie),
        ]:
            weights = projection.get("weight", format="array")

            print(
                name,
                "shape =", weights.shape,
                "nonzero =", np.count_nonzero(~np.isnan(weights)),
                "weight_sum =", np.nansum(weights)
            )

            connections = projection.get(
                ["weight", "delay"],
                format="list",
                with_address=True
            )

            print(f"\n=== {name} ===")
            print("Number of connections:", len(connections))
            print("First 20 connections:")

            for connection in connections[:20]:
                print(connection)

        w_final = projection_ee.get("weight", format="float")    # get the weight at the end of the simulation
        np.testing.assert_allclose(w_ref, w_final)

        pop_exc_spikes = pop_exc.get_data("spikes")
        pop_inh_spikes = pop_inh.get_data("spikes")
        pop_stim_exc_spikes = pop_stim_exc.get_data("spikes")
        pop_stim_inh_spikes = pop_stim_inh.get_data("spikes")

        v_neuron = pop_exc.get_data(membranePot)

        try:
            packets_signal = pop_exc.get_data("packets-per-timestep").segments[0].filter(name="packets-per-timestep")[0]
            packets_per_timestep = np.asarray(packets_signal, dtype=float)    # shape: (n_timesteps, n_cores)
            packets_times = np.asarray(packets_signal.times.rescale("ms").magnitude, dtype=float)
        except Exception as e:
            print(f"Warning: could not retrieve packets-per-timestep data: {e}")
            packets_per_timestep = None
            packets_times = None

        exc_spike_trains = (pop_exc_spikes.segments[0].spiketrains)
        inh_spike_trains = (pop_inh_spikes.segments[0].spiketrains)

        # Firing Rates
        exc_firing_rate = compute_average_firing_rate(exc_spike_trains, n_exc, t_sim)
        inh_firing_rate = compute_average_firing_rate(inh_spike_trains, n_inh, t_sim)

        cv = compute_cv_for_neurons(exc_spike_trains)

        print("Exc spike fingerprint:",spike_fingerprint(pop_exc_spikes.segments[0].spiketrains))
        print("Inh spike fingerprint:",spike_fingerprint(pop_inh_spikes.segments[0].spiketrains))

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        print(f"Finished {implementation} simulation.")

        p.end()

        return {
            "implementation": implementation,
            "timestamp": timestamp,
            "seed": seed,
            "use_static_synapses": use_static_synapses,

            "t_sim": t_sim,

            "n_neurons": n_neurons,
            "n_exc": n_exc,
            "n_inh": n_inh,

            "g": g,
            "rate_ext_input": rate_ext_input,
            "neurons_per_core": neurons_per_core,
            "poisson_generators_per_core": poisson_generators_per_core,
            "poisson_reduction_factor": poisson_reduction_factor,
            "n_poisson_generators": n_stim_exc + n_stim_inh,

            "exc_firing_rate": exc_firing_rate,
            "inh_firing_rate": inh_firing_rate,
            "cv": cv,

            "execution_time": execution_time,

            "pop_exc_spikes": pop_exc_spikes,
            "pop_inh_spikes": pop_inh_spikes,

            "v_neuron": v_neuron,
            "membranePot": membranePot,

            "randomize_initial_V_m": randomize_initial_V_m,
            "packets_per_timestep": packets_per_timestep,
            "packets_times": packets_times
        }


    def run_experiment(self, implementations: List[str], n_neurons: int, neurons_per_core: int, poisson_generators_per_core: int, use_exp_luts: bool, poisson_reduction_factor: int = 1):
        """
        Run reference and NESTML, compare their results,
        save results and generate plots.
        """
        use_static_synapses = False

        results = {}

        for implementation in implementations:

            if implementation == "builtin":
                results["builtin"] = self.run_balanced_network(
                    n_neurons=n_neurons,
                    neurons_per_core=neurons_per_core,
                    poisson_generators_per_core=poisson_generators_per_core,
                    use_nestml_neuron=False,
                    use_nestml_synapse=False,
                    use_static_synapses=use_static_synapses,
                    poisson_reduction_factor=poisson_reduction_factor)

                analyze_run(results["builtin"])

            elif implementation == "nestml":
                results["nestml"] = self.run_balanced_network(
                    n_neurons=n_neurons,
                    neurons_per_core=neurons_per_core,
                    poisson_generators_per_core=poisson_generators_per_core,
                    use_nestml_neuron=True,
                    use_nestml_synapse=True,
                    use_static_synapses=use_static_synapses,
                    poisson_reduction_factor=poisson_reduction_factor)
                results[implementation]["use_exp_luts"] = use_exp_luts
                analyze_run(results["nestml"])

            else:
                raise ValueError(f"Unknown implementation: {implementation}")

        builtin = results.get("builtin")

        comparisons = {}
        if builtin is not None:
            try:
                comparisons = compare_results(builtin, results)
            except:
                pass

        return results, comparisons


    @pytest.mark.parametrize("generate_code", [True, False], indirect=True)
    @pytest.mark.parametrize("n_neurons", [256, 512, 1024, 2048])
    @pytest.mark.parametrize("neurons_per_core", [128])
    @pytest.mark.parametrize("poisson_generators_per_core", [128])  # was: 64
    @pytest.mark.parametrize("poisson_reduction_factor", [1])    # use 1/q times the number of Poisson generators (each generator drives q neurons)
    def test_spinnaker_balanced_network(self, generate_code, n_neurons, neurons_per_core, poisson_generators_per_core, poisson_reduction_factor):
        use_exp_luts = generate_code
        assert use_exp_luts in [True, False]

        results, comparisons = self.run_experiment(["builtin", "nestml"], n_neurons=n_neurons, neurons_per_core=neurons_per_core, poisson_generators_per_core=poisson_generators_per_core, use_exp_luts=use_exp_luts, poisson_reduction_factor=poisson_reduction_factor)

        print_results(results, comparisons)
        save_results_to_csv(results, csv_results_filename)
        plot_results(results)

        return

        FIRING_RATE_ATOL = .4    # [spikes/s]
        np.testing.assert_allclose(results["builtin"]["exc_firing_rate"], results["nestml"]["exc_firing_rate"], rtol=0, atol=FIRING_RATE_ATOL)
        np.testing.assert_allclose(results["builtin"]["inh_firing_rate"], results["nestml"]["inh_firing_rate"], rtol=0, atol=FIRING_RATE_ATOL)

        for name, result in results.items():

            assert np.isfinite(result["exc_firing_rate"])
            assert np.isfinite(result["inh_firing_rate"])
            assert np.isfinite(result["cv"])

            assert result["exc_firing_rate"] > 0.0
            assert result["inh_firing_rate"] > 0.0

        # Comparison
        exc_rate_tolerance = 0.40
        inh_rate_tolerance = 0.40
        cv_tolerance = 0.20

        comparison = comparisons["nestml"]

        assert comparison["exc_relative_difference"] < exc_rate_tolerance
        assert comparison["inh_relative_difference"] < inh_rate_tolerance
        assert comparison["cv_absolute_difference"] < cv_tolerance
