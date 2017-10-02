#
# LineOperatorVisitor.py
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
expression : left=expression (plusOp='+'  | minusOp='-') right=expression
"""
from pynestml.src.main.python.org.nestml.ast.ASTArithmeticOperator import ASTArithmeticOperator
from pynestml.src.main.python.org.nestml.symbol_table.predefined.PredefinedTypes import PredefinedTypes
from pynestml.src.main.python.org.nestml.symbol_table.typechecker.TypeChecker import TypeChecker
from pynestml.src.main.python.org.nestml.visitor.ErrorStrings import ErrorStrings
from pynestml.src.main.python.org.nestml.visitor.NESTMLVisitor import NESTMLVisitor
from pynestml.src.main.python.org.nestml.visitor.expression_visitor.Either import Either
from pynestml.src.main.python.org.utils.Logger import Logger, LOGGING_LEVEL


class LineOperatorVisitor(NESTMLVisitor):

    def visitExpression(self, _expr=None):
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

        #Plus-exclusive code
        if arithOp.isPlusOp():
            #String concatenation has a prio. If one of the operands is a string, the remaining sub-expression becomes a string
            if (TypeChecker.isString(lhsType) or TypeChecker.isString(rhsType)) \
                    and (not TypeChecker.isVoid(rhsType) and not TypeChecker.isVoid(lhsType)):
                _expr.setTypeEither(Either.value(PredefinedTypes.getStringType()))
                return
        
        #Common code for plus and minus ops:
        if TypeChecker.isNumeric(lhsType) and TypeChecker.isNumeric(rhsType):
            #both match exactly -> any is valid
            if lhsType.equals(rhsType):
                _expr.setTypeEither(Either.value(lhsType))
                return
            #both numeric primitive, not matching -> one is real one is integer -> real
            if TypeChecker.isNumericPrimitive(lhsType) and TypeChecker.isNumericPrimitive(rhsType):
                _expr.setTypeEither(Either.value(PredefinedTypes.getRealType()))
                return
            #Both are units, not matching -> real, WARN
            if TypeChecker.isUnit(lhsType) and TypeChecker.isUnit(rhsType):
                errorMsg = ErrorStrings.messageAddSubTypeMismatch\
                    (self, lhsType.printSymbol(), rhsType.printSymbol(), "real", _expr.getSourcePosition())
                _expr.setTypeEither(Either.value(PredefinedTypes.getRealType()))
                Logger.logMessage(errorMsg, LOGGING_LEVEL.WARNING)
                return
            #one is unit and one numeric primitive and vice versa -> assume unit, WARN
            if (TypeChecker.isUnit(lhsType) and TypeChecker.isNumericPrimitive(rhsType)) \
                    or (TypeChecker.isUnit(rhsType) and TypeChecker.isNumericPrimitive(lhsType)):
                unitType = None
                if TypeChecker.isUnit(lhsType):
                    unitType = lhsType
                else:
                    unitType = rhsType
                errorMsg = ErrorStrings.messageAddSubTypeMismatch\
                    (self, lhsType.printSymbol(), rhsType.printSymbol(), unitType.printSymbol(), _expr.getSourcePosition())
                _expr.setTypeEither(Either.value(unitType))
                Logger.logMessage(errorMsg, LOGGING_LEVEL.WARNING)
                return

        #if we get here, we are in a general error state
        errorMsg = ErrorStrings.messageAddSubTypeMismatch\
            (self, lhsType.printSymbol(), rhsType.printSymbol(), "ERROR", _expr.getSourcePosition())
        _expr.setTypeEither(Either.error(errorMsg))
        Logger.logMessage(errorMsg, LOGGING_LEVEL.ERROR)