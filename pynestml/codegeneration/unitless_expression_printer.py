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

from pynestml.codegeneration.expressions_pretty_printer import ExpressionsPrettyPrinter
from pynestml.codegeneration.i_reference_converter import IReferenceConverter
from pynestml.codegeneration.nestml_reference_converter import NestMLReferenceConverter
from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.symbols.symbol import SymbolKind
from pynestml.symbols.predefined_units import PredefinedUnits
from pynestml.codegeneration.unit_converter import UnitConverter


class UnitlessExpressionPrinter(ExpressionsPrettyPrinter):
    """
    An adjusted version of the pretty printer which does not print units with literals.
    """

    def __init__(self, reference_converter=None, types_printer=None):
        """
        Standard constructor.
        :param reference_converter: a single reference converter object.
        :type reference_converter: IReferenceConverter
        """
        super(UnitlessExpressionPrinter, self).__init__(
            reference_converter=reference_converter, types_printer=types_printer)

    def print_expression(self, node, prefix=''):
        """Print an expression.

        Parameters
        ----------
        node : ASTExpressionNode
            The expression node to print.
        prefix : str
            *See documentation for the function ExpressionsPrettyPrinter::print_function_call().*


        Returns
        -------
        s : str
            The expression string.
        """
        # todo : printing of literals etc. should be done by constant converter, not a type converter
        if isinstance(node, ASTSimpleExpression):
            if node.is_numeric_literal():
                return self.types_printer.pretty_print(node.get_numeric_literal())
            elif node.is_variable() and node.get_scope() is not None:
                node_is_variable_symbol = node.get_scope().resolve_to_symbol(
                    node.variable.get_complete_name(), SymbolKind.VARIABLE) is not None
                if not node_is_variable_symbol and PredefinedUnits.is_unit(node.variable.get_complete_name()):
                    # case for a literal unit, e.g. "ms"
                    return str(UnitConverter.get_factor(PredefinedUnits.get_unit(node.variable.get_complete_name()).get_unit()))

        return super(UnitlessExpressionPrinter, self).print_expression(node, prefix=prefix)
