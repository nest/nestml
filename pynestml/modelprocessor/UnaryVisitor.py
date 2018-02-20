#
# UnaryVisitor.py
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
Expr = unaryOperator term=expression
unaryOperator : (unaryPlus='+' | unaryMinus='-' | unaryTilde='~');
"""
from pynestml.modelprocessor.ASTExpression import ASTExpression
from pynestml.modelprocessor.ASTUnaryOperator import ASTUnaryOperator
from pynestml.modelprocessor.Either import Either
from pynestml.modelprocessor.ErrorStrings import ErrorStrings
from pynestml.modelprocessor.ModelVisitor import NESTMLVisitor
from pynestml.utils.Logger import Logger, LOGGING_LEVEL


class UnaryVisitor(NESTMLVisitor):
    """
    Visits an expression consisting of a unary operator, e.g., -, and a sub-expression.
    """

    def visit_expression(self, _expr=None):
        """
        Visits a single unary operator and updates the type of the corresponding expression.
        :param _expr: a single expression
        :type _expr: ASTExpression
        """
        assert (_expr is not None and isinstance(_expr, ASTExpression)), \
            '(PyNestML.Visitor.UnaryVisitor) No or wrong type of expression provided (%s)!' % type(_expr)

        termTypeE = _expr.getExpression().getTypeEither()

        if termTypeE.isError():
            _expr.setTypeEither(termTypeE)
            return

        termType = termTypeE.getValue()
        unaryOp = _expr.getUnaryOperator()

        if unaryOp.isUnaryMinus():
            _expr.type = -termType
            return
        if unaryOp.isUnaryPlus():
            _expr.type = +termType
            return
        if unaryOp.isUnaryTilde():
            _expr.type = ~termType
            return
