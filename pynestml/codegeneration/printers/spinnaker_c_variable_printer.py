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

from typing import Dict, Optional

try:
    # Available in the standard library starting with Python 3.12
    from typing import override
except ImportError:
    # Fallback for Python 3.8 - 3.11
    from typing_extensions import override

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
from pynestml.utils.ast_utils import ASTUtils
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages


class SpinnakerCVariablePrinter(CppVariablePrinter):
    r"""
    Variable printer for C syntax and the Spinnaker API.
    """
    def __init__(self, expression_printer: ExpressionPrinter, with_origin: bool = True, with_vector_parameter: bool = True, variables_special_cases: Optional[Dict[str, str]] = None) -> None:
        super().__init__(expression_printer)
        self.with_origin = with_origin
        self.with_vector_parameter = with_vector_parameter
        self._state_symbols = []

        self.variables_special_cases = variables_special_cases

    @override
    def print_variable(self, node: ASTVariable) -> str:
        """
        Converts a single node to SpiNNaker C format.
        :param node: a single node.
        :return: a Spinnaker processable format.
        """
        assert isinstance(node, ASTVariable)

        if isinstance(node, ASTExternalVariable):
            # this node is part of the header in the synapse
            return "plastic_region_address->history." + node.name

        if node.get_name() == PredefinedVariables.E_CONSTANT:
            return "REAL_CONST(2.718282)"

        if node.get_name() == PredefinedVariables.PI_CONSTANT:
            return "REAL_CONST(3.14159)"

        symbol = node.get_scope().resolve_to_symbol(node.get_complete_name(), SymbolKind.VARIABLE)
        if symbol is None:
            # test if node name can be resolved to a type
            if PredefinedUnits.is_unit(node.get_complete_name()):
                return str(NESTUnitConverter.get_factor(PredefinedUnits.get_unit(node.get_complete_name()).get_unit()))

            code, message = Messages.get_could_not_resolve(node.get_name())
            Logger.log_message(log_level=LoggingLevel.ERROR, code=code, message=message,
                               error_position=node.get_source_position())
            return ""

        vector_param = ""
        if self.with_vector_parameter and symbol.has_vector_parameter():
            vector_param = "[" + self._expression_printer.print(node.get_vector_parameter()) + "]"

        if symbol.is_buffer():
            if isinstance(symbol.get_type_symbol(), UnitTypeSymbol):
                units_conversion_factor = NESTUnitConverter.get_factor(symbol.get_type_symbol().unit.unit)
            else:
                units_conversion_factor = 1
            s = ""
            if not units_conversion_factor == 1:
                s += "(" + str(units_conversion_factor) + " * "
            s += self._print_buffer_value(node)
            if not units_conversion_factor == 1:
                s += ")"
            return s

        if symbol.is_inline_expression:
            # there might not be a corresponding defined state node; insist on calling the getter function
            return "get_" + self._print(node, symbol, with_origin=False) + vector_param + "()"

        assert not symbol.is_kernel(), "Cannot print kernel; kernel should have been converted during code generation"

        return self._print(node, symbol, with_origin=self.with_origin) + vector_param

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

            return "input->inputs[" + var_name + "]"

        if variable_symbol.is_continuous_input_port():
            var_name = variable_symbol.get_symbol_name().upper()
            if variable.get_vector_parameter() is not None:
                vector_parameter = ASTUtils.get_numeric_vector_size(variable)
                var_name = var_name + "_" + str(vector_parameter)

            return "input->inputs[" + var_name + "]"

        return variable_symbol.get_symbol_name() + "_grid_sum_"

    def _print(self, variable: ASTVariable, symbol, with_origin: bool = True) -> str:
        assert all([isinstance(s, str) for s in self._state_symbols])

        variable_name = CppVariablePrinter._print_cpp_name(variable.get_complete_name())
        variable_symbol = variable.get_scope().resolve_to_symbol(variable.get_complete_name(), SymbolKind.VARIABLE)

        if symbol.is_local():
            return variable_name

        if variable.is_delay_variable():
            return self._print_delay_variable(variable)

        if with_origin == "header" and variable_symbol.name.startswith("__P"):
            return variable_name   # no origin, propagators are local variables

        if with_origin == "header" and variable_symbol.block_type in [BlockType.STATE, BlockType.EQUATION]:
            return "plastic_region_address->history." + variable_name

        if with_origin:
            return SPINNAKERCodeGeneratorUtils.print_symbol_origin(symbol, numerical_state_symbols=self._state_symbols) % variable_name

        return variable_name
