# -*- coding: utf-8 -*-
#
# brunel_alpha_nest.py
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

"""
Random balanced network (alpha synapses) connected with NEST
------------------------------------------------------------

This script simulates an excitatory and an inhibitory population on
the basis of the network used in [1]_.

In contrast to ``brunel-alpha-numpy.py``, this variant uses NEST's builtin
connection routines to draw the random connections instead of NumPy.

When connecting the network, customary synapse models are used, which
allow for querying the number of created synapses. Using spike
recorders, the average firing rates of the neurons in the populations
are established. The building as well as the simulation time of the
network are recorded.

References
~~~~~~~~~~

.. [1] Brunel N (2000). Dynamics of sparsely connected networks of excitatory and
       inhibitory spiking neurons. Journal of Computational Neuroscience 8,
       183-208.

"""

###############################################################################
# Import all necessary modules for simulation, analysis and plotting. Scipy
# should be imported before nest.

import time
import sys
import matplotlib.pyplot as plt
import nest
import nest.raster_plot
import numpy as np
import scipy.special as sp
import json
import argparse
import os


###############################################################################
# Definition of functions used in this example. First, define the `Lambert W`
# function implemented in SLI. The second function computes the maximum of
# the postsynaptic potential for a synaptic input current of unit amplitude
# (1 pA) using the `Lambert W` function. Thus function will later be used to
# calibrate the synaptic weights.

parser = argparse.ArgumentParser(description='Run a simulation with NEST')
parser.add_argument('--benchmarkPath', type=str, default='', help='Path to the nest installation')
parser.add_argument('--simulated_neuron', type=str, default='iaf_psc_alpha_neuron_Nestml', help='Name of the model to use')
parser.add_argument('--network_scale', type=int, default=2500, help='Number of neurons to use')
parser.add_argument('--nodes', type=int, default=2, required=False, help='Number of compute nodes to use')
parser.add_argument('--threads', type=int, default=4, help='Number of threads to use')
parser.add_argument('--iteration', type=int, help='iteration number used for the benchmark')

args = parser.parse_args()


def LambertWm1(x):
    # Using scipy to mimic the gsl_sf_lambert_Wm1 function.
    return sp.lambertw(x, k=-1 if x < 0 else 0).real


def ComputePSPnorm(tauMem, CMem, tauSyn):
    a = tauMem / tauSyn
    b = 1.0 / tauSyn - 1.0 / tauMem

    # time of maximum
    t_max = 1.0 / b * (-LambertWm1(-np.exp(-1.0 / a) / a) - 1.0 / a)

    # maximum of PSP for current of unit amplitude
    return (
        np.exp(1.0)
        / (tauSyn * CMem * b)
        * ((np.exp(-t_max / tauMem) - np.exp(-t_max / tauSyn)) / b - t_max * np.exp(-t_max / tauSyn))
    )


nest.ResetKernel()
nest.local_num_threads = parser.parse_args().threads


###############################################################################
# Assigning the current time to a variable in order to determine the build
# time of the network.

startbuild = time.time()


###############################################################################
# Assigning the simulation parameters to variables.

dt = 0.1  # the resolution in ms
simtime = 100.0 # 1000.0  # Simulation time in ms
delay = 1.5  # synaptic delay in ms

###############################################################################
# Definition of the parameters crucial for asynchronous irregular firing of
# the neurons.

g = 5.0  # ratio inhibitory weight/excitatory weight
eta = 2.0  # external rate relative to threshold rate
epsilon = 0.1  # connection probability

###############################################################################
# Definition of the number of neurons in the network and the number of neurons
# recorded from

order = args.network_scale
NE = 4 * order  # number of excitatory neurons
NI = 1 * order  # number of inhibitory neurons
N_neurons = NE + NI  # number of neurons in total
print(f"Number of neurons : {N_neurons}")
N_rec = 50  # record from 50 neurons

###############################################################################
# Definition of connectivity parameters

CE = int(epsilon * NE / (order / 2500))  # number of excitatory synapses per neuron
CI = int(epsilon * NI / (order / 2500))  # number of inhibitory synapses per neuron

# CE = int(epsilon * NE)  # number of excitatory synapses per neuron
# CI = int(epsilon * NI)  # number of inhibitory synapses per neuron
C_tot = int(CI + CE)  # total number of synapses per neuron

###############################################################################
# Initialization of the parameters of the integrate and fire neuron and the
# synapses. The parameters of the neuron are stored in a dictionary. The
# synaptic currents are normalized such that the amplitude of the PSP is J.

tauSyn = 0.5  # synaptic time constant in ms
tauMem = 20.0  # time constant of membrane potential in ms
CMem = 250.0  # capacitance of membrane in in pF
theta = 20.0  # membrane threshold potential in mV
neuron_params = {}
if args.simulated_neuron == "iaf_psc_alpha":
    neuron_params = {
        "C_m": CMem,
        "tau_m": tauMem,
        "tau_syn_ex": tauSyn,
        "tau_syn_in": tauSyn,
        "t_ref": 2.0,
        "E_L": 0.0,
        "V_reset": 0.0,
        "V_m": 0.0,
        "V_th": theta,
    }
elif args.simulated_neuron.startswith("iaf_psc_alpha") and "NESTML" in args.simulated_neuron.upper():
    neuron_params = {
        "C_m": CMem,
        "tau_m": tauMem,
        "tau_syn_exc": tauSyn,
        "tau_syn_inh": tauSyn,
        "refr_T": 2.0,
        "E_L": 0.0,
        "V_reset": 0.0,
        "V_m": 0.0,
        "V_th": theta,
    }
elif args.simulated_neuron == "aeif_psc_alpha":
    neuron_params = {
        "C_m": CMem,
        "g_L": CMem / tauMem,
        "tau_syn_ex": tauSyn,
        "tau_syn_in": tauSyn,
        "t_ref": 2.0,
        "E_L": 0.0,
        "V_reset": 0.0,
        "V_m": 0.0,
        "V_th": theta,
        "V_peak": theta
    }
elif args.simulated_neuron.startswith("aeif_psc_alpha") and "NESTML" in args.simulated_neuron.upper():
    neuron_params = {
        "C_m": CMem,
        "g_L": CMem / tauMem,
        "tau_syn_exc": tauSyn,
        "tau_syn_inh": tauSyn,
        "refr_T": 2.0,
        "E_L": 0.0,
        "V_reset": 0.0,
        "V_m": 0.0,
        "V_th": theta,
        "V_peak": theta
    }
else:
    assert False, "Unknown neuron model: " + str(args.simulated_neuron)

J = 0.1  # postsynaptic amplitude in mV
J_unit = ComputePSPnorm(tauMem, CMem, tauSyn)
J_ex = J / J_unit  # amplitude of excitatory postsynaptic current
J_in = -g * J_ex  # amplitude of inhibitory postsynaptic current

###############################################################################
# Definition of threshold rate, which is the external rate needed to fix the
# membrane potential around its threshold, the external firing rate and the
# rate of the poisson generator which is multiplied by the in-degree CE and
# converted to Hz by multiplication by 1000.

nu_th = (theta * CMem) / (J_ex * CE * np.exp(1) * tauMem * tauSyn)
nu_ex = eta * nu_th
p_rate = 1000.0 * nu_ex * CE

################################################################################
# Configuration of the simulation kernel by the previously defined time
# resolution used in the simulation. Setting ``print_time`` to `True` prints the
# already processed simulation time as well as its percentage of the total
# simulation time.


nest.resolution = dt
nest.print_time = True
nest.overwrite_files = True

try:
    nest.Install("nestmlmodule")
except:
    pass
nest.Install("nestmlOptimizedmodule")
nest.Install("nestmlplasticmodule")
nest.Install("nestmlnocomodule")
print("Building network")

###############################################################################
# Creation of the nodes using ``Create``. We store the returned handles in
# variables for later reference. Here the excitatory and inhibitory, as well
# as the poisson generator and two spike recorders. The spike recorders will
# later be used to record excitatory and inhibitory spikes. Properties of the
# nodes are specified via ``params``, which expects a dictionary.

modelName = args.simulated_neuron

nodes_ex = nest.Create(modelName, NE, params=neuron_params)
nodes_in = nest.Create(modelName, NI, params=neuron_params)
noise = nest.Create("poisson_generator", params={"rate": p_rate})
espikes = nest.Create("spike_recorder")
ispikes = nest.Create("spike_recorder")

e_mm = nest.Create("multimeter", params={"record_from": ["V_m"]})

###############################################################################
# Configuration of the spike recorders recording excitatory and inhibitory
# spikes by sending parameter dictionaries to ``set``. Setting the property
# `record_to` to *"ascii"* ensures that the spikes will be recorded to a file,
# whose name starts with the string assigned to the property `label`.

espikes.set(label="brunel-py-ex", record_to="ascii")
ispikes.set(label="brunel-py-in", record_to="ascii")

print("Connecting devices")

###############################################################################
# Definition of a synapse using ``CopyModel``, which expects the model name of
# a pre-defined synapse, the name of the customary synapse and an optional
# parameter dictionary. The parameters defined in the dictionary will be the
# default parameter for the customary synapse. Here we define one synapse for
# the excitatory and one for the inhibitory connections giving the
# previously defined weights and equal delays.

wr = nest.Create("weight_recorder")

if "lastic" in modelName:
    # use plastic synapses
    print("Using NESTML STDP synapse")
    if "iaf_psc_alpha" in args.simulated_neuron:
        nest.CopyModel("stdp_synapse_Nestml_Plastic__with_iaf_psc_alpha_neuron_Nestml_Plastic", "excitatory", {"weight": J_ex, "delay": delay, "d": delay, "lambda": 0., "weight_recorder": wr})
    else:
        if "noco" in args.simulated_neuron:
            nest.CopyModel("stdp_synapse_Nestml_Plastic_noco__with_aeif_psc_alpha_neuron_Nestml_Plastic_noco", "excitatory", {"weight": J_ex, "delay": delay, "d": delay, "lambda": 0., "weight_recorder": wr})
        else:
            nest.CopyModel("stdp_synapse_Nestml_Plastic__with_aeif_psc_alpha_neuron_Nestml_Plastic", "excitatory", {"weight": J_ex, "delay": delay, "d": delay, "lambda": 0., "weight_recorder": wr})

else:
    # use static synapses
    print("Using NEST built in STDP synapse")
    nest.CopyModel("stdp_synapse", "excitatory", {"weight": J_ex, "delay": delay, "lambda": 0., "weight_recorder": wr})
    # nest.CopyModel("static_synapse", "excitatory", {"weight": J_ex, "delay": delay})


nest.CopyModel("static_synapse", "excitatory_static", {"weight": J_ex, "delay": delay})


nest.CopyModel("static_synapse", "inhibitory", {"weight": J_in, "delay": delay})

#################################################################################
# Connecting the previously defined poisson generator to the excitatory and
# inhibitory neurons using the excitatory synapse. Since the poisson
# generator is connected to all neurons in the population the default rule
# (``all_to_all``) of ``Connect`` is used. The synaptic properties are inserted
# via ``syn_spec`` which expects a dictionary when defining multiple variables or
# a string when simply using a pre-defined synapse.

nest.Connect(noise, nodes_ex, syn_spec="excitatory_static")
nest.Connect(noise, nodes_in, syn_spec="excitatory_static")

###############################################################################
# Connecting the first ``N_rec`` nodes of the excitatory and inhibitory
# population to the associated spike recorders using excitatory synapses.
# Here the same shortcut for the specification of the synapse as defined
# above is used.


nest.Connect(e_mm, nodes_ex[0], syn_spec="excitatory_static")

if args.nodes > 1:
    local_neurons_ex = nest.GetLocalNodeCollection(nodes_ex)
    local_neurons_in = nest.GetLocalNodeCollection(nodes_in)

    # Convert to NodeCollection
    local_neurons_ex = nest.NodeCollection(local_neurons_ex.tolist())
    local_neurons_in = nest.NodeCollection(local_neurons_in.tolist())
else:
    local_neurons_ex = nodes_ex
    local_neurons_in = nodes_in

print("Local exc neurons: ", len(local_neurons_ex))
print("Local inh neurons: ", len(local_neurons_in))

nest.Connect(local_neurons_ex[:N_rec], espikes, syn_spec="excitatory_static")
nest.Connect(local_neurons_in[:N_rec], ispikes, syn_spec="excitatory_static")

print("Connecting network")

print("Excitatory connections")

###############################################################################
# Connecting the excitatory population to all neurons using the pre-defined
# excitatory synapse. Beforehand, the connection parameter are defined in a
# dictionary. Here we use the connection rule ``fixed_indegree``,
# which requires the definition of the indegree. Since the synapse
# specification is reduced to assigning the pre-defined excitatory synapse it
# suffices to insert a string.

conn_params_ex = {"rule": "fixed_indegree", "indegree": CE}
nest.Connect(nodes_ex, nodes_ex + nodes_in, conn_params_ex, "excitatory")

print("Inhibitory connections")

###############################################################################
# Connecting the inhibitory population to all neurons using the pre-defined
# inhibitory synapse. The connection parameter as well as the synapse
# parameter are defined analogously to the connection from the excitatory
# population defined above.

conn_params_in = {"rule": "fixed_indegree", "indegree": CI}
nest.Connect(nodes_in, nodes_ex + nodes_in, conn_params_in, "inhibitory")

###############################################################################
# Storage of the time point after the buildup of the network in a variable.

endbuild = time.time()

###############################################################################
# Simulation of the network.

print("Simulating")

nest.Simulate(simtime)

###############################################################################
# Storage of the time point after the simulation of the network in a variable.

endsimulate = time.time()

###############################################################################
# Reading out the total number of spikes received from the spike recorder
# connected to the excitatory population and the inhibitory population.

events_ex = espikes.n_events
events_in = ispikes.n_events

###############################################################################
# Calculation of the average firing rate of the excitatory and the inhibitory
# neurons by dividing the total number of recorded spikes by the number of
# neurons recorded from and the simulation time. The multiplication by 1000.0
# converts the unit 1/ms to 1/s=Hz.

rate_ex = events_ex / simtime * 1000.0 / N_rec
rate_in = events_in / simtime * 1000.0 / N_rec

###############################################################################
# Reading out the number of connections established using the excitatory and
# inhibitory synapse model. The numbers are summed up resulting in the total
# number of synapses.

num_synapses_ex = nest.GetDefaults("excitatory")["num_connections"]
num_synapses_in = nest.GetDefaults("inhibitory")["num_connections"]
num_synapses = num_synapses_ex + num_synapses_in

###############################################################################
# Establishing the time it took to build and simulate the network by taking
# the difference of the pre-defined time variables.

build_time = endbuild - startbuild
sim_time = endsimulate - endbuild

###############################################################################
# Printing the network properties, firing rates and building times.

print("Brunel network simulation (Python)")
print(f"                CE: {CE}")
print(f"                CI: {CI}")
print(f"Number of synapses: {num_synapses}")
print(f"       Excitatory : {num_synapses_ex}")
print(f"       Inhibitory : {num_synapses_in}")
# TODO:compare on different sizes
print(f"Excitatory rate   : {rate_ex:.2f} Hz")
print(f"Inhibitory rate   : {rate_in:.2f} Hz")

print(f"Building time     : {build_time:.2f} s")
print(f"Simulation time   : {sim_time:.2f} s")

###############################################################################
# Plot a raster of the excitatory neurons and a histogram.


def convert_np_arrays_to_lists(obj):
    if isinstance(obj, dict):
        return {k: convert_np_arrays_to_lists(v) for k, v in obj.items()}
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj

def _VmB(VmKey):
    r"""This code is from beNNch, https://github.com/INM-6/beNNch-models/, 2024-05-18"""
    _proc_status = '/proc/%d/status' % os.getpid()
    _scale = {'kB': 1024.0, 'mB': 1024.0 * 1024.0, 'KB': 1024.0, 'MB': 1024.0 * 1024.0}
    # get pseudo file  /proc/<pid>/status
    try:
        t = open(_proc_status)
        v = t.read()
        t.close()
    except:
        return 0.0  # non-Linux?
    # get VmKey line e.g. 'VmRSS:  9999  kB\n ...'
    i = v.index(VmKey)
    v = v[i:].split(None, 3)  # whitespace
    if len(v) < 3:
        return 0.0  # invalid format?
    # convert Vm value to bytes
    return float(v[1]) * _scale[v[2]]


def get_vmsize(since=0.0):
    """Return memory usage in bytes."""
    return _VmB('VmSize:') - since


def get_rss(since=0.0):
    """Return resident memory usage in bytes."""
    return _VmB('VmRSS:') - since


def get_vmpeak(since=0.0):
    """Return peak memory usage in bytes."""
    return _VmB('VmPeak:') - since


if args.benchmarkPath != "":
    path = args.benchmarkPath
    status = nest.GetKernelStatus()
    status["memory_benchmark"] = {"rss": get_rss(),
                                  "vmsize": get_vmsize(),
                                  "vmpeak": get_vmpeak()}
    status = convert_np_arrays_to_lists(status)
    if not os.path.exists(path):
        os.makedirs(path)
    with open(f"{path}/timing_[simulated_neuron={args.simulated_neuron}]_[network_scale={args.network_scale}]_[iteration={args.iteration}]_[nodes={args.nodes}]_[rank={nest.Rank()}].json", "w") as f:
        json.dump(status, f)
        f.close()

    nest.raster_plot.from_device(espikes, hist=True)
    plt.savefig(f"{path}/raster_plot_[simulated_neuron={args.simulated_neuron}]_[network_scale={args.network_scale}]_[iteration={args.iteration}]_[nodes={args.nodes}]_[rank={nest.Rank()}].png")
    plt.close()

    fig, ax = plt.subplots()
    ax.plot(e_mm.get()["events"]["times"], e_mm.get()["events"]["V_m"])
    plt.savefig(f"{path}/V_m_[simulated_neuron={args.simulated_neuron}]_[network_scale={args.network_scale}]_[iteration={args.iteration}]_[nodes={args.nodes}]_[rank={nest.Rank()}].png")
    plt.close()
