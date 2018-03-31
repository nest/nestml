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
Expr = unaryOperator term=expression
unaryOperator : (unaryPlus='+' | unaryMinus='-' | unaryTilde='~');
"""
from pynestml.modelprocessor.ASTUnaryOperator import ASTUnaryOperator
from pynestml.modelprocessor.ErrorStrings import ErrorStrings
from pynestml.modelprocessor.ASTVisitor import ASTVisitor
from pynestml.modelprocessor.Either import Either
from pynestml.modelprocessor.ASTExpression import ASTExpression
from pynestml.utils.Logger import Logger, LOGGING_LEVEL


class ASTUnaryVisitor(ASTVisitor):
    """
    Visits an expression consisting of a unary operator, e.g., -, and a sub-expression.
    """

    def visitExpression(self, _expr=None):
        """
        Visits a single unary operator and updates the type of the corresponding expression.
        :param _expr: a single expression
        :type _expr: ASTExpression
        """
        assert (_expr is not None and isinstance(_expr, ASTExpression)), \
            '(PyNestML.Visitor.UnaryVisitor) No or wrong type of expression provided (%s)!' % type(_expr)

        term_type_e = _expr.getExpression().getTypeEither()

        if term_type_e.isError():
            _expr.setTypeEither(term_type_e)
            return

        term_type = term_type_e.getValue()
        unary_op = _expr.getUnaryOperator()
        # unaryOp exists if we get into this visitor but make sure:
        assert unary_op is not None and isinstance(unary_op, ASTUnaryOperator)

        if unary_op.isUnaryMinus() or unary_op.isUnaryPlus():
            if term_type.isNumeric():
                _expr.setTypeEither(Either.value(term_type))
                return
            else:
                error_msg = ErrorStrings.messageNonNumericType(self, term_type.printSymbol(), _expr.get_source_position())
                _expr.setTypeEither(Either.error(error_msg))
                Logger.logMessage(error_msg, LOGGING_LEVEL.ERROR)
                return
        elif unary_op.isUnaryTilde():
            if term_type.isInteger():
                _expr.setTypeEither(Either.value(term_type))
                return
            else:
                error_msg = ErrorStrings.messageNonNumericType(self, term_type.printSymbol(), _expr.get_source_position())
                _expr.setTypeEither(Either.error(error_msg))
                Logger.logMessage(error_msg, LOGGING_LEVEL.ERROR)
                return
        # Catch-all if no case has matched
        error_msg = ErrorStrings.messageTypeError(self, str(_expr), _expr.get_source_position())
        Logger.logMessage(error_msg, LOGGING_LEVEL.ERROR)
        _expr.setTypeEither(Either.error(error_msg))
        return
