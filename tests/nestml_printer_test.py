# -*- coding: utf-8 -*-
#
# nestml_printer_test.py
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

import unittest

from pynestml.codegeneration.printers.nestml_printer import NESTMLPrinter
from pynestml.symbol_table.symbol_table import SymbolTable
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.symbols.predefined_types import PredefinedTypes
from pynestml.symbols.predefined_units import PredefinedUnits
from pynestml.symbols.predefined_variables import PredefinedVariables
from pynestml.utils.ast_source_location import ASTSourceLocation
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.model_parser import ModelParser


class NestMLPrinterTest(unittest.TestCase):
    """
    Tests if NESTMLPrinter works as intended.
    """

    def setUp(self):
        # setups the infrastructure
        PredefinedUnits.register_units()
        PredefinedTypes.register_types()
        PredefinedFunctions.register_functions()
        PredefinedVariables.register_variables()
        SymbolTable.initialize_symbol_table(ASTSourceLocation(start_line=0, start_column=0, end_line=0, end_column=0))
        Logger.init_logger(LoggingLevel.INFO)

    def test_block_with_variables_with_comments(self):
        block = '# pre1\n' \
                '# pre2\n' \
                'state: # in\n' \
                'end\n' \
                '# post1\n' \
                '# post2\n\n'
        model = ModelParser.parse_block_with_variables(block)
        model_printer = NESTMLPrinter()
        self.assertEqual(block, model_printer.print_node(model))

    def test_block_with_variables_without_comments(self):
        block = 'state:\n' \
                'end'
        model = ModelParser.parse_block_with_variables(block)
        model_printer = NESTMLPrinter()
        self.assertEqual(block, model_printer.print_node(model))

    def test_assignment_with_comments(self):
        assignment = '  # pre\n' \
                     '  a = b # in\n' \
                     '  # post\n' \
                     '\n'
        model = ModelParser.parse_block(assignment)
        model_printer = NESTMLPrinter()
        self.assertEqual(assignment, model_printer.print_node(model))

    def test_assignment_without_comments(self):
        assignment = 'a = b\n'
        model = ModelParser.parse_assignment(assignment)
        model_printer = NESTMLPrinter()
        self.assertEqual(assignment, model_printer.print_node(model))

    def test_function_with_comments(self):
        t_function = '# pre func\n' \
                     'function test(Tau_1 ms) real: # in func\n' \
                     '  # decl pre\n' \
                     '  exact_integration_adjustment real = ((1 / Tau_2) - (1 / Tau_1)) * ms # decl in\n' \
                     '  # decl post\n' \
                     '\n' \
                     '  return normalisation_factor\n' \
                     'end\n' \
                     '# post func\n\n'
        model = ModelParser.parse_function(t_function)
        model_printer = NESTMLPrinter()
        self.assertEqual(t_function, model_printer.print_node(model))

    def test_function_without_comments(self):
        t_function = 'function test(Tau_1 ms) real:\n' \
                     '  exact_integration_adjustment real = ((1 / Tau_2) - (1 / Tau_1)) * ms\n' \
                     '  return normalisation_factor\n' \
                     'end\n'
        model = ModelParser.parse_function(t_function)
        model_printer = NESTMLPrinter()
        self.assertEqual(t_function, model_printer.print_node(model))

    def test_function_call_with_comments(self):
        function_call = '  # pre\n' \
                        '  min(1,2) # in\n' \
                        '  # post\n\n'
        model = ModelParser.parse_block(function_call)
        model_printer = NESTMLPrinter()
        self.assertEqual(function_call, model_printer.print_node(model))

    def test_function_call_without_comments(self):
        function_call = 'min(1,2)\n'
        model = ModelParser.parse_stmt(function_call)
        model_printer = NESTMLPrinter()
        self.assertEqual(function_call, model_printer.print_node(model))

    def test_neuron_with_comments(self):
        neuron = '# pre\n' \
                 'neuron test: # in\n' \
                 'end\n' \
                 '# post\n\n'
        model = ModelParser.parse_nestml_compilation_unit(neuron)
        model_printer = NESTMLPrinter()
        self.assertEqual(neuron, model_printer.print_node(model))

    def test_neuron_with_comments(self):
        neuron = '# pre\n' \
                 'neuron test: # in\n' \
                 'end\n' \
                 '# post\n\n'
        model = ModelParser.parse_nestml_compilation_unit(neuron)
        model_printer = NESTMLPrinter()
        self.assertEqual(neuron, model_printer.print_node(model))

    def test_neuron_with_docstring(self):
        neuron = '"""hello, world\n' \
                 '\n' \
                 '3.141592653589793"""\n' \
                 'neuron test:\n' \
                 'end\n'
        model = ModelParser.parse_neuron(neuron)
        model_printer = NESTMLPrinter()
        self.assertEqual(neuron, model_printer.print_node(model))

    def test_declaration_with_comments(self):
        declaration = '  # pre\n' \
                      '  test mV = 10mV # in\n' \
                      '  # post\n\n'
        model = ModelParser.parse_block(declaration)
        model_printer = NESTMLPrinter()
        self.assertEqual(declaration, model_printer.print_node(model))

    def test_declaration_without_comments(self):
        declaration = 'test mV = 10mV\n'
        model = ModelParser.parse_declaration(declaration)
        model_printer = NESTMLPrinter()
        self.assertEqual(declaration, model_printer.print_node(model))

    def test_equations_block_with_comments(self):
        block = '# pre\n' \
                'equations: # in\n' \
                'end\n' \
                '# post\n\n'
        model = ModelParser.parse_equations_block(block)
        model_printer = NESTMLPrinter()
        self.assertEqual(block, model_printer.print_node(model))

    def test_equations_block_without_comments(self):
        block = 'equations:\n' \
                'end\n'
        model = ModelParser.parse_equations_block(block)
        model_printer = NESTMLPrinter()
        self.assertEqual(block, model_printer.print_node(model))

    def test_for_stmt_with_comments(self):
        stmt = '  # pre\n' \
               '  for i in 10 - 3.14...10 + 3.14 step -1: # in\n' \
               '  end\n' \
               '  # post\n\n'
        model = ModelParser.parse_block(stmt)
        model_printer = NESTMLPrinter()
        self.assertEqual(stmt, model_printer.print_node(model))

    def test_for_stmt_without_comments(self):
        stmt = 'for i in 10 - 3.14...10 + 3.14 step -1: # in\n' \
               'end\n'
        model = ModelParser.parse_for_stmt(stmt)
        model_printer = NESTMLPrinter()
        self.assertEqual(stmt, model_printer.print_node(model))

    def test_while_stmt_with_comments(self):
        stmt = '  # pre\n' \
               '  while true: # in \n' \
               '  end\n' \
               '  # post\n\n'
        model = ModelParser.parse_block(stmt)
        model_printer = NESTMLPrinter()
        self.assertEqual(stmt, model_printer.print_node(model))

    def test_while_stmt_without_comments(self):
        stmt = 'while true:\n' \
               'end\n'
        model = ModelParser.parse_while_stmt(stmt)
        model_printer = NESTMLPrinter()
        self.assertEqual(stmt, model_printer.print_node(model))

    def test_update_block_with_comments(self):
        block = '# pre\n' \
                'update: # in\n' \
                'end\n' \
                '# post\n\n'
        model = ModelParser.parse_update_block(block)
        model_printer = NESTMLPrinter()
        self.assertEqual(block, model_printer.print_node(model))

    def test_update_block_without_comments(self):
        block = 'update:\n' \
                'end\n'
        model = ModelParser.parse_update_block(block)
        model_printer = NESTMLPrinter()
        self.assertEqual(block, model_printer.print_node(model))

    def test_variable(self):
        var = 'V_m'
        model = ModelParser.parse_variable(var)
        model_printer = NESTMLPrinter()
        self.assertEqual(var, model_printer.print_node(model))

    def test_unit_type(self):
        unit = '1/(mV*kg**2)'
        model = ModelParser.parse_unit_type(unit)
        model_printer = NESTMLPrinter()
        self.assertEqual(unit, model_printer.print_node(model))

    def test_unary_operator(self):
        ops = {'-', '+', '~'}
        for op in ops:
            model = ModelParser.parse_unary_operator(op)
            model_printer = NESTMLPrinter()
            self.assertEqual(op, model_printer.print_node(model))
