#
# ASTParenthesesVisitor.py.py
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
rhs : leftParentheses='(' term=rhs rightParentheses=')'
"""
from pynestml.modelprocessor.ASTVisitor import ASTVisitor
from pynestml.modelprocessor.ASTExpression import ASTExpression


class ASTParenthesesVisitor(ASTVisitor):
    """
    Visits a single rhs encapsulated in brackets and updates its type.
    """

    def visit_expression(self, node=None):
        """
        Visits a single rhs encapsulated in parenthesis and updates its type.
        :param node: a single rhs
        :type node: ASTExpression
        """
        assert (node is not None and isinstance(node, ASTExpression)), \
            '(PyNestML.Visitor.ASTParenthesesVisitor) No or wrong type of rhs provided (%s)!' % type(node)
        node.set_type_either(node.get_expression().get_type_either())
        return
