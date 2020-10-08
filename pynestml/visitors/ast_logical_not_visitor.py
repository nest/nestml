# -*- coding: utf-8 -*-
#
# ast_logical_not_visitor.py
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
from pynestml.visitors.ast_visitor import ASTVisitor


class ASTLogicalNotVisitor(ASTVisitor):
    """
    Visits a single rhs and updates the type of the sub-rhs.
    """

    def visit_expression(self, node):
        """
        Visits a single rhs with a logical operator and updates the type.
        :param node: a single rhs
        :type node: ast_expression
        """
        expr_type = node.get_expression().type
        expr_type.referenced_object = node.get_expression()
        node.type = expr_type.negate()
