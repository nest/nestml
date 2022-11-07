# -*- coding: utf-8 -*-
#
# unitless_expression_printer.py
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
from pynestml.codegeneration.printers.unit_converter import UnitConverter
from pynestml.meta_model.ast_expression_node import ASTExpressionNode
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.symbols.symbol import SymbolKind
from pynestml.symbols.predefined_units import PredefinedUnits


class UnitlessExpressionPrinter(CppExpressionPrinter):
    r"""
    An adjusted version of the printer which does not print units with literals.
    """

    def print_expression(self, node: ASTExpressionNode, prefix: str = "") -> str:
        r"""Print an expression.

        Parameters
        ----------
        node
            The expression node to print.
        prefix
            *See documentation for the function CppExpressionsPrinter::print_function_call().*

        Returns
        -------
        s
            The expression string.
        """
        if isinstance(node, ASTSimpleExpression):
            if node.is_numeric_literal():
                return self.reference_converter.convert_constant(node.get_numeric_literal())

            if node.is_variable() and node.get_scope() is not None:
                node_is_variable_symbol = node.get_scope().resolve_to_symbol(
                    node.variable.get_complete_name(), SymbolKind.VARIABLE) is not None
                if not node_is_variable_symbol and PredefinedUnits.is_unit(node.variable.get_complete_name()):
                    # case for a literal unit, e.g. "ms"
                    return str(UnitConverter.get_factor(PredefinedUnits.get_unit(node.variable.get_complete_name()).get_unit()))

        return super(UnitlessExpressionPrinter, self).print_expression(node, prefix=prefix)
