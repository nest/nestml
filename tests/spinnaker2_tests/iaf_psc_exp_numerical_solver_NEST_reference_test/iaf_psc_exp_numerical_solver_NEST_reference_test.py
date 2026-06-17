import nest
import os
from pynestml.codegeneration.nest_code_generator_utils import NESTCodeGeneratorUtils
import pytest
from pynestml.codegeneration.nest_tools import NESTTools
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from pynestml.frontend.pynestml_frontend import generate_nest_target

matplotlib.use("Agg")

# Step 1: Install the NESTML model
codegen_opts = {
    "quantity_to_preferred_prefix": {"electrical potential": "m",  # needed for V_m_init and U_m
                                                 "electrical current": "p",
                                                 "electrical resistance": "G",
                                                 "time": "m",
                                                 "frequency": "m",
                                                 "electrical capacitance": "p",

                                                 },
    "solver": 'numeric',
    "numeric_solver": "rk45",
}


target_path = "iaf_psc_exp_neuron_NO_ISTIM"
module_name = "nestml_module"
input_path="/home/weih/nestml/models/neurons/iaf_psc_exp_neuron_NO_ISTIM.nestml"
generate_nest_target(input_path=input_path,
                     target_path=target_path,
                     logging_level="INFO",
                     module_name=module_name,
                     suffix='',
                     codegen_opts=codegen_opts)
print('pause')
# nest.ResetKernel()
# nest.set_verbosity("M_WARNING")
# nest.Install(module_name)
# nest.resolution = 0.1
#
# # Step 2: Create the Izhikevich neuron with synaptic currents
# neuron = nest.Create('izhikevich_neuron_psc_exp_NO_ISTIM')
# # Step 3: Create spike generators
# exc_spikes = nest.Create("spike_generator", params={
#     "spike_times": [10.0,20.0,35.0,39.0, 50.0, 80.0],  # Excitatory spikes (ms)
# })
#
# inh_spikes = nest.Create("spike_generator", params={
#     "spike_times": [30.0, 60.0],  # Inhibitory spikes (ms)
# })
#
# # Step 4: Connect spike generators to the neuron
#
# nest.Connect(exc_spikes, neuron, syn_spec={
#     "weight": 100.0,    # pA
#     "delay": 1.0,
# })
#
# nest.Connect(inh_spikes, neuron, syn_spec={
#     "weight": -100.0,   # pA
#     "delay": 1.0,
# })
#
# # Step 5: Set up recording devices
# voltmeter = nest.Create("multimeter", params={
#     "record_from": ["V_m", "I_syn_exc", "I_syn_inh"],
# "interval": nest.resolution,
# })
# spike_recorder = nest.Create("spike_recorder")
# nest.Connect(voltmeter, neuron)
# nest.Connect(neuron, spike_recorder)
#
# # Step 6: Simulate for 100ms
# nest.Simulate(100.0)
#
# # Step 7: Retrieve and plot data
# data = nest.GetStatus(voltmeter)[0]["events"]
# spikes = nest.GetStatus(spike_recorder, "events")[0]
#
# plt.figure(figsize=(10, 6))
#
# # Plot membrane potential
# plt.subplot(3, 1, 1)
# plt.plot(data["times"], data["V_m"], label="V_m (mV)")
# plt.plot(data['times', forw_eul_dict[0][:990]], label="Forward Euler/rk4 on SpiNNaker2")
# plt.scatter(spikes["times"], [30] * len(spikes["times"]), color="orange", marker="|", label="Spikes")
# plt.ylabel("V_m (mV)")
# plt.legend()
#
# # Plot excitatory current
# plt.subplot(3, 1, 2)
# plt.plot(data["times"], data["I_syn_exc"], label="I_syn_exc (pA)", color="blue")
# plt.ylabel("I_syn_exc (pA)")
# plt.legend()
#
# # Plot inhibitory current
# plt.subplot(3, 1, 3)
# plt.plot(data["times"], data["I_syn_inh"], label="I_syn_inh (pA)", color="orange")
# plt.xlabel("Time (ms)")
# plt.ylabel("I_syn_inh (pA)")
# plt.legend()
#
# plt.tight_layout()
# plt.savefig('plot')
print('pause')