# -*- coding: utf-8 -*-
#
# ast_unary_visitor.py
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
Expr = unaryOperator term=rhs
unaryOperator : (unaryPlus='+' | unaryMinus='-' | unaryTilde='~');
"""
from pynestml.visitors.ast_visitor import ASTVisitor


class ASTUnaryVisitor(ASTVisitor):
    """
    Visits an rhs consisting of a unary operator, e.g., -, and a sub-rhs.
    """

    def visit_expression(self, node):
        """
        Visits a single unary operator and updates the type of the corresponding expression.
        :param node: a single expression
        :type node: ast_expression
        """
        term_type = node.get_expression().type

        unary_op = node.get_unary_operator()

        term_type.referenced_object = node.get_expression()

        if unary_op.is_unary_minus:
            node.type = -term_type
            return
        if unary_op.is_unary_plus:
            node.type = +term_type
            return
        if unary_op.is_unary_tilde:
            node.type = ~term_type
            return
