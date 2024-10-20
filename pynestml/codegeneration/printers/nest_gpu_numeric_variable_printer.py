# -*- coding: utf-8 -*-
#
# nest_gpu_numeric_variable_printer.py
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
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.symbols.predefined_variables import PredefinedVariables
from pynestml.symbols.symbol import SymbolKind


class NESTGPUNumericVariablePrinter(CppVariablePrinter):
    """
    Variable printer for numeric (RK5) solver syntax for the NEST-GPU target
    """

    def print_variable(self, node: ASTVariable) -> str:
        """
        Converts a single name reference to a format that supports APIs from RK5 numeric solver in NEST-GPU
        """
        assert isinstance(node, ASTVariable)

        if node.get_name() == PredefinedVariables.E_CONSTANT:
            return "M_E"
        
        symbol = node.get_scope().resolve_to_symbol(node.get_complete_name(), SymbolKind.VARIABLE)

        var_cpp_name = super().print_variable(node)
        if symbol.is_state() and not symbol.is_inline_expression:
            return "y[i_" + var_cpp_name + "]"
        
        if symbol.is_parameters() or symbol.is_internals() or symbol.is_continuous_input_port():
            return "param[i_" + var_cpp_name + "]"
        
        if symbol.is_spike_input_port():
            return "y[N_SCAL_VAR + i_" + symbol.get_symbol_name() + "]"

        raise Exception("Unknown node type: " + symbol.get_symbol_name())
