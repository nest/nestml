# -*- coding: utf-8 -*-
#
# ode_toolbox_expression_printer.py
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

from pynestml.codegeneration.printers.cpp_expression_printer import CppExpressionPrinter
from pynestml.meta_model.ast_expression import ASTExpression


class ODEToolboxExpressionPrinter(CppExpressionPrinter):
    r"""
    Printer for ``ASTExpression`` nodes in ODE-toolbox syntax.
    """

    def print_ternary_operator(self, node: ASTExpression) -> str:
        """
        Prints a ternary operator. ODE-toolbox cannot handle this, so default to just printing the if-true case.
        :return: a string representation
        """
        if_true = self.print(node.get_if_true())

        return if_true