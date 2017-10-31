#
# LogicalNotVisitor.py
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
expression: logicalNot='not' term=expression
"""
from pynestml.nestml.PredefinedTypes import PredefinedTypes
from pynestml.nestml.ErrorStrings import ErrorStrings
from pynestml.nestml.NESTMLVisitor import NESTMLVisitor
from pynestml.nestml.Either import Either
from pynestml.nestml.ASTExpression import ASTExpression
from pynestml.utils.Logger import Logger, LOGGING_LEVEL
from pynestml.utils.Messages import MessageCode


class LogicalNotVisitor(NESTMLVisitor):
    """
    Visits a single expression and updates the type of the sub-expression.
    """

    def visitExpression(self, _expr=None):
        """
        Visits a single expression with a logical operator and updates the type.
        :param _expr: a single expression
        :type _expr: ASTExpression
        """
        assert (_expr is not None and isinstance(_expr, ASTExpression)), \
            '(PyNestML.Visitor.LogicalNotVisitor) No or wrong type of visitor provided (%s)!' % type(_expr)
        exprTypeE = _expr.getExpression().getTypeEither()

        if exprTypeE.isError():
            _expr.setTypeEither(exprTypeE)
            return

        exprType = exprTypeE.getValue()

        if exprType.isBoolean():
            _expr.setTypeEither(Either.value(PredefinedTypes.getBooleanType()))
        else:
            errorMsg = ErrorStrings.messageExpectedBool(self, _expr.getSourcePosition())
            _expr.setTypeEither(Either.error(errorMsg))
            Logger.logMessage(_errorPosition=_expr.getSourcePosition(),
                              _code=MessageCode.TYPE_DIFFERENT_FROM_EXPECTED,
                              _message=errorMsg, _logLevel=LOGGING_LEVEL.ERROR)
