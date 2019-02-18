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

nest.set_verbosity("M_ALL")

import time
import os
import psutil
import inspect
import unittest
import math
import numpy as np
import matplotlib.pyplot as plt
import tempfile

from pynestml.frontend.pynestml_frontend import to_nest, install_nest


#import os
#os.environ["NEST_PATH"] = "/home/archels/julich/nest-simulator-build"
#os.environ["SLI_PATH"] = "/tmp/nestml-target/sli"

nestml_model_path = "/home/archels/julich/nestml-fork/nestml/models/static_synapse.nestml"
nestml_target_directory = tempfile.mkdtemp(prefix="nestml-target-")
nest_path = "/home/archels/julich/nest-simulator-build"

os.environ["LD_LIBRARY_PATH"] += ":" + nestml_target_directory   #"/home/archels/julich/nest-simulator-build/lib:/home/archels/julich/nest-simulator-build/lib/python3.6/site-packages/nest:/tmp/nestml-target"

to_nest(input_path=nestml_model_path, target_path=nestml_target_directory, suffix="_nestml", logging_level="INFO")

import pdb;pdb.set_trace()

old_cwd = os.getcwd()
os.chdir(os.path.join(nestml_target_directory, "sli"))		# allow NEST to find the nestmlmodule-init.sli file

install_nest(models_path=nestml_target_directory, nest_path=nest_path)
nest.Install("nestmlmodule")

import pdb;pdb.set_trace()


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


resolution = .1	 # [ms]
delay = 1.  # [ms]

N = 1

pre_spike_times = [1., 11., 21.]	  # [ms]
weight = .5


#
#	memory profiling: before
#

#rss_before, vms_before, shared_before = get_process_memory()


#
#	set up
#

nest.ResetKernel()
nest.SetKernelStatus({'resolution': resolution})
wr = nest.Create('weight_recorder')
nest.CopyModel("static_connection_nestml", "static_connection_nestml_rec",
		   {"weight_recorder": wr[0], "weight": weight, "delay" : delay})
pre_sg = nest.Create("spike_generator", N,
				 params={"spike_times": pre_spike_times,
						 'allow_offgrid_spikes': True})
pre_parrot = nest.Create("parrot_neuron", N)
post = nest.Create("iaf_psc_delta", N)
mm = nest.Create("multimeter", params={ "record_from" : ["V_m"], 'interval' : resolution})#, 'withtime': True })
nest.Connect(pre_sg, pre_parrot, "one_to_one", syn_spec={"delay": delay})
nest.Connect(pre_parrot, post, "all_to_all", syn_spec={'model': 'static_connection_nestml_rec'})
nest.Connect(mm, post)


#
#	run
#

sim_time = np.amax(pre_spike_times) + 10. * delay
n_steps = int(np.ceil(sim_time / resolution)) + 1
nest.Simulate(sim_time)


#
#	memory profiling: after
#

"""rss_after, vms_after, shared_after = get_process_memory()
print("Profiling: RSS: {:>8} | VMS: {:>8} | SHR {:>8} ".format(format_bytes(rss_after - rss_before),
           format_bytes(vms_after - vms_before),
           format_bytes(shared_after - shared_before)))"""


#
#	analysis/plotting
#

fig, ax = plt.subplots(nrows=2)
ax1, ax2 = ax

n_spikes = len(pre_spike_times)
for i in range(n_spikes):
	ax1.plot(2 * [pre_spike_times[i]], [0, 1], linewidth=2, color="blue", alpha=.4)
ax1.set_ylabel("Pre spikes")

ax2.plot(nest.GetStatus(mm)[0]['events']['times'], nest.GetStatus(mm)[0]['events']['V_m'])
ax2.set_xlabel("Time [ms]")
ax2.set_ylabel("Post $V_m$")
ax2.legend()

for _ax in ax:
	_ax.grid(which="major", axis="both")
	_ax.grid(which="minor", axis="x", linestyle=":", alpha=.4)
	_ax.minorticks_on()
	_ax.set_xlim(0., sim_time)

fig.savefig("/tmp/static_synapse_test.png")



