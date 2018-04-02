#
# ASTLogicalNotVisitortor.py
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
rhs: logicalNot='not' term=rhs
"""
from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
from pynestml.modelprocessor.ErrorStrings import ErrorStrings
from pynestml.modelprocessor.ASTVisitor import ASTVisitor
from pynestml.modelprocessor.Either import Either
from pynestml.modelprocessor.ASTExpression import ASTExpression
from pynestml.utils.Logger import Logger, LOGGING_LEVEL
from pynestml.utils.Messages import MessageCode


class ASTLogicalNotVisitor(ASTVisitor):
    """
    Visits a single rhs and updates the type of the sub-rhs.
    """

    def visit_expression(self, node):
        """
        Visits a single rhs with a logical operator and updates the type.
        :param node: a single rhs
        :type node: ASTExpression
        """
        expr_type_e = node.get_expression().get_type_either()

        if expr_type_e.isError():
            node.set_type_either(expr_type_e)
            return

        expr_type = expr_type_e.getValue()

        if expr_type.is_boolean():
            node.set_type_either(Either.value(PredefinedTypes.getBooleanType()))
        else:
            error_msg = ErrorStrings.messageExpectedBool(self, node.get_source_position())
            node.set_type_either(Either.error(error_msg))
            Logger.logMessage(_errorPosition=node.get_source_position(),
                              _code=MessageCode.TYPE_DIFFERENT_FROM_EXPECTED,
                              _message=error_msg, _logLevel=LOGGING_LEVEL.ERROR)
