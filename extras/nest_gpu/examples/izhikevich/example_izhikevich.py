import sys
import nestgpu as ngpu
import numpy as np

neuron = ngpu.Create('izhikevich_neuron_nestml', 1)
# ngpu.SetStatus(neuron, {"V_m_init": -70.0, "V_m": -70.0})
# vm_init = ngpu.GetStatus(neuron, "V_m")
# print(f"V_m: {vm_init}")
spike = ngpu.Create("spike_generator")
spike_times = [10.0, 40.0]
n_spikes = 2

# set spike times and height
ngpu.SetStatus(spike, {"spike_times": spike_times})
delay = [1.0, 10.0]
weight = [1.0, -2.0]

conn_spec={"rule": "all_to_all"}


syn_spec_ex={'weight': weight[0], 'delay': delay[0]}
syn_spec_in={'weight': weight[1], 'delay': delay[1]}
ngpu.Connect(spike, neuron, conn_spec, syn_spec_ex)
ngpu.Connect(spike, neuron, conn_spec, syn_spec_in)

record = ngpu.CreateRecord("", ["V_m"], [neuron[0]], [0])

ngpu.Simulate(80.0)

data_list = ngpu.GetRecordData(record)
t=[row[0] for row in data_list]
V_m=[row[1] for row in data_list]
np.savetxt("izh_data.out", data_list, delimiter="\t")

data = np.loadtxt('test_izh_nest.txt', delimiter="\t")
t1=[x[0] for x in data ]
V_m1=[x[1] for x in data ]

import matplotlib.pyplot as plt

fig1 = plt.figure(1)
plt.plot(t, V_m, "r-", label="NEST GPU")
plt.plot(t1, V_m1, "b--", label="NEST")
plt.legend()
plt.draw()
plt.savefig("izhikevich_plot.png")
plt.close()
