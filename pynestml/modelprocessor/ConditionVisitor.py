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
from pynestml.modelprocessor.ASTExpression import ASTExpression
from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
from pynestml.modelprocessor.ErrorStrings import ErrorStrings
from pynestml.modelprocessor.ModelVisitor import NESTMLVisitor
from pynestml.modelprocessor.Either import Either
from pynestml.utils.Logger import Logger, LOGGING_LEVEL
from pynestml.utils.Messages import MessageCode


class ConditionVisitor(NESTMLVisitor):
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
            '(PyNestML.Visitor.ConditionVisitor) No or wrong type of expression provided (%s)!' % type(_expr)
        conditionE = _expr.getCondition().getTypeEither()
        ifTrueE = _expr.getIfTrue().getTypeEither()
        ifNotE = _expr.getIfNot().getTypeEither()

        if conditionE.isError():
            _expr.setTypeEither(conditionE)
            return
        if ifTrueE.isError():
            _expr.setTypeEither(ifTrueE)
            return
        if ifNotE.isError():
            _expr.setTypeEither(ifNotE)
            return

        ifTrue = ifTrueE.getValue()
        ifNot = ifNotE.getValue()

        # Condition must be a bool
        if not conditionE.getValue().equals(PredefinedTypes.getBooleanType()):
            errorMsg = ErrorStrings.messageTernary(self, _expr.getSourcePosition())
            _expr.setTypeEither(Either.error(errorMsg))
            Logger.logMessage(_message=errorMsg, _errorPosition=_expr.getSourcePosition(),
                              _code=MessageCode.TYPE_DIFFERENT_FROM_EXPECTED,
                              _logLevel=LOGGING_LEVEL.ERROR)
            return

        # Alternatives match exactly -> any is valid
        if ifTrue.equals(ifNot):
            _expr.setTypeEither(Either.value(ifTrue))
            return

        # Both are units but not matching-> real WARN
        if ifTrue.isUnit() and ifNot.isUnit():
            errorMsg = ErrorStrings.messageTernaryMismatch(self, ifTrue.printSymbol(), ifNot.printSymbol(),
                                                           _expr.getSourcePosition())
            _expr.setTypeEither(Either.value(PredefinedTypes.getRealType()))
            Logger.logMessage(_message=errorMsg,
                              _code=MessageCode.TYPE_DIFFERENT_FROM_EXPECTED,
                              _errorPosition=ifTrue.getSourcePosition(),
                              _logLevel=LOGGING_LEVEL.WARNING)
            return

        # one Unit and one numeric primitive and vice versa -> assume unit, WARN
        if (ifTrue.isUnit() and ifNot.isNumericPrimitive()) or (ifNot.isUnit() and ifTrue.isNumericPrimitive()):
            unitType = None
            if ifTrue.isUnit():
                unitType = ifTrue
            else:
                unitType = ifNot
            errorMsg = ErrorStrings.messageTernaryMismatch(self, str(ifTrue), str(ifNot),
                                                           _expr.getSourcePosition())
            _expr.setTypeEither(Either.value(unitType))
            Logger.logMessage(_message=errorMsg,
                              _code=MessageCode.TYPE_DIFFERENT_FROM_EXPECTED,
                              _errorPosition=ifTrue.getSourcePosition(),
                              _logLevel=LOGGING_LEVEL.WARNING)
            return

        # both are numeric primitives (and not equal) ergo one is real and one is integer -> real
        if ifTrue.isNumericPrimitive() and ifNot.isNumericPrimitive():
            _expr.setTypeEither(Either.value(PredefinedTypes.getRealType()))
            return

        # if we get here it is an error
        errorMsg = ErrorStrings.messageTernaryMismatch(self, str(ifTrue), str(ifNot),
                                                       _expr.getSourcePosition())
        _expr.setTypeEither(Either.error(errorMsg))
        Logger.logMessage(_message=errorMsg,
                          _errorPosition=_expr.getSourcePosition(),
                          _code=MessageCode.TYPE_DIFFERENT_FROM_EXPECTED,
                          _logLevel=LOGGING_LEVEL.ERROR)
