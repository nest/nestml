# -*- coding: utf-8 -*-
#
# test_spinnaker_stdp_psp.py
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
import time

from pynestml.frontend.pynestml_frontend import generate_spinnaker_target


class TestSpiNNakerSTDPPSP:
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

    def run_sim(self, pre_spike_times, weight=123, simtime=50):
        import pyNN.spiNNaker as p
        from pyNN.utility.plotting import Figure, Panel

        from python_models8.neuron.builds.iaf_psc_exp_neuron_nestml import iaf_psc_exp_neuron_nestml as iaf_psc_exp_neuron_nestml
        from python_models8.neuron.implementations.stdp_synapse_nestml_impl import stdp_synapse_nestmlDynamics as stdp_synapse_nestml

        p.setup(timestep=1.0)
        exc_input = "exc_spikes"
        inh_input = "inh_spikes"

        #inputs for presynaptic neuron
        pre_input = p.Population(1, p.SpikeSourceArray(spike_times=[0]), label="pre_input")
        post_neuron = p.Population(1, iaf_psc_exp_neuron_nestml(), label="post_neuron")

        stdp_model = stdp_synapse_nestml(weight=weight)
        stdp_projection = p.Projection(pre_input, post_neuron, p.OneToOneConnector(), receptor_type=exc_input, synapse_type=stdp_model)

        #record spikes
        pre_input.record(["spikes"])
        post_neuron.record(["spikes"])
        post_neuron.record(["V_m"])
        post_neuron.record(["I_syn_exc"])

        pre_input.set(spike_times=pre_spike_times)

        p.run(simtime)


        v_post_neuron = post_neuron.get_data("V_m")
        times = v_post_neuron.segments[0].analogsignals[0].times
        v_post_neuron = np.array(v_post_neuron.segments[0].filter(name="V_m")[0])
        i_syn_exc_post_neuron = post_neuron.get_data("I_syn_exc")
        i_syn_exc_post_neuron = np.array(i_syn_exc_post_neuron.segments[0].filter(name="I_syn_exc")[0])

        """pre_neo = pre_input.get_data("spikes")
        post_neo = post_neuron.get_data("spikes")

        pre_spike_times = pre_neo.segments[0].spiketrains
        post_spike_times = post_neo.segments[0].spiketrains

        import pdb;pdb.set_trace()"""

        p.end()

        return times, v_post_neuron, i_syn_exc_post_neuron


    @pytest.mark.parametrize("weight", [123, 1234])
    def test_stdp(self, weight):
        pre_spike_times = [10.]
        times, v_post_neuron, i_syn_exc_post_neuron = self.run_sim(pre_spike_times, weight=weight)

        fig, ax = plt.subplots(nrows=2)
        ax[0].plot(times, v_post_neuron, label="V_m")
        ax[1].plot(times, i_syn_exc_post_neuron, label="I_exc")
        for _ax in ax:
            _ax.grid(True)
            _ax.legend()
            _ax.set_xlim(np.amin(times), np.amax(times))

        ax[0].get_xticklabels([])
        ax[-1].set_xlabel("Time [ms]")

        fig.savefig("test_spinnaker_stdp_psp_" + str(time.strftime("%Y-%m-%d %H:%M:%S")) + ".png")

        assert len(np.unique(v_post_neuron)) > 1, "No PSPs detected in postsynaptic membrane potential"
        np.testing.assert_allclose(np.amax(i_syn_exc_post_neuron), weight)
