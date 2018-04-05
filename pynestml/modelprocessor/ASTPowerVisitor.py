#
# ASTPowerVisitor.pyor.py
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
from pynestml.modelprocessor.ASTExpression import ASTExpression
from pynestml.modelprocessor.ASTSimpleExpression import ASTSimpleExpression
from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
from pynestml.modelprocessor.ErrorStrings import ErrorStrings
from pynestml.modelprocessor.ASTVisitor import ASTVisitor
from pynestml.modelprocessor.Either import Either
from pynestml.utils.Logger import Logger, LoggingLevel


class ASTPowerVisitor(ASTVisitor):
    """
    Visits a single power rhs and updates its types accordingly.
    """

    def visit_expression(self, node):
        """
        Visits a single power rhs and updates the types.
        :param node: a single rhs.
        :type node: ASTExpression
        """
        base_type_e = node.get_lhs().get_type_either()
        exponent_type_e = node.get_rhs().get_type_either()

        if base_type_e.is_error():
            node.set_type_either(base_type_e)
            return

        if exponent_type_e.is_error():
            node.set_type_either(exponent_type_e)
            return

        base_type = base_type_e.get_value()
        exponent_type = exponent_type_e.get_value()

        if base_type.is_numeric() and exponent_type.is_numeric():
            if base_type.is_integer() and exponent_type.is_integer():
                node.set_type_either(Either.value(PredefinedTypes.get_integer_type()))
                return
            elif base_type.is_unit():
                # exponents to units MUST be integer and calculable at time of analysis.
                # Otherwise resulting unit is undefined
                if not exponent_type.is_integer():
                    error_msg = ErrorStrings.messageUnitBase(self, node.get_source_position())
                    node.set_type_either(Either.error(error_msg))
                    Logger.log_message(error_msg, LoggingLevel.ERROR)
                    return
                base_unit = base_type.get_encapsulated_unit()
                # TODO the following part is broken @ptraeder?
                exponent_value = self.calculate_numeric_value(
                    node.get_rhs())  # calculate exponent value if exponent composed of literals
                if exponent_value.is_value():
                    node.set_type_either(
                        Either.value(PredefinedTypes.get_type(base_unit ** exponent_value.get_value())))
                    return
                else:
                    error_msg = exponent_value.get_error()
                    node.set_type_either(Either.error(error_msg))
                    Logger.log_message(error_msg, LoggingLevel.ERROR)
                    return
            else:
                node.set_type_either(Either.value(PredefinedTypes.get_real_type()))
                return
        # Catch-all if no case has matched
        error_msg = ErrorStrings.messageUnitBase(self, node.get_source_position())
        node.set_type_either(Either.error(error_msg))
        Logger.log_message(error_msg, LoggingLevel.ERROR)

    def calculate_numeric_value(self, expr):
        """
        Calculates the numeric value of a exponent.
        :param expr: a single rhs
        :type expr: ASTSimpleExpression or ASTExpression
        :return: an Either object
        :rtype: Either
        """
        # TODO write tests for this by PTraeder
        if isinstance(expr, ASTExpression) and expr.is_encapsulated:
            return self.calculate_numeric_value(expr.get_expression())
        elif isinstance(expr, ASTSimpleExpression) and expr.get_numeric_literal() is not None:
            if isinstance(expr.get_numeric_literal(), int):
                literal = expr.get_numeric_literal()
                return Either.value(literal)
            else:
                error_message = ErrorStrings.messageUnitBase(self, expr.get_source_position())
                return Either.error(error_message)
        elif expr.is_unary_operator() and expr.get_unary_operator().isUnaryMinus():
            term = self.calculate_numeric_value(expr.get_expression())
            if term.is_error():
                return term
            return Either.value(-term.get_value())
        error_message = ErrorStrings.messageNonConstantExponent(self, expr.get_source_position())
        return Either.error(error_message)
