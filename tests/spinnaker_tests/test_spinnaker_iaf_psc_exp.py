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

from spinnaker_test_utils import figsize, plot_analog_signal, plot_spike_raster


class TestSpiNNakerIafPscExp:
    """SpiNNaker code generation tests"""

    @pytest.fixture(autouse=True,
                    scope="module")
    def generate_code(self):
        files = [
            os.path.join("models", "neurons", "iaf_psc_exp_neuron.nestml"),
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
                                  suffix=suffix)

    def test_iaf_psc_exp(self):
        # import spynnaker and plotting stuff
        import pyNN.spiNNaker as p
        import matplotlib.pyplot as plt

        # import models
        from python_models8.neuron.builds.iaf_psc_exp_neuron_nestml import iaf_psc_exp_neuron_nestml

        # TODO: Set names for exitatory input, membrane potential and synaptic response
        exc_input = "exc_spikes"
        membranePot = "V_m"
        synapticRsp = "I_syn_exc"

        # Set the run time of the execution
        run_time = 200

        # Set the time step of the simulation in milliseconds
        time_step = 1

        # Set the i_offset current
        i_offset = 0.0

        # Set the weight of input spikes
        weight = 2000

        # Set the times at which to input a spike
        spike_times = [1, 5, 100]

        p.setup(time_step)
        #p.set_number_of_synapse_cores(iaf_psc_exp_neuron_nestml, 0)    # Fix an issue with new feature in the main code, where sPyNNaker is trying to determine whether to use a split core model where neurons and synapses are on separate cores, or a single core model where they are processed on the same core. In the older code, this was a more manual decision, but in the main code it is happening automatically unless overridden.  This is particularly true when you use the 0.1ms timestep, where it will be attempting to keep to real-time execution by using split cores.

        spikeArray = {"spike_times": spike_times}
        excitation = p.Population(1, p.SpikeSourceArray(**spikeArray), label="input")

        spiking_neuron = p.Population(1, iaf_psc_exp_neuron_nestml(), label="iaf_psc_exp_neuron_nestml_spiking")
        p.Projection(
            excitation, spiking_neuron,
            p.OneToOneConnector(), receptor_type=exc_input,
            synapse_type=p.StaticSynapse(weight=weight))

        receiving_neuron = p.Population(1, iaf_psc_exp_neuron_nestml(), label="iaf_psc_exp_neuron_nestml_receiving")
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

        # run the simulation
        p.run(run_time)

        # grab recorded data
        spikes_spiking_neuron = spiking_neuron.get_data("spikes")
        v_spiking_neuron = spiking_neuron.get_data(membranePot)
        i_syn_exc_spiking_neuron = spiking_neuron.get_data(synapticRsp)

        spikes_receiving_neuron = receiving_neuron.get_data("spikes")
        v_receiving_neuron = receiving_neuron.get_data(membranePot)
        i_syn_exc_receiving_neuron = receiving_neuron.get_data(synapticRsp)

        combined_spikes = spikes_spiking_neuron.segments[0].spiketrains
        for spike in spikes_receiving_neuron.segments[0].spiketrains:
            combined_spikes.append(spike)

        fig, ax = plt.subplots(5, 1, sharex=True, figsize=figsize(11.2 / 6))
        plot_spike_raster(ax[0], combined_spikes, label="spikes")
        plot_analog_signal(ax[1], i_syn_exc_spiking_neuron.segments[0].filter(name=synapticRsp)[0], label=spiking_neuron.label, ylabel=r"$I_\mathrm{syn,exc}$")
        plot_analog_signal(ax[2], v_spiking_neuron.segments[0].filter(name=membranePot)[0], label=spiking_neuron.label, ylabel=r"$V_m$ [mV]")
        plot_analog_signal(ax[3], i_syn_exc_receiving_neuron.segments[0].filter(name=synapticRsp)[0], label=receiving_neuron.label, ylabel=r"$I_\mathrm{syn,exc}$")
        plot_analog_signal(ax[4], v_receiving_neuron.segments[0].filter(name=membranePot)[0], label=receiving_neuron.label, ylabel=r"$V_m$ [mV]")
        ax[-1].set_xlim(0, run_time)
        ax[-1].set_xlabel("Time [ms]")
        fig.suptitle("Generated: Two chained neurons")
        fig.align_ylabels(ax)
        fig.tight_layout()
        fig.savefig("test_spinnaker_iaf_psc_exp.png")
        plt.close(fig)

        p.end()
