import nest
import matplotlib.pyplot as plt


# import nestml module

nest.Install('nestmlmodule')

# network construction

neuron = nest.Create("iaf_psc_exp_multisynapse_neuron_nestml")

sg = nest.Create("spike_generator", params={"spike_times": [20., 80.]})
nest.Connect(sg, neuron, syn_spec={"receptor_type" : 1, "weight": 1000., "delay": 0.1})

sg2 = nest.Create("spike_generator", params={"spike_times": [40., 60.]})
nest.Connect(sg2, neuron, syn_spec={"receptor_type" : 2, "weight": 1000., "delay": 0.1})

sg3 = nest.Create("spike_generator", params={"spike_times": [30., 70.]})
nest.Connect(sg3, neuron, syn_spec={"receptor_type" : 3, "weight": 500., "delay": 0.1})

i_1 = nest.Create('multimeter', params={'record_from': ['I_shape', 'I_shape2', 'I_shape3'], 'interval': 0.1})
nest.Connect(i_1, neuron)

vm_1 = nest.Create('voltmeter')
nest.Connect(vm_1, neuron)

# simulate

nest.Simulate(125.)

# analysis

vm_1 = nest.GetStatus(vm_1)[0]["events"]
i_1 = nest.GetStatus(i_1)[0]["events"]

fig, ax = plt.subplots(nrows=4)

ax[0].plot(vm_1["times"], vm_1["V_m"], label="V_m")
ax[0].set_ylabel("voltage")

ax[1].plot(i_1["times"], i_1["I_shape"], label="I_shape")
ax[1].set_ylabel("current")

ax[2].plot(i_1["times"], i_1["I_shape2"], label="I_shape2")
ax[2].set_ylabel("current")

ax[3].plot(i_1["times"], i_1["I_shape3"], label="I_shape3")
ax[3].set_ylabel("current")

for _ax in ax:
	#_ax.legend()
	_ax.legend(loc="upper right")
	_ax.set_xlim(0., 125.)
	_ax.grid(True)

for _ax in ax[:-1]:
	_ax.set_xticklabels([])

ax[-1].set_xlabel("time")

plt.show()
