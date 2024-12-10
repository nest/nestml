import nestgpu as ngpu
import numpy as np

neuron = ngpu.Create("iaf_psc_exp_nestml")
sg = ngpu.Create("spike_generator")
spike_times = [10.0, 15., 23., 25., 36., 55., 62., 100., 125., 222., 333., 400.0, 550., 700.]
ngpu.SetStatus(sg, {"spike_times": spike_times})

conn_spec={"rule": "all_to_all"}
syn_spec_exc={'receptor':0, 'weight': 200.0, 'delay': 1.0}
syn_spec_in={'receptor':1, 'weight': -1.0, 'delay': 100.0}

ngpu.Connect(sg, neuron, conn_spec, syn_spec_exc)
ngpu.Connect(sg, neuron, conn_spec, syn_spec_in)

record = ngpu.CreateRecord("", ["V_m"], [neuron[0]], [0])

ngpu.Simulate(800.0)

data_list = ngpu.GetRecordData(record)
t=[row[0] for row in data_list]
V_m=[row[1] for row in data_list]

np.savetxt("test.out", data_list, delimiter="\t")
data = np.loadtxt('nest_data.txt', delimiter="\t")
t1=[x[0] for x in data ]
V_m1=[x[1] for x in data ]

import matplotlib.pyplot as plt

fig1 = plt.figure(1)
plt.plot(t, V_m, "r-", label="NEST GPU")
plt.plot(t1, V_m1, "b--", label="NEST")
plt.legend()
plt.draw()
#plt.pause(1)
#ngpu.waitenter("<Hit Enter To Close>")
plt.savefig("plot.png")
plt.close()

