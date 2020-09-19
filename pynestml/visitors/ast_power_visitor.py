# -*- coding: utf-8 -*-
#
# ast_power_visitor.py
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

"""
rhs : <assoc=right> left=rhs powOp='**' right=rhs
"""
from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.symbols.unit_type_symbol import UnitTypeSymbol
from pynestml.utils.either import Either
from pynestml.utils.error_strings import ErrorStrings
from pynestml.visitors.ast_visitor import ASTVisitor


class ASTPowerVisitor(ASTVisitor):
    """
    Visits a single power rhs and updates its types accordingly.
    """

    def visit_expression(self, node):
        """
        Visits a single power expression and updates the types.
        :param node: a single expression.
        :type node: ASTExpression
        """
        base_type = node.get_lhs().type
        exponent_type = node.get_rhs().type

        base_type.referenced_object = node.get_lhs()
        exponent_type.referenced_object = node.get_rhs()

        if base_type.is_instance_of(UnitTypeSymbol):
            node.type = self.try_to_calculate_resulting_unit(node)
            return
        else:
            node.type = base_type ** exponent_type
            return

    def try_to_calculate_resulting_unit(self, expr):
        base_type = expr.get_lhs().type
        exponent_numeric_value_either = self.calculate_numeric_value(expr.get_rhs())
        if exponent_numeric_value_either.is_value():
            return base_type ** exponent_numeric_value_either.get_value()
        else:
            return base_type ** None

    def calculate_numeric_value(self, expr):
        """
        Calculates the numeric value of a exponent.
        :param expr: a single expression
        :type expr: ASTSimpleExpression or ASTExpression
        :return: an Either object
        :rtype: Either
        """
        # TODO write tests for this by PTraeder
        if isinstance(expr, ASTExpression) and expr.is_encapsulated:
            return self.calculate_numeric_value(expr.get_expression())
        elif isinstance(expr, ASTSimpleExpression) and expr.get_numeric_literal() is not None:
            if isinstance(expr.get_numeric_literal(), int) \
                    or isinstance(expr.get_numeric_literal(), float):
                literal = expr.get_numeric_literal()
                return Either.value(literal)
            else:
                error_message = ErrorStrings.message_unit_base(self, expr.get_source_position())
                return Either.error(error_message)
        elif expr.is_unary_operator() and expr.get_unary_operator().is_unary_minus:
            term = self.calculate_numeric_value(expr.get_expression())
            if term.is_error():
                return term
            return Either.value(-term.get_value())
        error_message = ErrorStrings.message_non_constant_exponent(self, expr.get_source_position())
        return Either.error(error_message)
