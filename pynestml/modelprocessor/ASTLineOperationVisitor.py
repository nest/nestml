#
# ASTLineOperatorVisitor.py
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
from pynestml.modelprocessor.ASTArithmeticOperator import ASTArithmeticOperator
from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
from pynestml.modelprocessor.ErrorStrings import ErrorStrings
from pynestml.modelprocessor.ASTVisitor import ASTVisitor
from pynestml.modelprocessor.Either import Either
from pynestml.modelprocessor.ASTExpression import ASTExpression
from pynestml.utils.Logger import Logger, LOGGING_LEVEL
from pynestml.utils.Messages import MessageCode


class ASTLineOperatorVisitor(ASTVisitor):
    """
    Visits a single binary operation consisting of + or - and updates the type accordingly.
    """

    def visitExpression(self, _expr=None):
        """
        Visits a single expression containing a plus or minus operator and updates its type.
        :param _expr: a single expression
        :type _expr: ASTExpression
        """
        assert (_expr is not None and isinstance(_expr, ASTExpression)), \
            '(PyNestML.Visitor.ASTLineOperatorVisitor) No or wrong type of expression provided (%s)!' % type(_expr)
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

        # Plus-exclusive code
        if arith_op.isPlusOp():
            # String concatenation has a prio. If one of the operands is a string,
            # the remaining sub-expression becomes a string
            if (lhs_type.isString() or rhs_type.isString()) and (not rhs_type.isVoid() and not lhs_type.isVoid()):
                _expr.setTypeEither(Either.value(PredefinedTypes.getStringType()))
                return

        # Common code for plus and minus ops:
        if lhs_type.isNumeric() and rhs_type.isNumeric():
            # both match exactly -> any is valid
            if lhs_type.equals(rhs_type):
                _expr.setTypeEither(Either.value(lhs_type))
                return
            # both numeric primitive, not matching -> one is real one is integer -> real
            if lhs_type.isNumericPrimitive() and rhs_type.isNumericPrimitive():
                _expr.setTypeEither(Either.value(PredefinedTypes.getRealType()))
                return
            # Both are units, not matching -> real, WARN
            if lhs_type.isUnit() and rhs_type.isUnit():
                error_msg = ErrorStrings.messageAddSubTypeMismatch(self, lhs_type.printSymbol(),
                                                                   rhs_type.printSymbol(), 'real',
                                                                   _expr.get_source_position())
                _expr.setTypeEither(Either.value(PredefinedTypes.getRealType()))
                Logger.logMessage(_code=MessageCode.ADD_SUB_TYPE_MISMATCH,
                                  _errorPosition=_expr.get_source_position(),
                                  _message=error_msg, _logLevel=LOGGING_LEVEL.WARNING)
                return
            # one is unit and one numeric primitive and vice versa -> assume unit, WARN
            if (lhs_type.isUnit() and rhs_type.isNumericPrimitive()) or (
                    rhs_type.isUnit() and lhs_type.isNumericPrimitive()):
                if lhs_type.isUnit():
                    unit_type = lhs_type
                else:
                    unit_type = rhs_type
                error_msg = ErrorStrings.messageAddSubTypeMismatch(self, lhs_type.printSymbol(),
                                                                   rhs_type.printSymbol(), unit_type.printSymbol(),
                                                                   _expr.get_source_position())
                _expr.setTypeEither(Either.value(unit_type))
                Logger.logMessage(_code=MessageCode.ADD_SUB_TYPE_MISMATCH, _message=error_msg,
                                  _errorPosition=_expr.get_source_position(), _logLevel=LOGGING_LEVEL.WARNING)
                return

        # if we get here, we are in a general error state
        error_msg = ErrorStrings.messageAddSubTypeMismatch(self, lhs_type.printSymbol(),
                                                           rhs_type.printSymbol(), 'ERROR',
                                                           _expr.get_source_position())
        _expr.setTypeEither(Either.error(error_msg))
        Logger.logMessage(_code=MessageCode.ADD_SUB_TYPE_MISMATCH, _message=error_msg,
                          _errorPosition=_expr.get_source_position(), _logLevel=LOGGING_LEVEL.ERROR)
