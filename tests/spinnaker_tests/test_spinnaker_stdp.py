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
import matplotlib.pyplot as plt
import numpy as np
import pytest

from pynestml.frontend.pynestml_frontend import generate_spinnaker_target


class TestSpiNNakerSTDP:
    """Test that STDP synapse produces correct STDP window"""

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
        suffix = "_nestml"
        generate_spinnaker_target(input_path,
                                  target_path=target_path,
                                  install_path=install_path,
                                  logging_level=logging_level,
                                  suffix=suffix,
                                  codegen_opts=codegen_opts)

    def run_sim(self, pre_spike_times, post_spike_times, simtime=1100):
        import pyNN.spiNNaker as p
        from pyNN.utility.plotting import Figure, Panel

        from python_models8.neuron.builds.iaf_psc_exp_neuron_nestml import iaf_psc_exp_neuron_nestml as iaf_psc_exp_neuron_nestml
        from python_models8.neuron.implementations.stdp_synapse_nestml_impl import stdp_synapse_nestmlDynamics as stdp_synapse_nestml

#        p.reset()
        p.setup(timestep=1.0)
        exc_input = "exc_spikes"

        #inputs for pre and post synaptic neurons
        pre_input = p.Population(1, p.SpikeSourceArray(spike_times=[0]), label="pre_input")
        post_input = p.Population(1, p.SpikeSourceArray(spike_times=[0]), label="post_input")

        #pre and post synaptic spiking neuron populations
        pre_spiking = p.Population(1, iaf_psc_exp_neuron_nestml(), label="pre_spiking")
        post_spiking = p.Population(1, iaf_psc_exp_neuron_nestml(), label="post_spiking")

        weight_pre = 3000
        weight_post = 3000

        p.Projection(pre_input, pre_spiking, p.OneToOneConnector(), receptor_type=exc_input, synapse_type=p.StaticSynapse(weight=weight_pre))
        p.Projection(post_input, post_spiking, p.OneToOneConnector(), receptor_type=exc_input, synapse_type=p.StaticSynapse(weight=weight_post))

        stdp_model = stdp_synapse_nestml(weight=1.)
        stdp_projection = p.Projection(pre_spiking, post_spiking, p.AllToAllConnector(), synapse_type=stdp_model, receptor_type="ignore_spikes")   # connect to a port where incoming spikes are ignored, so the STDP synapse itself does not change the postsynaptic spike timing
#        stdp_projection = p.Projection(pre_spiking, post_spiking, p.AllToAllConnector(), synapse_type=stdp_model, receptor_type="exc_spikes")   # connect to a port where incoming spikes are ignored, so the STDP synapse itself does not change the postsynaptic spike timing

        #record spikes
        pre_spiking.record(["spikes"])
        post_spiking.record(["spikes"])

        #pre_input.set(spike_times=[100, 110, 120, 1000])
        pre_input.set(spike_times=pre_spike_times)
        post_input.set(spike_times=post_spike_times)

        p.run(simtime)

        pre_neo = pre_spiking.get_data("spikes")
        post_neo = post_spiking.get_data("spikes")

        pre_spike_times = pre_neo.segments[0].spiketrains
        post_spike_times = post_neo.segments[0].spiketrains

        w_curr = stdp_projection.get("weight", format="float")

        p.end()

        return w_curr[0][0], pre_spike_times, post_spike_times


    def test_stdp(self):
        res_weights = []
        spike_time_axis = []

        pre_spike_times = [250, 1000]

        for t_post in np.linspace(200, 300, 7):  # XXX Should be 19
                dw, actual_pre_spike_times, actual_post_spike_times = self.run_sim(pre_spike_times, [t_post])

                spike_time_axis.append(float(actual_post_spike_times[0][0]) - float(actual_pre_spike_times[0][0]))

                res_weights.append(dw)

                print("actual pre_spikes: " + str(actual_pre_spike_times))
                print("actual post_spikes: " + str(actual_post_spike_times))
                print("weights after simulation: " + str(dw))

        print("Simulation results")
        print("------------------")
        print("timevec after sim = " + str(spike_time_axis))
        print("weights after sim = " + str(res_weights))




        fig, ax = plt.subplots()
        ax.plot(spike_time_axis, res_weights, '.')
        ax.set_xlabel(r"$t_{pre} - t_{post} [ms]$")
        ax.set_ylabel(r"$\Delta w$")
        ax.set_title("STDP-Window")
        ax.grid(True)

#        ax.subplots_adjust(bottom=0.2)

        """ax.figtext(0.5, 0.05,
                        r"$\tau_+ = 20ms,\tau_- = 20ms, A_+ = 0.5, A_- = 0.5$",
                        ha='center',       # horizontal alignment
                        va='bottom',       # vertical alignment
                        fontsize=10,
                        color='gray')"""



        fig.savefig("nestml_stdp_window.png")
