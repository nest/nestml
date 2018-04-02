#
# ASTStringLiteralVisitor.py
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
simpleExpression : string=STRING_LITERAL
"""
from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
from pynestml.modelprocessor.ASTVisitor import ASTVisitor
from pynestml.modelprocessor.Either import Either
from pynestml.modelprocessor.ASTSimpleExpression import ASTSimpleExpression


class StringLiteralVisitor(ASTVisitor):
    """
    Visits a string literal and updates its type.
    """

    def visit_simple_expression(self, node=None):
        """
        Visits a singe simple rhs which consists of a string literal and updates the type.
        :param node: a simple rhs containing a string literal
        :type node: ASTSimpleExpression
        """
        assert (node is not None and isinstance(node, ASTSimpleExpression)), \
            '(PyNestML.Visitor.StringLiteralVisitor) No or wrong type of simple rhs provided (%s)!' % type(node)
        node.set_type_either(Either.value(PredefinedTypes.getStringType()))
        return
