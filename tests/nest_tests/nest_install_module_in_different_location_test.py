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

import os
import unittest

from pynestml.frontend.pynestml_frontend import to_nest, install_nest, add_libraries_to_sli
import tempfile
import glob
import nest


class NestInstallExistingModule(unittest.TestCase):
    """
    Tests installing modules from different location
    """

    def test_installing_module_outside_nest(self):

        model_name = "iaf_psc_exp"
        module_name = f'{model_name}module'

        input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, "models", "neurons", f"{model_name}.nestml"))))
        nest_path = nest.ll_api.sli_func("statusdict/prefix ::")
        install_dir = tempfile.mkdtemp(prefix="nest_install", suffix="")
        target_path = 'target'

        logging_level = 'INFO'
        store_log = False
        suffix = '_location_test'
        dev = True
        codegen_opts = {"templates": {
            "path": 'point_neuron',
            "model_templates": {
                "neuron": ['NeuronClass.cpp.jinja2', 'NeuronHeader.h.jinja2'],
                "synapse": ['SynapseHeader.h.jinja2']
            },
            "module_templates": ['setup/CMakeLists.txt.jinja2',
                                 'setup/ModuleHeader.h.jinja2', 'setup/ModuleClass.cpp.jinja2']
        }}

        to_nest(input_path, target_path, logging_level, module_name, store_log, suffix, dev, codegen_opts)
        install_nest(target_path, nest_path, install_dir)

        expected_found_module = f"{install_dir}/{module_name}.so"
        actual_found_module = glob.glob(f"{install_dir}/*so")

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
        

        # delete create folder
        import shutil
        shutil.rmtree(install_dir)
