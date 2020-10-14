# -*- coding: utf-8 -*-
#
# ast_line_operation_visitor.py
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
from pynestml.visitors.ast_visitor import ASTVisitor
from pynestml.symbols.error_type_symbol import ErrorTypeSymbol
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages


class ASTLineOperatorVisitor(ASTVisitor):
    """
    Visits a single binary operation consisting of + or - and updates the type accordingly.
    """

    def visit_expression(self, node):
        """
        Visits a single expression containing a plus or minus operator and updates its type.
        :param node: a single expression
        :type node: ast_expression
        """
        lhs_type = node.get_lhs().type
        rhs_type = node.get_rhs().type

        arith_op = node.get_binary_operator()

        lhs_type.referenced_object = node.get_lhs()
        rhs_type.referenced_object = node.get_rhs()

        node.type = ErrorTypeSymbol()
        if arith_op.is_plus_op:
            node.type = lhs_type + rhs_type
        elif arith_op.is_minus_op:
            node.type = lhs_type - rhs_type

        if isinstance(node.type, ErrorTypeSymbol):
            code, message = Messages.get_binary_operation_type_could_not_be_derived(lhs=str(node.get_lhs()), operator=str(
                arith_op), rhs=str(node.get_rhs()), lhs_type=str(lhs_type.print_nestml_type()), rhs_type=str(rhs_type.print_nestml_type()))
            Logger.log_message(code=code, message=message, error_position=node.get_source_position(),
                               log_level=LoggingLevel.ERROR)
