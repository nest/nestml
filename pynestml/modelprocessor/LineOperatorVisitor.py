#
# LineOperatorVisitor.py
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
expression : left=expression (plusOp='+'  | minusOp='-') right=expression
"""
from pynestml.modelprocessor.ImplicitMagnitudeCastException import ImplicitMagnitudeCastException
from pynestml.modelprocessor.ASTExpression import ASTExpression
from pynestml.modelprocessor.DeferredLoggingException import DeferredLoggingException
from pynestml.modelprocessor.ErrorTypeSymbol import ErrorTypeSymbol
from pynestml.modelprocessor.ImplicitCastException import ImplicitCastException
from pynestml.modelprocessor.ModelVisitor import NESTMLVisitor
from pynestml.utils.Logger import Logger, LOGGING_LEVEL


class LineOperatorVisitor(NESTMLVisitor):
    """
    Visits a single binary operation consisting of + or - and updates the type accordingly.
    """

    def visit_expression(self, _expr=None):
        """
        Visits a single expression containing a plus or minus operator and updates its type.
        :param _expr: a single expression
        :type _expr: ASTExpression
        """
        assert (_expr is not None and isinstance(_expr, ASTExpression)), \
            '(PyNestML.Visitor.LineOperatorVisitor) No or wrong type of expression provided (%s)!' % type(_expr)
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

        lhsType.referenced_object = _expr.getLhs()
        rhsType.referenced_object = _expr.getRhs()

        if arithOp.isPlusOp():
            _expr.type = lhsType + rhsType
            return
        elif arithOp.isMinusOp():
            _expr.type = lhsType - rhsType
            return
