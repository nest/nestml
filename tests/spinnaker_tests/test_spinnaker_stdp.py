# -*- coding: utf-8 -*-
#
# test_spinnaker_stdp.py
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


class TestSpiNNakerSTDP:
    """SpiNNaker code generation tests"""

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
        module_name = "nestmlmodule"
        suffix = "_nestml"
        generate_spinnaker_target(input_path,
                                  target_path=target_path,
                                  install_path=install_path,
                                  logging_level=logging_level,
                                  module_name=module_name,
                                  suffix=suffix,
                                  codegen_opts=codegen_opts)

    def test_stdp(self):
        # import spynnaker and plotting stuff
        import pyNN.spiNNaker as p
        from pyNN.utility.plotting import Figure, Panel
        import matplotlib.pyplot as plt


        # import models
        #from python_models8.neuron.builds.iaf_psc_exp_neuron_nestml__with_stdp_synapse_nestml import iaf_psc_exp_neuron_nestml__with_stdp_synapse_nestml as iaf_psc_exp_neuron_nestml
        #from python_models8.neuron.implementations.stdp_synapse_nestml__with_iaf_psc_exp_neuron_nestml_impl import stdp_synapse_nestml__with_iaf_psc_exp_neuron_nestmlDynamics as stdp_synapse_nestml

        from python_models8.neuron.builds.iaf_psc_exp_neuron_nestml import iaf_psc_exp_neuron_nestml as iaf_psc_exp_neuron_nestml
        from python_models8.neuron.implementations.stdp_synapse_nestml_impl import stdp_synapse_nestmlDynamics as stdp_synapse_nestml

        p.setup(timestep=1.0)
        exc_input = "exc_spikes"
        inh_input = "inh_spikes"

        #inputs for pre and post synaptic neurons
        pre_input = p.Population(1, p.SpikeSourceArray(spike_times=[0]), label="pre_input")
        post_input = p.Population(1, p.SpikeSourceArray(spike_times=[0]), label="post_input")

        #pre and post synaptic spiking neuron populations
        pre_spiking = p.Population(1, iaf_psc_exp_neuron_nestml(), label="pre_spiking")
        post_spiking = p.Population(1, iaf_psc_exp_neuron_nestml(), label="post_spiking")

        #pre w 5 post w 7
        weight_pre = 3000
        weight_post = 6000


        #connect exc populations with pre and post populations
        p.Projection(
            pre_input, pre_spiking,
            p.OneToOneConnector(), receptor_type=exc_input,
            synapse_type=p.StaticSynapse(weight=weight_pre))

        p.Projection(
            post_input, post_spiking,
            p.OneToOneConnector(), receptor_type=exc_input,
            synapse_type=p.StaticSynapse(weight=weight_post))



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



#        stdp_model = stdp_synapse_nestml()
#        stdp_projection = p.Projection(pre_spiking_neuron,post_spiking_neuron,p.OneToOneConnector(),synapse_type=stdp_model,receptor_type=exc_input)

        #connecting inputs with spiking neuron populations
        #pre_input2spiking = p.Projection(pre_input, pre_spiking, p.OneToOneConnector(), synapse_type=p.StaticSynapse(weight=weight_pre, delay=1),receptor_type=exc_input)
        #post_input2spiking = p.Projection(post_input, post_spiking, p.OneToOneConnector(), synapse_type=p.StaticSynapse(weight=weight_post, delay=1),receptor_type=exc_input)

        stdp_model = stdp_synapse_nestml()
        stdp_projection = p.Projection(pre_spiking, post_spiking, p.AllToAllConnector(), synapse_type=stdp_model, receptor_type=exc_input)
        #stdp_projection_inh = p.Projection(pre_spiking, post_spiking, p.AllToAllConnector(), synapse_type=stdp_model, receptor_type=inh_input)

        #initialise lists for axis
        res_weights = []
        spike_time_axis = []
        #run time of the simulator
        simtime = 1100
        #nr of iterations maxit has to be smaller than simtime
        max_it = 200
        #datapoints generated
        points_gen = 1


        #record spikes
        pre_spiking.record(["spikes"])
        post_spiking.record(["spikes"])

        pre_input.set(spike_times=[100, 110, 120, 1000])

        print("All properties: " + str(stdp_projection.get()))

        #calculate all data points
        for t_post in [142.]: #np.linspace(0,max_it,points_gen):
                post_input.set(spike_times=[t_post])

                p.run(simtime)


                #get weights for current run and append them into array
                w_curr = stdp_projection.get("weight",format="float")
                #post_tr_curr = stdp_projection.get("post_trace",format="float")
                print("w_curr = " + str(w_curr))
                #print("post_tr_curr = " + str(post_tr_curr))

                res_weights.append(w_curr[0][0])

                p.reset()


        pre_spike_times = []
        post_spike_times = []

        


        pre_neo = pre_spiking.get_data("spikes")
        post_neo = post_spiking.get_data("spikes")

        #get spike data and calculate axis
        for i in range(0,points_gen):

                pre_spikes = pre_neo.segments[i].spiketrains

                post_spikes = post_neo.segments[i].spiketrains
                #calculate x axis for plot

                spike_time_axis.append(float(pre_spikes[0][0]-post_spikes[0][0]))
                pre_spike_times.append(pre_spikes[0][0])
                post_spike_times.append(post_spikes[0][0])

        p.end()


        #for testing purposes
        print("HALLO pre_spikes")
        print(pre_spike_times)
        print("HALLO post_spikes")
        print(post_spike_times)
        print("HALLO spike time axis")
        print(spike_time_axis)
        print("weights after simulation: " + str(res_weights))


        #format weight axis an substract 2.5 from every entry

        weight_axis = [x - 2.5 for x in res_weights]


        #PLOT
        plt.plot(spike_time_axis, weight_axis,'.')
        plt.xlabel("$t_{pre} - t_{post} [ms]$")
        plt.ylabel("$\Delta w$")
        plt.title("STDP-Window")
        plt.grid(True)

        plt.subplots_adjust(bottom=0.2)

        plt.figtext(0.5, 0.05,
                        r"$\tau_+ = 20ms,\tau_- = 20ms, A_+ = 0.5, A_- = 0.5$",
                        ha='center',       # horizontal alignment
                        va='bottom',       # vertical alignment
                        fontsize=10,
                        color='gray')



        plt.savefig("plot.png")
