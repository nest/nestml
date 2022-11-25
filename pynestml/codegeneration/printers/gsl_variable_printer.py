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

from pynestml.codegeneration.printers.cpp_variable_printer import CppVariablePrinter
from pynestml.codegeneration.printers.unit_converter import UnitConverter
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.symbols.predefined_units import PredefinedUnits
from pynestml.symbols.predefined_variables import PredefinedVariables
from pynestml.symbols.symbol import SymbolKind
from pynestml.symbols.unit_type_symbol import UnitTypeSymbol
from pynestml.symbols.variable_symbol import VariableSymbol
from pynestml.utils.ast_utils import ASTUtils
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages


class GSLVariablePrinter(CppVariablePrinter):
    r"""
    Reference converter for C++ syntax and using the GSL (GNU Scientific Library) API from inside the ``extern "C"`` stepping function.
    """

    def print_variable(self, node: ASTVariable, prefix: str = '') -> str:
        """
        Converts a single name reference to a gsl processable format.
        :param node: a single variable
        :return: a gsl processable format of the variable
        """
        assert isinstance(node, ASTVariable)
        symbol = node.get_scope().resolve_to_symbol(node.get_complete_name(), SymbolKind.VARIABLE)

        if symbol.is_state() and not symbol.is_inline_expression:
            # ode_state[] here is---and must be---the state vector supplied by the integrator, not the state vector in the node, node.S_.ode_state[].
            return "ode_state[State_::" + CppVariablePrinter._print_cpp_name(node.get_complete_name()) + "]"

        if symbol.is_parameters():
            return "node.P_." + super().print_variable(node, prefix)

        if symbol.is_internals():
            return "node.V_." + super().print_variable(node, prefix)

        if symbol.is_input():
            return "node.B_." + super().print_variable(node, prefix) + "_grid_sum_"

        raise Exception("Unknown node type")

    def print_delay_variable(self, variable: ASTVariable, prefix: str =""):
        """
        Converts a delay variable to GSL processable format
        :param variable: variable to be converted
        :return: GSL processable format of the delay variable
        """
        symbol = variable.get_scope().resolve_to_symbol(variable.get_complete_name(), SymbolKind.VARIABLE)
        if symbol:
            if symbol.is_state() and symbol.has_delay_parameter():
                return prefix + "get_delayed_" + variable.get_name() + "()"

        raise RuntimeError(f"Cannot find the corresponding symbol for variable {variable.get_name()}")
