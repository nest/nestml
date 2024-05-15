# -*- coding: utf-8 -*-
#
# nest_resolution_builtin_test.py
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


class NestResolutionBuiltinTest(unittest.TestCase):
    """Check that the ``resolution()`` function returns a meaningful result in all contexts where it is can appear"""

    def setUp(self):
        """Generate the model code"""
        # generate the "jit" model (co-generated neuron and synapse), that does not rely on ArchivingNode
        input_files = [os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources", "iaf_psc_exp_resolution_test.nestml"))),
                       os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir, "valid", "CoCoResolutionLegallyUsed.nestml")))]
        generate_nest_target(input_path=input_files,
                             target_path="target",
                             logging_level="INFO",
                             module_name="nestmlmodule",
                             suffix="_nestml",
                             codegen_opts={"neuron_parent_class": "StructuralPlasticityNode",
                                           "neuron_parent_class_include": "structural_plasticity_node.h",
                                           "neuron_synapse_pairs": [{"neuron": "iaf_psc_exp_resolution_test_neuron",
                                                                     "synapse": "resolution_legally_used_synapse"}]})

    @pytest.mark.skipif(NESTTools.detect_nest_version().startswith("v2"),
                        reason="This test does not support NEST 2")
    def test_resolution_function(self):
        nest.set_verbosity("M_ALL")
        nest.ResetKernel()
        nest.Install("nestmlmodule")
        models = nest.Models(mtype="nodes")
        neuron_models = [m for m in models if str(nest.GetDefaults(m, "element_type")) == "neuron"]
        print(neuron_models)
        pre = nest.Create("iaf_psc_exp", 100)
        post = nest.Create("iaf_psc_exp_resolution_test_neuron_nestml__with_resolution_legally_used_synapse_nestml")
        nest.Connect(pre, post, "all_to_all",
                     syn_spec={'synapse_model': "resolution_legally_used_synapse_nestml__with_iaf_psc_exp_resolution_test_neuron_nestml"})
        nest.Simulate(100.0)
