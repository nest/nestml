#
# ComparisonOperatorVisitor.py
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
from pynestml.modelprocessor.ASTExpression import ASTExpression
from pynestml.modelprocessor.BooleanTypeSymbol import BooleanTypeSymbol
from pynestml.modelprocessor.Either import Either
from pynestml.modelprocessor.ErrorStrings import ErrorStrings
from pynestml.modelprocessor.ErrorTypeSymbol import ErrorTypeSymbol
from pynestml.modelprocessor.ModelVisitor import NESTMLVisitor
from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
from pynestml.modelprocessor.UnitTypeSymbol import UnitTypeSymbol
from pynestml.utils.Logger import Logger, LOGGING_LEVEL
from pynestml.utils.Messages import MessageCode


class ComparisonOperatorVisitor(NESTMLVisitor):
    """
    Visits a single expression consisting of a binary comparison operator.
    """

    def visit_expression(self, _expr=None):
        """
        Visits a single comparison operator expression and updates the type.
        :param _expr: an expression
        :type _expr: ASTExpression
        """
        lhs_type = _expr.getLhs().type
        rhs_type = _expr.getRhs().type

        lhs_type.referenced_object = _expr.getLhs()
        rhs_type.referenced_object = _expr.getRhs()

        if (lhs_type.isNumericPrimitive() and rhs_type.isNumericPrimitive()) \
                or (lhs_type.equals(rhs_type) and lhs_type.isNumeric()) or (
                    isinstance(lhs_type, BooleanTypeSymbol) and isinstance(rhs_type, BooleanTypeSymbol)):
            _expr.type = PredefinedTypes.getBooleanType()
            return

        # Error message for any other operation
        if (isinstance(lhs_type, UnitTypeSymbol) and rhs_type.isNumeric()) or (
                    isinstance(rhs_type, UnitTypeSymbol) and lhs_type.isNumeric()):
            # if the incompatibility exists between a unit and a numeric, the c++ will still be fine, just WARN
            error_msg = ErrorStrings.messageComparison(self, _expr.getSourcePosition())
            _expr.type = PredefinedTypes.getBooleanType()
            Logger.logMessage(_message=error_msg, _code=MessageCode.SOFT_INCOMPATIBILITY,
                              _errorPosition=_expr.getSourcePosition(),
                              _logLevel=LOGGING_LEVEL.WARNING)
            return
        else:
            # hard incompatibility, cannot recover in c++, ERROR
            error_msg = ErrorStrings.messageComparison(self, _expr.getSourcePosition())
            _expr.type = ErrorTypeSymbol()
            Logger.logMessage(_code=MessageCode.HARD_INCOMPATIBILITY,
                              _errorPosition=_expr.getSourcePosition(),
                              _message=error_msg, _logLevel=LOGGING_LEVEL.ERROR)
            return
