# -*- coding: utf-8 -*-
#
# test_random_functions_neuromod_spikes.py
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
import pytest

import nest

from pynestml.frontend.pynestml_frontend import generate_nest_target
from pynestml.codegeneration.nest_tools import NESTTools


@pytest.mark.skipif(NESTTools.detect_nest_version().startswith("v2"),
                    reason="This test does not support NEST 2")
class TestRandomFunctionsWithNeuromodSpikes:
    """Tests for random functions like ``random_uniform`` and ``random_normal`` with neuromodulated spikes
    """
    neuron_model_name = "iaf_psc_exp_neuron_nestml__with_random_functions_neuromod_synapse_nestml"
    synapse_model_name = "random_functions_neuromod_synapse_nestml__with_iaf_psc_exp_neuron_nestml"

    @pytest.fixture(scope="class", autouse=True)
    def setUp(self):
        files = [os.path.join("models", "neurons", "iaf_psc_exp_neuron.nestml"),
                 os.path.join("tests", "nest_tests", "resources",
                              "random_functions_neuromod_synapse.nestml")]
        input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, s))) for s in files]
        generate_nest_target(input_path=input_path,
                             logging_level="DEBUG",
                             suffix="_nestml",
                             codegen_opts={"neuron_parent_class": "StructuralPlasticityNode",
                                           "neuron_parent_class_include": "structural_plasticity_node.h",
                                           "neuron_synapse_pairs": [{"neuron": "iaf_psc_exp_neuron",
                                                                     "synapse": "random_functions_neuromod_synapse",
                                                                     "post_ports": ["post_spikes"],
                                                                     "vt_ports": ["mod_spikes"]}],
                                           "delay_variable": {
                                               "random_functions_neuromod_synapse": "d"},
                                           "weight_variable": {
                                               "random_functions_neuromod_synapse": "w"},
                                           "strictly_synaptic_vars": {"random_functions_neuromod_synapse": ["x", "y"]}})

    def test_random_functions_neuromod_synapse(self):
        pre_spike_times = [1., 11., 21.]  # [ms]
        post_spike_times = [6., 16., 26.]  # [ms]

        vt_spike_times = np.arange(10, 1010).astype(float)   # [ms]

        x, y = self.run_synapse_test(neuron_model_name=self.neuron_model_name,
                                     synapse_model_name=self.synapse_model_name,
                                     resolution=.1,  # [ms]
                                     delay=1.,  # [ms]
                                     pre_spike_times=pre_spike_times,
                                     post_spike_times=post_spike_times,
                                     vt_spike_times=vt_spike_times)

        # large tolerances because of few data points
        np.testing.assert_allclose(np.mean(x), .5, atol=1E-2)
        np.testing.assert_allclose(np.amin(x), 0., atol=1E-2)
        np.testing.assert_allclose(np.amax(x), 1., atol=1E-2)
        np.testing.assert_allclose(np.mean(y), 500., atol=5)
        np.testing.assert_allclose(np.std(y), 25, atol=1)

    def run_synapse_test(self, neuron_model_name,
                         synapse_model_name,
                         resolution=1.,  # [ms]
                         delay=1.,  # [ms]
                         sim_time=None,  # if None, computed from pre and post spike times
                         pre_spike_times=None,
                         post_spike_times=None,
                         vt_spike_times=None):

        if pre_spike_times is None:
            pre_spike_times = []

        if post_spike_times is None:
            post_spike_times = []

        if vt_spike_times is None:
            vt_spike_times = []

        if sim_time is None:
            sim_time = max(np.amax(pre_spike_times, initial=0.), np.amax(
                post_spike_times, initial=0.), np.amax(vt_spike_times, initial=0.)) + 5 * delay

        nest.ResetKernel()
        if not NESTTools.detect_nest_version().startswith("main"):
            nest.set_verbosity("M_ERROR")
        else:
            nest.verbosity = nest.VerbosityLevel.ERROR
        nest.SetKernelStatus({"resolution": resolution})
        nest.Install("nestmlmodule")

        print("Pre spike times: " + str(pre_spike_times))
        print("Post spike times: " + str(post_spike_times))
        print("VT spike times: " + str(vt_spike_times))

        # create spike_generators with these times
        pre_sg = nest.Create("spike_generator",
                             params={"spike_times": pre_spike_times})
        post_sg = nest.Create("spike_generator",
                              params={"spike_times": post_spike_times,
                                      "allow_offgrid_times": True})
        vt_sg = nest.Create("spike_generator",
                            params={"spike_times": vt_spike_times,
                                    "allow_offgrid_times": True})

        # create  volume transmitter
        vt = nest.Create("volume_transmitter")
        vt_parrot = nest.Create("parrot_neuron")
        nest.Connect(vt_sg, vt_parrot)
        nest.Connect(vt_parrot, vt, syn_spec={"synapse_model": "static_synapse",
                                              "weight": 1.,
                                              "delay": 1.})  # delay is ignored?!

        # set up custom synapse models
        wr = nest.Create("weight_recorder")
        nest.CopyModel(synapse_model_name, "neuromod_stdp_nestml_rec",
                       {"weight_recorder": wr[0], "w": 1., "d": delay, "receptor_type": 0,
                        "volume_transmitter": vt})

        # create parrot neurons and connect spike_generators
        pre_neuron = nest.Create("parrot_neuron")
        post_neuron = nest.Create(neuron_model_name)

        nest.Connect(pre_sg, pre_neuron, "one_to_one", syn_spec={"delay": 1.})
        nest.Connect(post_sg, post_neuron, "one_to_one",
                     syn_spec={"delay": 1., "weight": 9999., "receptor_type": 0})
        nest.Connect(pre_neuron, post_neuron, "all_to_all",
                     syn_spec={"synapse_model": "neuromod_stdp_nestml_rec", "receptor_type": 0})

        # get STDP synapse and weight before protocol
        syn = nest.GetConnections(source=pre_neuron, synapse_model="neuromod_stdp_nestml_rec")

        nest.Simulate(sim_time)

        return syn.x, syn.y
