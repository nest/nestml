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
from pynestml.utils.ast_utils import ASTUtils

from pynestml.codegeneration.printers.cpp_variable_printer import CppVariablePrinter
from pynestml.codegeneration.printers.expression_printer import ExpressionPrinter
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.symbols.symbol import SymbolKind


class GSLVariablePrinter(CppVariablePrinter):
    r"""
    Reference converter for C++ syntax and using the GSL (GNU Scientific Library) API from inside the ``extern "C"`` stepping function.
    """

    def print_variable(self, node: ASTVariable) -> str:
        """
        Converts a single name reference to a gsl processable format.
        :param node: a single variable
        :return: a gsl processable format of the variable
        """
        assert isinstance(node, ASTVariable)
        symbol = node.get_scope().resolve_to_symbol(node.get_complete_name(), SymbolKind.VARIABLE)

        if node.is_delay_variable():
            return self._print_delay_variable(node)

        if symbol.is_state() and not symbol.is_inline_expression:
            if "_is_numeric" in dir(node) and node._is_numeric:
                # ode_state[] here is---and must be---the state vector supplied by the integrator, not the state vector in the node, node.S_.ode_state[].
                return "ode_state[State_::" + CppVariablePrinter._print_cpp_name(node.get_complete_name()) + "]"

            # non-ODE state symbol
            return "node.S_." + CppVariablePrinter._print_cpp_name(node.get_complete_name())

        if symbol.is_parameters():
            return "node.P_." + super().print_variable(node)

        if symbol.is_internals():
            return "node.V_." + super().print_variable(node)

        if symbol.is_input():
            return "node.B_." + self._print_buffer_value(node)

        raise Exception("Unknown node type")

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
            if variable_symbol.get_vector_parameter() is not None:
                vector_parameter = ASTUtils.get_numeric_vector_size(variable_symbol)
                var_name = var_name + "_" + str(vector_parameter)

            return "spike_inputs_grid_sum_[node." + var_name + " - node.MIN_SPIKE_RECEPTOR]"

        return variable_symbol.get_symbol_name() + '_grid_sum_'
