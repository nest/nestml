# -*- coding: utf-8 -*-
#
# test_spinnaker_iaf_psc_exp.py
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
import numpy as np
import pytest

from pynestml.frontend.pynestml_frontend import generate_spinnaker_target

def compute_cv(spike_train):
    """
    Compute the coefficient of variation (CV) for a single spike train.
    
    Parameters:
    spike_train (list or numpy array): Timestamps of spikes in the spike train.
    
    Returns:
    float: Coefficient of variation (CV) of the inter-spike intervals.
    """
    # Calculate inter-spike intervals (ISI)
    isi = np.diff(spike_train)
    
    # Calculate mean and standard deviation of ISI
    mean_isi = np.mean(isi)
    std_isi = np.std(isi)
    
    # Calculate coefficient of variation
    cv = std_isi / mean_isi
    
    return cv

def compute_cv_for_neurons(spike_trains):
    cvs = []
    for spike_train in spike_trains:
        if len(spike_train):
            cvs.append(compute_cv(spike_train))
    print("Cvs: " + str(cvs))
    return np.mean(cvs)


class TestSpiNNakerIafPscExp:
    """SpiNNaker code generation tests"""

    @pytest.fixture(autouse=True,
                    scope="module")
    def generate_code(self):

#        codegen_opts = {"neuron_synapse_pairs": [{"neuron": "iaf_psc_exp"}]}
#                                                      "synapse": "stdp",
#                                                      "post_ports": ["post_spikes"]}]}


        files = [
            os.path.join("models", "neurons", "iaf_psc_exp.nestml"),
#            os.path.join("models", "synapses", "stdp_synapse.nestml")
            ]
        input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, s))) for s in files]
        target_path = "spinnaker-target"
        install_path = "spinnaker-install"
        logging_level = "DEBUG"
        module_name = "nestmlmodule"
        suffix = "_nestml"
        generate_spinnaker_target(input_path,
                                  target_path=target_path,
                                  install_path=install_path,
                                  logging_level=logging_level,
                                  module_name=module_name,
                                  suffix=suffix)
#                                  codegen_opts=codegen_opts)

    def test_iaf_psc_exp(self):

        # import spynnaker and plotting stuff
        import pyNN.spiNNaker as p
        from pyNN.utility.plotting import Figure, Panel
        import matplotlib.pyplot as plt

        # import models
        from python_models8.neuron.builds.iaf_psc_exp_nestml import iaf_psc_exp_nestml

        dt = 0.1 # the resolution in ms
        simtime = 10000.0 # Simulation time in ms
        delay = 1.5 # synaptic delay in ms
        g = 4.0 # ratio inhibitory weight/excitatory weight
        eta = 2 # external rate relative to threshold rate
        epsilon = 0.05 # connection probability
        order = 2500
        NE = 4 * order # number of excitatory neurons
        NI = 1 * order # number of inhibitory neurons
        N_neurons = NE + NI # number of neurons in total
        CE = int(epsilon * NE) # number of excitatory synapses per neuron
        CI = int(epsilon * NI) # number of inhibitory synapses per neuron
        C_tot = int(CI + CE) # total number of synapses per neuron
        tauMem = 20.0 # time constant of membrane potential in ms
        theta = 20.0 # membrane threshold potential in mV
        J = 0.1 # postsynaptic amplitude in mV
        neuron_params = {
        "C_m": 0.7,
        "tau_m": tauMem,
        "t_ref": 2.0,
        "E_L": 0.0,
        "V_reset": 0.0,
        "V_th": theta,
        "tau_syn_exc": 0.4,
        "tau_syn_inh": 0.4,
        }
        J_ex = J # amplitude of excitatory postsynaptic current
        J_in = -g * J_ex # amplitude of inhibitory postsynaptic current
        nu_th = theta / (J * CE * tauMem)
        nu_ex = eta * nu_th
        p_rate = 1000.0 * nu_ex * CE
        p.setup(dt)
        nodes_ex = p.Population(NE, iaf_psc_exp_nestml(**neuron_params))
        nodes_in = p.Population(NI, iaf_psc_exp_nestml(**neuron_params))
        noise = p.Population(20, p.SpikeSourcePoisson(rate=p_rate),
                             label="expoisson", seed=3)
        noise.record("spikes")
        nodes_ex.record("spikes")
        nodes_in.record("spikes")
        exc_conn = p.FixedTotalNumberConnector(CE)
        inh_conn = p.FixedTotalNumberConnector(CI)
        #p.Projection(nodes_ex, nodes_ex, exc_conn, receptor_type="exc_spikes", synapse_type=p.StaticSynapse(weight=J_ex, delay=delay))
        #p.Projection(nodes_ex, nodes_in, exc_conn, receptor_type="exc_spikes", synapse_type=p.StaticSynapse(weight=J_ex, delay=delay))
        #p.Projection(nodes_in, nodes_ex, inh_conn, receptor_type="inh_spikes", synapse_type=p.StaticSynapse(weight=J_in, delay=delay))
        #p.Projection(nodes_in, nodes_in, inh_conn, receptor_type="inh_spikes", synapse_type=p.StaticSynapse(weight=J_in, delay=delay))
        #p.Projection(noise, nodes_ex, exc_conn, receptor_type="exc_spikes", synapse_type=p.StaticSynapse(weight=J_ex, delay=delay))
        #p.Projection(noise, nodes_in, exc_conn, receptor_type="exc_spikes", synapse_type=p.StaticSynapse(weight=J_ex, delay=delay))

        p.run(simtime=simtime)


        exc_spikes = nodes_ex.get_data("spikes")
        inh_spikes = nodes_in.get_data("spikes")

        print("CV = " + str(compute_cv_for_neurons(exc_spikes.segments[0].spiketrains)))

        Figure(
         # raster plot of the presynaptic neuron spike times
         Panel(exc_spikes.segments[0].spiketrains, xlabel="Time/ms",
         xticks=True,
         yticks=True, markersize=0.2, xlim=(0, simtime)),
         # raster plot of the presynaptic neuron spike times
         Panel(inh_spikes.segments[0].spiketrains, xlabel="Time/ms",
         xticks=True,
         yticks=True, markersize=0.2, xlim=(0, simtime)),
        title="",)
        plt.savefig("balanced_network.png")
        plt.savefig("balanced_network.pdf")
