# -*- coding: utf-8 -*-
#
# sympy_simple_expression_printer.py
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

from pynestml.codegeneration.nest_unit_converter import NESTUnitConverter
from pynestml.codegeneration.printers.cpp_simple_expression_printer import CppSimpleExpressionPrinter
from pynestml.codegeneration.printers.simple_expression_printer import SimpleExpressionPrinter
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.symbols.predefined_units import PredefinedUnits
from pynestml.symbols.symbol import SymbolKind


class SympySimpleExpressionPrinter(CppSimpleExpressionPrinter):
    r"""
    Printer for ASTSimpleExpressions in Sympy syntax.
    """

    def print_simple_expression(self, node: ASTSimpleExpression) -> str:

        if node.is_numeric_literal():
            return self._constant_printer.print_constant(node.get_numeric_literal())

        if node.is_variable() and node.get_scope() is not None:
            node_is_variable_symbol = node.get_scope().resolve_to_symbol(
                node.variable.get_complete_name(), SymbolKind.VARIABLE) is not None
            if not node_is_variable_symbol and PredefinedUnits.is_unit(node.variable.get_complete_name()):
                # case for a literal unit, e.g. "ms"
                return str(NESTUnitConverter.get_factor(PredefinedUnits.get_unit(node.variable.get_complete_name()).get_unit()))

        if node.has_unit():
            if self._variable_printer.print(node.get_variable()) in ["1", "1.", "1.0"]:
                return str(node.get_numeric_literal())

            return str(node.get_numeric_literal()) + " * " + \
                self._variable_printer.print(node.get_variable())

        if node.is_numeric_literal():
            return str(node.get_numeric_literal())

        if node.is_inf_literal:
            return 'oo'

        if node.is_string():
            return str(node.get_string())

        if node.is_boolean_true:
            return 'true'

        if node.is_boolean_false:
            return 'false'

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
