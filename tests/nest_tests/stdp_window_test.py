# -*- coding: utf-8 -*-
#
# stdp_window_test.py
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

import numpy as np
import os
import pytest

import nest

from pynestml.codegeneration.nest_tools import NESTTools
from pynestml.frontend.pynestml_frontend import generate_nest_target

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.ticker
    import matplotlib.pyplot as plt
    TEST_PLOTS = True
except Exception:
    TEST_PLOTS = False


@pytest.fixture(autouse=True,
                scope="module")
def nestml_generate_target():
    r"""Generate the neuron model code"""

    # generate the "jit" model (co-generated neuron and synapse), that does not rely on ArchivingNode
    files = [os.path.join("models", "neurons", "iaf_psc_delta_neuron.nestml"),
             os.path.join("models", "neurons", "izhikevich_neuron.nestml"),
             os.path.join("models", "synapses", "stdp_synapse.nestml")]
    input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
        os.pardir, os.pardir, s))) for s in files]
    generate_nest_target(input_path=input_path,
                         logging_level="INFO",
                         suffix="_nestml",
                         codegen_opts={"neuron_synapse_pairs": [{"neuron": "iaf_psc_delta_neuron",
                                                                 "synapse": "stdp_synapse",
                                                                 "post_ports": ["post_spikes"]},
                                                                {"neuron": "izhikevich_neuron",
                                                                 "synapse": "stdp_synapse",
                                                                 "post_ports": ["post_spikes"]}],
                                       "delay_variable": {"stdp_synapse": "d"},
                                       "weight_variable": {"stdp_synapse": "w"}})


def run_stdp_network(pre_spike_time, post_spike_time,
                     neuron_model_name,
                     synapse_model_name,
                     resolution=1.,  # [ms]
                     delay=1.,  # [ms]
                     sim_time=None,  # if None, computed from pre and post spike times
                     custom_synapse_properties=None):

    print("Pre spike time: " + str(pre_spike_time))
    print("Post spike time: " + str(post_spike_time))

    nest.set_verbosity("M_ALL")

    nest.ResetKernel()
    nest.SetKernelStatus({"resolution": resolution})

    try:
        nest.Install("nestmlmodule")
    except Exception:
        # ResetKernel() does not unload modules for NEST Simulator < v3.7; ignore exception if module is already loaded on earlier versions
        pass

    wr = nest.Create("weight_recorder")
    if "__with" in synapse_model_name:
        weight_variable_name = "w"
    else:
        weight_variable_name = "weight"

    nest.CopyModel(synapse_model_name, "stdp_nestml_rec",
                   {"weight_recorder": wr[0], weight_variable_name: 1., "delay": delay, "receptor_type": 0, "mu_minus": 0., "mu_plus": 0.})

    # create spike_generators with these times
    pre_sg = nest.Create("spike_generator",
                         params={"spike_times": [pre_spike_time, sim_time - 10.]})
    post_sg = nest.Create("spike_generator",
                          params={"spike_times": [post_spike_time],
                                  "allow_offgrid_times": True})

    # create parrot neurons and connect spike_generators
    pre_neuron = nest.Create("parrot_neuron")
    post_neuron = nest.Create(neuron_model_name)

    if NESTTools.detect_nest_version().startswith("v2"):
        spikedet_pre = nest.Create("spike_detector")
        spikedet_post = nest.Create("spike_detector")
    else:
        spikedet_pre = nest.Create("spike_recorder")
        spikedet_post = nest.Create("spike_recorder")

    nest.Connect(pre_sg, pre_neuron, "one_to_one", syn_spec={"delay": 1.})
    nest.Connect(post_sg, post_neuron, "one_to_one", syn_spec={"delay": 1., "weight": 9999.})
    if NESTTools.detect_nest_version().startswith("v2"):
        nest.Connect(pre_neuron, post_neuron, "all_to_all", syn_spec={"model": "stdp_nestml_rec"})
    else:
        nest.Connect(pre_neuron, post_neuron, "all_to_all", syn_spec={"synapse_model": "stdp_nestml_rec"})

    nest.Connect(pre_neuron, spikedet_pre)
    nest.Connect(post_neuron, spikedet_post)

    # get STDP synapse and weight before protocol
    if custom_synapse_properties:
        syn = nest.GetConnections(source=pre_neuron, synapse_model="stdp_nestml_rec")
        nest.SetStatus(syn, custom_synapse_properties)

    initial_weight = nest.GetStatus(syn)[0][weight_variable_name]
    np.testing.assert_allclose(initial_weight, 1)
    nest.Simulate(sim_time)
    updated_weight = nest.GetStatus(syn)[0][weight_variable_name]

    actual_t_pre_sp = nest.GetStatus(spikedet_pre)[0]["events"]["times"][0]
    actual_t_post_sp = nest.GetStatus(spikedet_post)[0]["events"]["times"][0]

    dt = actual_t_post_sp - actual_t_pre_sp
    dw = updated_weight - initial_weight
    print("Returning " + str((dt, dw)))

    return dt, dw


@pytest.mark.parametrize("neuron_model_name,synapse_model_name", [("iaf_psc_delta_neuron_nestml__with_stdp_synapse_nestml", "stdp_synapse_nestml__with_iaf_psc_delta_neuron_nestml"),
                                                                  ("izhikevich_neuron_nestml__with_stdp_synapse_nestml", "stdp_synapse_nestml__with_izhikevich_neuron_nestml")])
def test_nest_stdp_synapse(neuron_model_name: str, synapse_model_name: str, fname_snip: str = ""):
    fname_snip += "_[neuron=" + neuron_model_name + "]"
    fname_snip += "_[synapse=" + synapse_model_name + "]"

    sim_time = 1000.  # [ms]
    pre_spike_time = 100.  # sim_time / 2  # [ms]
    delay = 10.   # [ms]

    # plot
    if TEST_PLOTS:
        fig, ax = plt.subplots()

    dt_vec = []
    dw_vec = []
    for post_spike_time in np.linspace(25, 175, 31) - delay:
        dt, dw = run_stdp_network(pre_spike_time, post_spike_time,
                                  neuron_model_name,
                                  synapse_model_name,
                                  resolution=1.,  # [ms]
                                  delay=delay,  # [ms]
                                  sim_time=sim_time,  # if None, computed from pre and post spike times
                                  custom_synapse_properties={"lambda": 1E-6, "alpha": 1.})

        dt_vec.append(dt)
        dw_vec.append(dw)

    # plot
    if TEST_PLOTS:
        ax.scatter(dt_vec, dw_vec)
        ax.set_xlabel(r"t_post - t_pre")
        ax.set_ylabel(r"$\Delta w$")

        for _ax in [ax]:
            _ax.grid(which="major", axis="both")
            _ax.grid(which="minor", axis="x", linestyle=":", alpha=.4)

        fig.suptitle("Neuron model: " + str(neuron_model_name.split("__with_")[0]))
        fig.savefig("/tmp/stdp_synapse_test" + fname_snip + "_window.png", dpi=300)
