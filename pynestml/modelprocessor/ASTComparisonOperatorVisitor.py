#
# ASTComparisonOperatorVisitor.py.py
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
expression : left=expression comparisonOperator right=expression
"""
from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
from pynestml.modelprocessor.ErrorStrings import ErrorStrings
from pynestml.modelprocessor.ASTVisitor import ASTVisitor
from pynestml.modelprocessor.Either import Either
from pynestml.modelprocessor.ASTExpression import ASTExpression
from pynestml.utils.Logger import Logger, LOGGING_LEVEL
from pynestml.utils.Messages import MessageCode


class ASTComparisonOperatorVisitor(ASTVisitor):
    """
    Visits a single expression consisting of a binary comparison operator.
    """

    def visitExpression(self, _expr=None):
        """
        Visits a single comparison operator expression and updates the type.
        :param _expr: an expression
        :type _expr: ASTExpression
        """
        assert (_expr is not None and isinstance(_expr, ASTExpression)), \
            '(PyNestML.Visitor.ASTConditionVisitor) No or wrong type of expression provided (%s)!' % type(_expr)
        lhs_type_e = _expr.getLhs().getTypeEither()
        rhs_type_e = _expr.getRhs().getTypeEither()

        if lhs_type_e.isError():
            _expr.setTypeEither(lhs_type_e)
            return
        if rhs_type_e.isError():
            _expr.setTypeEither(rhs_type_e)
            return

        lhs_type = lhs_type_e.getValue()
        rhs_type = rhs_type_e.getValue()

        if ((lhs_type.isReal() or lhs_type.isInteger()) and (rhs_type.isReal() or rhs_type.isInteger())) \
                or (lhs_type.equals(rhs_type) and lhs_type.isNumeric()) or (lhs_type.isBoolean() and rhs_type.isBoolean()):
            _expr.setTypeEither(Either.value(PredefinedTypes.getBooleanType()))
            return

        # Error message for any other operation
        if (lhs_type.isUnit() and rhs_type.isNumeric()) or (rhs_type.isUnit() and lhs_type.isNumeric()):
            # if the incompatibility exists between a unit and a numeric, the c++ will still be fine, just WARN
            error_msg = ErrorStrings.messageComparison(self, _expr.get_source_position())
            _expr.setTypeEither(Either.value(PredefinedTypes.getBooleanType()))
            Logger.logMessage(_message=error_msg, _code=MessageCode.SOFT_INCOMPATIBILITY,
                              _errorPosition=_expr.get_source_position(),
                              _logLevel=LOGGING_LEVEL.WARNING)
            return
        else:
            # hard incompatibility, cannot recover in c++, ERROR
            error_msg = ErrorStrings.messageComparison(self, _expr.get_source_position())
            _expr.setTypeEither(Either.error(error_msg))
            Logger.logMessage(_code=MessageCode.HARD_INCOMPATIBILITY,
                              _errorPosition=_expr.get_source_position(),
                              _message=error_msg, _logLevel=LOGGING_LEVEL.ERROR)
            return
