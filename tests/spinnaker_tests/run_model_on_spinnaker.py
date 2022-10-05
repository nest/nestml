# import spynnaker8 and plotting stuff
import spynnaker8 as p


import sys
print(sys.path)
#sys.path.append('/home/bbpnrsoa/sPyNNakerGit/sPyNNaker8NewModelTemplate')
sys.path.append('/home/bbpnrsoa/sPyNNakerGit/nestml-spinnaker-install')

from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt

import python_models8


# import models
#from python_models8.neuron.builds.my_full_neuron import MyFullNeuron
from python_models8.neuron.builds.iaf_psc_exp import iaf_psc_exp


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
    n_neurons, iaf_psc_exp(V_abs=0.,                 
                 I_kernel_inh__X__inh_spikes=0.,
                 I_kernel_exc__X__exc_spikes=0.,
                 C_m=250.,
                 tau_m=20.,
                 tau_syn_inh=2.,
                 tau_syn_exc=10.,
                 t_ref=2.,
                 E_L=0.,
                 V_reset=0.,
                 Theta=50.,
                 I_e=0.,
                 exc_spikes=0.,
                 inh_spikes=0.), label="my_full_neuron_pop")
    #n_neurons, MyFullNeuron(decay=.99999), label="my_full_neuron_pop")
p.Projection(
    input_pop, my_full_neuron_pop,
    p.OneToOneConnector(), receptor_type='excitatory',
    synapse_type=p.StaticSynapse(weight=weight))

my_full_neuron_pop.record(['v'])

p.run(run_time)

#print(stdp_connection.get('weight', 'list'))

# get v for each example
v_my_full_neuron_pop = my_full_neuron_pop.get_data('v')

%matplotlib inline

import numpy as np

y = np.array(v_my_full_neuron_pop.segments[0].filter(name='v')[0])[:, 0]
x = np.arange(len(y))

fix, ax = plt.subplots()
ax.semilogy(x, y)
ax.set_xlabel("Time (ms)")
ax.set_ylabel("Membrane potential (mV)")
#axdata_labels=[my_full_neuron_pop.label],
#          yticks=True, xlim=(0, run_time), xticks=True),
#    title="Simple my model examples",
#    annotations="Simulated with {}".format(p.name())
#)
plt.show()
