# -*- coding: utf-8 -*-
#
# python_stepping_function_variable_printer.py
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

from pynestml.codegeneration.printers.cpp_variable_printer import CppVariablePrinter
from pynestml.codegeneration.printers.variable_printer import VariablePrinter
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.symbols.predefined_variables import PredefinedVariables
from pynestml.symbols.symbol import SymbolKind


class PythonSteppingFunctionVariablePrinter(VariablePrinter):
    r"""
    Printer for variables in Python syntax and in the context of an ODE solver stepping function.
    """

    def print_variable(self, node: ASTVariable) -> str:
        """
        Print a variable.
        :param node: the variable to be printed
        :return: the string representation
        """
        assert isinstance(node, ASTVariable)

        if node.get_name() == PredefinedVariables.E_CONSTANT:
            return "np.e"

        symbol = node.get_scope().resolve_to_symbol(node.get_complete_name(), SymbolKind.VARIABLE)

        if symbol.is_state() and not symbol.is_inline_expression:
            if "_is_numeric" in dir(node) and node._is_numeric:
                # ode_state[] here is---and must be---the state vector supplied by the integrator, not the state vector in the node, node.S_.ode_state[].
                return "ode_state[node.S_.ode_state_variable_name_to_index[\"" + CppVariablePrinter._print_cpp_name(node.get_complete_name()) + "\"]]"

            # non-ODE state symbol
            return "node.S_." + CppVariablePrinter._print_cpp_name(node.get_complete_name())

        if symbol.is_parameters():
            return "node.P_." + CppVariablePrinter._print_cpp_name(node.get_complete_name())

        if symbol.is_internals():
            return "node.V_." + CppVariablePrinter._print_cpp_name(node.get_complete_name())

        if symbol.is_input():
            return "node.B_." + CppVariablePrinter._print_cpp_name(node.get_complete_name())

        raise Exception("Unknown node type")

    def print_delay_variable(self, variable: ASTVariable) -> str:
        """
        Print a delay variable.
        :param variable: the variable to be printed
        :return: the string representation
        """
        symbol = variable.get_scope().resolve_to_symbol(variable.get_complete_name(), SymbolKind.VARIABLE)
        if symbol:
            if symbol.is_state() and symbol.has_delay_parameter():
                return "get_delayed_" + variable.get_name() + "()"

        raise RuntimeError(f"Cannot find the corresponding symbol for variable {variable.get_name()}")
