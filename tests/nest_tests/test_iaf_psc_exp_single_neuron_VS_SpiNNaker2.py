import os.path

import nest
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pytest
from pynestml.codegeneration.nest_tools import NESTTools

from pynestml.frontend.pynestml_frontend import generate_nest_target

@pytest.mark.skipif(NESTTools.detect_nest_version().startswith("v2"),
                    reason="This test does not support NEST 2")
def test_iaf_psc_exp_single_neuron_VS_SpiNNaker2():
    """
    A test for iaf_psc_exp model single neuron spiking to compare
    spike times and v_mem plots with PySpiNNaker2 implementation
    """
    target_path = "target_iaf_psc_exp_single_neuron_VS_spiNNaker2"
    module_name = "nestml_module"
    input_path = os.path.realpath(os.path.join(os.path.dirname(__file__), "resources", "iaf_psc_exp_neuron.nestml"))
    generate_nest_target(input_path=input_path,
                         target_path=target_path,
                         logging_level="INFO",
                         module_name=module_name)
    nest.Install(module_name)
    nest.resolution = 1
    spikeSource = nest.Create("spike_train_injector",
                params={"spike_times": [1.0, 5.0, 100.0]})
    neuron = nest.Create("iaf_psc_exp_neuron")
    vm = nest.Create("multimeter", params={"interval": 1, "record_from": ["V_m"], "record_to": "memory", "time_in_steps":True})
    spikerecorderNeuron = nest.Create("spike_recorder")
    spikerecorderSource = nest.Create("spike_recorder")
    nest.Connect(vm, neuron)
    nest.Connect(neuron, spikerecorderNeuron)
    nest.Connect(spikeSource, spikerecorderSource)
    nest.Connect(spikeSource, neuron, syn_spec={"weight": 2000.0})
    nest.Simulate(150)
    t_step = [150.]
    # Plotting
    membraneVoltage = vm.get("events")
    spikesNeuron = spikerecorderNeuron.get("events")
    spikesSource = spikerecorderSource.get("events")


    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True, height_ratios=(1, 2, 1))

    indices, times = spikesSource["senders"], spikesSource["times"]
    ax1.plot(times, indices, "|", ms=20)
    ax1.set_ylabel("input spikes")
    ax1.set_ylim((-5, 5))

    times = np.arange(t_step[0])
    ax2.plot(membraneVoltage["times"].tolist(), membraneVoltage["V_m"].tolist(), label="iaf_psc_exp_neuron")
    ax2.axhline(-55, ls="--", c="0.5", label="threshold")
    ax2.axhline(0, ls="-", c="0.8", zorder=0)
    ax2.set_xlim(0, t_step[0])
    ax2.set_ylabel("voltage")
    ax2.legend()

    indices, times = spikesNeuron["senders"].tolist(), spikesNeuron["times"].tolist()
    ax3.plot(times, indices, "|", ms=20)
    ax3.set_ylabel("output spikes")
    ax3.set_xlabel("time step")
    ax3.set_ylim((-5, 5))
    fig.suptitle("NESTML iaf_psc_exp_single_neuron_VS_SpiNNaker2")
    plt.savefig("plot_timestep")
