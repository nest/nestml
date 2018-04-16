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
import copy

from pynestml.meta_model.ASTNodeFactory import ASTNodeFactory
from pynestml.visitors.ASTVisitor import ASTVisitor


class ImplicitVersionPropagator(ASTVisitor):
    """
    Updates the hierarchy of expressions by merging implicitVersions from sub-expressions into the implicitVersions
    of their parent
    """

    # TODO: this class is currently not used, but under construction

    @classmethod
    def propagate_implicit_versions(cls, node):
        instance = ImplicitVersionPropagator()
        node.accept(instance)
        return

    def visit_simple_expression(self, node):
        """
        set all implicitVersions to the original expressions iff implicitVersion was None
        :param node:
        :return:
        """

        if node.getImplicitVersion() is None:
            deepcopy = copy.deepcopy(node)
            node.setImplicitVersion(deepcopy)
        return

    def visit_expression(self, node):
        """
        set all implicitVersions to the original expressions iff implicitVersion was None
        :param node:
        :return:
        """

        if node.getImplicitVersion() is None:
            deepcopy = copy.deepcopy(node)
            node.setImplicitVersion(deepcopy)
        return

    def endvisit_expression(self, node):
        from pynestml.meta_model.ASTExpression import ASTExpression
        assert node is not None
        assert isinstance(node, ASTExpression)

        # make sure subexpressions are already evaluated
        if isinstance(node, ASTExpression):
            # todo by KP: getImplicitVersion is not there?
            if node.is_expression():
                assert node.get_expression().getImplicitVersion() is not None

            if node.is_compound_expression():
                assert node.get_lhs().getImplicitVersion() is not None
                assert node.get_rhs().getImplicitVersion() is not None

            if node.is_ternary_operator():
                assert node.get_condition().getImplicitVersion() is not None
                assert node.get_if_not().getImplicitVersion() is not None
                assert node.get_if_true().getImplicitVersion() is not None

        # handle expressions with only one sub expression ('term' in grammar)
        if node.get_expression() is not None:
            implicitVersion = ASTNodeFactory.create_ast_expression(
                is_encapsulated=node.isEncapsulated(),
                unary_operator=node.getUnaryOperator(),
                is_logical_not=node.isLogicalNot(),
                expression=node.getExpression().getImplicitVersion(),
                source_position=node.getSourcePosition())
        # handle expressions with 2 sub expressions ('left' and 'right' in grammar)
        if node.get_lhs() is not None:  # implicitly means that rhs is also not None
            implicitVersion = ASTNodeFactory.create_ast_compound_expression(
                lhs=node.getLhs().getImplicitVersion(),
                binary_operator=node.get_binary_operator(),
                rhs=node.getRhs().getImplicitVersion(),
                source_position=node.get_source_position())
        # handle ternary expressions ('condition' 'ifTrue' and 'ifNot' in grammar)
        if node.is_ternary_operator():
            implicitVersion = ASTNodeFactory.create_ast_ternary_expression(
                condition=node.getCondition().getImplicitVersion(),
                if_true=node.getIfTrue().getImplicitVersion(),
                if_not=node.getIfNot().getImplicitVersion(),
                source_position=node.get_source_position())

        # only update implicitVersion iff it is not set to the same as the original (this MUST be checked as we cannot assume we are on the first run of the visitor)
        if id(node) != id(node.getImplicitVersion()):
            peter = 2
            return

        return
