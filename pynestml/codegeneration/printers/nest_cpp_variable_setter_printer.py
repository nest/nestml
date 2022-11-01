# -*- coding: utf-8 -*-
#
# nest_cpp_variable_setter_printer.py
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

from pynestml.codegeneration.printers.nest_variable_printer import CppVariablePrinter
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_variable import ASTVariable


class NESTCppVariableSetterPrinter(CppVariablePrinter):
    r"""
    This is a printer for ASTVariables in C++ syntax. Nodes will be printed as calls to their setter methods.
    """

    def print_variable(self, node: ASTVariable, prefix: str = "") -> str:
        """
        Converts for a handed over symbol the corresponding name of the setter to a nest processable format.
        :param variable_symbol: a single variable symbol.
        :return: a string representation
        """
        assert isinstance(node, ASTVariable), "This printer can only print ``ASTVariable`` nodes"
        variable_symbol = node.get_type_symbol()
        return 'set_' + self._print_cpp_name(variable_symbol.get_symbol_name())
