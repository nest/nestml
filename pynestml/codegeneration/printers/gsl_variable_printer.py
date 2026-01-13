# -*- coding: utf-8 -*-
#
# gsl_variable_printer.py
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
from pynestml.codegeneration.nest_code_generator_utils import NESTCodeGeneratorUtils
from pynestml.codegeneration.nest_unit_converter import NESTUnitConverter
from pynestml.codegeneration.printers.cpp_variable_printer import CppVariablePrinter
from pynestml.codegeneration.printers.expression_printer import ExpressionPrinter
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.symbols.predefined_units import PredefinedUnits
from pynestml.symbols.symbol import SymbolKind
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages


class GSLVariablePrinter(CppVariablePrinter):
    r"""
    Variable printer for C++ syntax and using the GSL (GNU Scientific Library) API from inside the ``extern "C"`` stepping function.
    """

    def __init__(self, expression_printer: ExpressionPrinter, with_origin: bool = True, ):
        super().__init__(expression_printer)
        self.with_origin = with_origin

    def print_variable(self, variable: ASTVariable) -> str:
        """
        Converts a single name reference to a gsl processable format.
        :param variable: a single variable
        :return: a gsl processable format of the variable
        """
        assert isinstance(variable, ASTVariable)
        symbol = variable.get_scope().resolve_to_symbol(variable.get_complete_name(), SymbolKind.VARIABLE)

        if symbol is None:
            # test if variable name can be resolved to a type
            if PredefinedUnits.is_unit(variable.get_complete_name()):
                return str(
                    NESTUnitConverter.get_factor(PredefinedUnits.get_unit(variable.get_complete_name()).get_unit()))

            code, message = Messages.get_could_not_resolve(variable.get_name())
            Logger.log_message(log_level=LoggingLevel.ERROR, code=code, message=message,
                               error_position=variable.get_source_position())
            return ""

        if variable.is_delay_variable():
            return self._print_delay_variable(variable)

        if symbol.is_state() and not symbol.is_inline_expression:
            if "_is_numeric" in dir(variable) and variable._is_numeric:
                # ode_state[] here is---and must be---the state vector supplied by the integrator, not the state vector in the node, node.S_.ode_state[].
                return "ode_state[State_::" + CppVariablePrinter._print_cpp_name(variable.get_complete_name()) + "]"

        if symbol.is_input():
            return "node.B_." + self._print_buffer_value(variable)

        return self._print(variable, symbol, with_origin=self.with_origin)

    def _print_delay_variable(self, variable: ASTVariable) -> str:
        """
        Converts a delay variable to GSL processable format
        :param variable: variable to be converted
        :return: GSL processable format of the delay variable
        """
        symbol = variable.get_scope().resolve_to_symbol(variable.get_complete_name(), SymbolKind.VARIABLE)
        if symbol and symbol.is_state() and symbol.has_delay_parameter():
            return "node.get_delayed_" + variable.get_name() + "()"

        raise RuntimeError(f"Cannot find the corresponding symbol for variable {variable.get_name()}")

    def _print_buffer_value(self, variable: ASTVariable) -> str:
        """
        Converts for a handed over symbol the corresponding name of the buffer to a nest processable format.
        :param variable: a single variable symbol.
        :return: the corresponding representation as a string
        """
        variable_symbol = variable.get_scope().resolve_to_symbol(variable.get_complete_name(), SymbolKind.VARIABLE)
        if variable_symbol.is_spike_input_port():
            var_name = variable_symbol.get_symbol_name().upper()
            if variable.has_vector_parameter():
                if variable.get_vector_parameter().is_variable():
                    # the enum corresponding to the first input port in a vector of input ports will have the _0 suffixed to the enum's name.
                    var_name += "_0 + " + variable.get_vector_parameter().get_variable().get_name()
                else:
                    var_name += "_" + str(variable.get_vector_parameter())

            # add variable attribute if it exists
            if variable.attribute:
                return "spike_input_" + str(variable.name) + "__DOT__" + variable.attribute + "_grid_sum_"

            return "spike_input_" + str(variable) + "_grid_sum_"

        # case of continuous-type input port
        assert variable_symbol.is_continuous_input_port()
        return variable_symbol.get_symbol_name() + '_grid_sum_'

    def _print(self, variable, symbol, with_origin: bool = True):
        variable_name = CppVariablePrinter._print_cpp_name(variable.get_complete_name())
        if with_origin:
            return "node." + NESTCodeGeneratorUtils.print_symbol_origin(symbol, variable) % variable_name
        return "node." + variable_name
