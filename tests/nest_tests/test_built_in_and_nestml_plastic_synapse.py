# -*- coding: utf-8 -*-
#
# test_built_in_and_nestml_plastic_synapse.py
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
import os.path

import nest
import numpy as np
import pytest
from pynestml.codegeneration.nest_tools import NESTTools

from pynestml.frontend.pynestml_frontend import generate_nest_target


@pytest.mark.skipif(NESTTools.detect_nest_version().startswith("v2"),
                    reason="This test does not support NEST 2")
class TestBuiltInAndNESTMLPlasticSynapse:
    r"""Test that synaptic plasticity works with both a NEST built-in plastic synapse and a NESTML custom plastic synapse attached to the same neuron."""

    neuron_model = "iaf_psc_exp_nonlineardendrite"
    synapse_model = "stdsp_synapse_no_permanence"

    def setup_nest(self):
        files = [f"{TestBuiltInAndNESTMLPlasticSynapse.neuron_model}_alternate.nestml",
                 f"{TestBuiltInAndNESTMLPlasticSynapse.synapse_model}.nestml"]
        input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), "resources", s)) for s in files]

        generate_nest_target(
            input_path=input_path,
            target_path="module",
            logging_level="DEBUG",
            module_name=f"nestml_{TestBuiltInAndNESTMLPlasticSynapse.neuron_model}_{TestBuiltInAndNESTMLPlasticSynapse.synapse_model}_module",
            suffix="_nestml",
            codegen_opts={
                "neuron_synapse_pairs": [
                    {
                        "neuron": TestBuiltInAndNESTMLPlasticSynapse.neuron_model,
                        "synapse": TestBuiltInAndNESTMLPlasticSynapse.synapse_model,
                        "post_ports": ["post_spikes", ["z_post", "z"]],
                    }
                ],
            },
        )

        # install custom neuron models
        nest.Install(f"nestml_{TestBuiltInAndNESTMLPlasticSynapse.neuron_model}_{TestBuiltInAndNESTMLPlasticSynapse.synapse_model}_module")

    def _test_plasticity(self, neuron_model, synapse_model):

        print("testing plasticity for synapse mode " + str(synapse_model))

        # parameters
        Jns = 3000.0
        t_stop = 500.0   # [ms]
        initial_weight = 123.

        nest.ResetKernel()

        # create pre and post neurons
        pre_neuron = nest.Create(neuron_model)
        post_neuron = nest.Create(neuron_model)

        syn_spec = {
            "synapse_model": synapse_model,
            "receptor_type": 1,  # external input
            "lambda": 1E-3,
            "weight": initial_weight,
        }

        if synapse_model != "stdp_synapse":
            syn_spec["lambda_minus"] = 1E-4

        # connect pre and post
        nest.Connect(
            pre_neuron,
            post_neuron,
            syn_spec=syn_spec,
        )

        # create and connect stimulus source
        pre_stimulus = nest.Create(
            "spike_generator", {"spike_times": [float(5 * i) for i in range(1, 200)]}
        )
        post_stimulus = nest.Create(
            "spike_generator", {"spike_times": [float(10 + 5 * i) for i in range(1, 200)]}
        )
        sr_pre = nest.Create("spike_recorder")
        nest.Connect(pre_neuron, sr_pre)
        sr_post = nest.Create("spike_recorder")
        nest.Connect(post_neuron, sr_post)

        nest.Connect(pre_stimulus, pre_neuron, syn_spec={"weight": Jns, "receptor_type": 1})
        nest.Connect(
            post_stimulus, post_neuron, syn_spec={"weight": Jns, "receptor_type": 1}
        )

        connection_before = nest.GetConnections(synapse_model=synapse_model)
        weight_before = connection_before.get("weight")
        np.testing.assert_allclose(initial_weight, weight_before)

        print("\nconnections before learning:")
        print(connection_before)

        # simulate
        nest.Simulate(t_stop)

        connection_after = nest.GetConnections(synapse_model=synapse_model)
        weight_after = connection_after.get("weight")

        print("\nconnections after learning:")
        print(connection_after)

        assert np.abs(weight_before - weight_after) > 1., "Weight did not change during STDP induction protocol!"

    def test_plasticity(self):
        self.setup_nest()

        self._test_plasticity(
            neuron_model=f"{self.neuron_model}_nestml__with_{self.synapse_model}_nestml",
            synapse_model=f"{self.synapse_model}_nestml__with_{self.neuron_model}_nestml",
        )

        self._test_plasticity(
            neuron_model=f"{self.neuron_model}_nestml__with_{self.synapse_model}_nestml",
            synapse_model="stdp_synapse",
        )
