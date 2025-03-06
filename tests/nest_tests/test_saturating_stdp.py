# -*- coding: utf-8 -*-
#
# test_saturating_stdp.py
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
class TestSaturatingSTDP:

    @pytest.fixture(autouse=True,
                    scope="module")
    def generate_model_code(self):
        r"""Generate the NEST C++ code for neuron and synapse models"""

        files = [os.path.join("models", "neurons", "iaf_psc_delta_neuron.nestml"),
                 os.path.join("models", "neurons", "izhikevich_neuron.nestml"),
                 os.path.join("tests", "nest_tests", "resources", "stdp_saturating_synapse.nestml")]
        input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, s))) for s in files]
        generate_nest_target(input_path=input_path,
                             logging_level="INFO",
                             suffix="_nestml",
                             codegen_opts={"neuron_synapse_pairs": [{"neuron": "iaf_psc_delta_neuron",
                                                                     "synapse": "stdp_saturating_synapse",
                                                                     "post_ports": ["post_spikes"]},
                                                                    {"neuron": "izhikevich_neuron",
                                                                     "synapse": "stdp_saturating_synapse",
                                                                     "post_ports": ["post_spikes"]}],
                                           "delay_variable": {"stdp_saturating_synapse": "d"},
                                           "weight_variable": {"stdp_saturating_synapse": "w"}})

    @pytest.mark.parametrize("neuron_model_name,synapse_model_name", [("iaf_psc_delta_neuron_nestml__with_stdp_saturating_synapse_nestml", "stdp_saturating_synapse_nestml__with_iaf_psc_delta_neuron_nestml"),
                                                                      ("izhikevich_neuron_nestml__with_stdp_saturating_synapse_nestml", "stdp_saturating_synapse_nestml__with_izhikevich_neuron_nestml")])
    def test_stdp_saturating_synapse(self, neuron_model_name: str, synapse_model_name: str, fname_snip: str = ""):
        nest.ResetKernel()
        nest.Install("nestmlmodule")
        pre_sg = nest.Create("spike_generator", params={"spike_times": [1., 11., 21.]})

        pre_neuron = nest.Create("parrot_neuron")
        post_neuron = nest.Create(neuron_model_name)

        nest.Connect(pre_sg, pre_neuron, "one_to_one", syn_spec={"delay": 1.})
        nest.Connect(pre_neuron, post_neuron, "all_to_all", syn_spec={"synapse_model": synapse_model_name})

        nest.Simulate(50.)
