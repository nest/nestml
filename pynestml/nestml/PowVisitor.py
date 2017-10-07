#
# PowVisitor.py
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
expression : <assoc=right> left=expression powOp='**' right=expression
"""
from pynestml.nestml.ASTExpression import ASTExpression
from pynestml.nestml.ASTSimpleExpression import ASTSimpleExpression
from pynestml.nestml.PredefinedTypes import PredefinedTypes
from pynestml.nestml.TypeChecker import TypeChecker
from pynestml.nestml.ErrorStrings import ErrorStrings
from pynestml.nestml.NESTMLVisitor import NESTMLVisitor
from pynestml.nestml.Either import Either
from pynestml.utils.Logger import Logger, LOGGING_LEVEL


class PowVisitor(NESTMLVisitor):
    """
    Visits a single power expression and updates its types accordingly.
    """

    def visitExpression(self, _expr=None):
        assert _expr is not None
        baseTypeE = _expr.getLhs().getTypeEither()
        exponentTypeE = _expr.getRhs().getTypeEither()

        if baseTypeE.isError():
            _expr.setTypeEither(baseTypeE)
            return

        if exponentTypeE.isError():
            _expr.setTypeEither(exponentTypeE)
            return

        baseType = baseTypeE.getValue()
        exponentType = exponentTypeE.getValue()

        if TypeChecker.isNumeric(baseType) and TypeChecker.isNumeric(exponentType):
            if TypeChecker.isInteger(baseType) and TypeChecker.isInteger(exponentType):
                _expr.setTypeEither(Either.value(PredefinedTypes.getIntegerType()))
                return
            elif TypeChecker.isUnit(baseType):
                # exponents to units MUST be integer and calculable at time of analysis.
                # Otherwise resulting unit is undefined
                if not TypeChecker.isInteger(exponentType):
                    errorMsg = ErrorStrings.messageUnitBase(self, _expr.getSourcePosition())
                    _expr.setTypeEither(Either.error(errorMsg))
                    Logger.logMessage(errorMsg, LOGGING_LEVEL.ERROR)
                    return
                baseUnit = baseType.getSympyUnit()
                exponentValue = self.calculateNumericValue(
                    _expr.getRhs())  # calculate exponent value if exponent composed of literals
                if exponentValue.isValue():
                    _expr.setTypeEither(
                        Either.value(PredefinedTypes.getTypeIfExists(baseUnit ** exponentValue.getValue())))
                    return
                else:
                    errorMsg = exponentValue.getError()
                    _expr.setTypeEither(Either.error(errorMsg))
                    Logger.logMessage(errorMsg, LOGGING_LEVEL.ERROR)
                    return
            else:
                _expr.setTypeEither(Either.value(PredefinedTypes.getRealType()))
                return
        # Catch-all if no case has matched
        errorMsg = ErrorStrings.messageUnitBase(self, _expr.getSourcePosition())
        _expr.setTypeEither(Either.error(errorMsg))
        Logger.logMessage(errorMsg, LOGGING_LEVEL.ERROR)

    def calculateNumericValue(self, _expr=None):
        # TODO write tests for this
        if isinstance(_expr, ASTExpression) and _expr.isEncapsulated():
            return self.calculateNumericValue(_expr.getExpr())
        elif isinstance(_expr, ASTSimpleExpression) and _expr.getNumericLiteral() is not None:
            if isinstance(_expr.getNumericLiteral(), int):
                literal = _expr.getNumericLiteral()
                return Either.value(literal)
            else:
                errorMessage = ErrorStrings.messageUnitBase(self, _expr.getSourcePosition())
                return Either.error(errorMessage)
        elif _expr.isUnaryOperator() and _expr.getUnaryOperator().isUnaryMinus():
            term = self.calculateNumericValue(_expr.getExpression)
            if term.isError():
                return term
            return Either.value(-term.getValue())
        errorMessage = ErrorStrings.messageNonConstantExponent(self, _expr.getSourcePosition)
        return Either.error(errorMessage)
