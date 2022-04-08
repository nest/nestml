# -*- coding: utf-8 -*-
#
# nest_custom_templates_test.py
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
import unittest

import nest

from pynestml.frontend.pynestml_frontend import generate_target


class NestCustomTemplatesTest(unittest.TestCase):
    """
    Tests the code generation and installation with custom NESTML templates for NEST
    """

    def test_custom_templates(self):
        input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, "models", "neurons", "iaf_psc_exp.nestml"))))
        target_path = "target"
        target_platform = "NEST"
        logging_level = "INFO"
        module_name = "nestmlmodule"
        suffix = "_nestml"

        codegen_opts = {"templates": {"path": "point_neuron",
                                      "model_templates": {"neuron": ["@NEURON_NAME@.cpp.jinja2", "@NEURON_NAME@.h.jinja2"],
                                                          "synapse": ["@SYNAPSE_NAME@.h.jinja2"]},
                                      "module_templates": ["setup/CMakeLists.txt.jinja2",
                                                           "setup/@MODULE_NAME@.h.jinja2", "setup/@MODULE_NAME@.cpp.jinja2"]}}

        generate_target(input_path, target_platform, target_path,
                        logging_level=logging_level,
                        module_name=module_name,
                        suffix=suffix,
                        codegen_opts=codegen_opts)
        nest.set_verbosity("M_ALL")

        nest.ResetKernel()
        nest.Install("nestmlmodule")

        nrn = nest.Create("iaf_psc_exp_nestml")
        mm = nest.Create("multimeter")
        mm.set({"record_from": ["V_m"]})

        nest.Connect(mm, nrn)

        nest.Simulate(5.0)

    def test_custom_templates_with_synapse(self):
        models = ["neurons/iaf_psc_delta.nestml", "synapses/stdp_triplet_naive.nestml"]
        input_paths = [os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, "models", fn)))) for fn in models]
        target_path = "target"
        target_platform = "NEST"
        logging_level = "INFO"
        module_name = "nestmlmodule"
        suffix = "_nestml"

        codegen_opts = {
            "neuron_parent_class": "StructuralPlasticityNode",
            "neuron_parent_class_include": "structural_plasticity_node.h",
            "neuron_synapse_pairs": [{"neuron": "iaf_psc_delta",
                                      "synapse": "stdp_triplet",
                                      "post_ports": ["post_spikes"]}],
            "templates": {
                "path": "point_neuron",
                "model_templates": {
                    "neuron": ["@NEURON_NAME@.cpp.jinja2", "@NEURON_NAME@.h.jinja2"],
                    "synapse": ["@SYNAPSE_NAME@.h.jinja2"]
                },
                "module_templates": ["setup/CMakeLists.txt.jinja2",
                                     "setup/@MODULE_NAME@.h.jinja2", "setup/@MODULE_NAME@.cpp.jinja2"]
            }
        }

        neuron_model_name = "iaf_psc_delta_nestml__with_stdp_triplet_nestml"
        synapse_model_name = "stdp_triplet_nestml__with_iaf_psc_delta_nestml"

        generate_target(input_paths, target_platform, target_path,
                        logging_level=logging_level,
                        module_name=module_name,
                        suffix=suffix,
                        codegen_opts=codegen_opts)
        nest.set_verbosity("M_ALL")
