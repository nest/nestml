#
# ASTBinaryLogicVisitortor.py
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
rhs: left=rhs logicalOperator right=rhs
"""
from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
from pynestml.modelprocessor.ErrorStrings import ErrorStrings
from pynestml.modelprocessor.ASTVisitor import ASTVisitor
from pynestml.modelprocessor.Either import Either
from pynestml.modelprocessor.ASTExpression import ASTExpression
from pynestml.utils.Logger import Logger, LOGGING_LEVEL


class ASTBinaryLogicVisitor(ASTVisitor):
    """
    Visits a single binary logical operator rhs and updates its types.
    """

    def visit_expression(self, node):
        """
        Visits an rhs which uses a binary logic operator and updates the type.
        :param node: a single rhs.
        :type node: ASTExpression
        """
        assert (node is not None and isinstance(node, ASTExpression)), \
            '(PyNestML.Visitor.ASTBinaryLogicVisitor) No or wrong type of rhs provided (%s)!' % type(node)
        lhs_type = node.get_lhs().get_type_either()
        rhs_type = node.get_rhs().get_type_either()

        if lhs_type.isError():
            node.set_type_either(lhs_type)
            return
        if rhs_type.isError():
            node.set_type_either(rhs_type)
            return

        if lhs_type.getValue().is_boolean() and rhs_type.getValue().is_boolean():
            node.set_type_either(Either.value(PredefinedTypes.getBooleanType()))
        else:
            error_msg = ErrorStrings.messageLogicOperandsNotBool(self, node.get_source_position())
            node.set_type_either(Either.error(error_msg))
            Logger.logMessage(error_msg, LOGGING_LEVEL.ERROR)
        return
