#
# DotOperatorVisitor.py
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
expression : left=expression (timesOp='*' | divOp='/' | moduloOp='%') right=expression
"""
from __future__ import division
from pynestml.modelprocessor.ASTExpression import ASTExpression
from pynestml.modelprocessor.ModelVisitor import NESTMLVisitor


class DotOperatorVisitor(NESTMLVisitor):
    """
    This visitor is used to derive the correct type of expressions which use a binary dot operator.
    """

    def visit_expression(self, _expr=None):
        """
        Visits a single expression and updates the type.
        :param _expr: a single expression
        :type _expr: ASTExpression
        """
        lhs_type = _expr.getLhs().type
        rhs_type = _expr.getRhs().type

        arith_op = _expr.getBinaryOperator()

        lhs_type.referenced_object = _expr.getLhs()
        rhs_type.referenced_object = _expr.getRhs()

        if arith_op.isModuloOp():
            _expr.type = lhs_type % rhs_type
            return
        if arith_op.isDivOp():
            _expr.type = lhs_type / rhs_type
            return
        if arith_op.isTimesOp():
            _expr.type = lhs_type * rhs_type
            return
