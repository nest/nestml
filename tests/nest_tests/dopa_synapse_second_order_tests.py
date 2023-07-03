# -*- coding: utf-8 -*-
#
# dopa_synapse_second_order_tests.py
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

sim_mdl = True
sim_ref = True


class TestDopaSecondOrder:
    r"""
    Test second-order integration in a neuromodulated synapse.
    """

    neuron_model_name = "iaf_psc_exp_nestml__with_dopa_synapse_second_order_nestml"
    synapse_model_name = "dopa_synapse_second_order_nestml__with_iaf_psc_exp_nestml"

    @pytest.fixture(scope="module", autouse=True)
    def setUp(self):
        r"""generate code for neuron and synapse and build NEST user module"""
        files = [os.path.join("models", "neurons", "iaf_psc_exp.nestml"),
                 os.path.join("tests", "nest_tests", "resources", "dopa_synapse_second_order.nestml")]
        input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, s))) for s in files]
        generate_nest_target(input_path=input_path,
                             logging_level="DEBUG",
                             module_name="nestmlmodule",
                             suffix="_nestml",
                             codegen_opts={"neuron_parent_class": "StructuralPlasticityNode",
                                           "neuron_parent_class_include": "structural_plasticity_node.h",
                                           "neuron_synapse_pairs": [{"neuron": "iaf_psc_exp",
                                                                     "synapse": "dopa_synapse_second_order",
                                                                     "vt_ports": ["dopa_spikes"]}]})

    @pytest.mark.skipif(NESTTools.detect_nest_version().startswith("v2"),
                        reason="This test does not support NEST 2")
    def test_nest_stdp_synapse(self):

        resolution = .1   # [ms]

        nest.ResetKernel()
        nest.SetKernelStatus({"resolution": resolution})
        nest.Install("nestmlmodule")

        # create spike_generators with these times
        pre_sg = nest.Create("poisson_generator",
                             params={"rate": 10.})
        vt_sg = nest.Create("poisson_generator",
                            params={"rate": 20.})

        # create volume transmitter
        vt = nest.Create("volume_transmitter")
        vt_parrot = nest.Create("parrot_neuron")
        nest.Connect(vt_sg, vt_parrot)
        nest.Connect(vt_parrot, vt, syn_spec={"synapse_model": "static_synapse",
                                              "weight": 1.,
                                              "delay": 1.})   # delay is ignored!
        vt_gid = vt.get("global_id")

        # set up custom synapse model
        wr = nest.Create("weight_recorder")
        wr_ref = nest.Create('weight_recorder')
        nest.CopyModel(synapse_model_name, "stdp_nestml_rec",
                       {"weight_recorder": wr[0], "w": 1., "d": delay, "receptor_type": 0,
                        "vt": vt_gid})

        # create parrot neurons and connect spike_generators
        pre_neuron = nest.Create("parrot_neuron")
        post_neuron = nest.Create(neuron_model_name)

        spikedet_pre = nest.Create("spike_recorder")
        spikedet_post = nest.Create("spike_recorder")
        spikedet_vt = nest.Create("spike_recorder")
