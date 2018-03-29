#
# ASTConditionVisitor.py
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
from pynestml.modelprocessor.ASTExpression import ASTExpression
from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
from pynestml.modelprocessor.ErrorStrings import ErrorStrings
from pynestml.modelprocessor.ASTVisitor import ASTVisitor
from pynestml.modelprocessor.Either import Either
from pynestml.utils.Logger import Logger, LOGGING_LEVEL
from pynestml.utils.Messages import MessageCode


class ASTConditionVisitor(ASTVisitor):
    """
    This visitor is used to derive the correct type of a ternary operator, i.e., of all its subexpressions.
    """

    def visitExpression(self, _expr=None):
        """
        Visits an expression consisting of the ternary operator and updates its type.
        :param _expr: a single expression
        :type _expr: ASTExpression
        """
        assert (_expr is not None and (isinstance(_expr, ASTExpression))), \
            '(PyNestML.Visitor.ASTConditionVisitor) No or wrong type of expression provided (%s)!' % type(_expr)
        condition_e = _expr.getCondition().getTypeEither()
        if_true_e = _expr.getIfTrue().getTypeEither()
        if_not_e = _expr.getIfNot().getTypeEither()

        if condition_e.isError():
            _expr.setTypeEither(condition_e)
            return
        if if_true_e.isError():
            _expr.setTypeEither(if_true_e)
            return
        if if_not_e.isError():
            _expr.setTypeEither(if_not_e)
            return

        if_true = if_true_e.getValue()
        if_not = if_not_e.getValue()

        # Condition must be a bool
        if not condition_e.getValue().equals(PredefinedTypes.getBooleanType()):
            error_msg = ErrorStrings.messageTernary(self, _expr.getSourcePosition())
            _expr.setTypeEither(Either.error(error_msg))
            Logger.logMessage(_message=error_msg, _errorPosition=_expr.getSourcePosition(),
                              _code=MessageCode.TYPE_DIFFERENT_FROM_EXPECTED,
                              _logLevel=LOGGING_LEVEL.ERROR)
            return

        # Alternatives match exactly -> any is valid
        if if_true.equals(if_not):
            _expr.setTypeEither(Either.value(if_true))
            return

        # Both are units but not matching-> real WARN
        if if_true.isUnit() and if_not.isUnit():
            error_msg = ErrorStrings.messageTernaryMismatch(self, if_true.printSymbol(), if_not.printSymbol(),
                                                            _expr.getSourcePosition())
            _expr.setTypeEither(Either.value(PredefinedTypes.getRealType()))
            Logger.logMessage(_message=error_msg,
                              _code=MessageCode.TYPE_DIFFERENT_FROM_EXPECTED,
                              _errorPosition=if_true.getSourcePosition(),
                              _logLevel=LOGGING_LEVEL.WARNING)
            return

        # one Unit and one numeric primitive and vice versa -> assume unit, WARN
        if (if_true.isUnit() and if_not.isNumericPrimitive()) or (if_not.isUnit() and if_true.isNumericPrimitive()):
            unit_type = None
            if if_true.isUnit():
                unit_type = if_true
            else:
                unit_type = if_not
            error_msg = ErrorStrings.messageTernaryMismatch(self, str(if_true), str(if_not),
                                                            _expr.getSourcePosition())
            _expr.setTypeEither(Either.value(unit_type))
            Logger.logMessage(_message=error_msg,
                              _code=MessageCode.TYPE_DIFFERENT_FROM_EXPECTED,
                              _errorPosition=if_true.getSourcePosition(),
                              _logLevel=LOGGING_LEVEL.WARNING)
            return

        # both are numeric primitives (and not equal) ergo one is real and one is integer -> real
        if if_true.isNumericPrimitive() and if_not.isNumericPrimitive():
            _expr.setTypeEither(Either.value(PredefinedTypes.getRealType()))
            return

        # if we get here it is an error
        error_msg = ErrorStrings.messageTernaryMismatch(self, str(if_true), str(if_not),
                                                        _expr.getSourcePosition())
        _expr.setTypeEither(Either.error(error_msg))
        Logger.logMessage(_message=error_msg,
                          _errorPosition=_expr.getSourcePosition(),
                          _code=MessageCode.TYPE_DIFFERENT_FROM_EXPECTED,
                          _logLevel=LOGGING_LEVEL.ERROR)
