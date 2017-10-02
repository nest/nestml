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
from pynestml.nestml.PredefinedTypes import PredefinedTypes
from pynestml.nestml.TypeChecker import TypeChecker
from pynestml.nestml.ErrorStrings import ErrorStrings
from pynestml.nestml.NESTMLVisitor import NESTMLVisitor
from pynestml.nestml.Either import Either
from pynestml.utils.Logger import Logger, LOGGING_LEVEL


class ConditionVisitor(NESTMLVisitor):
    def visitExpression(self, _expr=None):
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
            errorMsg = ErrorStrings.messageTernary(self, _expr.getSourcePosition)
            _expr.setTypeEither(Either.error(errorMsg))
            Logger.logMessage(errorMsg, LOGGING_LEVEL.ERROR)
            return

        # Alternatives match exactly -> any is valid
        if ifTrue.equals(ifNot):
            _expr.setTypeEither(Either.value(ifTrue))
            return

        # Both are units but not matching-> real WARN
        if TypeChecker.isUnit(ifTrue) and TypeChecker.isUnit(ifNot):
            errorMsg = ErrorStrings.messageTernaryMismatch(self, ifTrue.printSymbol(), ifNot.printSymbol(),
                                                           _expr.getSourcePosition())
            _expr.setTypeEither(Either.value(PredefinedTypes.getRealType()))
            Logger.logMessage(errorMsg, LOGGING_LEVEL.WARNING)
            return

        # one Unit and one numeric primitive and vice versa -> assume unit, WARN
        if (TypeChecker.isUnit(ifTrue) and TypeChecker.isNumericPrimitive(ifNot)) \
                or (TypeChecker.isUnit(ifNot) and TypeChecker.isNumericPrimitive(ifTrue)):
            unitType = None
            if TypeChecker.isUnit(ifTrue):
                unitType = ifTrue
            else:
                unitType = ifNot
            errorMsg = ErrorStrings.messageTernaryMismatch(self, ifTrue.printAST(), ifNot.printAST(),
                                                           _expr.getSourcePosition())
            _expr.setTypeEither(Either.value(unitType))
            Logger.logMessage(errorMsg, LOGGING_LEVEL.WARNING)
            return

        # both are numeric primitives (and not equal) ergo one is real and one is integer -> real
        if TypeChecker.isNumericPrimitive(ifTrue) and TypeChecker.isNumericPrimitive(ifNot):
            _expr.setTypeEither(Either.value(PredefinedTypes.getRealType()))
            return

        # if we get here it is an error
        errorMsg = ErrorStrings.messageTernaryMismatch(self, ifTrue.printAST(), ifNot.printAST(),
                                                       _expr.getSourcePosition)
        _expr.setTypeEither(Either.error(errorMsg))
        Logger.logMessage(errorMsg, LOGGING_LEVEL.ERROR)
