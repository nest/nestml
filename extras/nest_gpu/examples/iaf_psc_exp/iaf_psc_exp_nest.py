import nest
import numpy as np
import matplotlib.pyplot as plt

neuron = nest.Create("iaf_psc_exp")
sg = nest.Create("spike_generator")
spike_times = [10.0, 15., 23., 25., 36., 55., 62., 100., 125., 222., 333., 400.0, 550., 700.]
nest.SetStatus(sg, {"spike_times": spike_times})

conn_spec = {"rule": "all_to_all"}
syn_spec_exc = {'receptor_type': 0, 'weight': 200.0, 'delay': 1.0}
syn_spec_in = {'receptor_type': 0, 'weight': -1.0, 'delay': 100.0}

nest.Connect(sg, neuron, conn_spec, syn_spec_exc)
nest.Connect(sg, neuron, conn_spec, syn_spec_in)

mm = nest.Create("multimeter", {"record_from": ["V_m"]})
nest.Connect(mm, neuron)

nest.Simulate(800.)

times = mm.get("events")["times"]
v_m = mm.get("events")["V_m"]

# Save to file
full_arr = np.stack([times, v_m], axis=1)
np.savetxt("nest_data.txt", full_arr, delimiter='\t')

# Plot
plt.plot(times, v_m)
plt.xlabel("Time [ms]")
plt.ylabel("V_m")
plt.show()
