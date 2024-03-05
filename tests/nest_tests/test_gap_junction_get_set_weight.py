# -*- coding: utf-8 -*-
#
# test_gap_junction_get_set_weight.py
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
import scipy

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


@pytest.mark.skipif(NESTTools.detect_nest_version().startswith("v2"),
                    reason="This test does not support NEST 2")
class TestGapJunctionGetSetWeight:
    r"""Test that getting and setting the gap junction weight works correctly"""

    neuron_model = "iaf_psc_exp"

    @pytest.fixture(autouse=True)
    def generate_code(self):

        codegen_opts = {"gap_junctions": {"enable": True,
                                          "gap_current_port": "I_stim",
                                          "membrane_potential_variable": "V_m"}}

        files = [os.path.join("models", "neurons", self.neuron_model + ".nestml")]
        input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(os.pardir, os.pardir, s))) for s in files]
        generate_nest_target(input_path=input_path,
                             logging_level="DEBUG",
                             module_name="nestml_gap_module",
                             suffix="_nestml",
                             codegen_opts=codegen_opts)

        nest.Install("nestml_gap_module")

    def test_gap_junction_get_set_weight(self):
        pre_neuron = nest.Create(self.neuron_model + "_nestml")
        post_neuron = nest.Create(self.neuron_model + "_nestml")

        nest.Connect(pre_neuron, post_neuron, syn_spec={"weight": 42.})

        nest.Connect(pre_neuron,
                     post_neuron,
                     conn_spec={"rule": "one_to_one", "make_symmetric": True},
                     syn_spec={"synapse_model": "gap_junction",
                               "weight": 123.})

        static_syn = nest.GetConnections(pre_neuron, post_neuron, synapse_model="static_synapse")
        gap_syn = nest.GetConnections(pre_neuron, post_neuron, synapse_model="gap_junction")

        np.testing.assert_allclose(static_syn.weight, 42.)
        np.testing.assert_allclose(gap_syn.weight, 123.)

        static_syn.weight += 3.14159
        gap_syn.weight += 2.71828

        np.testing.assert_allclose(static_syn.weight, 42. + 3.14159)
        np.testing.assert_allclose(gap_syn.weight, 123. + 2.71828)

        nest.Simulate(10.)

        np.testing.assert_allclose(static_syn.weight, 42. + 3.14159)
        np.testing.assert_allclose(gap_syn.weight, 123. + 2.71828)
