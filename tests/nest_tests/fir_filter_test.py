# -*- coding: utf-8 -*-
#
# fir_filter_test.py
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

import os

import numpy as np

try:
    import matplotlib
    import matplotlib.pyplot as plt

    TEST_PLOTS = True
except BaseException:
    TEST_PLOTS = False

import nest
import scipy
import scipy.signal
import scipy.stats

from pynestml.frontend.pynestml_frontend import to_nest, install_nest


def generate_filter_coefficients(order: int):
    """
    Generate the filter coefficients for the given order
    :param order: order of the filter
    :return: a list with the coefficients for the filter
    """
    Ts = 1E-4
    f_sampling = 1 / Ts
    f_cutoff = 50.  # [Hz]
    f_nyquist = f_sampling // 2
    cutoff = f_cutoff / f_nyquist

    return scipy.signal.firwin(order, cutoff, pass_zero=True)


def plot_nestml(spike_times, times, y):
    """
    Generate the filtered output plot computed via NESTML
    :param spike_times: times when spikes occur
    :param times: total simualtion time
    :param y: output of the filter for the simulation time
    """
    plt.figure()
    plt.scatter(spike_times, np.zeros_like(spike_times), label='input', marker="d", color="orange")
    plt.plot(times, y, label='filter')
    plt.xlabel("Time (ms)")
    plt.ylabel("Filter output")
    plt.legend()
    plt.title('FIR Filter (NESTML)')
    plt.savefig("/tmp/fir_filter_output_nestml.png")


def plot_scipy(spike_times, num, stop):
    """
    Generate the filtered output plot computed via scipy
    :param spike_times: times when spikes occur
    :param num:
    :param stop:
    :return:
    """
    spikes, bin_edges = np.histogram(spike_times, bins=np.linspace(0, num, stop))  # to create binned spikes
    plt.figure()
    output = scipy.signal.lfilter(h, 1, spikes)
    plt.scatter(spike_times, np.zeros_like(spike_times), label='input', marker="d", color="orange")
    plt.plot(bin_edges[1:], output, label="filter")
    plt.xlabel("Time (ms)")
    plt.ylabel("Filter output")
    plt.legend()
    plt.title('FIR filter (scipy)')
    plt.savefig('/tmp/fir_filter_output_scipy.png')


nestml_model_file = 'FIR_filter.nestml'
nestml_model_name = 'fir_filter_nestml'
target_path = '/tmp/fir-filter'
logging_level = 'INFO'
module_name = 'nestmlmodule'
store_log = False
suffix = '_nestml'
dev = True

# Generate the NEST code
input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'resources', nestml_model_file)))
nest_path = nest.ll_api.sli_func("statusdict/prefix ::")
to_nest(input_path, target_path, logging_level, module_name, store_log, suffix, dev)
install_nest(target_path, nest_path)

t_sim = 101.

nest.set_verbosity("M_ALL")
nest.Install(module_name)

nest.ResetKernel()

# Create a fir_filter node
neuron = nest.Create(nestml_model_name)

# Create a spike generator
spikes = [1.5, 1.5, 1.5, 6.7, 10., 10.1, 10.1, 11.3, 11.3, 20., 22.5, 30., 40., 42., 42., 42., 50.5, 50.5, 75., 88.,
          93., 93., 98.9, 98.9]
sg = nest.Create("spike_generator", params={"spike_times": spikes})
nest.Connect(sg, neuron)

# Get N (order of the filter)
n = nest.GetStatus(neuron, "N")[0]
print("N: {}".format(n))

# Set filter coefficients
h = generate_filter_coefficients(n)
nest.SetStatus(neuron, {"h": h})
print("h: ", h)

# Multimeter
multimeter = nest.Create('multimeter')
nest.SetStatus(multimeter, {'interval': 0.1})
multimeter.set({"record_from": ["y"]})  # output of the filter
nest.Connect(multimeter, neuron)

# Spike recorder
sr = nest.Create("spike_recorder")
nest.Connect(sg, sr)
nest.Connect(neuron, sr)

# Simulate
nest.Simulate(t_sim)

# Record from multimeter
events = multimeter.get("events")
y = events["y"]
times = events["times"]
spike_times = nest.GetStatus(sr, keys='events')[0]['times']

# Plots
if TEST_PLOTS:
    plot_nestml(spike_times, times, y)
    plot_scipy(spike_times, t_sim - 1, len(y))
