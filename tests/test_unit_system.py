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

import copy
import os
import pickle
import pytest

from pynestml.codegeneration.printers.constant_printer import ConstantPrinter
from pynestml.codegeneration.printers.cpp_expression_printer import CppExpressionPrinter
from pynestml.codegeneration.printers.cpp_printer import CppPrinter
from pynestml.codegeneration.printers.cpp_simple_expression_printer import CppSimpleExpressionPrinter
from pynestml.codegeneration.printers.cpp_type_symbol_printer import CppTypeSymbolPrinter
from pynestml.codegeneration.printers.cpp_variable_printer import CppVariablePrinter
from pynestml.codegeneration.printers.nest_cpp_function_call_printer import NESTCppFunctionCallPrinter
from pynestml.codegeneration.printers.nestml_expression_printer import NESTMLExpressionPrinter
from pynestml.codegeneration.printers.nestml_function_call_printer import NESTMLFunctionCallPrinter
from pynestml.codegeneration.printers.nestml_simple_expression_printer import NESTMLSimpleExpressionPrinter
from pynestml.codegeneration.printers.nestml_variable_printer import NESTMLVariablePrinter
from pynestml.codegeneration.printers.python_expression_printer import PythonExpressionPrinter
from pynestml.codegeneration.printers.python_function_call_printer import PythonFunctionCallPrinter
from pynestml.codegeneration.printers.python_simple_expression_printer import PythonSimpleExpressionPrinter
from pynestml.codegeneration.printers.python_variable_printer import PythonVariablePrinter
from pynestml.frontend.pynestml_frontend import generate_target
from pynestml.symbol_table.symbol_table import SymbolTable
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.symbols.predefined_types import PredefinedTypes
from pynestml.symbols.predefined_units import PredefinedUnits
from pynestml.symbols.predefined_variables import PredefinedVariables
from pynestml.utils.ast_source_location import ASTSourceLocation
from pynestml.utils.ast_utils import ASTUtils
from pynestml.utils.implicit_conversion_factor import ImplicitConversionFactor
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
        self.printer = NESTMLExpressionPrinter(NESTMLSimpleExpressionPrinter(cpp_variable_printer,
                                                                             ConstantPrinter(),
                                                                             function_call_printer))
        cpp_variable_printer._expression_printer = self.printer
        variable_printer._expression_printer = self.printer
        function_call_printer._expression_printer = self.printer

        request.cls.printer = self.printer

        # printers for generated C++ and Python code, which hold numeric literals in NEST units
        cpp_printer_variable_printer = CppVariablePrinter(None)
        cpp_printer_function_call_printer = NESTCppFunctionCallPrinter(None)
        self.cpp_printer = CppExpressionPrinter(CppSimpleExpressionPrinter(cpp_printer_variable_printer,
                                                                           ConstantPrinter(),
                                                                           cpp_printer_function_call_printer))
        cpp_printer_variable_printer._expression_printer = self.cpp_printer
        cpp_printer_function_call_printer._expression_printer = self.cpp_printer

        python_printer_variable_printer = PythonVariablePrinter(None, with_origin=False)
        python_printer_function_call_printer = PythonFunctionCallPrinter(None)
        self.python_printer = PythonExpressionPrinter(PythonSimpleExpressionPrinter(python_printer_variable_printer,
                                                                                    ConstantPrinter(),
                                                                                    python_printer_function_call_printer))
        python_printer_variable_printer._expression_printer = self.python_printer
        python_printer_function_call_printer._expression_printer = self.python_printer

        request.cls.cpp_printer = self.cpp_printer
        request.cls.python_printer = self.python_printer

    def get_first_statement_in_update_block(self, model):
        if model.get_model_list()[0].get_update_blocks()[0]:
            return model.get_model_list()[0].get_update_blocks()[0].get_stmts_body().get_stmts()[0]

        return None

    def get_first_declaration_in_state_block(self, model):
        assert len(model.get_model_list()[0].get_state_blocks()) == 1

        return model.get_model_list()[0].get_state_blocks()[0].get_declarations()[0]

    def get_first_declared_function(self, model):
        return model.get_model_list()[0].get_functions()[0]

    def print_rhs_of_first_assignment_in_update_block(self, model, printer=None):
        assignment = self.get_first_statement_in_update_block(model).small_stmt.get_assignment()
        expression = assignment.get_expression()

        return (printer or self.printer).print(expression)

    def print_first_function_call_in_update_block(self, model, printer=None):
        function_call = self.get_first_statement_in_update_block(model).small_stmt.get_function_call()

        return (printer or self.printer).print(function_call)

    def print_rhs_of_first_declaration_in_state_block(self, model, printer=None):
        declaration = self.get_first_declaration_in_state_block(model)
        expression = declaration.get_expression()

        return (printer or self.printer).print(expression)

    def print_first_return_statement_in_first_declared_function(self, model, printer=None):
        func = self.get_first_declared_function(model)
        return_expression = func.get_stmts_body().get_stmts()[0].small_stmt.get_return_stmt().get_expression()
        return (printer or self.printer).print(return_expression)

    def test_expression_after_magnitude_conversion_in_direct_assignment(self):
        model = ModelParser.parse_file(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources")), "DirectAssignmentWithDifferentButCompatibleUnits.nestml"))
        printed_rhs_expression = self.print_rhs_of_first_assignment_in_update_block(model)

        assert printed_rhs_expression == "(1000.0 * (10 V))"

    def test_expression_after_nested_magnitude_conversion_in_direct_assignment(self):
        model = ModelParser.parse_file(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources")), "DirectAssignmentWithDifferentButCompatibleNestedUnits.nestml"))
        printed_rhs_expression = self.print_rhs_of_first_assignment_in_update_block(model)

        assert printed_rhs_expression == "(1000.0 * (10 V + 5 mV + 20 V + 1 kV))"

    def test_expression_after_magnitude_conversion_in_compound_assignment(self):
        model = ModelParser.parse_file(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources")), "CompoundAssignmentWithDifferentButCompatibleUnits.nestml"))
        printed_rhs_expression = self.print_rhs_of_first_assignment_in_update_block(model)

        assert printed_rhs_expression == "(0.001 * (1200 mV))"

    def test_expression_after_magnitude_conversion_in_declaration(self):
        model = ModelParser.parse_file(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources")), "DeclarationWithDifferentButCompatibleUnitMagnitude.nestml"))
        printed_rhs_expression = self.print_rhs_of_first_declaration_in_state_block(model)

        assert printed_rhs_expression == "(1000.0 * (10 V))"

    def test_expression_after_type_conversion_in_declaration(self):
        model = ModelParser.parse_file(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources")), "DeclarationWithDifferentButCompatibleUnits.nestml"))
        declaration = self.get_first_declaration_in_state_block(model)
        from astropy import units as u

        assert declaration.get_expression().type.unit.unit == u.mV

    def test_declaration_with_same_variable_name_as_unit(self):
        Logger.init_logger(LoggingLevel.DEBUG)

        generate_target(input_path=os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources")), "DeclarationWithSameVariableNameAsUnit.nestml"), target_platform="NONE", logging_level="DEBUG")

        assert len(Logger.get_messages("BlockTest", LoggingLevel.ERROR)) == 0
        assert len(Logger.get_messages("BlockTest", LoggingLevel.WARNING)) == 3

    def test_expression_after_magnitude_conversion_in_standalone_function_call(self):
        model = ModelParser.parse_file(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources")), "FunctionCallWithDifferentButCompatibleUnits.nestml"))
        printed_function_call = self.print_first_function_call_in_update_block(model)

        assert printed_function_call == "foo((1000.0 * (10 V)))"

    def test_expression_after_magnitude_conversion_in_rhs_function_call(self):
        model = ModelParser.parse_file(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources")), "RhsFunctionCallWithDifferentButCompatibleUnits.nestml"))
        printed_function_call = self.print_rhs_of_first_assignment_in_update_block(model)

        assert printed_function_call == "foo((1000.0 * (10 V)))"

    def test_return_stmt_after_magnitude_conversion_in_function_body(self):
        model = ModelParser.parse_file(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources")), "FunctionBodyReturnStatementWithDifferentButCompatibleUnits.nestml"))
        printed_return_stmt = self.print_first_return_statement_in_first_declared_function(model)

        assert printed_return_stmt == "(0.001 * (bar))"

    @pytest.mark.parametrize("printer_name", ["cpp_printer", "python_printer"])
    @pytest.mark.parametrize("model_file_name, print_function, expected", [
        ("DirectAssignmentWithDifferentButCompatibleUnits.nestml", "print_rhs_of_first_assignment_in_update_block", "10000."),
        ("DirectAssignmentWithDifferentButCompatibleNestedUnits.nestml", "print_rhs_of_first_assignment_in_update_block", "10000. + 5. + 20000. + 1000000."),
        ("CompoundAssignmentWithDifferentButCompatibleUnits.nestml", "print_rhs_of_first_assignment_in_update_block", "(0.001 * (1200.))"),
        ("DeclarationWithDifferentButCompatibleUnitMagnitude.nestml", "print_rhs_of_first_declaration_in_state_block", "10000."),
        ("FunctionCallWithDifferentButCompatibleUnits.nestml", "print_first_function_call_in_update_block", "foo(10000.)"),
        ("RhsFunctionCallWithDifferentButCompatibleUnits.nestml", "print_rhs_of_first_assignment_in_update_block", "foo(10000.)"),
        ("FunctionBodyReturnStatementWithDifferentButCompatibleUnits.nestml", "print_first_return_statement_in_first_declared_function", "(0.001 * (bar))")])
    def test_generated_code_after_magnitude_conversion(self, printer_name, model_file_name, print_function, expected):
        r"""
        Generated C++ and Python code holds a numeric literal in NEST units: for instance, it holds ``10 V`` as ``10000.`` (mV). The factor from V to mV is therefore not printed. The factor is printed if the target is declared in V, because generated code can hold such a variable in V or in mV.
        """
        model = ModelParser.parse_file(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources")), model_file_name))

        assert getattr(self, print_function)(model, getattr(self, printer_name)) == expected

    @pytest.mark.parametrize("statement, expected_cpp, expected_python", [
        ("V_squared", "(((2000.)) * ((2000.)))", "(2000.)**2"),    # (2 V)**2 = 4000000 mV**2
        ("V_root", "pow((4000000.), 0.5)", "(4000000.)**0.5"),    # (4 V**2)**0.5 = 2000 mV
        ("g", "pow((0.05), (-1))", "(0.05)**(-1)"),    # (50 MOhm)**-1 = 20 nS
        ("f", "(1000.0 * (pow((100.), (-1))))", "(1000.0 * ((100.)**(-1)))"),    # (0.1 s)**-1 = 10 Hz; generated code holds 0.1 s as 100. (in ms)
        ("V_param", "(1000.0 * (pow((2000.), p)))", "(1000.0 * ((2000.)**p))"),    # known limitation: the exponent is not a constant, so the scale is not known and the factor of main stays; for p = 1, the value is 1000 times too large
        (0, "2000. / (1.)", "2000. / (1.)"),    # V_product *= 2 V / (1 mV): multiply by 2000
        (1, "2. / (1000.)", "2. / (1000.)"),    # V_quotient /= 2 mV / (1 V): divide by 0.002
        (2, "1.00000000e+09 * 1.00000000e-12", "1.00000000e+09 * 1.00000000e-12"),    # V_volt *= 1 mA * 1 Ohm * V**-1: multiply by 0.001
        (3, "1.00000000e+09 * 1.00000000e-12", "1.00000000e+09 * 1.00000000e-12")])    # V_volt /= 1 mA * 1 Ohm * V**-1: divide by 0.001
    def test_generated_code_for_power_and_compound_product(self, statement, expected_cpp, expected_python):
        r"""
        Generated C++ and Python code holds ``(2 V)**2`` in mV**2, so the factor from V**2 to mV**2 is not printed. In a compound product or quotient, such as ``V_m *= 2 V / (1 mV)``, the variable is multiplied or divided by the value of the right-hand side without a unit, whatever the unit in which generated code holds the variable.
        """
        model = ModelParser.parse_file(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources")), "PowerAndCompoundProductWithDifferentButCompatibleUnits.nestml"))
        if isinstance(statement, int):
            expression = model.get_model_list()[0].get_update_blocks()[0].get_stmts_body().get_stmts()[statement].small_stmt.get_assignment().get_expression()
        else:
            declarations = model.get_model_list()[0].get_state_blocks()[0].get_declarations()
            expression = [decl for decl in declarations if decl.get_variables()[0].get_name() == statement][0].get_expression()

        assert self.cpp_printer.print(expression) == expected_cpp
        assert self.python_printer.print(expression) == expected_python

    def test_cpp_printer_parenthesizes_divisor_of_integer_quotient(self):
        r"""
        ``x //= a / b`` must divide ``x`` by the quotient ``a / b``, not by ``a`` and then by ``b``.
        """
        model = ModelParser.parse_file(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources")), "PowerAndCompoundProductWithDifferentButCompatibleUnits.nestml"))
        assignment = model.get_model_list()[0].get_update_blocks()[0].get_stmts_body().get_stmts()[4].small_stmt.get_assignment()

        assert CppPrinter(self.cpp_printer).print_assignment(assignment) == "V_floor = (int)(V_floor / (2. / (1000.)))"

    @pytest.mark.parametrize("variable_name, expected", [("V_max", 1E-3), ("V_pow", None)])
    def test_held_unit_scale_of_function_call(self, variable_name, expected):
        r"""
        Generated code holds the value of ``max(1 V, 2 mV)`` in mV, the unit of its arguments. ``pow()`` also returns the type of its first argument, but its value is not in the unit of its arguments, so the unit is not known.
        """
        model = ModelParser.parse_file(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources")), "PowerAndCompoundProductWithDifferentButCompatibleUnits.nestml"))
        declarations = model.get_model_list()[0].get_state_blocks()[0].get_declarations()
        expression = [decl for decl in declarations if decl.get_variables()[0].get_name() == variable_name][0].get_expression()

        scale = ASTUtils.get_held_unit_scale(expression)
        if expected is None:
            assert scale is None
        else:
            assert scale == pytest.approx(expected)

    @staticmethod
    def nestml_printer() -> NESTMLExpressionPrinter:
        r"""
        Give a NESTML printer that also prints function calls in NESTML syntax; ``self.printer`` prints them in C++ syntax.
        """
        variable_printer = NESTMLVariablePrinter(None)
        function_call_printer = NESTMLFunctionCallPrinter(None)
        printer = NESTMLExpressionPrinter(NESTMLSimpleExpressionPrinter(variable_printer, ConstantPrinter(), function_call_printer))
        variable_printer._expression_printer = printer
        function_call_printer._expression_printer = printer
        return printer

    @pytest.mark.parametrize("variable_name, expected_cpp, expected_python, expected_nestml", [
        ("f_tern", "(1000.0 * ((false) ? (1.) : ((0.001 * (1.)))))", "(1000.0 * ((1.) if (False) else ((0.001 * (1.)))))", "(1000.0 * (false?1 kHz:1 Hz))"),    # generated code holds 1 kHz in kHz, but 1 Hz in Hz
        ("V_tern", "(true) ? (1000.) : (1.)", "(1000.) if (True) else (1.)", "(1000.0 * (true?1 V:1 mV))"),    # generated code holds both branches in mV
        ("f_min", "std::min(1., (0.001 * (2 * 1.)))", "min(1., (0.001 * (2 * 1.)))", "min(1 kHz, 2 * 1 Hz)"),
        ("f_clip", "(1000.0 * (std::min(2., std::max(0.001, 1.))))", "(1000.0 * (clip(1., 0.001, 2.)))", "(1000.0 * (clip(1 kHz, 1 s**-1, 2 kHz)))"),    # generated code holds 1 s**-1 as 0.001 (in 1/ms), so all arguments have the same scale
        ("x_tern", "(false) ? (f * 1.) : (1. / (1000.))", "(f * 1.) if (False) else (1. / (1000.))", "false?f * 1 ms:1 ms / (1 s)"),    # values without a physical dimension are not converted
        ("x_min", "std::min(f * 1., 1. / (1000.))", "min(f * 1., 1. / (1000.))", "min(f * 1 ms, 1 ms / (1 s))")])
    def test_generated_code_for_branches_and_arguments_with_different_units(self, variable_name, expected_cpp, expected_python, expected_nestml):
        r"""
        NESTML does not convert the branches of a conditional expression or the arguments of a function with template parameters. Generated code converts a branch or an argument if it holds it in a unit with another scale, unless the value has no physical dimension (see ASTUtils.convert_to_held_unit_of()). The output of the NESTML printer does not change.
        """
        model = ModelParser.parse_file(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources")), "OperandsWithDifferentButCompatibleUnits.nestml"))
        declarations = model.get_model_list()[0].get_state_blocks()[0].get_declarations()
        expression = [decl for decl in declarations if decl.get_variables()[0].get_name() == variable_name][0].get_expression()

        assert self.cpp_printer.print(expression) == expected_cpp
        assert self.python_printer.print(expression) == expected_python
        assert self.nestml_printer().print(expression) == expected_nestml

    @pytest.mark.parametrize("statement_index, expected_cpp, expected_python, expected_nestml", [
        (0, "f < (1000.0 * (0.05))", "f < (1000.0 * (0.05))", "f < 50 s**-1"),    # generated code holds f in Hz, but 50 s**-1 as 0.05 (in 1/ms)
        (1, "f > (1000.0 * (1.))", "f > (1000.0 * (1.))", "f > 1 kHz"),
        (2, "1000. > 999.", "1000. > 999.", "1 V > 999 mV"),    # generated code holds both operands in mV
        (3, "V_volt > 1.", "V_volt > 1.", "V_volt > 1 mV"),    # the unit in which generated code holds V_volt is not known
        (4, "f > 5", "f > 5", "f > 5")])    # a number without a physical unit is not converted
    def test_generated_code_for_comparisons_with_different_units(self, statement_index, expected_cpp, expected_python, expected_nestml):
        r"""
        NESTML does not convert the operands of a comparison. Generated code converts the right operand if it holds it in a unit with another scale. The output of the NESTML printer does not change.
        """
        model = ModelParser.parse_file(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources")), "OperandsWithDifferentButCompatibleUnits.nestml"))
        statement = model.get_model_list()[0].get_update_blocks()[0].get_stmts_body().get_stmts()[statement_index]
        condition = statement.compound_stmt.get_if_stmt().get_if_clause().get_condition()

        assert self.cpp_printer.print(condition) == expected_cpp
        assert self.python_printer.print(condition) == expected_python
        assert self.nestml_printer().print(condition) == expected_nestml

    def test_conversion_factors_of_conditions_after_parsing(self):
        r"""
        ModelParser.parse_file() does not run the CoCos, and no CoCo derives the type of an ``onCondition`` condition. The comparisons in ``elif``, ``while`` and ``onCondition`` conditions must nevertheless have their conversion factors after parsing.
        """
        model = ModelParser.parse_file(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources")), "OperandsWithDifferentButCompatibleUnits.nestml")).get_model_list()[0]
        statements = model.get_update_blocks()[0].get_stmts_body().get_stmts()

        assert self.cpp_printer.print(statements[4].compound_stmt.get_if_stmt().get_elif_clauses()[0].get_condition()) == "f > (1000.0 * (2.))"
        assert self.cpp_printer.print(statements[5].compound_stmt.get_while_stmt().get_condition()) == "f > (1000.0 * (1.))"
        assert self.cpp_printer.print(model.get_on_condition_blocks()[0].get_cond_expr()) == "f < (1000.0 * (2.))"

    def test_implicit_conversion_factor(self):
        factor = ImplicitConversionFactor(1000., 1.)
        assert str(factor) == "1000.0"

        for duplicate in [copy.copy(factor), copy.deepcopy(factor), pickle.loads(pickle.dumps(factor))]:
            assert isinstance(duplicate, ImplicitConversionFactor)
            assert duplicate == 1000.
            assert duplicate.nest_factor == 1.
