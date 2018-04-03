#
# UnaryVisitor.py
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
Expr = unaryOperator term=rhs
unaryOperator : (unaryPlus='+' | unaryMinus='-' | unaryTilde='~');
"""
from pynestml.modelprocessor.ASTExpression import ASTExpression
from pynestml.modelprocessor.ASTUnaryOperator import ASTUnaryOperator
from pynestml.modelprocessor.ASTVisitor import ASTVisitor
from pynestml.modelprocessor.Either import Either
from pynestml.modelprocessor.ErrorStrings import ErrorStrings
from pynestml.utils.Logger import Logger, LoggingLevel


class ASTUnaryVisitor(ASTVisitor):
    """
    Visits an rhs consisting of a unary operator, e.g., -, and a sub-rhs.
    """

    def visit_expression(self, node):
        """
        Visits a single unary operator and updates the type of the corresponding rhs.
        :param node: a single rhs
        :type node: ASTExpression
        """
        term_type_e = node.get_expression().get_type_either()

        if term_type_e.isError():
            node.set_type_either(term_type_e)
            return

        term_type = term_type_e.getValue()
        unary_op = node.get_unary_operator()
        # unaryOp exists if we get into this visitor but make sure:
        assert unary_op is not None and isinstance(unary_op, ASTUnaryOperator)

        if unary_op.isUnaryMinus() or unary_op.isUnaryPlus():
            if term_type.is_numeric():
                node.set_type_either(Either.value(term_type))
                return
            else:
                error_msg = ErrorStrings.messageNonNumericType(self, term_type.print_symbol(),
                                                               node.get_source_position())
                node.set_type_either(Either.error(error_msg))
                Logger.log_message(error_msg, LoggingLevel.ERROR)
                return
        elif unary_op.isUnaryTilde():
            if term_type.is_integer():
                node.set_type_either(Either.value(term_type))
                return
            else:
                error_msg = ErrorStrings.messageNonNumericType(self, term_type.print_symbol(),
                                                               node.get_source_position())
                node.set_type_either(Either.error(error_msg))
                Logger.log_message(error_msg, LoggingLevel.ERROR)
                return
        # Catch-all if no case has matched
        error_msg = ErrorStrings.messageTypeError(self, str(node), node.get_source_position())
        Logger.log_message(error_msg, LoggingLevel.ERROR)
        node.set_type_either(Either.error(error_msg))
        return
