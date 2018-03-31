#
# ASTDotOperatorVisitortor.py
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
from pynestml.modelprocessor.ASTVisitor import ASTVisitor
from pynestml.modelprocessor.Either import Either
from pynestml.modelprocessor.ASTExpression import ASTExpression
from pynestml.utils.Logger import Logger, LOGGING_LEVEL
from pynestml.utils.Messages import MessageCode


class ASTDotOperatorVisitor(ASTVisitor):
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
            '(PyNestML.Visitor.ASTDotOperatorVisitor) No or wrong type of expression provided (%s)!' % type(_expr)
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

        arith_op = _expr.getBinaryOperator()
        # arithOp exists if we get into this visitor, but make sure:
        assert arith_op is not None and isinstance(arith_op, ASTArithmeticOperator)

        if arith_op.is_modulo_op:
            if lhs_type.isInteger() and rhs_type.isInteger():
                _expr.setTypeEither(Either.value(PredefinedTypes.getIntegerType()))
                return
            else:
                error_msg = ErrorStrings.messageExpectedInt(self, _expr.get_source_position())
                _expr.setTypeEither(Either.error(error_msg))
                Logger.logMessage(_code=MessageCode.TYPE_DIFFERENT_FROM_EXPECTED,
                                  _message=error_msg,
                                  _errorPosition=_expr.get_source_position(),
                                  _logLevel=LOGGING_LEVEL.ERROR)
                return
        if arith_op.is_div_op or arith_op.is_times_op:
            if lhs_type.isNumeric() and rhs_type.isNumeric():
                # If both are units, calculate resulting Type
                if lhs_type.isUnit() and rhs_type.isUnit():
                    left_unit = lhs_type.getEncapsulatedUnit()
                    right_unit = rhs_type.getEncapsulatedUnit()
                    if arith_op.is_times_op:
                        return_type = PredefinedTypes.getTypeIfExists(left_unit * right_unit)
                        _expr.setTypeEither(Either.value(return_type))
                        return
                    elif arith_op.is_div_op:
                        return_type = PredefinedTypes.getTypeIfExists(left_unit / right_unit)
                        _expr.setTypeEither(Either.value(return_type))
                        return
                # if lhs is Unit, and rhs real or integer, return same Unit
                if lhs_type.isUnit():
                    _expr.setTypeEither(Either.value(lhs_type))
                    return
                # if lhs is real or integer and rhs a unit, return unit for timesOP and inverse(unit) for divOp
                if rhs_type.isUnit():
                    if arith_op.is_times_op:
                        _expr.setTypeEither(Either.value(rhs_type))
                        return
                    elif arith_op.is_div_op:
                        right_unit = rhs_type.getEncapsulatedUnit()
                        return_type = PredefinedTypes.getTypeIfExists(1 / right_unit)
                        _expr.setTypeEither(Either.value(return_type))
                        return
                # if no Units are involved, Real takes priority
                if lhs_type.isReal() or rhs_type.isReal():
                    _expr.setTypeEither(Either.value(PredefinedTypes.getRealType()))
                    return
                # here, both are integers, but check to be sure
                if lhs_type.isInteger() and rhs_type.isInteger():
                    _expr.setTypeEither(Either.value(PredefinedTypes.getIntegerType()))
                    return
        # Catch-all if no case has matched
        type_mismatch = lhs_type.printSymbol() + " / " if arith_op.is_div_op else " * " + rhs_type.printSymbol()
        error_msg = ErrorStrings.messageTypeMismatch(self, type_mismatch, _expr.get_source_position())
        _expr.setTypeEither(Either.error(error_msg))
        Logger.logMessage(_message=error_msg,
                          _code=MessageCode.TYPE_DIFFERENT_FROM_EXPECTED,
                          _errorPosition=_expr.get_source_position(),
                          _logLevel=LOGGING_LEVEL.ERROR)
