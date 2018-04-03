#
# ASTComparisonOperatorVisitor.py.py
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
rhs : left=rhs comparisonOperator right=rhs
"""
from pynestml.modelprocessor.ASTExpression import ASTExpression
from pynestml.modelprocessor.ASTVisitor import ASTVisitor
from pynestml.modelprocessor.Either import Either
from pynestml.modelprocessor.ErrorStrings import ErrorStrings
from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
from pynestml.utils.Logger import Logger, LoggingLevel
from pynestml.utils.Messages import MessageCode


class ASTComparisonOperatorVisitor(ASTVisitor):
    """
    Visits a single rhs consisting of a binary comparison operator.
    """

    def visit_expression(self, node):
        """
        Visits a single comparison operator rhs and updates the type.
        :param node: an rhs
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

        if ((lhs_type.is_real() or lhs_type.is_integer()) and (rhs_type.is_real() or rhs_type.is_integer())) \
                or (lhs_type.equals(rhs_type) and lhs_type.is_numeric()) or (lhs_type.is_boolean() and
                                                                             rhs_type.is_boolean()):
            node.set_type_either(Either.value(PredefinedTypes.getBooleanType()))
            return

        # Error message for any other operation
        if (lhs_type.is_unit() and rhs_type.is_numeric()) or (rhs_type.is_unit() and lhs_type.is_numeric()):
            # if the incompatibility exists between a unit and a numeric, the c++ will still be fine, just WARN
            error_msg = ErrorStrings.messageComparison(self, node.get_source_position())
            node.set_type_either(Either.value(PredefinedTypes.getBooleanType()))
            Logger.log_message(message=error_msg, code=MessageCode.SOFT_INCOMPATIBILITY,
                               error_position=node.get_source_position(),
                               log_level=LoggingLevel.WARNING)
            return
        else:
            # hard incompatibility, cannot recover in c++, ERROR
            error_msg = ErrorStrings.messageComparison(self, node.get_source_position())
            node.set_type_either(Either.error(error_msg))
            Logger.log_message(code=MessageCode.HARD_INCOMPATIBILITY,
                               error_position=node.get_source_position(),
                               message=error_msg, log_level=LoggingLevel.ERROR)
            return
