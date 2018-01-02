#
# ParenthesesVisitor.py
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
expression : leftParentheses='(' term=expression rightParentheses=')'
"""
from pynestml.modelprocessor.ModelVisitor import NESTMLVisitor
from pynestml.modelprocessor.ASTExpression import ASTExpression


class ParenthesesVisitor(NESTMLVisitor):
    """
    Visits a single expression encapsulated in brackets and updates its type.
    """

    def visitExpression(self, _expr=None):
        """
        Visits a single expression encapsulated in parenthesis and updates its type.
        :param _expr: a single expression
        :type _expr: ASTExpression
        """
        assert (_expr is not None and isinstance(_expr, ASTExpression)), \
            '(PyNestML.Visitor.ParenthesesVisitor) No or wrong type of expression provided (%s)!' % type(_expr)
        _expr.setTypeEither(_expr.getExpression().getTypeEither())
        return
