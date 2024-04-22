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
import pytest

from pynestml.frontend.pynestml_frontend import generate_spinnaker_target


class TestSpiNNakerIafPscExp:
    """SpiNNaker code generation tests"""

    @pytest.fixture(autouse=True,
                    scope="module")
    def generate_code(self):
        # codegen_opts = {"neuron_synapse_pairs": [{"neuron": "iaf_psc_exp_neuron",
        #                                           "synapse": "stdp_synapse",
        #                                           "post_ports": ["post_spikes"]}]}

        files = [
            os.path.join("models", "neurons", "iaf_psc_exp_neuron.nestml"),
            # os.path.join("models", "synapses", "stdp_synapse.nestml")
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
        #                          codegen_opts=codegen_opts)

    def test_iaf_psc_exp(self):
        # import spynnaker and plotting stuff
        import pyNN.spiNNaker as p
        from pyNN.utility.plotting import Figure, Panel
        import matplotlib.pyplot as plt

        # import models
        from python_models8.neuron.builds.iaf_psc_exp_nestml import iaf_psc_exp_nestml

        # TODO: Set names for exitatory input, membrane potential and synaptic response
        exc_input = "exc_spikes"
        membranePot = "V_m"
        synapticRsp = "I_kernel_exc__X__exc_spikes"

        # Set the run time of the execution
        run_time = 150

        # Set the time step of the simulation in milliseconds
        time_step = 0.1

        # Set the number of neurons to simulate
        n_neurons = 1

        # Set the i_offset current
        i_offset = 0.0

        # Set the weight of input spikes
        weight = 2000

        # Set the times at which to input a spike
        spike_times = [1, 5, 100]

        p.setup(time_step)

        spikeArray = {"spike_times": spike_times}
        excitation = p.Population(
            n_neurons, p.SpikeSourceArray(**spikeArray), label="input")

        spiking_neuron = p.Population(
            n_neurons, iaf_psc_exp_nestml(), label="iaf_psc_exp_nestml_spiking")
        p.Projection(
            excitation, spiking_neuron,
            p.OneToOneConnector(), receptor_type=exc_input,
            synapse_type=p.StaticSynapse(weight=weight))

        receiving_neuron = p.Population(
            n_neurons, iaf_psc_exp_nestml(), label="iaf_psc_exp_nestml_receiving")
        p.Projection(
            spiking_neuron, receiving_neuron,
            p.OneToOneConnector(), receptor_type=exc_input,
            synapse_type=p.StaticSynapse(weight=weight))

        spiking_neuron.record(["spikes"])
        spiking_neuron.record([membranePot])
        spiking_neuron.record([synapticRsp])

        receiving_neuron.record(["spikes"])
        receiving_neuron.record([membranePot])
        receiving_neuron.record([synapticRsp])

        p.run(run_time)

        # get v for each example
        spikes_spiking_neuron = spiking_neuron.get_data("spikes")
        v_spiking_neuron = spiking_neuron.get_data(membranePot)
        i_syn_exc_spiking_neuron = spiking_neuron.get_data(synapticRsp)

        spikes_receiving_neuron = receiving_neuron.get_data("spikes")
        v_receiving_neuron = receiving_neuron.get_data(membranePot)
        i_syn_exc_receiving_neuron = receiving_neuron.get_data(synapticRsp)

        combined_spikes = spikes_spiking_neuron.segments[0].spiketrains
        for spike in spikes_receiving_neuron.segments[0].spiketrains:
            combined_spikes.append(spike)

        Figure(
            # pylint: disable=no-member
            # membrane potentials for each example

            Panel(combined_spikes,
                  xlabel="Time (ms)",
                  data_labels=["spikes"],
                  yticks=True, xlim=(0, run_time), xticks=True),

            Panel(v_spiking_neuron.segments[0].filter(name=membranePot)[0],
                  xlabel="Time (ms)",
                  ylabel="Membrane potential (mV)",
                  data_labels=[spiking_neuron.label],
                  yticks=True, xlim=(0, run_time), xticks=True),

            Panel(i_syn_exc_spiking_neuron.segments[0].filter(name=synapticRsp)[0],
                  xlabel="Time (ms)",
                  ylabel="Synaptic response",
                  data_labels=[spiking_neuron.label],
                  yticks=True, xlim=(0, run_time), xticks=True),

            Panel(v_receiving_neuron.segments[0].filter(name=membranePot)[0],
                  xlabel="Time (ms)",
                  ylabel="Membrane potential (mV)",
                  data_labels=[receiving_neuron.label],
                  yticks=True, xlim=(0, run_time), xticks=True),

            Panel(i_syn_exc_receiving_neuron.segments[0].filter(name=synapticRsp)[0],
                  xlabel="Time (ms)",
                  ylabel="Synaptic response",
                  data_labels=[receiving_neuron.label],
                  yticks=True, xlim=(0, run_time), xticks=True),

            title="Generated: Two chained neurons",
            annotations="Simulated with {}".format(p.name())
        )
        plt.savefig("spinnaker.png")

        p.end()
