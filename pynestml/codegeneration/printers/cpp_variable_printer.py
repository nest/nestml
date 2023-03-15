# -*- coding: utf-8 -*-
#
# cpp_variable_printer.py
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

from pynestml.codegeneration.printers.variable_printer import VariablePrinter
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.symbols.predefined_variables import PredefinedVariables


class CppVariablePrinter(VariablePrinter):

    @classmethod
    def _print_cpp_name(cls, variable_name: str) -> str:
        """
        Converts a handed over name to the corresponding NEST/C++ naming guideline. This is chosen to be compatible with the naming strategy for ode-toolbox, such that the variable name in a NESTML statement like "G_ahp' += 1" will be converted into "G_ahp__d".

        :param variable_name: a single name.
        :return: a string representation
        """
        differential_order = variable_name.count("\"")
        if differential_order > 0:
            return variable_name.replace("\"", "").replace("$", "__DOLLAR") + "__" + "d" * differential_order

        return variable_name.replace("$", "__DOLLAR")

    def print_variable(self, node: ASTVariable) -> str:
        """
        Print a variable.
        :param node: a single variable symbol or variable
        :return: a string representation
        """
        assert isinstance(node, ASTVariable)

        if node.get_name() == PredefinedVariables.E_CONSTANT:
            return "numerics::e"

        return CppVariablePrinter._print_cpp_name(node.get_complete_name())
