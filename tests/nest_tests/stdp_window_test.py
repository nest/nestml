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

nest_version = NESTTools.detect_nest_version()


@pytest.fixture(autouse=True,
                scope="module")
def nestml_generate_target():
    r"""Generate the neuron model code"""

    # generate the "jit" model (co-generated neuron and synapse), that does not rely on ArchivingNode
    generate_nest_target(input_path=["models/neurons/iaf_psc_delta.nestml", "models/synapses/stdp_synapse.nestml"],
                         target_path="/tmp/nestml-jit",
                         logging_level="INFO",
                         module_name="nestml_jit_module",
                         suffix="_nestml",
                         codegen_opts={"neuron_parent_class": "StructuralPlasticityNode",
                                       "neuron_parent_class_include": "structural_plasticity_node.h",
                                       "neuron_synapse_pairs": [{"neuron": "iaf_psc_delta",
                                                                 "synapse": "stdp",
                                                                 "post_ports": ["post_spikes"]}]})
    nest.Install("nestml_jit_module")


def run_stdp_network(pre_spike_time, post_spike_time,
                     neuron_model_name,
                     synapse_model_name,
                     resolution=1.,  # [ms]
                     delay=1.,  # [ms]
                     sim_time=None,  # if None, computed from pre and post spike times
                     fname_snip="",
                     custom_synapse_properties=None):

    print("Pre spike time: " + str(pre_spike_time))
    print("Post spike time: " + str(post_spike_time))

    nest.set_verbosity("M_ALL")

    nest.ResetKernel()
    nest.SetKernelStatus({"resolution": resolution})

    wr = nest.Create("weight_recorder")
    if "__with" in synapse_model_name:
        weight_variable_name = "w"
        nest.CopyModel(synapse_model_name, "stdp_nestml_rec",
                       {"weight_recorder": wr[0], weight_variable_name: 1., "delay": delay, "the_delay": delay, "receptor_type": 0, "mu_minus": 0., "mu_plus": 0.})
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

    if nest_version.startswith("v2"):
        spikedet_pre = nest.Create("spike_detector")
        spikedet_post = nest.Create("spike_detector")
    else:
        spikedet_pre = nest.Create("spike_recorder")
        spikedet_post = nest.Create("spike_recorder")

    nest.Connect(pre_sg, pre_neuron, "one_to_one", syn_spec={"delay": 1.})
    nest.Connect(post_sg, post_neuron, "one_to_one", syn_spec={"delay": 1., "weight": 9999.})
    if nest_version.startswith("v2"):
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


@pytest.mark.parametrize("neuron_model_name", ["iaf_psc_delta_nestml__with_stdp_nestml"])
@pytest.mark.parametrize("synapse_model_name", ["stdp_nestml__with_iaf_psc_delta_nestml"])
def test_nest_stdp_synapse(neuron_model_name: str, synapse_model_name: str, fname_snip: str = ""):
    fname = "stdp_window_test"
    if len(fname_snip) > 0:
        fname += "_" + fname_snip

    sim_time = 1000.  # [ms]
    pre_spike_time = 100.  # sim_time / 2  # [ms]
    delay = 10.   # [ms]

    # plot
    if TEST_PLOTS:
        fig, ax = plt.subplots()

    dt_vec = []
    dw_vec = []
    for post_spike_time in np.arange(25, 175).astype(float) - delay:
        dt, dw = run_stdp_network(pre_spike_time, post_spike_time,
                                  neuron_model_name,
                                  synapse_model_name,
                                  resolution=1.,  # [ms]
                                  delay=delay,  # [ms]
                                  sim_time=sim_time,  # if None, computed from pre and post spike times
                                  fname_snip=fname_snip,
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

        fig.savefig("/tmp/stdp_synapse_test" + fname_snip + "_window.png", dpi=300)
