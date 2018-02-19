#
# BinaryLogicVisitor.py
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
from pynestml.modelprocessor.ASTExpression import ASTExpression
from pynestml.modelprocessor.BooleanTypeSymbol import BooleanTypeSymbol
from pynestml.modelprocessor.Either import Either
from pynestml.modelprocessor.ErrorStrings import ErrorStrings
from pynestml.modelprocessor.ModelVisitor import NESTMLVisitor
from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
from pynestml.utils.Logger import Logger, LOGGING_LEVEL


class BinaryLogicVisitor(NESTMLVisitor):
    """
    Visits a single binary logical operator expression and updates its types.
    """

    def visit_expression(self, _expr=None):
        """
        Visits an expression which uses a binary logic operator and updates the type.
        :param _expr: a single expression.
        :type _expr: ASTExpression
        """
        assert (_expr is not None and isinstance(_expr, ASTExpression)), \
            '(PyNestML.Visitor.BinaryLogicVisitor) No or wrong type of expression provided (%s)!' % type(_expr)
        lhsType = _expr.getLhs().getTypeEither()
        rhsType = _expr.getRhs().getTypeEither()

        if lhsType.isError():
            _expr.setTypeEither(lhsType)
            return
        if rhsType.isError():
            _expr.setTypeEither(rhsType)
            return

        if isinstance(lhsType.getValue(), BooleanTypeSymbol) and isinstance(rhsType.getValue(), BooleanTypeSymbol):
            _expr.setTypeEither(Either.value(PredefinedTypes.getBooleanType()))
        else:
            errorMsg = ErrorStrings.messageLogicOperandsNotBool(self, _expr.getSourcePosition())
            _expr.setTypeEither(Either.error(errorMsg))
            Logger.logMessage(errorMsg, LOGGING_LEVEL.ERROR)
        return
