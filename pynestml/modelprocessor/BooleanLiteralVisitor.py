#
# BooleanLiteralVisitor.py
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
simpleExpression : BOOLEAN_LITERAL // true & false;
"""
from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
from pynestml.modelprocessor.ASTVisitor import ASTVisitor
from pynestml.modelprocessor.Either import Either
from pynestml.modelprocessor.ASTSimpleExpression import ASTSimpleExpression


class BooleanLiteralVisitor(ASTVisitor):
    """
    Visits a single boolean literal and updates its type.
    """

    def visitSimpleExpression(self, _expr=None):
        """
        Visits a single simple expression containing a boolean literal and updates its type.
        :param _expr: a simple expression.
        :type _expr: ASTSimpleExpression
        """
        assert (_expr is not None and isinstance(_expr, ASTSimpleExpression)), \
            '(PyNestML.Visitor.BooleanLiteralVisitor) No or wrong type of simple expression provided (%s)!' % type(
                _expr)
        _expr.setTypeEither(Either.value(PredefinedTypes.getBooleanType()))
        return
