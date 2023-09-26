# -*- coding: utf-8 -*-
#
# spinnaker_c_variable_printer.py
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

from __future__ import annotations

from pynestml.utils.ast_utils import ASTUtils

from pynestml.codegeneration.spinnaker_code_generator_utils import SPINNAKERCodeGeneratorUtils
from pynestml.codegeneration.printers.cpp_variable_printer import CppVariablePrinter
from pynestml.codegeneration.printers.expression_printer import ExpressionPrinter
from pynestml.codegeneration.nest_unit_converter import NESTUnitConverter
from pynestml.meta_model.ast_external_variable import ASTExternalVariable
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.symbols.predefined_units import PredefinedUnits
from pynestml.symbols.predefined_variables import PredefinedVariables
from pynestml.symbols.symbol import SymbolKind
from pynestml.symbols.unit_type_symbol import UnitTypeSymbol
from pynestml.symbols.variable_symbol import BlockType
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages


class SpinnakerCVariablePrinter(CppVariablePrinter):
    r"""
    Variable printer for C syntax and the Spinnaker API.
    """

    def __init__(self, expression_printer: ExpressionPrinter, with_origin: bool = True, with_vector_parameter: bool = True) -> None:
        super().__init__(expression_printer)
        self.with_origin = with_origin
        self.with_vector_parameter = with_vector_parameter
        self._state_symbols = []

    def print_variable(self, variable: ASTVariable) -> str:
        """
        Converts a single variable to Spinnaker processable format.
        :param variable: a single variable.
        :return: a Spinnaker processable format.
        """
        assert isinstance(variable, ASTVariable)

        if isinstance(variable, ASTExternalVariable):
            raise Exception("SpiNNaker does not suport external variables")

        if variable.get_name() == PredefinedVariables.E_CONSTANT:
            return "REAL_CONST(2.718282)"

        symbol = variable.get_scope().resolve_to_symbol(variable.get_complete_name(), SymbolKind.VARIABLE)
        if symbol is None:
            # test if variable name can be resolved to a type
            if PredefinedUnits.is_unit(variable.get_complete_name()):
                return str(NESTUnitConverter.get_factor(PredefinedUnits.get_unit(variable.get_complete_name()).get_unit()))

            code, message = Messages.get_could_not_resolve(variable.get_name())
            Logger.log_message(log_level=LoggingLevel.ERROR, code=code, message=message,
                               error_position=variable.get_source_position())
            return ""

        vector_param = ""
        if self.with_vector_parameter and symbol.has_vector_parameter():
            vector_param = "[" + self._print_vector_parameter_name_reference(variable) + "]"

        if symbol.is_buffer():
            if isinstance(symbol.get_type_symbol(), UnitTypeSymbol):
                units_conversion_factor = NESTUnitConverter.get_factor(symbol.get_type_symbol().unit.unit)
            else:
                units_conversion_factor = 1
            s = ""
            if not units_conversion_factor == 1:
                s += "(" + str(units_conversion_factor) + " * "
            s += self._print_buffer_value(variable)
            if not units_conversion_factor == 1:
                s += ")"
            return s

        if symbol.is_inline_expression:
            # there might not be a corresponding defined state variable; insist on calling the getter function
            return "get_" + self._print(variable, symbol, with_origin=False) + vector_param + "()"

        assert not symbol.is_kernel(), "Cannot print kernel; kernel should have been converted during code generation"

        if symbol.is_state() or symbol.is_inline_expression:
            return self._print(variable, symbol, with_origin=self.with_origin) + vector_param

        return self._print(variable, symbol, with_origin=self.with_origin) + vector_param

    def _print_delay_variable(self, variable: ASTVariable) -> str:
        """
        Converts a delay variable to SPINNAKER processable format
        :param variable:
        :return:
        """
        symbol = variable.get_scope().resolve_to_symbol(variable.get_complete_name(), SymbolKind.VARIABLE)
        if symbol and symbol.is_state() and symbol.has_delay_parameter():
            return "get_delayed_" + variable.get_name() + "()"

        return ""

    def _print_vector_parameter_name_reference(self, variable: ASTVariable) -> str:
        """
        Converts the vector parameter into SPINNAKER processable format
        :param variable:
        :return:
        """
        vector_parameter = variable.get_vector_parameter()
        vector_parameter_var = vector_parameter.get_variable()
        if vector_parameter_var:
            vector_parameter_var.scope = variable.get_scope()

            symbol = vector_parameter_var.get_scope().resolve_to_symbol(vector_parameter_var.get_complete_name(),
                                                                        SymbolKind.VARIABLE)
            if symbol and symbol.block_type == BlockType.LOCAL:
                return symbol.get_symbol_name()

        return self._expression_printer.print(vector_parameter)

    def _print_buffer_value(self, variable: ASTVariable) -> str:
        """
        Converts for a handed over symbol the corresponding name of the buffer to a SPINNAKER processable format.
        :param variable: a single variable symbol.
        :return: the corresponding representation as a string
        """
        variable_symbol = variable.get_scope().resolve_to_symbol(variable.get_complete_name(), SymbolKind.VARIABLE)
        if variable_symbol.is_spike_input_port():
            var_name = variable_symbol.get_symbol_name().upper()
            if variable.get_vector_parameter() is not None:
                vector_parameter = ASTUtils.get_numeric_vector_size(variable)
                var_name = var_name + "_" + str(vector_parameter)

            return "input->inputs[" + var_name + " - MIN_SPIKE_RECEPTOR]"

        if variable_symbol.is_continuous_input_port():
            var_name = variable_symbol.get_symbol_name().upper()
            if variable.get_vector_parameter() is not None:
                vector_parameter = ASTUtils.get_numeric_vector_size(variable)
                var_name = var_name + "_" + str(vector_parameter)

            return "input->inputs[" + var_name + " - MIN_SPIKE_RECEPTOR]"

        return variable_symbol.get_symbol_name() + '_grid_sum_'

    def _print(self, variable: ASTVariable, symbol, with_origin: bool = True) -> str:
        assert all([isinstance(s, str) for s in self._state_symbols])

        variable_name = CppVariablePrinter._print_cpp_name(variable.get_complete_name())

        if symbol.is_local():
            return variable_name

        if variable.is_delay_variable():
            return self._print_delay_variable(variable)

        if with_origin:
            return SPINNAKERCodeGeneratorUtils.print_symbol_origin(symbol, numerical_state_symbols=self._state_symbols) % variable_name

        return variable_name
