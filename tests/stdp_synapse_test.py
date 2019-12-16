# -*- coding: utf-8 -*-
#
# stdp_synapse_test.py
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


import time
import os
import psutil
import inspect
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

#to_nest(input_path="/home/archels/nestml-synapses/models/stdp_synapse.nestml", target_path="/tmp/nestml-target", suffix="_nestml", logging_level="INFO")
#install_nest(models_path="/tmp/nestml-target", nest_path="/home/archels/nest-simulator-build")

nest.set_verbosity("M_ALL")
#nest.set_debug(True)

nest.Install("nestmlmodule")

#nest.Simulate(1.)




resolution = 1.	 # [ms]
delay = 1.  # [ms]

pre_spike_times = [2., 5., 7., 8., 10., 11., 15., 17., 20., 21., 22., 23., 26., 28.]	  # [ms]
# pre_spike_times = 1 + np.round(100 * np.sort(np.abs(np.random.randn(100))))	  # [ms]
post_spike_times =  np.sort(np.unique(1 + np.round(10 * np.sort(np.abs(np.random.randn(10))))))	 # [ms]

print("Pre spike times: " + str(pre_spike_times))
print("Post spike times: " + str(post_spike_times))

nest.set_verbosity("M_WARNING")

post_weights = {'parrot': []}

nest.ResetKernel()
nest.SetKernelStatus({'resolution': resolution})

wr = nest.Create('weight_recorder')
wr_ref = nest.Create('weight_recorder')
nest.CopyModel("stdp_connection_nestml", "stdp_connection_nestml_rec",
			   {"weight_recorder": wr[0], "w": 1.9876, "the_delay" : 1.})
nest.CopyModel("stdp_synapse", "stdp_connection_ref_rec",
			   {"weight_recorder": wr[0]})

# create spike_generators with these times
pre_sg = nest.Create("spike_generator", 
					 params={"spike_times": pre_spike_times,
							 'allow_offgrid_spikes': True})
post_sg = nest.Create("spike_generator", 
					 params={"spike_times": post_spike_times,
							 'allow_offgrid_spikes': True})

# create parrot neurons and connect spike_generators
pre_parrot = nest.Create("parrot_neuron")
post_parrot = nest.Create("parrot_neuron")
pre_parrot_ref = nest.Create("parrot_neuron")
post_parrot_ref = nest.Create("parrot_neuron")
#mm = nest.Create("multimeter", params={"record_from" : ["V_m"], 'interval' : .1, 'withtime': True })
spikedet_pre = nest.Create("spike_detector", params={'precise_times': True})
spikedet_post = nest.Create("spike_detector", params={'precise_times': True})

nest.Connect(pre_sg, pre_parrot, "one_to_one", syn_spec={"delay": 1.})
nest.Connect(post_sg, post_parrot, "one_to_one", syn_spec={"delay": 1.})
nest.Connect(pre_sg, pre_parrot_ref, "one_to_one", syn_spec={"delay": 1.})
nest.Connect(post_sg, post_parrot_ref, "one_to_one", syn_spec={"delay": 1.})
nest.Connect(pre_parrot, post_parrot, "all_to_all", syn_spec={'model': 'stdp_connection_nestml_rec'})
nest.Connect(pre_parrot_ref, post_parrot_ref, "all_to_all", syn_spec={'model': 'stdp_connection_ref_rec'})

nest.Connect(pre_parrot, spikedet_pre)
nest.Connect(post_parrot, spikedet_post)

# get STDP synapse and weight before protocol
syn = nest.GetConnections(source=pre_parrot, synapse_model="stdp_connection_nestml_rec")
syn_ref = nest.GetConnections(source=pre_parrot_ref, synapse_model="stdp_connection_ref_rec")

sim_time = np.amax(pre_spike_times) + 5 * delay
n_steps = int(np.ceil(sim_time / resolution)) + 1
t = 0.
t_hist = []
w_hist = []
w_hist_ref = []
while t <= sim_time:
    nest.Simulate(resolution)
    t += resolution
    t_hist.append(t)
    w_hist_ref.append(nest.GetStatus(syn_ref)[0]['weight'])
    w_hist.append(nest.GetStatus(syn)[0]['w'])

#nest.Simulate(sim_time)
#wr_weights = nest.GetStatus(wr, "events")[0]["weights"]

fig, ax = plt.subplots(nrows=3)
ax1, ax3, ax2 = ax

pre_spike_times_ = nest.GetStatus(spikedet_pre, "events")[0]["times"]
n_spikes = len(pre_spike_times_)
for i in range(n_spikes):
	ax1.plot(2 * [pre_spike_times_[i] + delay], [0, 1], linewidth=2, color="blue", alpha=.4)

post_spike_times_ = nest.GetStatus(spikedet_post, "events")[0]["times"]
n_spikes = len(post_spike_times_)
for i in range(n_spikes):
	ax3.plot(2 * [post_spike_times_[i]], [0, 1], linewidth=2, color="red", alpha=.4)

ax2.plot(t_hist, w_hist, marker="o", label="nestml")
ax2.plot(t_hist, w_hist_ref, linestyle="--", marker="x", label="ref")
#ax2.plot(wr_weights)

ax2.set_xlabel("Time [ms]")
ax1.set_ylabel("Pre spikes")
ax3.set_ylabel("Post spikes")
ax2.set_ylabel("w")
ax2.legend()
for _ax in ax:
	_ax.grid(which="major", axis="both")
	_ax.grid(which="minor", axis="x", linestyle=":", alpha=.4)
	_ax.minorticks_on()
	_ax.set_xlim(0., sim_time)
fig.savefig("/tmp/stdp_synapse_test.png")



