# -*- coding: utf-8 -*-
#
# latex_simple_expression_printer.py
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
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.meta_model.ast_node import ASTNode


class LatexSimpleExpressionPrinter(SimpleExpressionPrinter):
    r"""
    Printer for ASTSimpleExpressions in LaTeX syntax.
    """

    def print(self, node: ASTNode) -> str:
        if isinstance(node, ASTSimpleExpression):
            return self.print_simple_expression(node)

        return super().print(node)

    def print_simple_expression(self, node: ASTSimpleExpression) -> str:
        assert isinstance(node, ASTSimpleExpression)

        if node.has_unit():
            s = ""
            if node.get_numeric_literal() != 1:
                s += "{0:E}".format(node.get_numeric_literal())
                s += r"\cdot"
            s += self._variable_printer.print(node.get_variable())
            return s

        if node.is_numeric_literal():
            return str(node.get_numeric_literal())

        if node.is_inf_literal:
            return r"\infty"

        if node.is_string():
            return node.get_string()

        if node.is_boolean_true:
            return "true"

        if node.is_boolean_false:
            return "false"

        if node.is_variable():
            return self._variable_printer.print_variable(node.get_variable())

        if node.is_function_call():
            return self._function_call_printer.print(node.get_function_call())

        raise Exception("Unknown node type")
