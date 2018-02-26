#
# ConditionVisitor.py
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
expression : condition=expression '?' ifTrue=expression ':' ifNot=expression
"""
from copy import copy

from pynestml.modelprocessor.ASTExpression import ASTExpression
from pynestml.modelprocessor.Either import Either
from pynestml.modelprocessor.ErrorStrings import ErrorStrings
from pynestml.modelprocessor.ErrorTypeSymbol import ErrorTypeSymbol
from pynestml.modelprocessor.ModelVisitor import NESTMLVisitor
from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
from pynestml.modelprocessor.UnitTypeSymbol import UnitTypeSymbol
from pynestml.utils.Logger import Logger, LOGGING_LEVEL
from pynestml.utils.Messages import MessageCode


class ConditionVisitor(NESTMLVisitor):
    """
    This visitor is used to derive the correct type of a ternary operator, i.e., of all its subexpressions.
    """

    def visit_expression(self, _expr=None):
        """
        Visits an expression consisting of the ternary operator and updates its type.
        :param _expr: a single expression
        :type _expr: ASTExpression
        """
        if_true = _expr.getIfTrue().type
        if_not = _expr.getIfNot().type
        condition = _expr.getCondition().type

        condition.referenced_object = _expr.getCondition()
        if_true.referenced_object = _expr.getIfTrue()
        if_not.referenced_object = _expr.getIfNot()

        # Condition must be a bool
        if not condition.equals(PredefinedTypes.getBooleanType()):
            error_msg = ErrorStrings.messageTernary(self, _expr.getSourcePosition())
            _expr.type = ErrorTypeSymbol()
            Logger.logMessage(_message=error_msg, _errorPosition=_expr.getSourcePosition(),
                              _code=MessageCode.TYPE_DIFFERENT_FROM_EXPECTED,
                              _logLevel=LOGGING_LEVEL.ERROR)
            return

        # Alternatives match exactly -> any is valid
        if if_true.equals(if_not):
            _expr.type = copy(if_true)
            return

        # Both are units but not matching-> real WARN
        if isinstance(if_true, UnitTypeSymbol) and isinstance(if_not, UnitTypeSymbol):
            # TODO: This is not covered by our tests, and it doesnt work
            error_msg = ErrorStrings.messageTernaryMismatch(self, if_true.print_symbol(), if_not.print_symbol(),
                                                            _expr.getSourcePosition())
            _expr.type = PredefinedTypes.getRealType()
            Logger.logMessage(_message=error_msg,
                              _code=MessageCode.TYPE_DIFFERENT_FROM_EXPECTED,
                              _errorPosition=_expr.getIfTrue().getSourcePosition(),
                              _logLevel=LOGGING_LEVEL.WARNING)
            return

        # one Unit and one numeric primitive and vice versa -> assume unit, WARN
        if (isinstance(if_true, UnitTypeSymbol) and if_not.isNumericPrimitive()) or (
                    isinstance(if_not, UnitTypeSymbol) and if_true.isNumericPrimitive()):

            if isinstance(if_true, UnitTypeSymbol):
                unit_type = if_true
            else:
                unit_type = if_not
            error_msg = ErrorStrings.messageTernaryMismatch(self, str(if_true), str(if_not),
                                                            _expr.getSourcePosition())
            _expr.type = copy(unit_type)
            Logger.logMessage(_message=error_msg,
                              _code=MessageCode.TYPE_DIFFERENT_FROM_EXPECTED,
                              _errorPosition=_expr.getIfTrue().getSourcePosition(),
                              _logLevel=LOGGING_LEVEL.WARNING)
            return

        # both are numeric primitives (and not equal) ergo one is real and one is integer -> real
        if if_true.isNumericPrimitive() and if_not.isNumericPrimitive():
            _expr.type = PredefinedTypes.getRealType()
            return

        # if we get here it is an error
        error_msg = ErrorStrings.messageTernaryMismatch(self, str(if_true), str(if_not),
                                                        _expr.getSourcePosition())
        _expr.type = ErrorTypeSymbol()
        Logger.logMessage(_message=error_msg,
                          _errorPosition=_expr.getSourcePosition(),
                          _code=MessageCode.TYPE_DIFFERENT_FROM_EXPECTED,
                          _logLevel=LOGGING_LEVEL.ERROR)
