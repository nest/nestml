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
from pynestml.codegeneration.printers.cpp_simple_expression_printer import CppSimpleExpressionPrinter
from pynestml.codegeneration.printers.cpp_type_symbol_printer import CppTypeSymbolPrinter
from pynestml.codegeneration.printers.cpp_variable_printer import CppVariablePrinter
from pynestml.codegeneration.printers.nest_cpp_function_call_printer import NESTCppFunctionCallPrinter
from pynestml.codegeneration.printers.nestml_expression_printer import NESTMLExpressionPrinter
from pynestml.codegeneration.printers.nestml_simple_expression_printer import NESTMLSimpleExpressionPrinter
from pynestml.codegeneration.printers.nestml_variable_printer import NESTMLVariablePrinter
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
