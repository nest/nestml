#
# nest_codegenerator_preparation_test.py
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

from pynestml.meta_model.ast_source_location import ASTSourceLocation

from pynestml.codegeneration.nest_codegenerator import NESTCodeGenerator
from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.symbol_table.symbol_table import SymbolTable
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.symbols.predefined_types import PredefinedTypes
from pynestml.symbols.predefined_units import PredefinedUnits
from pynestml.symbols.predefined_variables import PredefinedVariables
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.model_parser import ModelParser


class CodeGeneratorPreparationTest(unittest.TestCase):
    """
    Tests preparing code generation (no actual generated code written to file)
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

    def test_model_preparation(self):
        input_path = str(os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, 'models', 'iaf_psc_alpha.nestml'))))
        compilation_unit = ModelParser.parse_model(input_path)
        assert len(compilation_unit.get_neuron_list()) == 1
        ast_neuron = compilation_unit.get_neuron_list()[0]
        equations_block = ast_neuron.get_equations_block()
        # the idea here is to go through the rhs, print expressions, use the same mechanism as before, and reread them
        # again
        # TODO: add tests for this function
        # this function changes stuff inplace
        nestCodeGenerator = NESTCodeGenerator()
        nestCodeGenerator.make_functions_self_contained(equations_block.get_ode_functions())

        nestCodeGenerator.replace_functions_through_defining_expressions(equations_block.get_ode_equations(),
                                                       equations_block.get_ode_functions())

        json_representation = nestCodeGenerator.transform_ode_and_shapes_to_json(equations_block)
        self.assertTrue("convolve(I_shape_in, in_spikes)" in json_representation["odes"][0]["definition"])
        self.assertTrue("convolve(I_shape_ex, ex_spikes)" in json_representation["odes"][0]["definition"])

    def test_solve_odes_and_shapes(self):
        input_path = str(os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, 'models', 'iaf_psc_alpha.nestml'))))
        compilation_unit = ModelParser.parse_model(input_path)
        assert len(compilation_unit.get_neuron_list()) == 1
        ast_neuron = compilation_unit.get_neuron_list()[0]

        nestCodeGenerator = NESTCodeGenerator()
        ast_neuron = nestCodeGenerator.transform_shapes_and_odes(ast_neuron, {})

