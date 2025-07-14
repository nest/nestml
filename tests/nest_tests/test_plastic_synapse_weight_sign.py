# -*- coding: utf-8 -*-
#
# test_plastic_synapse_weight_sign.py
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

from typing import Sequence

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


synapse_model_names = ["stdp_synapse"]#, "triplet_stdp_synapse", "stdp_nn_symm", "stdp_nn_restr_symm", "stdp_nn_pre_centered"]

class TestPlasticSynapseWeightSign:
    r"""Test that the sign of the weight of plastic synapses never changes (negative stays negative, positive stays positive)"""

    neuron_model_name = "iaf_psc_exp_neuron"

    @pytest.fixture(autouse=True,
                    scope="module")
    def generate_model_code(self):
        """Generate the model code"""

        codegen_opts = {"neuron_synapse_pairs": []}

        files = [os.path.join("models", "neurons", self.neuron_model_name + ".nestml")]
        for synapse_model_name in synapse_model_names:
            files.append(os.path.join("models", "synapses", synapse_model_name + ".nestml"))
            codegen_opts["neuron_synapse_pairs"].append({"neuron": self.neuron_model_name,
                                                         "synapse": synapse_model_name,
                                                         "post_ports": ["post_spikes"]})

        input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(os.pardir, os.pardir, s))) for s in files]
        generate_nest_target(input_path=input_path,
                             logging_level="DEBUG",
                             suffix="_nestml",
                             codegen_opts=codegen_opts)

    @pytest.mark.parametrize("synapse_model_name", synapse_model_names)
    @pytest.mark.parametrize("test", ["potentiation", "depression"])
    def test_nest_stdp_synapse(self, synapse_model_name: str, test: str):
        pre_spike_times = np.linspace(100., 1000., 10)

        if test == "potentiation":
            init_weight = -1.
            post_spike_times = pre_spike_times + 10.
        else:
            init_weight = 1.
            post_spike_times = pre_spike_times - 10.

        nest.ResetKernel()
        nest.Install("nestmlmodule")

        # create spike_generators with these times
        pre_sg = nest.Create("spike_generator",
                             params={"spike_times": pre_spike_times,
                                     "allow_offgrid_times": True})
        post_sg = nest.Create("spike_generator",
                              params={"spike_times": post_spike_times,
                                      "allow_offgrid_times": True})

        pre_neuron = nest.Create("parrot_neuron")
        post_neuron = nest.Create(self.neuron_model_name + "_nestml__with_" + synapse_model_name + "_nestml")

        nest.Connect(pre_sg, pre_neuron, syn_spec={"weight": 9999.})
        nest.Connect(post_sg, post_neuron, syn_spec={"weight": 9999.})
        nest.Connect(pre_neuron, post_neuron, syn_spec={"synapse_model": synapse_model_name + "_nestml__with_" + self.neuron_model_name + "_nestml",
                                                        "weight": init_weight})

        syn = nest.GetConnections(source=pre_neuron, synapse_model=synapse_model_name + "_nestml__with_" + self.neuron_model_name + "_nestml")

        nest.Simulate(100. + max(np.amax(pre_spike_times), np.amax(post_spike_times)))

        assert np.sign(syn.weight) == np.sign(init_weight)
