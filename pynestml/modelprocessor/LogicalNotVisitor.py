#
# LogicalNotVisitor.py
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
expression: logicalNot='not' term=expression
"""
from pynestml.modelprocessor.ASTExpression import ASTExpression
from pynestml.modelprocessor.ModelVisitor import NESTMLVisitor


class LogicalNotVisitor(NESTMLVisitor):
    """
    Visits a single expression and updates the type of the sub-expression.
    """

    def visit_expression(self, _expr=None):
        """
        Visits a single expression with a logical operator and updates the type.
        :param _expr: a single expression
        :type _expr: ASTExpression
        """
        expr_type = _expr.getExpression().type

        expr_type.referenced_object = _expr.getExpression()

        _expr.type = expr_type.negate()
