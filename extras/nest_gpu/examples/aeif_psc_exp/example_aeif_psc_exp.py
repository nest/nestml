import sys
import nestgpu as ngpu
import numpy as np
tolerance = 5e-6
neuron = ngpu.Create('aeif_psc_exp_neuron_nestml', 1)
ngpu.SetStatus(neuron, {"V_peak": 0.0, "a": 4.0, "b":80.5,
                        "E_L":-70.6,
                        "g_L":300.0, 
                        "tau_exc": 40.0,
                        "tau_inh": 20.0})
spike = ngpu.Create("spike_generator")
spike_times = [10.0, 400.0]
n_spikes = 2

# set spike times and height
ngpu.SetStatus(spike, {"spike_times": spike_times})
delay = [1.0, 100.0]
weight = [1.0, 2.0]

conn_spec={"rule": "all_to_all"}


syn_spec_ex={'receptor':0, 'weight': weight[0], 'delay': delay[0]}
syn_spec_in={'receptor':1, 'weight': weight[1], 'delay': delay[1]}
ngpu.Connect(spike, neuron, conn_spec, syn_spec_ex)
ngpu.Connect(spike, neuron, conn_spec, syn_spec_in)

record = ngpu.CreateRecord("", ["V_m"], [neuron[0]], [0])
ngpu.Simulate(800.0)
# ngpu.Simulate(15.0)

data_list = ngpu.GetRecordData(record)
t=[row[0] for row in data_list]
V_m=[row[1] for row in data_list]

data = np.loadtxt('test_aeif_psc_exp_nest.txt', delimiter="\t")
t1=[x[0] for x in data ]
V_m1=[x[1] for x in data ]
print (len(t))
print (len(t1))

dV=[V_m[i*10+20]-V_m1[i] for i in range(len(t1))]
rmse =np.std(dV)/abs(np.mean(V_m))
print("rmse : ", rmse, " tolerance: ", tolerance)
if rmse>tolerance:
    sys.exit(1)

import matplotlib.pyplot as plt

fig1 = plt.figure(1)
plt.plot(t, V_m, "r-", label="NEST GPU")
plt.plot(t1, V_m1, "b--", label="NEST")
plt.legend()
plt.draw()
plt.savefig("aeif_psc_exp_plot.png")
plt.close()

sys.exit(0)
