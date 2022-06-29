# -*- coding: utf-8 -*-
#
# nest_install_module_in_different_location_test.py
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

import glob
import nest
import os
import tempfile
import unittest

from pynestml.frontend.pynestml_frontend import generate_nest_target


class NestInstallExistingModule(unittest.TestCase):
    """
    Tests installing modules from different location
    """

    def test_installing_module_outside_nest(self):

        model_name = "iaf_psc_exp"
        module_name = f"{model_name}module"

        input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, "models", "neurons", f"{model_name}.nestml"))))
        install_path = tempfile.mkdtemp(prefix="nest_install", suffix="")
        target_path = "target"
        logging_level = "INFO"
        store_log = False
        suffix = "_location_test"
        dev = True
        codegen_opts = {"templates": {
            "path": "point_neuron",
            "model_templates": {
                "neuron": ["@NEURON_NAME@.cpp.jinja2", "@NEURON_NAME@.h.jinja2"],
                "synapse": ["@SYNAPSE_NAME@.h.jinja2"]
            },
            "module_templates": ["setup/CMakeLists.txt.jinja2",
                                 "setup/@MODULE_NAME@.h.jinja2", "setup/@MODULE_NAME@.cpp.jinja2"]
        }}

        generate_nest_target(input_path,
                             target_path=target_path,
                             logging_level=logging_level,
                             module_name=module_name,
                             store_log=store_log,
                             suffix=suffix,
                             install_path=install_path,
                             dev=dev,
                             codegen_opts=codegen_opts)

        expected_found_module = f"{install_path}/{module_name}.so"
        actual_found_module = glob.glob(f"{install_path}/*so")

        # check if tmp folder contains only one module
        self.assertEqual(len(actual_found_module), 1)
        # compare the expected module name with the actual found one
        self.assertEqual(actual_found_module[0], expected_found_module)

        # install module
        nest.set_verbosity("M_ALL")
        nest.ResetKernel()
        nest.Install(module_name)

        # check model existence
        has_model = f"{model_name}{suffix}" in nest.Models()
        self.assertTrue(has_model)

        # delete created folder
        import shutil
        shutil.rmtree(install_path)
