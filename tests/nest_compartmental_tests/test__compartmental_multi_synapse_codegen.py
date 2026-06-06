# -*- coding: utf-8 -*-
#
# test__compartmental_multi_synapse_codegen.py
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
import unittest

import nest
import pytest

from pynestml.frontend.pynestml_frontend import generate_nest_compartmental_target


class TestCompartmentalMultiSynapseCodegen(unittest.TestCase):
    MODULE_NAME = "cm_multi_synapse_module"
    TARGET_DIR = "target_multi_synapse"

    @pytest.fixture(scope="module", autouse=True)
    def setup(self):
        tests_path = os.path.realpath(os.path.dirname(__file__))
        resources_path = os.path.join(tests_path, "resources")
        target_path = os.path.join(tests_path, self.TARGET_DIR)

        if not os.path.exists(target_path):
            os.makedirs(target_path)

        nest.ResetKernel()
        nest.SetKernelStatus(dict(resolution=.1))

        generate_nest_compartmental_target(
            input_path=[
                os.path.join(resources_path, "concmech.nestml"),
                os.path.join(resources_path, "cm_default.nestml"),
                os.path.join(resources_path, "cm_stdp_synapse.nestml"),
                os.path.join(resources_path, "cm_stdp_nn_symm_synapse.nestml"),
            ],
            target_path=target_path,
            module_name=self.MODULE_NAME,
            suffix="_nestml",
            logging_level="DEBUG",
            codegen_opts={
                "neuron_synapse_pairs": [
                    {
                        "neuron": "multichannel_test_model",
                        "synapses": {
                            "stdp_synapse": {"post_ports": ["post_spikes"]},
                            "stdp_nn_symm_synapse": {"post_ports": ["post_spikes"]},
                        },
                    },
                    {
                        "neuron": "cm_default",
                        "synapses": {
                            "stdp_synapse": {"post_ports": ["post_spikes"]},
                            "stdp_nn_symm_synapse": {"post_ports": ["post_spikes"]},
                        },
                    },
                ],
                "delay_variable": {
                    "stdp_synapse": "d",
                    "stdp_nn_symm_synapse": "d",
                },
                "weight_variable": {
                    "stdp_synapse": "w",
                    "stdp_nn_symm_synapse": "w",
                },
            },
        )

        nest.Install(self.MODULE_NAME + ".so")

    def test_create_two_neurons_with_two_synapse_receptor_variants(self):
        compartment_params = {"C_m": 10.0, "g_C": 0.0, "g_L": 1.5, "e_L": -70.0}
        receptor_params = {"w": 1.0, "d": 0.1, "e_AMPA": -70.0}

        multichannel_neuron = nest.Create("multichannel_test_model_nestml")
        multichannel_neuron.compartments = [{"parent_idx": -1, "params": compartment_params}]
        multichannel_neuron.receptors = [
            {"comp_idx": 0, "receptor_type": "AMPA_stdp_synapse_nestml", "params": receptor_params},
            {"comp_idx": 0, "receptor_type": "AMPA_stdp_nn_symm_synapse_nestml", "params": receptor_params},
        ]

        cm_default_neuron = nest.Create("cm_default_nestml")
        cm_default_neuron.compartments = [{"parent_idx": -1, "params": compartment_params}]
        cm_default_neuron.receptors = [
            {"comp_idx": 0, "receptor_type": "AMPA_stdp_synapse_nestml", "params": receptor_params},
            {"comp_idx": 0, "receptor_type": "AMPA_stdp_nn_symm_synapse_nestml", "params": receptor_params},
        ]
