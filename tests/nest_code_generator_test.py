# -*- coding: utf-8 -*-
#
# nest_code_generator_test.py
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

import json
import os
import unittest
import json

from pynestml.utils.ast_source_location import ASTSourceLocation

from pynestml.codegeneration.nest_code_generator import NESTCodeGenerator
from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.symbol_table.symbol_table import SymbolTable
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.symbols.predefined_types import PredefinedTypes
from pynestml.symbols.predefined_units import PredefinedUnits
from pynestml.symbols.predefined_variables import PredefinedVariables
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.model_parser import ModelParser


class CodeGeneratorTest(unittest.TestCase):
    """
    Tests code generator with an IAF psc and cond model, both with alpha and delta synaptic kernels
    """

    def setUp(self):
        PredefinedUnits.register_units()
        PredefinedTypes.register_types()
        PredefinedFunctions.register_functions()
        PredefinedVariables.register_variables()
        SymbolTable.initialize_symbol_table(ASTSourceLocation(start_line=0, start_column=0, end_line=0, end_column=0))
        Logger.init_logger(LoggingLevel.INFO)

        self.target_path = str(os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, 'target'))))

    def test_iaf_psc_alpha(self):
        input_path = str(os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, 'models', 'neurons', 'iaf_psc_alpha.nestml'))))

        params = list()
        params.append('--input_path')
        params.append(input_path)
        params.append('--logging_level')
        params.append('INFO')
        params.append('--target_path')
        params.append(self.target_path)
        params.append('--dev')
        FrontendConfiguration.parse_config(params)

        compilation_unit = ModelParser.parse_model(input_path)

        nestCodeGenerator = NESTCodeGenerator()
        nestCodeGenerator.generate_code(compilation_unit.get_neuron_list(), compilation_unit.get_synapse_list())

    def test_iaf_psc_delta(self):
        input_path = str(os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, 'models', 'neurons', 'iaf_psc_delta.nestml'))))

        params = list()
        params.append('--input_path')
        params.append(input_path)
        params.append('--logging_level')
        params.append('INFO')
        params.append('--target_path')
        params.append(self.target_path)
        params.append('--dev')
        FrontendConfiguration.parse_config(params)

        compilation_unit = ModelParser.parse_model(input_path)

        nestCodeGenerator = NESTCodeGenerator()
        nestCodeGenerator.generate_code(compilation_unit.get_neuron_list(), compilation_unit.get_synapse_list())

    def test_iaf_cond_alpha_functional(self):
        input_path = str(os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, 'models', 'neurons', 'iaf_cond_alpha.nestml'))))

        params = list()
        params.append('--input_path')
        params.append(input_path)
        params.append('--logging_level')
        params.append('INFO')
        params.append('--target_path')
        params.append(self.target_path)
        params.append('--dev')
        FrontendConfiguration.parse_config(params)

        compilation_unit = ModelParser.parse_model(input_path)
        iaf_cond_alpha_functional = list()
        iaf_cond_alpha_functional.append(compilation_unit.get_neuron_list()[0])

        nestCodeGenerator = NESTCodeGenerator()
        nestCodeGenerator.generate_code(iaf_cond_alpha_functional, [])

    def test_iaf_psc_alpha_with_codegen_opts(self):
        input_path = str(os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, 'models', 'neurons', 'iaf_psc_alpha.nestml'))))

        code_opts_path = str(os.path.realpath(os.path.join(os.path.dirname(__file__),
                                                           os.path.join('resources', 'code_options.json'))))
        codegen_opts = {"templates": {
            "path": "point_neuron",
            "model_templates": {
                "neuron": ['@NEURON_NAME@.cpp.jinja2', '@NEURON_NAME@.h.jinja2'],
                "synapse": []
            },
            "module_templates": ['setup/CMakeLists.txt.jinja2',
                                 'setup/@MODULE_NAME@.h.jinja2', 'setup/@MODULE_NAME@.cpp.jinja2']
        }}

        with open(code_opts_path, 'w+') as f:
            json.dump(codegen_opts, f)

        params = list()
        params.append('--input_path')
        params.append(input_path)
        params.append('--logging_level')
        params.append('INFO')
        params.append('--target_path')
        params.append(self.target_path)
        params.append('--dev')
        params.append('--codegen_opts')
        params.append(code_opts_path)
        FrontendConfiguration.parse_config(params)

        compilation_unit = ModelParser.parse_model(input_path)

        nestCodeGenerator = NESTCodeGenerator(codegen_opts)
        nestCodeGenerator.generate_code(compilation_unit.get_neuron_list(), list())

    def test_iaf_psc_alpha_with_codegen_opts(self):
        input_path = str(os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, 'models', 'neurons', 'iaf_psc_alpha.nestml'))))

        code_opts_path = str(os.path.realpath(os.path.join(os.path.dirname(__file__),
                                                           os.path.join('resources', 'code_options.json'))))
        codegen_opts = {"templates": {
            "path": "point_neuron",
            "model_templates": {"neuron": ['@NEURON_NAME@.cpp.jinja2', '@NEURON_NAME@.h.jinja2']},
            "module_templates": ['setup/CMakeLists.txt.jinja2',
                                 'setup/@MODULE_NAME@.h.jinja2', 'setup/@MODULE_NAME@.cpp.jinja2']
        }}

        with open(code_opts_path, 'w+') as f:
            json.dump(codegen_opts, f)

        params = list()
        params.append('--input_path')
        params.append(input_path)
        params.append('--logging_level')
        params.append('INFO')
        params.append('--target_path')
        params.append(self.target_path)
        params.append('--dev')
        params.append('--codegen_opts')
        params.append(code_opts_path)
        FrontendConfiguration.parse_config(params)

        compilation_unit = ModelParser.parse_model(input_path)

        nestCodeGenerator = NESTCodeGenerator(codegen_opts)
        nestCodeGenerator.generate_code(compilation_unit.get_neuron_list())

    def tearDown(self):
        import shutil
        shutil.rmtree(self.target_path)
