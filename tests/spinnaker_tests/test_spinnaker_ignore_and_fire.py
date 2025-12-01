# -*- coding: utf-8 -*-
#
# test_spinnaker_ignore_and_fire.py
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
        files = [
            os.path.join("models", "neurons", "ignore_and_fire_neuron.nestml"),
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

    def test_ignore_and_fire(self):
        # import spynnaker and plotting stuff
        import pyNN.spiNNaker as p
        from pyNN.utility.plotting import Figure, Panel
        import matplotlib.pyplot as plt

        # import models
        from python_models8.neuron.builds.ignore_and_fire_neuron_nestml import ignore_and_fire_neuron_nestml

        # TODO: Set names for exitatory input, membrane potential and synaptic response
        exc_input = "spikes"
        membranePot = "phase"

        # Set the run time of the execution
        run_time = 100

        # Set the time step of the simulation in milliseconds
        time_step = 1

        # Set the number of neurons to simulate
        n_neurons = 1

        # Set the sending population firing rate
        sender_firing_rate = 100.

        # Set the receiving population firing rate
        receiver_firing_rate = 10.


        receiver_firing_rate /= 1000.    # XXX: this is to work around a bug!
        receiver_firing_period_steps = 1 / receiver_firing_rate

        sender_firing_rate /= 1000.    # XXX: this is to work around a bug!
        sender_firing_period_steps = 1 / sender_firing_rate

        # Set the weight of input spikes
        weight = 2000

        # Set the times at which to input a spike
        spike_times = [25, 50, 75]

        p.setup(time_step)
        #p.set_number_of_synapse_cores(ignore_and_fire_neuron_nestml, 0)    # Fix an issue with new feature in the main code, where sPyNNaker is trying to determine whether to use a split core model where neurons and synapses are on separate cores, or a single core model where they are processed on the same core. In the older code, this was a more manual decision, but in the main code it is happening automatically unless overridden.  This is particularly true when you use the 0.1ms timestep, where it will be attempting to keep to real-time execution by using split cores.

        spikeArray = {"spike_times": spike_times}
        excitation = p.Population(n_neurons, p.SpikeSourceArray(**spikeArray), label="input")

        spiking_neuron = p.Population(n_neurons, ignore_and_fire_neuron_nestml(), label="ignore_and_fire_neuron_nestml_spiking")
        spiking_neuron.set(firing_period_steps=sender_firing_period_steps)
        spiking_neuron.set(firing_rate=sender_firing_rate)

        p.Projection(
            excitation, spiking_neuron,
            p.OneToOneConnector(), receptor_type=exc_input,
            synapse_type=p.StaticSynapse(weight=weight))

        receiving_neuron = p.Population(n_neurons, ignore_and_fire_neuron_nestml(), label="ignore_and_fire_neuron_nestml_receiving")
        receiving_neuron.set(firing_period_steps=receiver_firing_period_steps)
        receiving_neuron.set(firing_rate=receiver_firing_rate)

        p.Projection(
            spiking_neuron, receiving_neuron,
            p.OneToOneConnector(), receptor_type=exc_input,
            synapse_type=p.StaticSynapse(weight=weight))

        spiking_neuron.record(["spikes"])
        spiking_neuron.record([membranePot])

        receiving_neuron.record(["spikes"])
        receiving_neuron.record([membranePot])

        p.run(run_time)

        # get v for each example
        spikes_spiking_neuron = spiking_neuron.get_data("spikes")
        v_spiking_neuron = spiking_neuron.get_data(membranePot)

        spikes_receiving_neuron = receiving_neuron.get_data("spikes")
        v_receiving_neuron = receiving_neuron.get_data(membranePot)

        plt.clf()

        Figure(
            # membrane potentials for each example

            Panel(spikes_spiking_neuron.segments[0].spiketrains,
                  xlabel="Time (ms)",
                  data_labels=["spikes sender"],
                  yticks=True, xlim=(0, run_time), xticks=True),

            Panel(spikes_receiving_neuron.segments[0].spiketrains,
                  xlabel="Time (ms)",
                  data_labels=["spikes receiver"],
                  yticks=True, xlim=(0, run_time), xticks=True),

            #Panel(combined_spikes,
            #      xlabel="Time (ms)",
            #      data_labels=["spikes"],
            #      yticks=True, xlim=(0, run_time), xticks=True),

            Panel(v_spiking_neuron.segments[0].filter(name=membranePot)[0],
                  xlabel="Time (ms)",
                  ylabel="Membrane potential (mV)",
                  data_labels=[spiking_neuron.label],
                  yticks=True, xlim=(0, run_time), xticks=True),

            Panel(v_receiving_neuron.segments[0].filter(name=membranePot)[0],
                  xlabel="Time (ms)",
                  ylabel="Membrane potential (mV)",
                  data_labels=[receiving_neuron.label],
                  yticks=True, xlim=(0, run_time), xticks=True),

            title="Ignore-and-fire neuron demo",
            annotations="Simulated with {}".format(p.name())
        )
        plt.savefig("spinnaker_ignore_and_fire.png")

        import pdb;pdb.set_trace()

        p.end()
