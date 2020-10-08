# -*- coding: utf-8 -*-
#
# ast_binary_logic_visitor.py
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
from pynestml.symbols.boolean_type_symbol import BooleanTypeSymbol
from pynestml.symbols.error_type_symbol import ErrorTypeSymbol
from pynestml.symbols.predefined_types import PredefinedTypes
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_visitor import ASTVisitor


class ASTBinaryLogicVisitor(ASTVisitor):
    """
    Visits a single binary logical operator rhs and updates its types.
    """

    def visit_expression(self, node):
        """
        Visits an expression which uses a binary logic operator and updates the type.
        :param node: a single expression.
        :type node: ast_expression
        """
        lhs_type = node.get_lhs().type
        rhs_type = node.get_rhs().type

        lhs_type.referenced_object = node.get_lhs()
        rhs_type.referenced_object = node.get_rhs()

        if isinstance(lhs_type, BooleanTypeSymbol) and isinstance(rhs_type, BooleanTypeSymbol):
            node.type = PredefinedTypes.get_boolean_type()
        else:
            if isinstance(lhs_type, BooleanTypeSymbol):
                offending_type = lhs_type
            else:
                offending_type = rhs_type
            code, message = Messages.get_type_different_from_expected(BooleanTypeSymbol(), offending_type)
            Logger.log_message(code=code, message=message,
                               error_position=lhs_type.referenced_object.get_source_position(),
                               log_level=LoggingLevel.ERROR)
            node.type = ErrorTypeSymbol()
        return
