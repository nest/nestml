# -*- coding: utf-8 -*-
#
# stdp_synapse_test.py
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

sim_mdl = True
sim_ref = True


class TestNestSTDPSynapse:

    neuron_model_name = "iaf_psc_exp_neuron_nestml__with_stp_synapse_nestml"
    synapse_model_name = "stp_synapse_nestml__with_iaf_psc_exp_neuron_nestml"

    @pytest.fixture(autouse=True,
                    scope="module")
    def generate_model_code(self):
        """Generate the model code"""

        codegen_opts = {"neuron_synapse_pairs": [{"neuron": "iaf_psc_exp_neuron",
                                                      "synapse": "stp_synapse",
                                                      "post_ports": ["post_spikes"]}],
                            "delay_variable": {"stp_synapse": "d"},
                            "weight_variable": {"stp_synapse": "w"}}
        files = [os.path.join("models", "neurons", "iaf_psc_exp_neuron.nestml"),
                 os.path.join("models", "synapses", "stp_synapse.nestml")]
        input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
                       os.pardir, os.pardir, s))) for s in files]
        generate_nest_target(input_path=input_path,
                             logging_level="DEBUG",
                             suffix="_nestml",
                             codegen_opts=codegen_opts)
    def test_foo(self):
        nest.Install("nestmlmodule")
        n = nest.Create("iaf_psc_exp_neuron_nestml__with_stp_synapse_nestml", 2)
        nest.Connect(n[0], n[1], syn_spec={"synapse_model": "stp_synapse_nestml__with_iaf_psc_exp_neuron_nestml"})
        nest.Simulate(100)

