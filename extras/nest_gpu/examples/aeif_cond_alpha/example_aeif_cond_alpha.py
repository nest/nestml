import os
import sys
import nestgpu as ngpu
import numpy as np
tolerance = 0.0001
neuron = ngpu.Create("aeif_cond_alpha_alt_neuron_nestml", 1)
ngpu.SetStatus(neuron, {"V_peak": 0.0, "a": 4.0, "b":80.5, "E_L":-70.6,
                        "g_L":300.0, 'E_exc':20.0, 'E_inh': -85.0,
                        'tau_syn_exc':40.0, 'tau_syn_inh': 20.0})

spike = ngpu.Create("spike_generator")
spike_times = [10.0, 400.0]
n_spikes = 2

# set spike times and heights
ngpu.SetStatus(spike, {"spike_times": spike_times})
delay = [1.0, 100.0]
weight = [0.1, 0.2]

conn_spec={"rule": "all_to_all"}
syn_spec_ex={'receptor':0, 'weight': weight[0], 'delay': delay[0]}
syn_spec_in={'receptor':1, 'weight': weight[1], 'delay': delay[1]}
ngpu.Connect(spike, neuron, conn_spec, syn_spec_ex)
ngpu.Connect(spike, neuron, conn_spec, syn_spec_in)

record = ngpu.CreateRecord("", ["V_m"], [neuron[0]], [0])

ngpu.Simulate(800.0)

data_list = ngpu.GetRecordData(record)
t=[row[0] for row in data_list]
V_m=[row[1] for row in data_list]

nest_data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_aeif_cond_alpha_nest.txt")
data = np.loadtxt(nest_data_file, delimiter="\t")
t1=[x[0] for x in data ]
V_m1=[x[1] for x in data ]
print (len(t))
print (len(t1))

dV=[V_m[i*10+20]-V_m1[i] for i in range(len(t1))]
#print(dV)
rmse =np.std(dV)/abs(np.mean(V_m))
print("rmse : ", rmse, " tolerance: ", tolerance)
#if rmse>tolerance:
#    sys.exit(1)
#sys.exit(0)

import matplotlib.pyplot as plt

fig1 = plt.figure(1)
plt.plot(t, V_m, "r-", label="NEST GPU")
plt.plot(t1, V_m1, "b--", label="NEST")
plt.legend()
plt.draw()
plt.savefig("aeif_cond_alpha_plot.png")
plt.close()
