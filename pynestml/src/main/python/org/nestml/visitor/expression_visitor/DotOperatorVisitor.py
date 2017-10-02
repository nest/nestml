#
# DotOperatorVisitor.py
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
expression : left=expression (timesOp='*' | divOp='/' | moduloOp='%') right=expression
"""
from pynestml.src.main.python.org.nestml.ast.ASTArithmeticOperator import ASTArithmeticOperator
from pynestml.src.main.python.org.nestml.symbol_table.predefined.PredefinedTypes import PredefinedTypes
from pynestml.src.main.python.org.nestml.symbol_table.typechecker.TypeChecker import TypeChecker
from pynestml.src.main.python.org.nestml.visitor.ErrorStrings import ErrorStrings
from pynestml.src.main.python.org.nestml.visitor.NESTMLVisitor import NESTMLVisitor
from pynestml.src.main.python.org.nestml.visitor.expression_visitor.Either import Either
from pynestml.src.main.python.org.utils.Logger import Logger, LOGGING_LEVEL


class DotOperatorVisitor(NESTMLVisitor):

    def visitExpression(self, _expr = None):
        lhsTypeE = _expr.getLhs().getTypeEither()
        rhsTypeE = _expr.getRhs().getTypeEither()

        if lhsTypeE.isError():
            _expr.setTypeEither(lhsTypeE)
            return

        if rhsTypeE.isError():
            _expr.setTypeEither(rhsTypeE)
            return

        lhsType = lhsTypeE.getValue()
        rhsType = rhsTypeE.getValue()

        arithOp = _expr.getBinaryOperator()
        #arithOp exists if we get into this visitor, but make sure:
        assert arithOp is not None and isinstance(arithOp,ASTArithmeticOperator)

        if arithOp.isModuloOp():
            if TypeChecker.isInteger(lhsType) and TypeChecker.isInteger(rhsType):
                _expr.setTypeEither(Either.value(PredefinedTypes.getIntegerType()))
                return
            else:
                errorMsg = ErrorStrings.messageExpectedInt(self, _expr.getSourcePosition())
                _expr.setTypeEither(Either.error(errorMsg))
                Logger.logMessage(errorMsg, LOGGING_LEVEL.ERROR)
                return
        if arithOp.isDivOp() or arithOp.isTimesOp():
            if TypeChecker.isNumeric(lhsType) and TypeChecker.isNumeric(rhsType):
                #If both are units, calculate resulting Type
                if TypeChecker.isUnit(lhsType) and TypeChecker.isUnit(rhsType):
                    leftUnit = lhsType.getSympyUnit()
                    rightUnit = rhsType.getSympyUnit()
                    if arithOp.isTimesOp():
                        returnType = PredefinedTypes.getTypeIfExists(leftUnit*rightUnit)
                        _expr.setTypeEither(Either.value(returnType))
                        return
                    elif arithOp.isDivOp():
                        returnType = PredefinedTypes.getTypeIfExists(leftUnit/rightUnit)
                        _expr.setTypeEither(Either.value(returnType))
                        return
                #if lhs is Unit, and rhs real or integer, return same Unit
                if TypeChecker.isUnit(lhsType):
                    _expr.setTypeEither(Either.value(lhsType))
                    return
                #if lhs is real or integer and rhs a unit, return unit for timesOP and inverse(unit) for divOp
                if TypeChecker.isUnit(rhsType):
                    if arithOp.isTimesOp():
                        _expr.setTypeEither(Either.value(rhsType))
                        return
                    elif arithOp.isDivOp():
                        rightUnit = rhsType.getSympyUnit()
                        returnType = PredefinedTypes.getTypeIfExists(1/rightUnit)
                        _expr.setTypeEither(Either.value(returnType))
                        return
                #if no Units are involved, Real takes priority
                if TypeChecker.isReal(lhsType) or TypeChecker.isReal(rhsType):
                    _expr.setTypeEither(Either.value(PredefinedTypes.getRealType()))
                    return
                # here, both are integers, but check to be sure
                if TypeChecker.isInteger(lhsType) and TypeChecker.isInteger(rhsType):
                    _expr.setTypeEither(Either.value(PredefinedTypes.getIntegerType()))
                    return
        #Catch-all if no case has matched
        typeMissmatch = lhsType.printSymbol() + " / " if arithOp.isDivOp() else " * " + rhsType.printSymbol()
        errorMsg = ErrorStrings.messageTypeMismatch(self, typeMissmatch, _expr.getSourcePosition())
        _expr.setTypeEither(Either.error(errorMsg))
        Logger.logMessage(errorMsg, LOGGING_LEVEL.ERROR)