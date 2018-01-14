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
from pynestml.modelprocessor.ASTArithmeticOperator import ASTArithmeticOperator
from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
from pynestml.modelprocessor.ErrorStrings import ErrorStrings
from pynestml.modelprocessor.ModelVisitor import NESTMLVisitor
from pynestml.modelprocessor.Either import Either
from pynestml.modelprocessor.ASTExpression import ASTExpression
from pynestml.utils.Logger import Logger, LOGGING_LEVEL
from pynestml.utils.Messages import MessageCode


class DotOperatorVisitor(NESTMLVisitor):
    """
    This visitor is used to derive the correct type of expressions which use a binary dot operator.
    """

    def visitExpression(self, _expr=None):
        """
        Visits a single expression and updates the type.
        :param _expr: a single expression
        :type _expr: ASTExpression
        """
        assert (_expr is not None and isinstance(_expr, ASTExpression)), \
            '(PyNestML.Visitor.DotOperatorVisitor) No or wrong type of expression provided (%s)!' % type(_expr)
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
        # arithOp exists if we get into this visitor, but make sure:
        assert arithOp is not None and isinstance(arithOp, ASTArithmeticOperator)

        if arithOp.isModuloOp():
            if lhsType.isInteger() and rhsType.isInteger():
                _expr.setTypeEither(Either.value(PredefinedTypes.getIntegerType()))
                return
            else:
                errorMsg = ErrorStrings.messageExpectedInt(self, _expr.getSourcePosition())
                _expr.setTypeEither(Either.error(errorMsg))
                Logger.logMessage(_code=MessageCode.TYPE_DIFFERENT_FROM_EXPECTED,
                                  _message=errorMsg,
                                  _errorPosition=_expr.getSourcePosition(),
                                  _logLevel=LOGGING_LEVEL.ERROR)
                return
        if arithOp.isDivOp() or arithOp.isTimesOp():
            if lhsType.isNumeric() and rhsType.isNumeric():
                # If both are units, calculate resulting Type
                if lhsType.isUnit() and rhsType.isUnit():
                    leftUnit = lhsType.getEncapsulatedUnit()
                    rightUnit = rhsType.getEncapsulatedUnit()
                    if arithOp.isTimesOp():
                        returnType = PredefinedTypes.getTypeIfExists(leftUnit * rightUnit)
                        _expr.setTypeEither(Either.value(returnType))
                        return
                    elif arithOp.isDivOp():
                        returnType = PredefinedTypes.getTypeIfExists(leftUnit / rightUnit)
                        _expr.setTypeEither(Either.value(returnType))
                        return
                # if lhs is Unit, and rhs real or integer, return same Unit
                if lhsType.isUnit():
                    _expr.setTypeEither(Either.value(lhsType))
                    return
                # if lhs is real or integer and rhs a unit, return unit for timesOP and inverse(unit) for divOp
                if rhsType.isUnit():
                    if arithOp.isTimesOp():
                        _expr.setTypeEither(Either.value(rhsType))
                        return
                    elif arithOp.isDivOp():
                        rightUnit = rhsType.getEncapsulatedUnit()
                        returnType = PredefinedTypes.getTypeIfExists(1 / rightUnit)
                        _expr.setTypeEither(Either.value(returnType))
                        return
                # if no Units are involved, Real takes priority
                if lhsType.isReal() or rhsType.isReal():
                    _expr.setTypeEither(Either.value(PredefinedTypes.getRealType()))
                    return
                # here, both are integers, but check to be sure
                if lhsType.isInteger() and rhsType.isInteger():
                    _expr.setTypeEither(Either.value(PredefinedTypes.getIntegerType()))
                    return
        # Catch-all if no case has matched
        typeMismatch = lhsType.printSymbol() + " / " if arithOp.isDivOp() else " * " + rhsType.printSymbol()
        errorMsg = ErrorStrings.messageTypeMismatch(self, typeMismatch, _expr.getSourcePosition())
        _expr.setTypeEither(Either.error(errorMsg))
        Logger.logMessage(_message=errorMsg,
                          _code=MessageCode.TYPE_DIFFERENT_FROM_EXPECTED,
                          _errorPosition=_expr.getSourcePosition(),
                          _logLevel=LOGGING_LEVEL.ERROR)
