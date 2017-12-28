#
# ImplicitVersionPropagator.py
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
from pynestml.nestml.ASTExpression import ASTExpression
from pynestml.nestml.NESTMLVisitor import NESTMLVisitor

"""
Updates the hierarchy of expressions by merging implicitVersions from sub-expressions into the implicitVersions of their parent
"""

class ImplicitVersionPropagator(NESTMLVisitor):

    @classmethod
    def propagateImplicitVersions(cls,_astElement):
        instance = ImplicitVersionPropagator()
        _astElement.accept(instance)
        return

    def visitSimpleExpression(self, _expr=None):
        """
        set all implicitVersions to the original expressions iff implicitVersion was None
        :param _expr:
        :return:
        """

        if _expr.getImplicitVersion() is None:
            _expr.setImplicitVersion(_expr)
        return

    def visitExpression(self, _expr=None):
        """
        set all implicitVersions to the original expressions iff implicitVersion was None
        :param _expr:
        :return:
        """

        if _expr.getImplicitVersion() is None:
            _expr.setImplicitVersion(_expr)
        return


    def endvisitExpression(self, _expr=None):

        assert _expr is not None
        assert isinstance(_expr,ASTExpression)

        #make sure subexpressions are already evaluated
        if isinstance(_expr,ASTExpression):
            if _expr.isExpression():
                assert _expr.getExpression().getImplicitVersion() is not None

            if _expr.isCompoundExpression():
                assert _expr.getLhs().getImplicitVersion() is not None
                assert _expr.getRhs().getImplicitVersion() is not None

            if _expr.isTernaryOperator():
                assert _expr.getCondition().getImplicitVersion() is not None
                assert _expr.getIfNot().getImplicitVersion() is not None
                assert _expr.getIfTrue().getImplicitVersion() is not None


        #handle expressions with only one sub expression ('term' in grammar)
        if _expr.getExpression() is not None:
            implicitVersion = ASTExpression.makeExpression(_expr.isEncapsulated(),
                                                           _unaryOperator=_expr.getUnaryOperator(),
                                                           _isLogicalNot=_expr.isLogicalNot(),
                                                           _expression=_expr.getExpression().getImplicitVersion(),
                                                           _sourcePosition= _expr.getSourcePosition())
        #handle expressions with 2 sub expressions ('left' and 'right' in grammar)
        if _expr.getLhs() is not None: #implicitly means that rhs is also not None
            implicitVersion = ASTExpression.makeCompoundExpression(_lhs= _expr.getLhs().getImplicitVersion(),
                                                                   _binaryOperator= _expr.getBinaryOperator(),
                                                                   _rhs= _expr.getRhs().getImplicitVersion(),
                                                                   _sourcePosition=_expr.getSourcePosition())
        #handle ternary expressions ('condition' 'ifTrue' and 'ifNot' in grammar)
        if _expr.isTernaryOperator():
            implicitVersion = ASTExpression.makeTernaryExpression(_condition=_expr.getCondition().getImplicitVersion(),
                                                                  _ifTrue= _expr.getIfTrue().getImplicitVersion(),
                                                                  _ifNot= _expr.getIfNot().getImplicitVersion(),
                                                                  _sourcePosition= _expr.getSourcePosition())

        #only update implicitVersion iff it is not set to the same as the original (this MUST be checked as we cannot assume we are on the first run of the visitor)
        if id(_expr) != id(_expr.getImplicitVersion()):
            peter = 2
            return


        return

