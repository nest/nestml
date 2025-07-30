# -*- coding: utf-8 -*-
#
# c_simple_expression_printer.py
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

from pynestml.codegeneration.printers.simple_expression_printer import SimpleExpressionPrinter
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.codegeneration.printers.c_simple_expression_printer import CSimpleExpressionPrinter

class Spinnaker2CSimpleExpressionPrinter(CSimpleExpressionPrinter):
    r"""
    Printer for ASTSimpleExpressions in C syntax for SpiNNaker2
    Currently floats are used for everything, thus a 'f' is added to numeric literals like '2.0' to become '2.0f'
    """

    def print_simple_expression(self, node: ASTSimpleExpression) -> str:
        if node.has_unit():
            if self._variable_printer.print(node.get_variable()) in ["1", "1.", "1.0"]:
                return str(node.get_numeric_literal())

            return str(node.get_numeric_literal()) + " * " + self._variable_printer.print(node.get_variable())

        if node.is_numeric_literal():
            return str(float(str(node.get_numeric_literal())))+"f"

        return super().print_simple_expression(node)