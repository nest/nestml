# -*- coding: utf-8 -*-
#
# test_homogeneous_parameters_synapse.py
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
import unittest

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
class TestHomogeneousParametersSynapse:
    r"""Test code generation and basic functionality of synapse with homogeneous parameters.
    """

    @pytest.fixture(scope="module", autouse=True)
    def setUp(self):
        r"""generate code for neuron and synapse and build NEST user module"""
        files = [os.path.join("models", "neurons", "iaf_psc_exp.nestml"),
                 os.path.join("tests", "nest_tests", "resources", "homogeneous_parameters_synapse.nestml")]
        input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, s))) for s in files]
        generate_nest_target(input_path=input_path,
                             logging_level="INFO",
                             module_name="nestmlmodule",
                             suffix="_nestml")

    def test_homogeneous_parameters_synapse(self):

        fname_snip = ""

        sim_time = 50.
        synapse_model_name = "static_synapse_nestml"
        neuron_model_name = "iaf_psc_exp_nestml"

        nest.ResetKernel()
        nest.set_verbosity("M_ALL")
        nest.SetKernelStatus({"resolution": .1})
        nest.Install("nestmlmodule")

        # create spike_generators with these times
        pre_sg = nest.Create("spike_generator",
                             params={"spike_times": 10. * (1 + np.arange(sim_time))})

        pre_neuron = nest.Create("parrot_neuron")
        post_neuron = nest.Create(neuron_model_name)

        nest.Connect(pre_sg, pre_neuron, "one_to_one")
        nest.Connect(pre_neuron, post_neuron, "all_to_all", syn_spec={"synapse_model": synapse_model_name})

        V_m_before_sim = post_neuron.V_m

        nest.Simulate(sim_time)

        V_m_after_sim = post_neuron.V_m

        assert V_m_after_sim > V_m_before_sim
