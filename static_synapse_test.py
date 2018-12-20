# -*- coding: utf-8 -*-
#
# test_stdp_multiplicity.py
#
# This file is part of NEST.
#
# Copyright (C) 2004 The NEST Initiative
#
# NEST is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# NEST is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NEST.  If not, see <http://www.gnu.org/licenses/>.

# This script tests the parrot_neuron in NEST.

import nest
import unittest
import math
import numpy as np
import matplotlib.pyplot as plt


#import os
#os.environ["NEST_PATH"] = "/home/archels/julich/nest-simulator-build"
#os.environ["LD_LIBRARY_PATH"] = "/home/archels/julich/nest-simulator-build/lib:/home/archels/julich/nest-simulator-build/lib/python3.6/site-packages/nest:/tmp/nestml-target"
#os.environ["SLI_PATH"] = "/tmp/nestml-target/sli"

from pynestml.frontend.pynestml_frontend import to_nest, install_nest

#to_nest(input_path="/home/archels/julich/nestml-fork/nestml/models/aeif_cond_alpha.nestml", target_path="/tmp/nestml-target", suffix="_nestml", logging_level="INFO")
to_nest(input_path="/home/archels/nestml/models/static_synapse.nestml", target_path="/tmp/nestml-target", suffix="_nestml", logging_level="INFO")
#to_nest(input_path="/home/archels/julich/nestml-fork/nestml/models/ht_neuron.nestml", target_path="/tmp/nestml-target", suffix="_nestml")
#to_nest(input_path="/home/archels/julich/nestml-fork/nestml/models", target_path="/tmp/nestml-target", suffix="_nestml")

install_nest(models_path="/tmp/nestml-target", nest_path="/home/archels/nest-simulator-build")

nest.set_verbosity("M_ALL")
#nest.set_debug(True)

nest.Install("nestmlmodule")

#nest.Simulate(1.)





import time
import os
import psutil
import inspect
def get_process_memory():
    process = psutil.Process(os.getpid())
    mi = process.memory_info()
    return mi.rss, mi.vms, mi.shared


def format_bytes(bytes):
    if abs(bytes) < 1000:
        return str(bytes)+"B"
    elif abs(bytes) < 1e6:
        return str(round(bytes/1e3,2)) + "kB"
    elif abs(bytes) < 1e9:
        return str(round(bytes / 1e6, 2)) + "MB"
    else:
        return str(round(bytes / 1e9, 2)) + "GB"

rss_before, vms_before, shared_before = get_process_memory()


resolution = .1	 # [ms]
delay = 1.  # [ms]

N = 2000

pre_spike_times = [2., 5., 7., 8., 10., 11., 15., 17., 20., 21., 22., 23., 26., 28.]	  # [ms]
# pre_spike_times = 1 + np.round(100 * np.sort(np.abs(np.random.randn(100))))	  # [ms]
# post_spike_times =  np.sort(np.unique(1 + np.round(100 * np.sort(np.abs(np.random.randn(100))))))	 # [ms]

print("Pre spike times: " + str(pre_spike_times))

nest.set_verbosity("M_WARNING")

post_weights = {'parrot': []}

nest.ResetKernel()
nest.SetKernelStatus({'resolution': resolution})

wr = nest.Create('weight_recorder')
nest.CopyModel("static_connection_nestml", "static_connection_nestml_rec",
			   {"weight_recorder": wr[0], "weight": 1., "delay" : 2.})

# create spike_generators with these times
pre_sg = nest.Create("spike_generator", N, 
					 params={"spike_times": pre_spike_times,
							 'allow_offgrid_spikes': True})

# create parrot neurons and connect spike_generators
pre_parrot = nest.Create("parrot_neuron", N)
post = nest.Create("iaf_psc_delta", N)
mm = nest.Create("multimeter", params={"record_from" : ["V_m"], 'interval' : .1, 'withtime': True })
spikedet = nest.Create("spike_detector", params={'precise_times': True})

nest.Connect(pre_sg, pre_parrot, "one_to_one",
			 syn_spec={"delay": delay})
nest.Connect(pre_parrot, post, "all_to_all",
	syn_spec={'model': 'static_connection_nestml_rec'})
nest.Connect(mm, post)

nest.Connect(
	pre_parrot + post,
	spikedet
)

# get STDP synapse and weight before protocol
#syn = nest.GetConnections(source=pre_parrot,
#						  synapse_model="static_connection_nestml_rec")
#w_pre = nest.GetStatus(syn)[0]['weight']

sim_time = np.amax(pre_spike_times) + 5 * delay
n_steps = int(np.ceil(sim_time / resolution)) + 1
nest.Simulate(sim_time)

rss_after, vms_after, shared_after = get_process_memory()
print("Profiling: RSS: {:>8} | VMS: {:>8} | SHR {:>8} "
    .format(format_bytes(rss_after - rss_before),
            format_bytes(vms_after - vms_before),
            format_bytes(shared_after - shared_before)))



"""

homogeneous weights: Profiling: RSS:   8.72GB | VMS:   9.12GB | SHR 380.93kB 
                     Profiling: RSS:   8.71GB | VMS:   9.12GB | SHR 131.07kB 

hetero weights: Profiling: RSS:   8.75GB | VMS:   9.15GB | SHR 233.47kB 


"""


import pdb;pdb.set_trace()






fig, ax = plt.subplots(nrows=3)
ax1, ax3, ax2 = ax

n_spikes = len(pre_spike_times)
for i in range(n_spikes):
	ax1.plot(2 * [pre_spike_times[i] + delay], [0, 1], linewidth=2, color="blue", alpha=.4)

post_spike_times = nest.GetStatus(spikedet, "events")[0]["times"]
n_spikes = len(post_spike_times)
for i in range(n_spikes):
		ax3.plot(2 * [post_spike_times[i]], [0, 1], linewidth=2, color="red", alpha=.4)

ax2.plot(nest.GetStatus(mm)[0]['events']['times'], nest.GetStatus(mm)[0]['events']['V_m'])
ax2.set_xlabel("Time [ms]")
ax1.set_ylabel("Pre spikes")
ax3.set_ylabel("Post spikes")
ax2.set_ylabel("Trace")
ax2.legend()
for _ax in ax:
	_ax.grid(which="major", axis="both")
	_ax.grid(which="minor", axis="x", linestyle=":", alpha=.4)
	_ax.minorticks_on()
	_ax.set_xlim(0., sim_time)
fig.savefig("/tmp/static_synapse_test.png")



