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
from pynestml.codegeneration.nest_unit_converter import NESTUnitConverter
from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.symbols.predefined_units import PredefinedUnits
from pynestml.symbols.symbol import SymbolKind
from pynestml.symbols.unit_type_symbol import UnitTypeSymbol
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
        exponent_numeric_value = self.calculate_numeric_value(expr.get_rhs())
        return base_type ** exponent_numeric_value

    def calculate_numeric_value(self, expr):
        """
        Calculates the numeric value of a exponent.
        :param expr: a single expression
        :type expr: ASTSimpleExpression or ASTExpression
        :return: a numeric value or unit type
        """
        if isinstance(expr, ASTExpression):
            if expr.is_encapsulated:
                return self.calculate_numeric_value(expr.get_expression())

            if expr.is_unary_operator() and expr.get_unary_operator().is_unary_minus:
                term = self.calculate_numeric_value(expr.get_expression())
                return -term

            if expr.get_binary_operator() is not None:
                op = expr.get_binary_operator()
                lhs = expr.get_lhs()
                rhs = expr.get_rhs()
                if op.is_plus_op:
                    return self.calculate_numeric_value(lhs) + self.calculate_numeric_value(rhs)

                if op.is_minus_op:
                    return self.calculate_numeric_value(lhs) - self.calculate_numeric_value(rhs)

                if op.is_times_op:
                    return self.calculate_numeric_value(lhs) * self.calculate_numeric_value(rhs)

                if op.is_div_op:
                    return self.calculate_numeric_value(lhs) / self.calculate_numeric_value(rhs)

                if op.is_modulo_op:
                    return self.calculate_numeric_value(lhs) % self.calculate_numeric_value(rhs)

            return self.calculate_numeric_value(expr)

        if isinstance(expr, ASTSimpleExpression):
            if expr.get_numeric_literal() is not None:
                if isinstance(expr.get_numeric_literal(), int) \
                        or isinstance(expr.get_numeric_literal(), float):
                    literal = expr.get_numeric_literal()
                    return literal

                error_message = ErrorStrings.message_unit_base(self, expr.get_source_position())

                raise Exception(error_message)

            # expr is a variable
            variable = expr.get_variable()
            symbol = variable.get_scope().resolve_to_symbol(variable.get_complete_name(), SymbolKind.VARIABLE)
            if symbol is None:
                if PredefinedUnits.is_unit(variable.get_complete_name()):
                    return NESTUnitConverter.get_factor(PredefinedUnits.get_unit(variable.get_complete_name()).get_unit())

                raise Exception("Declaration for symbol '" + str(variable) + "' not found and is not a unit.")

            return self.calculate_numeric_value(symbol.get_declaring_expression())

        error_message = ErrorStrings.message_non_constant_exponent(self, expr.get_source_position())
        raise Exception(error_message)
