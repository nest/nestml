# -*- coding: utf-8 -*-
#
# test_vectors_synapse.py
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

import nest
import numpy as np

from pynestml.frontend.pynestml_frontend import generate_nest_target


class TestVectorsSynapse:
    """
    Checks if the vector variables in a synapse model are declared, initialized, and accessed properly.
    """

    def test_vectors_synapse(self):
        files = [os.path.join("models", "neurons", "iaf_psc_exp_neuron.nestml"),
                 os.path.join("tests", "nest_tests", "resources", "vectors_test_synapse.nestml")]
        input_paths = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(os.pardir, os.pardir, s)))
                       for s in files]
        codegen_opts = {
            "neuron_synapse_pairs": [{"neuron": "iaf_psc_exp_neuron",
                                      "synapse": "vectors_test_synapse"}],
            "delay_variable": {"vectors_test_synapse": "d"},
            "weight_variable": {"vectors_test_synapse": "w"}
        }
        generate_nest_target(input_path=input_paths,
                             codegen_opts=codegen_opts,
                             target_path="target_vec_syn",
                             logging_level="INFO")
        neuron_model = "iaf_psc_exp_neuron__with_vectors_test_synapse"
        synapse_model = "vectors_test_synapse__with_iaf_psc_exp_neuron"

        nest.ResetKernel()
        nest.resolution = 1.0
        spike_times = [1.0, 3.0, 7.0]
        sim_time = 10.
        delay = 1.0

        nest.Install("nestmlmodule")

        neuron = nest.Create(neuron_model)
        par_neuron = nest.Create("parrot_neuron")
        sg = nest.Create("spike_generator", params={"spike_times": spike_times})
        nest.Connect(sg, par_neuron)
        nest.Connect(par_neuron, neuron, syn_spec={"synapse_model": synapse_model, "d": delay})

        nest.Simulate(sim_time)
        conn = nest.GetConnections(par_neuron, neuron)
        ca_buffer = conn.get("ca_buffer")

        original_indices = {int(x) + int(delay) for x in spike_times}
        expected_buffer = [2 if i in original_indices else 0 for i in range(int(sim_time))]

        np.testing.assert_array_equal(ca_buffer, expected_buffer)
