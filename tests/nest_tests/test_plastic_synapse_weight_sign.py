# -*- coding: utf-8 -*-
#
# test_plastic_synapse_weight_sign.py
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

# try to import matplotlib; set the result in the flag TEST_PLOTS
try:
    import logging
    import matplotlib as mpl
    mpl.use("agg")
    logging.getLogger('matplotlib').setLevel(logging.WARNING)    # prevent matplotlib from printing a lot of debug messages when NESTML is running in DEBUG logging_level
    import matplotlib.pyplot as plt
    TEST_PLOTS = True
except BaseException:
    TEST_PLOTS = False

import nest

from pynestml.codegeneration.nest_tools import NESTTools
from pynestml.frontend.pynestml_frontend import generate_nest_target


synapse_model_names = ["stdp_synapse", "stdp_triplet_synapse"]   # TODO: nearest-neighbour STDP synapses cannot yet be tested using this protocol


@pytest.mark.skipif(NESTTools.detect_nest_version().startswith("v2"),
                    reason="This test does not support NEST 2")
class TestPlasticSynapseWeightSign:
    r"""Test that the sign of the weight of plastic synapses never changes (negative stays negative, positive stays positive)"""

    neuron_model_name = "iaf_psc_exp_neuron"

    @pytest.fixture(autouse=True,
                    scope="module")
    def generate_model_code(self):
        r"""Generate the model code"""

        codegen_opts = {"neuron_synapse_pairs": [],
                        "delay_variable": {},
                        "weight_variable": {}}

        files = [os.path.join("models", "neurons", self.neuron_model_name + ".nestml")]
        for synapse_model_name in synapse_model_names:
            files.append(os.path.join("models", "synapses", synapse_model_name + ".nestml"))
            codegen_opts["neuron_synapse_pairs"].append({"neuron": self.neuron_model_name,
                                                         "synapse": synapse_model_name,
                                                         "post_ports": ["post_spikes"]})
            codegen_opts["delay_variable"][synapse_model_name] = "d"
            codegen_opts["weight_variable"][synapse_model_name] = "w"

        input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(os.pardir, os.pardir, s))) for s in files]
        generate_nest_target(input_path=input_path,
                             logging_level="DEBUG",
                             suffix="_nestml",
                             codegen_opts=codegen_opts)

    @pytest.mark.parametrize("synapse_model_name", synapse_model_names)
    @pytest.mark.parametrize("test", ["potentiation", "depression"])
    def test_nest_stdp_synapse(self, synapse_model_name: str, test: str):
        if synapse_model_name == "stdp_triplet_synapse":
            # no adjustable learning rate for this synapse
            pre_spike_times = np.linspace(100., 1000000., 1000)
        else:
            pre_spike_times = np.linspace(100., 10000., 10)

        init_weight = 1.

        if test == "potentiation":
            post_spike_times = pre_spike_times + 10.
        else:
            assert test == "depression"
            post_spike_times = pre_spike_times - 10.

        nest.ResetKernel()
        nest.set_verbosity("M_ERROR")

        nest.Install("nestmlmodule")

        # create spike_generators with these times
        pre_sg = nest.Create("spike_generator",
                             params={"spike_times": pre_spike_times,
                                     "allow_offgrid_times": True})
        post_sg = nest.Create("spike_generator",
                              params={"spike_times": post_spike_times,
                                      "allow_offgrid_times": True})

        pre_neuron = nest.Create("parrot_neuron")
        post_neuron = nest.Create(self.neuron_model_name + "_nestml__with_" + synapse_model_name + "_nestml")

        nest.Connect(pre_sg, pre_neuron, syn_spec={"weight": 9999.})
        nest.Connect(post_sg, post_neuron, syn_spec={"weight": 9999.})

        syn_opts = {"synapse_model": synapse_model_name + "_nestml__with_" + self.neuron_model_name + "_nestml",
                    "w": init_weight,
                    "Wmin": 0,
                    "Wmax": np.pi}
        if synapse_model_name == "stdp_synapse":
            syn_opts.update({"lambda": .1,    # high learning rate
                             "mu_plus": 0.,    # additive STDP
                             "mu_minus": 0.})    # additive STDP
        nest.Connect(pre_neuron, post_neuron, syn_spec=syn_opts)
        syn = nest.GetConnections(source=pre_neuron, synapse_model=synapse_model_name + "_nestml__with_" + self.neuron_model_name + "_nestml")

        nest.Simulate(100. + max(np.amax(pre_spike_times), np.amax(post_spike_times)))

        if test == "potentiation":
            post_spike_times = pre_spike_times + 10.
            np.testing.assert_allclose(np.abs(syn.weight), np.pi)
        else:
            assert test == "depression"
            np.testing.assert_allclose(np.abs(syn.weight), 0.)
