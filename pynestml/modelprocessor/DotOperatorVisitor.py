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
        assert (_expr is not None and isinstance(_expr, ASTExpression)), \
            '(PyNestML.Visitor.DotOperatorVisitor) No or wrong type of expression provided (%s)!' % type(_expr)
        lhsTypeE = _expr.getLhs().getTypeEither()
        rhsTypeE = _expr.getRhs().getTypeEither()

        if lhsTypeE.isError():
            _expr.setTypeEither(lhsTypeE)
            return

        if rhsTypeE.isError():
            _expr.setTypeEither(rhsTypeE)
            return

        lhsType = lhsTypeE.getValue()
        rhsType = rhsTypeE.getValue()

        arithOp = _expr.getBinaryOperator()
        if arithOp.isModuloOp():
            _expr.type = lhsType % rhsType
            return
        if arithOp.isDivOp():
            _expr.type = lhsType / rhsType
            return
        if arithOp.isTimesOp():
            _expr.type = lhsType * rhsType
            return