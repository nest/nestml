# -*- coding: utf-8 -*-
#
# spinnaker_python_simple_expression_printer.py
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

from spinn_front_end_common.interface.ds import DataType

from pynestml.codegeneration.printers.simple_expression_printer import SimpleExpressionPrinter
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.meta_model.ast_variable import ASTVariable


class SpinnakerPythonSimpleExpressionPrinter(SimpleExpressionPrinter):
    r"""
    Printer for ASTSimpleExpressions in Python syntax.
    """

    def print_simple_expression(self, node: ASTSimpleExpression) -> str:
        if node.has_unit():
            if self._variable_printer.print(node.get_variable()) in ["1", "1.", "1.0"]:
                return str(node.get_numeric_literal())

            return str(node.get_numeric_literal()) + " * " + \
                self._variable_printer.print(node.get_variable())

        if isinstance(node, ASTVariable):
            return self._variable_printer.print(node.get_variable())

        if node.is_numeric_literal():
            return str(node.get_numeric_literal())

        if node.is_inf_literal:
            return str(DataType.S1615.max)  # Max value of s1615 datatype

        if node.is_string():
            return str(node.get_string())

        if node.is_boolean_true:
            # Spinnaker supports no bool datatype
            return '1'

        if node.is_boolean_false:
            # Spinnaker supports no bool datatype
            return '0'

        if node.is_variable() or node.is_delay_variable():
            return self._variable_printer.print(node.get_variable())

        if node.is_function_call():
            return self._function_call_printer.print_function_call(node.get_function_call())

        raise Exception("Unknown node type: " + str(node))

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
