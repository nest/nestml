# -*- coding: utf-8 -*-
#
# nestml_simple_expression_printer.py
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


class NESTMLSimpleExpressionPrinter(SimpleExpressionPrinter):
    r"""
    Printer for ASTSimpleExpressions in NESTML syntax.
    """

    def _print(self, node: ASTNode) -> str:
        if isinstance(node, ASTVariable):
            return self._variable_printer.print(node)

        if isinstance(node, ASTFunctionCall):
            return self._function_call_printer.print(node)

        return self.print_simple_expression(node)

    def print(self, node: ASTNode) -> str:
        if node.get_implicit_conversion_factor() and not node.get_implicit_conversion_factor() == 1:
            return "(" + str(node.get_implicit_conversion_factor()) + " * (" + self._print(node) + "))"

        return self._print(node)

    def print_simple_expression(self, node: ASTSimpleExpression) -> str:
        if node.is_function_call():
            return self.print(node.function_call)

        if node.is_boolean_true:
            return "true"

        if node.is_boolean_false:
            return "false"

        if node.is_inf_literal:
            return "inf"

        if node.is_numeric_literal():
            if node.variable is not None:
                # numeric literal + physical unit
                return str(node.numeric_literal) + self.print(node.variable)

            return str(node.numeric_literal)

        if node.is_variable():
            return self._variable_printer.print_variable(node.get_variable())

        if node.is_string():
            return node.get_string()

        raise RuntimeError("Simple rhs at %s not specified!" % str(node.get_source_position()))
