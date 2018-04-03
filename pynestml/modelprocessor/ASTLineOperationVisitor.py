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
rhs : left=rhs (plusOp='+'  | minusOp='-') right=rhs
"""
from pynestml.modelprocessor.ASTArithmeticOperator import ASTArithmeticOperator
from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
from pynestml.modelprocessor.ErrorStrings import ErrorStrings
from pynestml.modelprocessor.ASTVisitor import ASTVisitor
from pynestml.modelprocessor.Either import Either
from pynestml.modelprocessor.ASTExpression import ASTExpression
from pynestml.utils.Logger import Logger, LoggingLevel
from pynestml.utils.Messages import MessageCode


class ASTLineOperatorVisitor(ASTVisitor):
    """
    Visits a single binary operation consisting of + or - and updates the type accordingly.
    """

    def visit_expression(self, node):
        """
        Visits a single rhs containing a plus or minus operator and updates its type.
        :param node: a single rhs
        :type node: ASTExpression
        """
        lhs_type_e = node.get_lhs().get_type_either()
        rhs_type_e = node.get_rhs().get_type_either()

        if lhs_type_e.isError():
            node.set_type_either(lhs_type_e)
            return
        if rhs_type_e.isError():
            node.set_type_either(rhs_type_e)
            return

        lhs_type = lhs_type_e.getValue()
        rhs_type = rhs_type_e.getValue()

        arith_op = node.get_binary_operator()
        # arithOp exists if we get into this visitor, but make sure:
        assert arith_op is not None and isinstance(arith_op, ASTArithmeticOperator)

        # Plus-exclusive code
        if arith_op.is_plus_op:
            # String concatenation has a prio. If one of the operands is a string,
            # the remaining sub-rhs becomes a string
            if (lhs_type.is_string() or rhs_type.is_string()) and (not rhs_type.is_void() and not lhs_type.is_void()):
                node.set_type_either(Either.value(PredefinedTypes.getStringType()))
                return

        # Common code for plus and minus ops:
        if lhs_type.is_numeric() and rhs_type.is_numeric():
            # both match exactly -> any is valid
            if lhs_type.equals(rhs_type):
                node.set_type_either(Either.value(lhs_type))
                return
            # both numeric primitive, not matching -> one is real one is integer -> real
            if lhs_type.is_numeric_primitive() and rhs_type.is_numeric_primitive():
                node.set_type_either(Either.value(PredefinedTypes.getRealType()))
                return
            # Both are units, not matching -> real, WARN
            if lhs_type.is_unit() and rhs_type.is_unit():
                error_msg = ErrorStrings.messageAddSubTypeMismatch(self, lhs_type.print_symbol(),
                                                                   rhs_type.print_symbol(), 'real',
                                                                   node.get_source_position())
                node.set_type_either(Either.value(PredefinedTypes.getRealType()))
                Logger.log_message(code=MessageCode.ADD_SUB_TYPE_MISMATCH,
                                   error_position=node.get_source_position(),
                                   message=error_msg, log_level=LoggingLevel.WARNING)
                return
            # one is unit and one numeric primitive and vice versa -> assume unit, WARN
            if (lhs_type.is_unit() and rhs_type.is_numeric_primitive()) or (
                    rhs_type.is_unit() and lhs_type.is_numeric_primitive()):
                if lhs_type.is_unit():
                    unit_type = lhs_type
                else:
                    unit_type = rhs_type
                error_msg = ErrorStrings.messageAddSubTypeMismatch(self, lhs_type.print_symbol(),
                                                                   rhs_type.print_symbol(), unit_type.print_symbol(),
                                                                   node.get_source_position())
                node.set_type_either(Either.value(unit_type))
                Logger.log_message(code=MessageCode.ADD_SUB_TYPE_MISMATCH, message=error_msg,
                                   error_position=node.get_source_position(), log_level=LoggingLevel.WARNING)
                return

        # if we get here, we are in a general error state
        error_msg = ErrorStrings.messageAddSubTypeMismatch(self, lhs_type.print_symbol(),
                                                           rhs_type.print_symbol(), 'ERROR',
                                                           node.get_source_position())
        node.set_type_either(Either.error(error_msg))
        Logger.log_message(code=MessageCode.ADD_SUB_TYPE_MISMATCH, message=error_msg,
                           error_position=node.get_source_position(), log_level=LoggingLevel.ERROR)
