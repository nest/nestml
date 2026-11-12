# -*- coding: utf-8 -*-
#
# test_rng_in_synapse.py
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


class TestRNGInSynapse:
    r"""
    Test that random sampling function can be called inside ``update`` block inside a synapse model.
    """

    @pytest.fixture(scope="module", autouse=True)
    def setUp(self):
        r"""generate code for neuron and synapse and build NEST user module"""
        files = [os.path.join("models", "neurons", "iaf_psc_exp_neuron.nestml"),
                 os.path.join("tests", "nest_tests", "resources", "rng_synapse.nestml")]
        input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, s))) for s in files]
        generate_nest_target(input_path=input_path,
                             logging_level="DEBUG",
                             module_name="nestmlmodule",
                             suffix="_nestml",
                             codegen_opts={"weight_variable": {"rng_synapse": "w"}})

    def test_rng_synapse(self):
        sim_time = 1000.
        neuron_model_name = "iaf_psc_exp_neuron_nestml"
        synapse_model_name = "rng_synapse_nestml"

        nest.ResetKernel()
        NESTTools.set_nest_verbosity("ALL")
        nest.SetKernelStatus({"resolution": .1})
        nest.Install("nestmlmodule")

        # create spike_generators with these times
        pre_sg = nest.Create("spike_generator",
                             params={"spike_times": 1 + np.arange(sim_time)})

        # set up custom synapse models
        wr = nest.Create("weight_recorder")
        nest.CopyModel(synapse_model_name, "syn_nestml_rec", {"weight_recorder": wr[0]})

        pre_neuron = nest.Create("parrot_neuron")
        post_neuron = nest.Create(neuron_model_name)

        nest.Connect(pre_sg, pre_neuron, "one_to_one")
        nest.Connect(pre_neuron, post_neuron, "all_to_all", syn_spec={"synapse_model": "syn_nestml_rec"})

        syn = nest.GetConnections(source=pre_neuron, synapse_model="syn_nestml_rec")
        assert syn.weight == 1.

        n_samples = int(sim_time)
        samples = []
        for i in range(n_samples):
            nest.Simulate(1.)
            samples.append(syn.foo)

        np.testing.assert_allclose(np.mean(samples), 0, atol=0.1)
        np.testing.assert_allclose(np.std(samples), 1, atol=0.1)
