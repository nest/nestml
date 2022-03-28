# -*- coding: utf-8 -*-
#
# nest2_compat_test.py
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
import pytest
import unittest

import nest

from pynestml.frontend.pynestml_frontend import generate_target


@pytest.mark.skipif(os.environ.get("NEST_VERSION_MAJOR") != "2",
                    reason="Should be run with NEST 2.20.*")
class Nest2CompatTest(unittest.TestCase):
    """
    Tests the code generation and installation with custom NESTML templates for NEST
    """

    def test_custom_templates(self):
        input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, "models", "neurons", "iaf_psc_exp.nestml"))))
        target_path = "target"
        target_platform = "NEST2"
        logging_level = "INFO"
        module_name = "nestmlmodule"
        suffix = "_nestml"

        codegen_opts = {
            "neuron_parent_class_include": "archiving_node.h",
            "neuron_parent_class": "Archiving_Node",
            "templates": {
                "path": os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "pynestml", "codegeneration",
                                     "resources_nest", "point_neuron_nest2"),
                "model_templates": {
                    "neuron": ["NeuronClass.cpp.jinja2", "NeuronHeader.h.jinja2"],
                    "synapse": ["SynapseHeader.h.jinja2"]
                },
                "module_templates": ["setup/CMakeLists.txt.jinja2", "setup/ModuleHeader.h.jinja2",
                                     "setup/ModuleClass.cpp.jinja2"]}}

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
        nest.SetStatus(mm, {"record_from": ["V_m"]})

        nest.Connect(mm, nrn)

        nest.Simulate(5.0)
