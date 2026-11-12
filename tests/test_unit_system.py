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

from astropy import units as u

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
from pynestml.codegeneration.printers.python_standalone_printer import PythonStandalonePrinter
from pynestml.codegeneration.printers.python_simple_expression_printer import PythonSimpleExpressionPrinter
from pynestml.codegeneration.printers.python_variable_printer import PythonVariablePrinter
from pynestml.codegeneration.python_standalone_unit_converter import PythonStandaloneUnitConverter
from pynestml.frontend.pynestml_frontend import generate_target
from pynestml.symbol_table.symbol_table import SymbolTable
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.symbols.predefined_quantities import PredefinedQuantities
from pynestml.symbols.predefined_types import PredefinedTypes
from pynestml.symbols.predefined_units import PredefinedUnits
from pynestml.symbols.predefined_variables import PredefinedVariables
from pynestml.symbols.real_type_symbol import RealTypeSymbol
from pynestml.symbols.symbol import SymbolKind
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
        self.printer = NESTMLExpressionPrinter(NESTMLSimpleExpressionPrinter(cpp_variable_printer,
                                                                             ConstantPrinter(),
                                                                             function_call_printer))
        cpp_variable_printer._expression_printer = self.printer
        variable_printer._expression_printer = self.printer
        function_call_printer._expression_printer = self.printer

        request.cls.printer = self.printer

        # printers for generated code: C++ code for NEST holds all values in NEST units (mV, pA, ms, ...; see NESTUnitConverter), Python-standalone code in SI units (V, A, s, ...; see PythonStandaloneUnitConverter)
        cpp_printer_variable_printer = CppVariablePrinter(None)
        cpp_printer_function_call_printer = NESTCppFunctionCallPrinter(None)
        self.cpp_printer = CppExpressionPrinter(CppSimpleExpressionPrinter(cpp_printer_variable_printer,
                                                                           ConstantPrinter(),
                                                                           cpp_printer_function_call_printer))
        cpp_printer_variable_printer._expression_printer = self.cpp_printer
        cpp_printer_function_call_printer._expression_printer = self.cpp_printer

        python_printer_variable_printer = PythonVariablePrinter(None, with_origin=False, unit_converter=PythonStandaloneUnitConverter)
        python_printer_function_call_printer = PythonFunctionCallPrinter(None)
        self.python_printer = PythonExpressionPrinter(PythonSimpleExpressionPrinter(python_printer_variable_printer,
                                                                                    ConstantPrinter(),
                                                                                    python_printer_function_call_printer,
                                                                                    unit_converter=PythonStandaloneUnitConverter))
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

    def _parse(self, fname):
        Logger.init_logger(LoggingLevel.INFO)
        Logger.set_current_node(None)
        return ModelParser.parse_file(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources")), fname))

    # Variables are typed by physical quantity (for instance, "voltage"), which only fixes the physical dimension. Expressions of the same dimension can therefore be used interchangeably, irrespective of the magnitude of their units, and no (implicit) conversion factors are inserted: the magnitude of a unit is part of the value of a literal such as ``10 V``.

    def test_no_conversion_in_direct_assignment(self):
        model = self._parse("DirectAssignmentWithDifferentButCompatibleUnits.nestml")
        printed_rhs_expression = self.print_rhs_of_first_assignment_in_update_block(model)

        assert printed_rhs_expression == "10 V"

    def test_no_conversion_in_nested_direct_assignment(self):
        model = self._parse("DirectAssignmentWithDifferentButCompatibleNestedUnits.nestml")
        printed_rhs_expression = self.print_rhs_of_first_assignment_in_update_block(model)

        assert printed_rhs_expression == "10 V + 5 mV + 20 V + 1 kV"

    def test_no_conversion_in_compound_assignment(self):
        model = self._parse("CompoundAssignmentWithDifferentButCompatibleUnits.nestml")
        printed_rhs_expression = self.print_rhs_of_first_assignment_in_update_block(model)

        assert printed_rhs_expression == "1200 mV"

    def test_no_conversion_in_declaration(self):
        model = self._parse("DeclarationWithDifferentButCompatibleUnitMagnitude.nestml")
        printed_rhs_expression = self.print_rhs_of_first_declaration_in_state_block(model)

        assert printed_rhs_expression == "10 V"

    def test_declaration_with_compatible_dimension(self):
        r"""(10 pA) / (100 pF) * (1 ms) has dimension voltage, so it can initialise a variable of quantity "voltage"."""
        model = self._parse("DeclarationWithDifferentButCompatibleUnits.nestml")
        declaration = self.get_first_declaration_in_state_block(model)

        assert declaration.get_data_type().get_quantity() == "voltage"
        assert declaration.get_data_type().get_type_symbol().equals(declaration.get_expression().type)
        assert declaration.get_expression().type.equals(PredefinedTypes.get_type("mV"))
        assert not declaration.get_expression().type.equals(PredefinedTypes.get_type("pA"))

    def test_declaration_with_same_variable_name_as_unit(self):
        Logger.init_logger(LoggingLevel.DEBUG)

        generate_target(input_path=os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources")), "DeclarationWithSameVariableNameAsUnit.nestml"), target_platform="NONE", logging_level="DEBUG")

        assert len(Logger.get_messages("BlockTest", LoggingLevel.ERROR)) == 0
        assert len(Logger.get_messages("BlockTest", LoggingLevel.WARNING)) == 3

    def test_no_conversion_in_standalone_function_call(self):
        model = self._parse("FunctionCallWithDifferentButCompatibleUnits.nestml")
        printed_function_call = self.print_first_function_call_in_update_block(model)

        assert printed_function_call == "foo(10 V)"

    def test_no_conversion_in_rhs_function_call(self):
        model = self._parse("RhsFunctionCallWithDifferentButCompatibleUnits.nestml")
        printed_function_call = self.print_rhs_of_first_assignment_in_update_block(model)

        assert printed_function_call == "foo(10 V)"

    def test_no_conversion_in_return_stmt_in_function_body(self):
        model = self._parse("FunctionBodyReturnStatementWithDifferentButCompatibleUnits.nestml")
        printed_return_stmt = self.print_first_return_statement_in_first_declared_function(model)

        assert printed_return_stmt == "bar"

    def test_quantity_types_compare_by_dimension(self):
        voltage = PredefinedTypes.get_type(PredefinedQuantities.parse("voltage"))
        assert voltage.equals(PredefinedTypes.get_type("mV"))
        assert voltage.equals(PredefinedTypes.get_type("V"))
        assert voltage.equals(PredefinedTypes.get_type(PredefinedQuantities.parse("current * resistance")))
        assert not voltage.equals(PredefinedTypes.get_type("pA"))

        assert PredefinedTypes.get_type(PredefinedQuantities.parse("conductance / time")).equals(PredefinedTypes.get_type(u.nS / u.ms))
        assert PredefinedTypes.get_type(PredefinedQuantities.parse("1 / time")).equals(PredefinedTypes.get_type("ms")**-1)

        # a dimensionless ratio is real, irrespective of the magnitude of its units
        assert PredefinedTypes.get_type(u.V / u.mV).equals(PredefinedTypes.get_real_type())

    @pytest.mark.parametrize("quantity, expected_unit", [
        ("(voltage / time)**-(1/2)", (u.V / u.s)**-0.5),
        ("(time / voltage)**(1/2)", (u.V / u.s)**-0.5),
        ("time**(1/2) * voltage**-(1/2)", (u.V / u.s)**-0.5),
        ("(conductance / capacitance)**(1/2)", u.s**-0.5),
        ("frequency**0.5", u.s**-0.5),
        ("(current * resistance)**2 / (voltage * time)", u.V / u.s),
        ("1 / (amount of substance / volume)**(3/2)", (u.mol / u.m**3)**-1.5),
        ("(electrical potential)**-2 * time**-1", u.V**-2 / u.s),
        ("(force * length / charge)**-(3/2)", u.V**-1.5),
        ("((voltage / current)**2 * conductance)**(1/2) / resistance", u.Ohm**-0.5),
    ])
    def test_complex_quantity_expressions(self, quantity, expected_unit):
        r"""Quantity expressions combining products, quotients and (negative, fractional) powers have the expected physical dimension."""
        unit = PredefinedQuantities.parse(quantity)
        assert unit.is_equivalent(expected_unit)
        assert PredefinedTypes.get_type(unit).equals(PredefinedTypes.get_type(expected_unit))

        # the same expression with a different sign of the exponent, a different exponent or a different base has a different dimension
        assert not unit.is_equivalent(expected_unit**-1)
        assert not unit.is_equivalent(expected_unit**2)
        assert not unit.is_equivalent(expected_unit * u.s)

    def test_complex_quantity_spellings(self):
        r"""Different ways of writing the same physical dimension yield equal types; different dimensions yield different types."""
        def type_of(quantity):
            return PredefinedTypes.get_type(PredefinedQuantities.parse(quantity))

        same = ["(voltage / time)**-(1/2)", "(time / voltage)**(1/2)", "time**0.5 / voltage**0.5", "(current * resistance / time)**-(1/2)", "(1 / time)**-(1/2) * (electric potential)**-(1/2)"]
        for quantity in same:
            assert type_of(quantity).equals(type_of(same[0])), quantity

        for quantity in ["(voltage / time)**(1/2)", "(voltage / time)**-(1/3)", "(voltage * time)**-(1/2)", "(current / time)**-(1/2)"]:
            assert not type_of(quantity).equals(type_of(same[0])), quantity

        # numeric literals with complex units have the type of the corresponding quantity
        assert type_of("(conductance / capacitance)**(1/2)").equals(type_of("time**-(1/2)"))
        assert type_of("frequency**(1/2)").equals(PredefinedTypes.get_type((u.nS / u.uF)**0.5))

    def test_continuous_input_port_unit_is_inserted(self):
        r"""A continuous input port declared with a unit yields plain numbers in that unit: references to the port are multiplied by the unit explicitly."""
        model = self._parse("ContinuousInputPortUnits.nestml")
        assert len(Logger.get_messages(model.get_model_list()[0], LoggingLevel.ERROR)) == 0

        ode = model.get_model_list()[0].get_equations_blocks()[0].get_ode_equations()[0]
        assert self.printer.print(ode.get_rhs()) == "-V_m / tau_m + (I_stim * 1 pA) / C_m + I_dimensionless * 1 nA / C_m"

        # the port variable itself is a plain number
        scope = model.get_model_list()[0].get_scope()
        assert isinstance(scope.resolve_to_symbol("I_stim", SymbolKind.VARIABLE).get_type_symbol(), RealTypeSymbol)

        # the inserted expression has the dimension of a current
        inserted_expr = ode.get_rhs().get_lhs().get_rhs().get_lhs()
        assert str(inserted_expr) == "(I_stim * 1 pA)"
        assert inserted_expr.type.equals(PredefinedTypes.get_type("pA"))

    # The tests below are adapted from the branch ``sepahead/fix-double-unit-conversion``. Each value is converted exactly once, from the unit in which it is written in the model to the preferred unit of the target platform (NEST units for C++, SI units for Python-standalone).

    @pytest.mark.parametrize("model_file_name, print_function, expected_cpp, expected_python", [
        ("DirectAssignmentWithDifferentButCompatibleUnits.nestml", "print_rhs_of_first_assignment_in_update_block", "10000.", "10."),
        ("DirectAssignmentWithDifferentButCompatibleNestedUnits.nestml", "print_rhs_of_first_assignment_in_update_block", "10000. + 5. + 20000. + 1000000.", "10. + 0.005 + 20. + 1000."),
        ("CompoundAssignmentWithDifferentButCompatibleUnits.nestml", "print_rhs_of_first_assignment_in_update_block", "1200.", "1.2"),
        ("DeclarationWithDifferentButCompatibleUnitMagnitude.nestml", "print_rhs_of_first_declaration_in_state_block", "10000.", "10."),
        ("FunctionCallWithDifferentButCompatibleUnits.nestml", "print_first_function_call_in_update_block", "foo(10000.)", "foo(10.)"),
        ("RhsFunctionCallWithDifferentButCompatibleUnits.nestml", "print_rhs_of_first_assignment_in_update_block", "foo(10000.)", "foo(10.)"),
        ("FunctionBodyReturnStatementWithDifferentButCompatibleUnits.nestml", "print_first_return_statement_in_first_declared_function", "bar", "bar")])
    def test_generated_code_after_magnitude_conversion(self, model_file_name, print_function, expected_cpp, expected_python):
        r"""
        Generated code holds a numeric literal in the preferred units of the target platform: for instance, it holds ``10 V`` as ``10000.`` (mV) in C++ code for NEST and as ``10.`` (V) in Python-standalone code. As variables are typed by quantity and are held in the same preferred units, no further conversion factor is printed.
        """
        model = ModelParser.parse_file(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources")), model_file_name))

        assert getattr(self, print_function)(model, self.cpp_printer) == expected_cpp
        assert getattr(self, print_function)(model, self.python_printer) == expected_python

    @pytest.mark.parametrize("statement, expected_cpp, expected_python", [
        ("V_squared", "(((2000.)) * ((2000.)))", "(2.)**2"),    # (2 V)**2 = 4000000 mV**2 = 4 V**2
        ("V_root", "pow((4000000.), 0.5)", "(4.)**0.5"),    # (4 V**2)**0.5 = 2000 mV = 2 V
        ("g", "pow((0.05), (-1))", "(50000000.)**(-1)"),    # (50 MOhm)**-1 = 20 nS = 2E-8 S; NEST holds 50 MOhm as 0.05 (GOhm)
        ("f", "pow((100.), (-1))", "(0.1)**(-1)"),    # (0.1 s)**-1 = 0.01 ms**-1 = 10 s**-1
        ("V_param", "pow((2000.), p)", "(2.)**p"),    # for p = 1: 2000 mV = 2 V
        ("V_max", "std::max(1000., 2.)", "max(1., 0.002)"),    # both arguments in the same unit
        (0, "2000. / (1.)", "2. / (0.001)"),    # V_product *= 2 V / (1 mV): multiply by 2000
        (1, "2. / (1000.)", "0.002 / (1.)"),    # V_quotient /= 2 mV / (1 V): divide by 0.002
        (2, "1.00000000e+09 * 1.00000000e-12", "0.001 * 1."),    # V_volt *= 1 mA * 1 Ohm * V**-1: multiply by 0.001
        (3, "1.00000000e+09 * 1.00000000e-12", "0.001 * 1.")])    # V_volt /= 1 mA * 1 Ohm * V**-1: divide by 0.001
    def test_generated_code_for_power_and_compound_product(self, statement, expected_cpp, expected_python):
        r"""
        Generated code holds ``(2 V)**2`` in the square of the preferred unit of voltage (mV**2 for NEST, V**2 for Python-standalone), so no further factor is printed. In a compound product or quotient, such as ``V_m *= 2 V / (1 mV)``, the variable is multiplied or divided by the (dimensionless) value of the right-hand side.
        """
        model = ModelParser.parse_file(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources")), "PowerAndCompoundProductWithDifferentButCompatibleUnits.nestml"))
        if isinstance(statement, int):
            expression = model.get_model_list()[0].get_update_blocks()[0].get_stmts_body().get_stmts()[statement].small_stmt.get_assignment().get_expression()
        else:
            declarations = model.get_model_list()[0].get_state_blocks()[0].get_declarations()
            expression = [decl for decl in declarations if decl.get_variables()[0].get_name() == statement][0].get_expression()

        assert self.cpp_printer.print(expression) == expected_cpp
        assert self.python_printer.print(expression) == expected_python

    def test_printers_parenthesize_divisor_of_integer_quotient(self):
        r"""
        ``x //= a / b`` has the same semantics as ``x /= a / b`` (with the result truncated to an integer), so it must divide ``x`` by the quotient ``a / b``, not by ``a`` and then by ``b``.

        As integer division is only defined for dimensionless values (see ``CoCoTruncationOperandsDimensionless``), the result is the same for every target platform: 1 // 0.002 = 500.
        """
        model = ModelParser.parse_file(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources")), "PowerAndCompoundProductWithDifferentButCompatibleUnits.nestml"))
        assignment = model.get_model_list()[0].get_update_blocks()[0].get_stmts_body().get_stmts()[4].small_stmt.get_assignment()

        assert CppPrinter(self.cpp_printer).print_assignment(assignment) == "n_floor = (int)(n_floor / (2. / (1000.)))"
        assert PythonStandalonePrinter(self.python_printer).print_assignment(assignment) == "n_floor = int(n_floor / (0.002 / (1.)))"

    def test_printers_integer_division_to_explicit_resolution(self):
        r"""
        ``(V // 1 mV) * 1 mV`` truncates a voltage to a resolution of 1 mV. The quotient ``V / 1 mV`` is dimensionless, so the result is the same for every target platform, although the voltage and the literal are printed in different units.
        """
        model = ModelParser.parse_file(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources")), "PowerAndCompoundProductWithDifferentButCompatibleUnits.nestml"))
        assignment = model.get_model_list()[0].get_update_blocks()[0].get_stmts_body().get_stmts()[5].small_stmt.get_assignment()

        assert CppPrinter(self.cpp_printer).print_assignment(assignment) == "V_grid = ((long)(V_grid / (1.))) * 1."
        assert PythonStandalonePrinter(self.python_printer).print_assignment(assignment) == "V_grid = (int(V_grid / (0.001))) * 0.001"
        assert self.nestml_printer().print(assignment.get_expression()) == "(V_grid // 1 mV) * 1 mV"

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
        ("f_tern", "(false) ? (1.) : (0.001)", "(1000.) if (False) else (1.)", "false?1 kHz:1 Hz"),    # NEST holds frequencies in 1/ms
        ("V_tern", "(true) ? (1000.) : (1.)", "(1.) if (True) else (0.001)", "true?1 V:1 mV"),
        ("f_min", "std::min(1., 2 * 0.001)", "min(1000., 2 * 1.)", "min(1 kHz, 2 * 1 Hz)"),
        ("f_clip", "std::min(2., std::max(0.001, 1.))", "clip(1000., 1., 2000.)", "clip(1 kHz, 1 s**-1, 2 kHz)"),
        ("x_tern", "(false) ? (f * 1.) : (1. / (1000.))", "(f * 0.001) if (False) else (0.001 / (1.))", "false?f * 1 ms:1 ms / (1 s)"),    # dimensionless: the same value in either system of units
        ("x_min", "std::min(f * 1., 1. / (1000.))", "min(f * 0.001, 0.001 / (1.))", "min(f * 1 ms, 1 ms / (1 s))")])
    def test_generated_code_for_branches_and_arguments_with_different_units(self, variable_name, expected_cpp, expected_python, expected_nestml):
        r"""
        The branches of a conditional expression and the arguments of a function with template parameters can be written in different units. Generated code holds each of them in the preferred unit of the target platform, so they can be compared and combined directly. The output of the NESTML printer does not change.
        """
        model = ModelParser.parse_file(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources")), "OperandsWithDifferentButCompatibleUnits.nestml"))
        declarations = model.get_model_list()[0].get_state_blocks()[0].get_declarations()
        expression = [decl for decl in declarations if decl.get_variables()[0].get_name() == variable_name][0].get_expression()

        assert self.cpp_printer.print(expression) == expected_cpp
        assert self.python_printer.print(expression) == expected_python
        assert self.nestml_printer().print(expression) == expected_nestml

    @pytest.mark.parametrize("statement_index, expected_cpp, expected_python, expected_nestml", [
        (0, "f < 0.05", "f < 50.", "f < 50 s**-1"),    # NEST holds f, and 50 s**-1, in 1/ms
        (1, "f > 1.", "f > 1000.", "f > 1 kHz"),
        (2, "1000. > 999.", "1. > 0.999", "1 V > 999 mV"),
        (3, "V_volt > 1.", "V_volt > 0.001", "V_volt > 1 mV"),
        (4, "f > 5", "f > 5", "f > 5")])    # a number without a physical unit is not converted
    def test_generated_code_for_comparisons_with_different_units(self, statement_index, expected_cpp, expected_python, expected_nestml):
        r"""
        The operands of a comparison can be written in different units. Generated code holds both in the preferred unit of the target platform. The output of the NESTML printer does not change.
        """
        model = ModelParser.parse_file(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources")), "OperandsWithDifferentButCompatibleUnits.nestml"))
        statement = model.get_model_list()[0].get_update_blocks()[0].get_stmts_body().get_stmts()[statement_index]
        condition = statement.compound_stmt.get_if_stmt().get_if_clause().get_condition()

        assert self.cpp_printer.print(condition) == expected_cpp
        assert self.python_printer.print(condition) == expected_python
        assert self.nestml_printer().print(condition) == expected_nestml

    def test_conversion_of_conditions_after_parsing(self):
        r"""
        The literals in ``elif``, ``while`` and ``onCondition`` conditions are converted to the preferred units of the target platform, like those in any other expression.
        """
        model = ModelParser.parse_file(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources")), "OperandsWithDifferentButCompatibleUnits.nestml")).get_model_list()[0]
        statements = model.get_update_blocks()[0].get_stmts_body().get_stmts()

        assert self.cpp_printer.print(statements[4].compound_stmt.get_if_stmt().get_elif_clauses()[0].get_condition()) == "f > 2."
        assert self.cpp_printer.print(statements[5].compound_stmt.get_while_stmt().get_condition()) == "f > 1."
        assert self.cpp_printer.print(model.get_on_condition_blocks()[0].get_cond_expr()) == "f < 2."
        assert self.python_printer.print(model.get_on_condition_blocks()[0].get_cond_expr()) == "f < 2000."
