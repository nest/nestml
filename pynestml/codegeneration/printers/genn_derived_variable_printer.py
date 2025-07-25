# -*- coding: utf-8 -*-
#
# genn_derived_variable_printer.py
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

from pynestml.codegeneration.nest_unit_converter import NESTUnitConverter
from pynestml.codegeneration.printers.expression_printer import ExpressionPrinter
from pynestml.codegeneration.printers.python_variable_printer import PythonVariablePrinter
from pynestml.codegeneration.printers.variable_printer import VariablePrinter
from pynestml.codegeneration.python_code_generator_utils import PythonCodeGeneratorUtils
from pynestml.meta_model.ast_external_variable import ASTExternalVariable
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.symbols.predefined_units import PredefinedUnits
from pynestml.symbols.predefined_variables import PredefinedVariables
from pynestml.symbols.symbol import SymbolKind
from pynestml.symbols.unit_type_symbol import UnitTypeSymbol
from pynestml.symbols.variable_symbol import BlockType
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages


class GeNNDerivedVariablePrinter(PythonVariablePrinter):
    r"""
    Variable printer for Python syntax.
    """

    def __init__(self, expression_printer: ExpressionPrinter, with_origin: bool = False, with_vector_parameter: bool = True) -> None:
        super().__init__(expression_printer)
        self.with_origin = with_origin
        self.with_vector_parameter = with_vector_parameter

    def print_variable(self, variable: ASTVariable) -> str:
        """
        Converts a single variable to nest processable format.
        :param variable: a single variable.
        :return: a string representation
        """
        assert isinstance(variable, ASTVariable)

        # print external variables (such as a variable in the synapse that needs to call the getter method on the postsynaptic partner)
        if isinstance(variable, ASTExternalVariable):
            _name = str(variable)
            if variable.get_alternate_name():
                if not variable._altscope:
                    # get the value from the postsynaptic partner continuous-time buffer (for post_connected_continuous_input_ports); this has been buffered in a local temp variable starting with "__"
                    return variable.get_alternate_name()

                # get the value from the postsynaptic partner (without time specified)
                # the disadvantage of this approach is that the time the value is to be obtained is not explicitly specified, so we will actually get the value at the end of the min_delay timestep
                return "__target.get_" + variable.get_alternate_name() + "()"

            # grab the value from the postsynaptic spiking history buffer
            return "start.get_" + _name + "()"

        if variable.get_name() == PredefinedVariables.E_CONSTANT:
            return "math.e"

        if variable.get_name() == PredefinedVariables.PI_CONSTANT:
            return "math.pi"

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
            vector_param = "[" + self._expression_printer.print(variable.get_vector_parameter()) + "]"

        if symbol.is_buffer():
            if isinstance(symbol.get_type_symbol(), UnitTypeSymbol):
                units_conversion_factor = NESTUnitConverter.get_factor(symbol.get_type_symbol().unit.unit)
            else:
                units_conversion_factor = 1
            s = ""
            if not units_conversion_factor == 1:
                s += "(" + str(units_conversion_factor) + " * "
            s += self._print(variable, symbol, with_origin=self.with_origin) + vector_param
            s += vector_param
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

    def _print_delay_variable(self, variable: ASTVariable):
        """
        Converts a delay variable to NEST processable format
        :param variable:
        :return:
        """
        symbol = variable.get_scope().resolve_to_symbol(variable.get_complete_name(), SymbolKind.VARIABLE)
        if symbol:
            if symbol.is_state() and symbol.has_delay_parameter():
                return "get_delayed_" + variable.get_name() + "()"
        return ""

    def _print(self, variable, symbol, with_origin: bool = True) -> str:
        variable_name = PythonVariablePrinter._print_python_name(variable.get_complete_name())

        if variable_name in ["dt", "__h"]:
            return "dt"

        if variable.is_delay_variable():
            raise Exception("The GeNN code generator does not yet support delay variables")

        return "pars[\"" + variable_name + "\"]"
