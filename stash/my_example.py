# import spynnaker and plotting stuff
import pyNN.spiNNaker as p
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt

# import models

from python_models8.neuron.builds.my_full_neuron import MyFullNeuron
from python_models8.neuron.builds.iaf_psc_exp_nestml import iaf_psc_exp_nestml


# iaf_psc_exp default values
r = 0
E_L = -0.07
V_m = E_L
I_kernel_exc__X__exc_spikes = 0
I_kernel_inh__X__inh_spikes = 0
C_m = 0.00000025
tau_m = 0.01
tau_syn_inh = 0.002
tau_syn_exc = 0.002
t_ref = 0.002

V_reset = -0.07
V_th = -0.055
I_e = 0
exc_spikes = 0
inh_spikes = 0

# Set the run time of the execution
run_time = 1000

# Set the time step of the simulation in milliseconds
time_step = 1.0

# Set the number of neurons to simulate
n_neurons = 1

# Set the i_offset current
i_offset = 0.0

# Set the weight of input spikes
weight = 2.0

# Set the times at which to input a spike
spike_times = range(0, run_time, 100)

p.setup(time_step)

spikeArray = {"spike_times": spike_times}
input_pop = p.Population(
    n_neurons, p.SpikeSourceArray(**spikeArray), label="input")

my_full_neuron_pop = p.Population(
    n_neurons, MyFullNeuron(), label="my_full_neuron_pop")
p.Projection(
    input_pop, my_full_neuron_pop,
    p.OneToOneConnector(), receptor_type='excitatory',
    synapse_type=p.StaticSynapse(weight=weight))

iaf_psc_exp_pop = p.Population(
    n_neurons, iaf_psc_exp_nestml(r, V_m, I_kernel_exc__X__exc_spikes, I_kernel_inh__X__inh_spikes, C_m, tau_m, tau_syn_inh, tau_syn_exc, t_ref, E_L, V_reset, V_th, I_e, exc_spikes, inh_spikes), label="my_full_neuron_pop")
p.Projection(
    input_pop, iaf_psc_exp_pop,
    p.OneToOneConnector(), receptor_type='exc_spikes',
    synapse_type=p.StaticSynapse(weight=weight))

my_full_neuron_pop.record(['v'])
iaf_psc_exp_pop.record(['V_m'])

p.run(run_time)

# get v for each example
v_my_full_neuron_pop = my_full_neuron_pop.get_data('v')
v_iaf_psc_exp_pop = iaf_psc_exp_pop.get_data('v')

Figure(
    # pylint: disable=no-member
    # membrane potentials for each example
    Panel(v_my_full_neuron_pop.segments[0].filter(name='v')[0],
          xlabel="Time (ms)",
          ylabel="Membrane potential (mV)",
          data_labels=[my_full_neuron_pop.label],
          yticks=True, xlim=(0, run_time), xticks=True),

    Panel(iaf_psc_exp_pop.segments[0].filter(name='v')[0],
          xlabel="Time (ms)",
          ylabel="Membrane potential (mV)",
          data_labels=[iaf_psc_exp_pop.label],
          yticks=True, xlim=(0, run_time), xticks=True),

    title="Simple my model examples",
    annotations="Simulated with {}".format(p.name())
)
plt.show()

p.end()
