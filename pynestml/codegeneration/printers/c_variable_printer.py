# -*- coding: utf-8 -*-
#
# c_variable_printer.py
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


class CVariablePrinter(VariablePrinter):

    def print_variable(self, node: ASTVariable) -> str:
        """
        Print a variable.
        :param node: a single variable symbol or variable
        :return: a string representation
        """
        assert isinstance(node, ASTVariable)

        if node.get_name() == PredefinedVariables.E_CONSTANT:
            return "REAL_CONST(2.718282)"

        return CppVariablePrinter._print_cpp_name(node.get_complete_name())
