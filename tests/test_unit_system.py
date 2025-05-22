# -*- coding: utf-8 -*-
#
# test_unit_system.py
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

from pynestml.codegeneration.printers.constant_printer import ConstantPrinter
from pynestml.codegeneration.printers.cpp_expression_printer import CppExpressionPrinter
from pynestml.codegeneration.printers.cpp_simple_expression_printer import CppSimpleExpressionPrinter
from pynestml.codegeneration.printers.cpp_type_symbol_printer import CppTypeSymbolPrinter
from pynestml.codegeneration.printers.cpp_variable_printer import CppVariablePrinter
from pynestml.codegeneration.printers.nest_cpp_function_call_printer import NESTCppFunctionCallPrinter
from pynestml.codegeneration.printers.nestml_variable_printer import NESTMLVariablePrinter
from pynestml.frontend.pynestml_frontend import generate_target
from pynestml.symbol_table.symbol_table import SymbolTable
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.symbols.predefined_types import PredefinedTypes
from pynestml.symbols.predefined_units import PredefinedUnits
from pynestml.symbols.predefined_variables import PredefinedVariables
from pynestml.utils.ast_source_location import ASTSourceLocation
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.model_parser import ModelParser


class TestUnitSystem:
    r"""
    Test class for units system.
    """

    @pytest.fixture(scope="class", autouse=True)
    def setUp(self, request):
        Logger.set_logging_level(LoggingLevel.INFO)

        SymbolTable.initialize_symbol_table(ASTSourceLocation(start_line=0, start_column=0, end_line=0, end_column=0))

        PredefinedUnits.register_units()
        PredefinedTypes.register_types()
        PredefinedVariables.register_variables()
        PredefinedFunctions.register_functions()

        Logger.init_logger(LoggingLevel.INFO)

        variable_printer = NESTMLVariablePrinter(None)
        function_call_printer = NESTCppFunctionCallPrinter(None)
        cpp_variable_printer = CppVariablePrinter(None)
        self.printer = CppExpressionPrinter(CppSimpleExpressionPrinter(cpp_variable_printer,
                                                                       ConstantPrinter(),
                                                                       function_call_printer))
        cpp_variable_printer._expression_printer = self.printer
        variable_printer._expression_printer = self.printer
        function_call_printer._expression_printer = self.printer

        request.cls.printer = self.printer

    def get_first_statement_in_update_block(self, model):
        if model.get_model_list()[0].get_update_blocks()[0]:
            return model.get_model_list()[0].get_update_blocks()[0].get_stmts_body().get_stmts()[0]

        return None

    def get_first_declaration_in_state_block(self, model):
        assert len(model.get_model_list()[0].get_state_blocks()) == 1

        return model.get_model_list()[0].get_state_blocks()[0].get_declarations()[0]

    def get_first_declared_function(self, model):
        return model.get_model_list()[0].get_functions()[0]

    def print_rhs_of_first_assignment_in_update_block(self, model):
        assignment = self.get_first_statement_in_update_block(model).small_stmt.get_assignment()
        expression = assignment.get_expression()

        return self.printer.print(expression)

    def print_first_function_call_in_update_block(self, model):
        function_call = self.get_first_statement_in_update_block(model).small_stmt.get_function_call()

        return self.printer.print(function_call)

    def print_rhs_of_first_declaration_in_state_block(self, model):
        declaration = self.get_first_declaration_in_state_block(model)
        expression = declaration.get_expression()

        return self.printer.print(expression)

    def print_first_return_statement_in_first_declared_function(self, model):
        func = self.get_first_declared_function(model)
        return_expression = func.get_stmts_body().get_stmts()[0].small_stmt.get_return_stmt().get_expression()
        return self.printer.print(return_expression)

    def test_expression_after_magnitude_conversion_in_direct_assignment(self):
        model = ModelParser.parse_file(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'resources')), 'DirectAssignmentWithDifferentButCompatibleUnits.nestml'))
        printed_rhs_expression = self.print_rhs_of_first_assignment_in_update_block(model)

        assert printed_rhs_expression == '(1000.0 * (10 * V))'

    def test_expression_after_nested_magnitude_conversion_in_direct_assignment(self):
        model = ModelParser.parse_file(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'resources')), 'DirectAssignmentWithDifferentButCompatibleNestedUnits.nestml'))
        printed_rhs_expression = self.print_rhs_of_first_assignment_in_update_block(model)

        assert printed_rhs_expression == '(1000.0 * (10 * V + (0.001 * (5 * mV)) + 20 * V + (1000.0 * (1 * kV))))'

    def test_expression_after_magnitude_conversion_in_compound_assignment(self):
        model = ModelParser.parse_file(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'resources')), 'CompoundAssignmentWithDifferentButCompatibleUnits.nestml'))
        printed_rhs_expression = self.print_rhs_of_first_assignment_in_update_block(model)

        assert printed_rhs_expression == '(0.001 * (1200 * mV))'

    def test_expression_after_magnitude_conversion_in_declaration(self):
        model = ModelParser.parse_file(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'resources')), 'DeclarationWithDifferentButCompatibleUnitMagnitude.nestml'))
        printed_rhs_expression = self.print_rhs_of_first_declaration_in_state_block(model)

        assert printed_rhs_expression == '(1000.0 * (10 * V))'

    def test_expression_after_type_conversion_in_declaration(self):
        model = ModelParser.parse_file(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'resources')), 'DeclarationWithDifferentButCompatibleUnits.nestml'))
        declaration = self.get_first_declaration_in_state_block(model)
        from astropy import units as u

        assert declaration.get_expression().type.unit.unit == u.mV

    def test_declaration_with_same_variable_name_as_unit(self):
        Logger.init_logger(LoggingLevel.DEBUG)

        generate_target(input_path=os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'resources')), 'DeclarationWithSameVariableNameAsUnit.nestml'), target_platform="NONE", logging_level="DEBUG")

        assert len(Logger.get_all_messages_of_level_and_or_node("BlockTest", LoggingLevel.ERROR)) == 0
        assert len(Logger.get_all_messages_of_level_and_or_node("BlockTest", LoggingLevel.WARNING)) == 3

    def test_expression_after_magnitude_conversion_in_standalone_function_call(self):
        model = ModelParser.parse_file(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'resources')), 'FunctionCallWithDifferentButCompatibleUnits.nestml'))
        printed_function_call = self.print_first_function_call_in_update_block(model)

        assert printed_function_call == 'foo((1000.0 * (10 * V)))'

    def test_expression_after_magnitude_conversion_in_rhs_function_call(self):
        model = ModelParser.parse_file(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'resources')), 'RhsFunctionCallWithDifferentButCompatibleUnits.nestml'))
        printed_function_call = self.print_rhs_of_first_assignment_in_update_block(model)

        assert printed_function_call == 'foo((1000.0 * (10 * V)))'

    def test_return_stmt_after_magnitude_conversion_in_function_body(self):
        model = ModelParser.parse_file(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'resources')), 'FunctionBodyReturnStatementWithDifferentButCompatibleUnits.nestml'))
        printed_return_stmt = self.print_first_return_statement_in_first_declared_function(model)

        assert printed_return_stmt == '(0.001 * (bar))'
