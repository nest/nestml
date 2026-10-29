# -*- coding: utf-8 -*-

# test_spinnaker_stdp_window.py

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
from pyNN.utility.plotting import Figure, Panel
from pyNN.random import RandomDistribution
from pyNN.random import NumpyRNG

from pynestml.frontend.pynestml_frontend import generate_spinnaker_target

from analyze_sample_profile import analyze_run



#
#   parse command-line arguments
#

parser = argparse.ArgumentParser()
parser.add_argument('--n-neurons', type=int, default=128, help='Number of neurons')
parser.add_argument('--neurons-per-core', type=int, default=32, help='Number of neurons per core')
parser.add_argument('--poisson-generators-per-core', type=int, default=32, help='Number of Poisson generators per core')
args = parser.parse_args()


#
#   options for saving benchmark results to file
#

csv_results_filename = "benchmark_balanced_networks_results.csv"


#
#   options for saving connections and constructing network using saved connections
#

USE_SAVED_CONNECTIONS = False

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

    fieldnames = ["timestamp", "implementation", "seed", "use_static_synapses", "use_exp_luts","N", "g", "p_conn", "rate_ext_input", "neurons_per_core", "poisson_generators_per_core", "t_sim",
        "exc_firing_rate", "inh_firing_rate", "cv", "execution_time"]

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
                "use_exp_luts": result["use_exp_luts"],
                "N": result["n_neurons"],
                "g": result["g"],
                "p_conn": result["p_conn"],
                "rate_ext_input": result["rate_ext_input"],
                "neurons_per_core": result["neurons_per_core"],
                "poisson_generators_per_core": result["poisson_generators_per_core"],
                "t_sim": result["t_sim"],
                "exc_firing_rate": result["exc_firing_rate"],
                "inh_firing_rate": result["inh_firing_rate"],
                "cv": result["cv"],
                "execution_time": result["execution_time"],

            }

            writer.writerow(row)


def plot_membrane_potential(results):
    """
    Plot the membrane potential of a neuron and save the figure.
    """
    fig, ax = plt.subplots(nrows=1, dpi=300)

    ax.set_xlabel("Time [ms]")
    ax.set_ylabel("Membrane potential [mV]")
    ax.set_title(f"\nBalanced Network - {results['implementation']} | N={results['n_neurons']}, g={results['g']}, neurons/core={results['neurons_per_core']} \n"
                 f"p_conn={results['p_conn']}, input={results['rate_ext_input']} Hz |\n")

    ax.plot(results['v_neuron'].segments[0].filter(name=results['membranePot'])[0])

    plt.savefig(
        f"spinnaker_bal_net_V_m__{results['implementation']}_{results['timestamp']}.png"
    )
    plt.close("all")


def plot_raster(results):
    """
    Plot the raster of spikes for excitatory and inhibitory populations and save the figure.
    """

    Figure(Panel(results['pop_exc_spikes'].segments[0].spiketrains,
                 xlabel="Time/ms",
                 xticks=True,
                 yticks=True,
                 markersize=5,
                 xlim=(0, results["t_sim"])),
               # raster plot of the presynaptic neuron spike times
           Panel(results['pop_inh_spikes'].segments[0].spiketrains,
                 xlabel="Time/ms",
                 xticks=True,
                 yticks=True,
                 markersize=5,
                 xlim=(0, results["t_sim"])),

                title=(
                    f"Balanced Network - {results['implementation']} | N={results['n_neurons']}, g={results['g']}, "
                    f"neurons/core={results['neurons_per_core']}\n"
                    f"p_conn={results['p_conn']}, input={results['rate_ext_input']} Hz | "
                    f"CV={results['cv']:.3f}, "
                    f"Exc={results['exc_firing_rate']:.2f} Hz, "
                    f"Inh={results['inh_firing_rate']:.2f} Hz \n"
                )
            )

    plt.savefig(
        f"bal_net_N{results['n_neurons']}_g{results['g']}_core{results['neurons_per_core']}_"
        f"impl_{results['implementation']}_{results['timestamp']}.png"
    )

    plt.savefig(
        f"bal_net_N{results['n_neurons']}_g{results['g']}_core{results['neurons_per_core']}_"
        f"impl_{results['implementation']}_{results['timestamp']}.pdf"
    )
    plt.close("all")


def plot_results(results):

    for name, result in results.items():

        if result is None:
            continue

        plot_membrane_potential(result)

        plot_raster(result)


class TestSpiNNakerBalancedNetwork:
    """SpiNNaker code generation tests"""

    @pytest.fixture(autouse=True,
                    scope="module")
    def generate_code(self):
        use_exp_luts = os.environ.get("USE_EXP_LUTS", "true").lower() == "true"

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



    def run_balanced_network(self, use_nestml_neuron, use_nestml_synapse, use_static_synapses: bool, use_exp_luts):
        from python_models8.neuron.implementations.stdp_synapse_nestml_impl import stdp_synapse_nestmlDynamics as stdp_synapse_nestml
        from python_models8.neuron.builds.iaf_psc_exp_neuron_nestml import iaf_psc_exp_neuron_nestml

        t_sim = 1000    # total time to simulator for [ms]
        p_conn = .1    # connection probability
        rate_ext_input = 50.    # external input rate (eta parameter) [s⁻¹]
        n_neurons = args.n_neurons
        n_exc = int(round(n_neurons * 0.8))
        n_inh = int(round(n_neurons * 0.2))
        g = 10.    # the ratio between excitation and inhibition
                   # try 10 for asynchronous irregular activity. Try 1 for population-wide activity bursts

        if use_nestml_neuron:
            neuron_model = iaf_psc_exp_neuron_nestml

            receptor_name_exc = "exc_spikes"
            receptor_name_inh = "inh_spikes"
            membranePot = "V_m"

            neuron_parameters = {
                "C_m": 250,
                "tau_m": 10,
                "tau_syn_inh": 2,
                "tau_syn_exc": 2,
                "refr_T": 2,
                "E_L": -70,
                "V_reset": -70,
                "V_th": -55
            }
        else:
            neuron_model = p.IF_curr_exp

            receptor_name_exc = "excitatory"
            receptor_name_inh = "inhibitory"
            membranePot = "v"

            neuron_parameters = {
                "tau_m": 10,
                "cm": 1E-3 * 250,
                "v_rest": -70,
                "v_reset": -70,
                "v_thresh": -55,
                "tau_syn_E": 2,
                "tau_syn_I": 2,
                "tau_refrac": 2
            }

        p.setup(timestep=1.0)
        p.reset()
        p.set_number_of_neurons_per_core(neuron_model, args.neurons_per_core)
        p.set_number_of_neurons_per_core(p.SpikeSourcePoisson, args.poisson_generators_per_core)


        # Initial Weights
        weight_exc = 1E3 * 0.5
        weight_inh = -g * weight_exc
        weight_input = 1E3

        if not use_nestml_neuron:
            weight_exc *= 1E-3
            weight_inh *= 1E-3
            weight_input *= 1E-3



        #STDP Parameters
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

        seed = int(os.environ.get("SEED", "1"))

        # excitatory and inhibitory populations
        pop_exc = p.Population(n_exc, neuron_model, label="Excitatory", seed=seed, additional_parameters={"max_atoms_per_core": neurons_per_core})
        pop_inh = p.Population(n_inh, neuron_model, label="Inhibitory", seed=seed+1, additional_parameters={"max_atoms_per_core": neurons_per_core})

        # print("\n===CHECK POPULATION SEEDS ===")
        # print("SEED =", seed)
        # print("Exc population seed =", seed)
        # print("Inh population seed =", seed + 1)

        pop_exc.set(**neuron_parameters)
        pop_inh.set(**neuron_parameters)


        # external stimulus to exc and inh populations
        stim_exc = p.Population(n_exc, p.SpikeSourcePoisson(rate=rate_ext_input), label="Stim_Exc", additional_parameters={"seed": seed + 2})
        stim_inh = p.Population(n_inh, p.SpikeSourcePoisson(rate=rate_ext_input), label="Stim_Inh", additional_parameters={"seed": seed + 3})

        # print("\n=== CHECK POISSON SEEDS ===")
        # print("Stim Exc seed =", seed + 2)
        # print("Stim Inh seed =", seed + 3)

        p.Projection(stim_exc, pop_exc, p.OneToOneConnector(), p.StaticSynapse(weight=weight_input, delay=1.), receptor_type=receptor_name_exc)
        p.Projection(stim_inh, pop_inh, p.OneToOneConnector(), p.StaticSynapse(weight=weight_input, delay=1.), receptor_type=receptor_name_exc)


        # Exc and Inh Connections
        #delays_exc = RandomDistribution("normal_clipped", mu=1.5, sigma=0.75, low=1.0, high=1.6)
        #weights_exc = RandomDistribution("normal_clipped", mu=weight_exc, sigma=0.1, low=0.0, high=np.inf)
        delays_exc = 1.
        weights_exc = weight_exc
        #conn_exc = p.FixedProbabilityConnector(p_conn)

        #delays_inh = RandomDistribution("normal_clipped", mu=0.75, sigma=0.375, low=1.0, high=1.6)
        #weights_inh = RandomDistribution("normal_clipped", mu=abs(weight_inh), sigma=0.1, low=0, high=np.inf)
        delays_inh = 1.
        weights_inh = weight_inh
        #conn_inh = p.FixedProbabilityConnector(p_conn)

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

            connector_ee = p.FixedProbabilityConnector(p_conn)
            connector_ei = p.FixedProbabilityConnector(p_conn)
            connector_ii = p.FixedProbabilityConnector(p_conn)
            connector_ie = p.FixedProbabilityConnector(p_conn)

            print("Generated new connections with FixedProbabilityConnector")


        # STDP synapses
        if use_nestml_synapse:
            stdp_ie = p.StaticSynapse(weight=np.abs(weights_inh), delay=delays_inh)
            stdp_ii = p.StaticSynapse(weight=np.abs(weights_inh), delay=delays_inh)
            if use_static_synapses:
                stdp_ee = p.StaticSynapse(weight=weights_exc, delay=delays_exc)
                stdp_ei = p.StaticSynapse(weight=weights_exc, delay=delays_exc)
            else:
                stdp_ee = stdp_synapse_nestml(weight=weights_exc, delay=delays_exc)
                stdp_ei = stdp_synapse_nestml(weight=weights_exc, delay=delays_exc)

                print("STDP VARIABLES:")
                print(stdp_ee._nestml_model_variables)
                print(stdp_ei._nestml_model_variables)

                stdp_ee._nestml_model_variables["lambda"] = learning_rate
                stdp_ei._nestml_model_variables["lambda"] = learning_rate

                # for stdp_model in [stdp_ee, stdp_ei, stdp_ie, stdp_ii]:
                #     stdp_model._nestml_model_variables["lambda"] = learning_rate
                #     stdp_model._nestml_model_variables["tau_tr_pre"] = tau_pre_trace
                #     stdp_model._nestml_model_variables["tau_tr_post"] = tau_post_trace
                #     stdp_model._nestml_model_variables["Wmin"] = Wmin_exc
                #     stdp_model._nestml_model_variables["Wmax"] = Wmax_exc
                print("STDP lambda:", stdp_ee._nestml_model_variables["lambda"])
                print("STDP lambda:", stdp_ei._nestml_model_variables["lambda"])
            # Recurrent projections
            projection_ee=p.Projection(pop_exc, pop_exc, connector_ee, synapse_type=stdp_ee, receptor_type=receptor_name_exc)
            projection_ei=p.Projection(pop_exc, pop_inh, connector_ei, synapse_type=stdp_ei, receptor_type=receptor_name_exc)
            projection_ii=p.Projection(pop_inh, pop_inh, connector_ii, synapse_type=stdp_ii, receptor_type=receptor_name_inh)
            projection_ie=p.Projection(pop_inh, pop_exc, connector_ie, synapse_type=stdp_ie, receptor_type=receptor_name_inh)

        else: 
            # Built-in additive STDP
            if use_static_synapses:
               synapse_exc = p.StaticSynapse(weight=weights_exc, delay=delays_exc)
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


                synapse_exc = p.STDPMechanism(
                    timing_dependence=timing_rule,
                    weight_dependence=weight_rule_exc,
                    weight=weights_exc,
                    delay=delays_exc
                )

            synapse_inh = p.StaticSynapse(weight=np.abs(weights_inh), delay=delays_inh)

            projection_ee=p.Projection(pop_exc, pop_exc, connector_ee, synapse_type=synapse_exc, receptor_type=receptor_name_exc)
            projection_ei=p.Projection(pop_exc, pop_inh, connector_ei, synapse_type=synapse_exc, receptor_type=receptor_name_exc)
            projection_ii=p.Projection(pop_inh, pop_inh, connector_ii, synapse_type=synapse_inh, receptor_type=receptor_name_inh)
            projection_ie=p.Projection(pop_inh, pop_exc, connector_ie, synapse_type=synapse_inh, receptor_type=receptor_name_inh)


        # Initial membrane potentials
        if use_nestml_neuron:
            # pop_exc.initialize(V_m=RandomDistribution("uniform", (-65.0, -55.0), rng=rng_v_exc))
            # pop_inh.initialize(V_m=RandomDistribution("uniform", (-65.0, -55.0), rng=rng_v_inh))
            pop_exc.initialize(V_m=-60.0)
            pop_inh.initialize(V_m=-60.0)

        else:
            # pop_exc.initialize(v=RandomDistribution("uniform", (-65.0, -55.0), rng=rng_v_exc))
            # pop_inh.initialize(v=RandomDistribution("uniform", (-65.0, -55.0), rng=rng_v_inh))
            pop_exc.initialize(v=-60.0)
            pop_inh.initialize(v=-60.0)

        # # Gives error
        # print("\n=== CHECK INITIAL V ===")

        # if use_nestml_neuron:
            # print("Exc V:", pop_exc.get("V_m")[:10])
            # print("Inh V:", pop_inh.get("V_m")[:10])
        # else:
            # print("Exc v:", pop_exc.get("v")[:10])
            # print("Inh v:", pop_inh.get("v")[:10])

        # Recording
        pop_exc[:5].record([membranePot])    # record only from the first 5 neurons
        pop_inh.record("spikes")
        pop_exc.record("spikes")

        stim_exc.record("spikes")
        stim_inh.record("spikes")


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


        
        """for i in range(10):
            w_final = projection_ee.get("weight", format="float")    # get the weight at the end of the simulation


            p.run(t_sim / 10)


            #print("At i = " + str(i) + ":")
            #print(np.unique(w_final))
            np.testing.assert_allclose(w_ref, w_final)"""




        pop_exc_spikes = pop_exc.get_data("spikes")
        pop_inh_spikes = pop_inh.get_data("spikes")

        stim_exc_spikes = stim_exc.get_data("spikes")
        stim_inh_spikes = stim_inh.get_data("spikes")

        # print("\n=== CHECK POISSON SPIKES ===")

        # for i, train in enumerate(
        #     stim_exc_spikes.segments[0].spiketrains[:3]
        # ):
        #     print(f"Stim Exc neuron {i}:", np.asarray(train)[:20])

        # for i, train in enumerate(
        #     stim_inh_spikes.segments[0].spiketrains[:3]
        # ):
        #     print(f"Stim Inh neuron {i}:", np.asarray(train)[:20])


        print("\n=== CHECK NETWORK SPIKES ===")

        for i, train in enumerate(
            pop_exc_spikes.segments[0].spiketrains[:3]
        ):
            print(f"Exc neuron {i}:", np.asarray(train)[:20])

        for i, train in enumerate(
            pop_inh_spikes.segments[0].spiketrains[:3]
        ):
            print(f"Inh neuron {i}:", np.asarray(train)[:20])


        v_neuron = pop_exc.get_data(membranePot)


        exc_spike_trains = (pop_exc_spikes.segments[0].spiketrains)
        inh_spike_trains = (pop_inh_spikes.segments[0].spiketrains)


        # Firing Rates
        exc_firing_rate = compute_average_firing_rate(exc_spike_trains, n_exc, t_sim)
        inh_firing_rate = compute_average_firing_rate(inh_spike_trains, n_inh, t_sim)

        cv = compute_cv_for_neurons(exc_spike_trains)

        print("Exc spike fingerprint:",spike_fingerprint(pop_exc_spikes.segments[0].spiketrains))
        print("Inh spike fingerprint:",spike_fingerprint(pop_inh_spikes.segments[0].spiketrains))


        # Timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        implementation = "nestml" if use_nestml_neuron or use_nestml_synapse else "builtin"

        print(f"Finished {implementation} simulation.")

        p.end()

        return {
            "implementation": implementation,
            "timestamp": timestamp,
            "seed": seed,
            "use_static_synapses": use_static_synapses,
            "use_exp_luts": use_exp_luts,

            "t_sim": t_sim,

            "n_neurons": n_neurons,
            "n_exc": n_exc,
            "n_inh": n_inh,

            "g": g,
            "p_conn": p_conn,
            "rate_ext_input": rate_ext_input,
            "neurons_per_core": neurons_per_core,
            "poisson_generators_per_core": poisson_generators_per_core,

            "exc_firing_rate": exc_firing_rate,
            "inh_firing_rate": inh_firing_rate,
            "cv": cv,

            "execution_time": execution_time,

            "pop_exc_spikes": pop_exc_spikes,
            "pop_inh_spikes": pop_inh_spikes,

            "v_neuron": v_neuron,
            "membranePot": membranePot
        }


    def run_experiment(self, implementations, use_exp_luts=True):
        """
        Run reference and NESTML, compare their results,
        save results and generate plots.
        """
        use_static_synapses = False

        results = {}

        for implementation in implementations:

            if implementation == "builtin":
                results["builtin"] = self.run_balanced_network(
                    use_nestml_neuron=False,
                    use_nestml_synapse=False,
                    use_static_synapses=use_static_synapses,
                    use_exp_luts=None)

                analyze_run(results["builtin"])

            elif implementation == "nestml":
                results["nestml"] = self.run_balanced_network(
                    use_nestml_neuron=True,
                    use_nestml_synapse=True, 
                    use_static_synapses=use_static_synapses,
                    use_exp_luts=use_exp_luts)

                analyze_run(results["nestml"])

            else:
                raise ValueError(f"Unknown implementation: {implementation}")

        builtin = results.get("builtin")

        if builtin is not None:
            comparisons = compare_results(builtin, results)
        else:
            comparisons = {}

        print_results(results, comparisons)
        save_results_to_csv(results, csv_results_filename)
        plot_results(results)

        return results, comparisons


    def test_spinnaker_balanced_network(self):
        results, comparisons = self.run_experiment(["builtin", "nestml"], use_exp_luts=True)

        FIRING_RATE_ATOL = .4    # [spikes/s]
        np.testing.assert_allclose(results["builtin"]["exc_firing_rate"], results["nestml"]["exc_firing_rate"], rtol=0, atol=FIRING_RATE_ATOL)
        np.testing.assert_allclose(results["builtin"]["inh_firing_rate"], results["nestml"]["inh_firing_rate"], rtol=0, atol=FIRING_RATE_ATOL)

        for name, result in results.items():

            assert np.isfinite(result["exc_firing_rate"])
            assert np.isfinite(result["inh_firing_rate"])
            assert np.isfinite(result["cv"])

            assert result["exc_firing_rate"] > 0.0
            assert result["inh_firing_rate"] > 0.0

        # Comparison değerleri
        exc_rate_tolerance = 0.40
        inh_rate_tolerance = 0.40
        cv_tolerance = 0.20

        comparison = comparisons["nestml"]

        assert comparison["exc_relative_difference"] < exc_rate_tolerance
        assert comparison["inh_relative_difference"] < inh_rate_tolerance
        assert comparison["cv_absolute_difference"] < cv_tolerance



    def test_nestml(self):
        results, comparisons = self.run_experiment(["nestml"], use_exp_luts=False)

        result = results["nestml"]

        assert np.isfinite(result["exc_firing_rate"])
        assert np.isfinite(result["inh_firing_rate"])
        assert np.isfinite(result["cv"])

        assert result["exc_firing_rate"] > 0.0
        assert result["inh_firing_rate"] > 0.0

        assert comparisons == {}
