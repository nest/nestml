# -*- coding: utf-8 -*-
#
# test_nest_gpu_synapse_code_generation.py
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
import multiprocessing as mp

# try to import matplotlib; set the result in the flag TEST_PLOTS
try:
    import matplotlib as mpl

    mpl.use("agg")
    import matplotlib.pyplot as plt

    TEST_PLOTS = True
except BaseException:
    TEST_PLOTS = False

from pynestml.frontend.pynestml_frontend import generate_nest_gpu_target


class TestNESTGPUSynapseCodeGeneration:
    # @pytest.fixture(scope="module", autouse=True)
    def test_nest_gpu_syn(self):
        files = [os.path.join("models", "neurons", "iaf_psc_exp_neuron.nestml"),
                 os.path.join("models", "synapses", "stdp_nn_symm_synapse.nestml")]
        input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, s))) for s in files]
        target_path = "target_gpu_syn"
        logging_level = "INFO"
        suffix = "_nestml"
        codegen_opts = {"neuron_synapse_pairs": [{"neuron": "iaf_psc_exp_neuron",
                                                  "synapses": {
                                                      "stdp_nn_symm_synapse": {"post_ports": ["post_spikes"]}}}],
                        "weight_variable": {"stdp_nn_symm_synapse": "w"},
                        "strictly_synaptic_vars": {"stdp_nn_symm_synapse": ["pre_trace", "post_trace"]}}
        generate_nest_gpu_target(input_path, target_path,
                                 logging_level=logging_level,
                                 suffix=suffix,
                                 codegen_opts=codegen_opts)
