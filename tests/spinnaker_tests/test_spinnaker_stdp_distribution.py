# -*- coding: utf-8 -*-
#
# test_spinnaker_stdp_distribution.py
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


class TestSpiNNakerSTDPDistribution:
    """SpiNNaker code generation tests"""

    @pytest.fixture(autouse=True,
                    scope="module")
    def generate_code(self):
        codegen_opts = {"neuron_synapse_pairs": [{"neuron": "iaf_psc_exp", #"iaf_delta_neuron",
                                                  "synapse": "stdp_synapse",
                                                  "post_ports": ["post_spikes"]}],
                        "delay_variable":{"stdp_synapse":"d"},
                        "weight_variable":{"stdp_synapse":"w"}}

        files = [
            os.path.join("models", "neurons", "iaf_psc_exp_neuron.nestml"),
#            os.path.join("models", "neurons", "iaf_delta_neuron.nestml"),
            os.path.join("models", "synapses", "stdp_additive_synapse.nestml")
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

    def run_sim(self, n_inputs=1, input_rate=10., simtime=1000):
        r"""
        input_rate is in spikes/s
        simtime is in ms and should be about 100 s for convergence
        """
        import pyNN.spiNNaker as p
        from pyNN.utility.plotting import Figure, Panel

        from python_models8.neuron.builds.iaf_psc_exp_neuron_nestml import iaf_psc_exp_neuron_nestml as iaf_neuron_nestml
        #from python_models8.neuron.builds.iaf_delta_neuron_nestml import iaf_delta_neuron_nestml as iaf_delta_neuron_nestml
        from python_models8.neuron.implementations.stdp_synapse_nestml_impl import stdp_synapse_nestmlDynamics as stdp_synapse_nestml

#        p.reset()
        p.setup(timestep=1.0)
        exc_input = "exc_spikes"

        neuron_parameters = { # XXX UNUSED
            "E_L": -70.,  # [mV]
            "V_reset": -65.,    # [mV]
            "V_th": -50.,    # [mV]
            "tau_m": 20.,  # [ms]
            "t_refr": 5.,    # [ms]
        }

        stdp_parameters = { # XXX UNUSED
            "W_min": 0.,
            "W_max": 30.,
            "tau_pre": 20.,    # [ms]
            "tau_post": 20.,    # [ms]
            "A_pot": 0.01,
            "A_dep": 0.02
        }

        initial_weight = 1500.    # [mV]

        #inputs for pre and post synaptic neurons
        pre_input = p.Population(n_inputs, p.SpikeSourcePoisson(rate=input_rate), label="pre_input")
        post_neuron = p.Population(1, iaf_neuron_nestml(), label="post_neuron")

        #weight_pre = 3000
        #weight_post = 3000

        #p.Projection(pre_input, pre_spiking, p.OneToOneConnector(), receptor_type=exc_input, synapse_type=p.StaticSynapse(weight=weight_pre))
        #p.Projection(pre_input, post_neuron, p.OneToOneConnector(), receptor_type=exc_input, synapse_type=p.StaticSynapse(weight=weight_post))

        #stdp_model = stdp_synapse_nestml(weight=50000) # should cause a 5 mV deflection in the postsynaptic potential



        #stdp_model = p.StaticSynapse(weight=initial_weight) # should cause a 2.5 mV deflection in the postsynaptic potential
        stdp_model = stdp_synapse_nestml(weight=initial_weight) # should cause a 2.5 mV deflection in the postsynaptic potential
        stdp_projection = p.Projection(pre_input, post_neuron, p.AllToAllConnector(), synapse_type=stdp_model, receptor_type=exc_input)

        # XXX: TODO: # Initialize weights to a random value around the midpoint
        # stdp_projection.w = f'rand() * {INITIAL_WEIGHT / b2.mV} * mV'


        #record spikes
        pre_input.record(["spikes"])
        post_neuron.record(["spikes"])
        post_neuron.record(["V_m"])


        #pre_input.set(spike_times=[100, 110, 120, 1000])
        #pre_input.set(spike_times=pre_spike_times)
        #post_input.set(spike_times=post_spike_times)

        p.run(simtime)

        pre_neo = pre_input.get_data("spikes")
        post_neo = post_neuron.get_data("spikes")

        pre_spike_times = pre_neo.segments[0].spiketrains
        post_spike_times = post_neo.segments[0].spiketrains

        w = stdp_projection.get("weight", format="float")

        v_post_neuron = post_neuron.get_data("V_m")
        times = v_post_neuron.segments[0].analogsignals[0].times
        v_post_neuron = np.array(v_post_neuron.segments[0].filter(name="V_m")[0])

        p.end()
        print(w)

        import pdb;pdb.set_trace()

        return times, v_post_neuron, w, pre_spike_times, post_spike_times


    def test_stdp(self):
        times, v_post_neuron, dw, actual_pre_spike_times, actual_post_spike_times = self.run_sim()
        print("actual pre_spikes: " + str(actual_pre_spike_times))
        print("actual post_spikes: " + str(actual_post_spike_times))
        print("weights after simulation: " + str(dw))


        fig, ax = plt.subplots(nrows=2)
        ax[0].plot(actual_pre_spike_times, np.zeros_like(actual_pre_spike_times), '.')
        ax[0].plot(actual_post_spike_times, np.ones_like(actual_post_spike_times), '.')
        ax[1].plot(times, v_post_neuron)
        ax[1].set_ylabel("V_m")
        ax[-1].set_xlabel(r"$t$ [ms]")
        ax[0].set_ylabel(r"$w$")
        for _ax in ax:
            _ax.grid(True)

#        ax.subplots_adjust(bottom=0.2)

        """ax.figtext(0.5, 0.05,
                        r"$\tau_+ = 20ms,\tau_- = 20ms, A_+ = 0.5, A_- = 0.5$",
                        ha='center',       # horizontal alignment
                        va='bottom',       # vertical alignment
                        fontsize=10,
                        color='gray')"""



        fig.savefig("plot.png")
