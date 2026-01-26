# -*- coding: utf-8 -*-
#
# test_neuron_with_multiple_different_plastic_synapses.py
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
    matplotlib.use('Agg')
    import matplotlib.ticker
    import matplotlib.pyplot as plt
    TEST_PLOTS = True
except Exception:
    TEST_PLOTS = False

sim_mdl = True
sim_ref = True


@pytest.mark.skipif(NESTTools.detect_nest_version().startswith("v2"),
                    reason="This test does not support NEST 2")
class TestNeuronWithMultipleDifferentSynapses:
    neuron_model_name = "iaf_psc_exp_neuron_nestml__with_stdp_nn_symm_synapse_nestml"
    synapse1_model_name = "stdp_nn_symm_synapse_nestml__with_iaf_psc_exp_neuron_nestml"
    synapse2_model_name = "stdp_nn_restr_symm_synapse_nestml__with_iaf_psc_exp_neuron_nestml"

    @pytest.fixture(scope="module", autouse=True)
    def setUp(self):
        """Generate the model code"""

        files = [os.path.join("models", "neurons", "iaf_psc_exp_neuron.nestml"),
                 os.path.join("models", "synapses", "stdp_nn_symm_synapse.nestml"),
                 os.path.join("models", "synapses", "stdp_nn_restr_symm_synapse.nestml")]
        input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, s))) for s in files]
        generate_nest_target(input_path=input_path,
                             logging_level="DEBUG",
                             module_name="nestmlmodule",
                             suffix="_nestml",
                             codegen_opts={"neuron_synapse_pairs": [{"neuron": "iaf_psc_exp_neuron",
                                                                     "synapses": {"stdp_nn_symm_synapse": {"post_ports": ["post_spikes"]},
                                                                                  "stdp_nn_restr_symm_synapse": {"post_ports": ["post_spikes"]}}}],
                                           "delay_variable": {"stdp_nn_symm_synapse": "d",
                                                              "stdp_nn_restr_symm_synapse": "d"},
                                           "weight_variable": {"stdp_nn_symm_synapse": "w",
                                                               "stdp_nn_restr_symm_synapse": "w"}})

    def test_stdp_nn_synapse(self):
        nest.ResetKernel()
        nest.set_verbosity("M_ALL")
        nest.Install("nestmlmodule")

        post_neuron = nest.Create(TestNeuronWithMultipleDifferentSynapses.neuron_model_name)
        pre_neuron1 = nest.Create("parrot_neuron")
        pre_neuron2 = nest.Create("parrot_neuron")

        nest.Connect(pre_neuron1, post_neuron, syn_spec={"synapse_model": TestNeuronWithMultipleDifferentSynapses.synapse1_model_name})
        nest.Connect(pre_neuron2, post_neuron, syn_spec={"synapse_model": TestNeuronWithMultipleDifferentSynapses.synapse2_model_name})

        nest.Simulate(100.)
