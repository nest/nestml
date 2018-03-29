#
# ASTBinaryLogicVisitortor.py
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
expression: left=expression logicalOperator right=expression
"""
from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
from pynestml.modelprocessor.ErrorStrings import ErrorStrings
from pynestml.modelprocessor.ASTVisitor import ASTVisitor
from pynestml.modelprocessor.Either import Either
from pynestml.modelprocessor.ASTExpression import ASTExpression
from pynestml.utils.Logger import Logger, LOGGING_LEVEL


class ASTBinaryLogicVisitor(ASTVisitor):
    """
    Visits a single binary logical operator expression and updates its types.
    """

    def visitExpression(self, _expr=None):
        """
        Visits an expression which uses a binary logic operator and updates the type.
        :param _expr: a single expression.
        :type _expr: ASTExpression
        """
        assert (_expr is not None and isinstance(_expr, ASTExpression)), \
            '(PyNestML.Visitor.ASTBinaryLogicVisitor) No or wrong type of expression provided (%s)!' % type(_expr)
        lhs_type = _expr.getLhs().getTypeEither()
        rhs_type = _expr.getRhs().getTypeEither()

        if lhs_type.isError():
            _expr.setTypeEither(lhs_type)
            return
        if rhs_type.isError():
            _expr.setTypeEither(rhs_type)
            return

        if lhs_type.getValue().isBoolean() and rhs_type.getValue().isBoolean():
            _expr.setTypeEither(Either.value(PredefinedTypes.getBooleanType()))
        else:
            error_msg = ErrorStrings.messageLogicOperandsNotBool(self, _expr.getSourcePosition())
            _expr.setTypeEither(Either.error(error_msg))
            Logger.logMessage(error_msg, LOGGING_LEVEL.ERROR)
        return
