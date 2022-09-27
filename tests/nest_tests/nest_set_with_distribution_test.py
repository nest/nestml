# -*- coding: utf-8 -*-
#
# nest_set_with_distribution_test.py
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
from nest.lib.hl_api_exceptions import NESTErrors

from pynestml.codegeneration.nest_tools import NESTTools
from pynestml.frontend.pynestml_frontend import generate_nest_target


nest_version = NESTTools.detect_nest_version()


class TestNestSetWithDistribution:
    r"""
    Tests that parameters and state variables can be set with samples from a probability distribution.
    """

    @pytest.fixture(scope="module", autouse=True)
    def setUp(self):
        """Generate the model code"""

        codegen_opts = {"neuron_synapse_pairs": [{"neuron": "iaf_psc_exp",
                                                  "synapse": "stdp",
                                                  "post_ports": ["post_spikes"]}]}

        # generate the "jit" model (co-generated neuron and synapse), that does not rely on ArchivingNode
        files = [os.path.join("models", "neurons", "iaf_psc_exp.nestml"),
                 os.path.join("models", "synapses", "stdp_synapse.nestml")]
        input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, s))) for s in files]
        generate_nest_target(input_path=input_path,
                             target_path="/tmp/nestml-jit",
                             logging_level="INFO",
                             module_name="nestmlmodule",
                             suffix="_nestml",
                             codegen_opts=codegen_opts)


    @pytest.mark.skipif(nest_version.startswith("v2"),
                        reason="This test does not support NEST 2")
    def test_nest_set_with_distribution(self):
        nest.set_verbosity("M_ALL")

        nest.ResetKernel()
        nest.Install("nestmlmodule")

        neur = nest.Create("iaf_psc_exp_nestml__with_stdp_nestml", 100)
        neur.V_abs = nest.random.uniform(0., 1.)    # test setting a state variable
        neur.V_reset = nest.random.uniform(0., 1.)    # test setting a parameter

        nest.Connect(neur, neur, syn_spec={"synapse_model": "stdp_nestml__with_iaf_psc_exp_nestml"})
        syn = nest.GetConnections(source=neur)
        syn.w = nest.random.uniform(0., 1.)    # test setting a state variable
        syn.alpha = nest.random.uniform(0., 1.)    # test setting a parameter
