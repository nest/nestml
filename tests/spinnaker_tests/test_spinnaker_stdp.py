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
        #!! delay variable added
        codegen_opts = {"neuron_synapse_pairs": [{"neuron": "iaf_psc_exp_neuron",
                                                  "synapse": "stdp_synapse",
                                                  "post_ports": ["post_spikes"]}],
                        "delay_variable":{"stdp_synapse":"d"},
                        "weight_variable":{"stdp_synapse":"w"}}




        files = [
            os.path.join("models", "neurons", "iaf_psc_exp_neuron.nestml"),
        #!!
            os.path.join("models", "synapses", "stdp_synapse.nestml")
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
                                  suffix=suffix,
                                  codegen_opts=codegen_opts)

    def test_iaf_psc_exp(self):
        # import spynnaker and plotting stuff
        import pyNN.spiNNaker as p
        from pyNN.utility.plotting import Figure, Panel
        import matplotlib.pyplot as plt


        # import models
        from python_models8.neuron.builds.iaf_psc_exp_neuron_nestml__with_stdp_synapse_nestml import iaf_psc_exp_neuron_nestml__with_stdp_synapse_nestml as iaf_psc_exp_neuron_nestml
        from python_models8.neuron.builds.stdp_synapse_nestml__with_iaf_psc_exp_neuron_nestml import stdp_synapse_nestml__with_iaf_psc_exp_neuron_nestml as stdp_synapse_nestml
#        from python_models8.neuron.builds.stdp_synapse_nestml__with_iaf_psc_exp_neuron_nestml_timing import MyTimingDependence
 #       from python_models8.neuron.builds.stdp_synapse_nestml__with_iaf_psc_exp_neuron_nestml_weight import MyWeightDependence


        # TODO: Set names for exitatory input, membrane potential and synaptic response
        exc_input = "exc_spikes"
        membranePot = "V_m"
        synapticRsp = "I_syn_exc"

        # Set the run time of the execution
        run_time = 1500

        # Set the time step of the simulation in milliseconds
        time_step = 1

        # Set the number of neurons to simulate
        n_neurons = 1

        # Set the i_offset current
        i_offset = 0.0

        # Set the weight of input spikes
        weight = 2000

        # Set the times at which to input a spike
        pre_spike_times = [1, 5, 100]
        post_spike_times = [1, 5, 100]

        p.setup(time_step)

        #pre and post excitation neurons
        pre_spikeArray = {"spike_times": pre_spike_times}
        pre_excitation = p.Population(
            n_neurons, p.SpikeSourceArray(**pre_spikeArray), label="input")

        post_spikeArray = {"spike_times": post_spike_times}
        post_excitation = p.Population(
            n_neurons, p.SpikeSourceArray(**post_spikeArray), label="input")

        #pre and post spiking neuron populations which are connected later with stdp synapse
        pre_spiking_neuron = p.Population(
            n_neurons, iaf_psc_exp_neuron_nestml(), label="iaf_psc_exp_neuron_nestml_spiking")
        post_spiking_neuron = p.Population(
            n_neurons, iaf_psc_exp_neuron_nestml(), label="iaf_psc_exp_neuron_nestml_spiking")


        #connect exc populations with pre and post populations
        p.Projection(
            pre_excitation, pre_spiking_neuron,
            p.OneToOneConnector(), receptor_type=exc_input,
            synapse_type=p.StaticSynapse(weight=weight))

        p.Projection(
            post_excitation, post_spiking_neuron,
            p.OneToOneConnector(), receptor_type=exc_input,
            synapse_type=p.StaticSynapse(weight=weight))



        """
        #pop and proj for testing reasons
        pre_receiving_neuron = p.Population(
            n_neurons, iaf_psc_exp_neuron_nestml(), label="iaf_psc_exp_neuron_nestml_receiving")
        p.Projection(
            pre_spiking_neuron, pre_receiving_neuron,
            p.OneToOneConnector(), receptor_type=exc_input,
            synapse_type=p.StaticSynapse(weight=weight))


        post_receiving_neuron = p.Population(
            n_neurons, iaf_psc_exp_neuron_nestml(), label="iaf_psc_exp_neuron_nestml_receiving")
        p.Projection(
            post_spiking_neuron, post_receiving_neuron,
            p.OneToOneConnector(), receptor_type=exc_input,
            synapse_type=p.StaticSynapse(weight=weight))
        """



#TODO connect pre and post receiver neurons with stdp synapse

        #timing and weight are fixed in stdp model
        #timing_rule = MyTimingDependence(my_depression_parameter=20.0, my_potentiation_parameter=20.0,A_plus=2, A_minus=2)
        #weight_rule = MyWeightDependence(w_max=10, w_min=0)

        stdp_model = stdp_synapse_nestml()
        stdp_projection = p.Projection(pre_spiking_neuron,post_spiking_neuron,p.OneToOneConnector(),synapse_type=stdp_model,receptor_type=exc_input)




#TODO rename/delete recording variables
        """
        spiking_neuron.record(["spikes"])
        spiking_neuron.record([membranePot])
        spiking_neuron.record([synapticRsp])

        receiving_neuron.record(["spikes"])
        receiving_neuron.record([membranePot])
        receiving_neuron.record([synapticRsp])
        """




        p.run(run_time)
        """
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
        """

        """

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
        """
        p.end()
