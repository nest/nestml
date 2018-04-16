#
# ASTAssignment.py
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

from pynestml.meta_model.ASTNode import ASTNode
from pynestml.meta_model.ASTVariable import ASTVariable


class ASTAssignment(ASTNode):
    """
    This class is used to store assignments.
    Grammar:
        assignment : lhsVariable=variable
            (directAssignment='='       |
            compoundSum='+='     |
            compoundMinus='-='   |
            compoundProduct='*=' |
            compoundQuotient='/=') rhs;
    """
    lhs = None
    is_direct_assignment = False
    is_compound_sum = False
    is_compound_minus = False
    is_compound_product = False
    is_compound_quotient = False
    rhs = None

    def __init__(self, lhs=None, is_direct_assignment=False, is_compound_sum=False, is_compound_minus=False,
                 is_compound_product=False, is_compound_quotient=False, rhs=None, source_position=None):
        """
        Standard constructor.
        :param lhs: the left-hand side variable to which is assigned to.
        :type lhs: ASTVariable
        :param is_direct_assignment: is a direct assignment
        :type is_direct_assignment: bool
        :param is_compound_sum: is a compound sum
        :type is_compound_sum: bool
        :param is_compound_minus: is a compound minus
        :type is_compound_minus: bool
        :param is_compound_product: is a compound product
        :type is_compound_product: bool
        :param is_compound_quotient: is a compound quotient
        :type is_compound_quotient: bool
        :param rhs: an meta_model-rhs object
        :type rhs: ASTExpression
        :param source_position: The source position of the assignment
        :type source_position: ASTSourceLocation
        """
        super(ASTAssignment, self).__init__(source_position)
        self.lhs = lhs
        self.is_direct_assignment = is_direct_assignment
        self.is_compound_sum = is_compound_sum
        self.is_compound_minus = is_compound_minus
        self.is_compound_product = is_compound_product
        self.is_compound_quotient = is_compound_quotient
        self.rhs = rhs
        return

    def get_variable(self):
        """
        Returns the left-hand side variable.
        :return: left-hand side variable object.
        :rtype: ASTVariable
        """
        return self.lhs

    def get_expression(self):
        """
        Returns the right-hand side rhs.
        :return: rhs object.
        :rtype: ASTExpression
        """
        return self.rhs

    def get_parent(self, ast):
        """
        Indicates whether a this node contains the handed over node.
        :param ast: an arbitrary meta_model node.
        :type ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        if self.get_variable() is ast:
            return self
        elif self.get_expression() is ast:
            return self
        if self.get_variable().get_parent(ast) is not None:
            return self.get_variable().get_parent(ast)
        if self.get_expression().get_parent(ast) is not None:
            return self.get_expression().get_parent(ast)
        return None

    def __str__(self):
        """
        Returns a string representing the assignment.
        :return: a string representing the assignment.
        :rtype: str
        """
        ret = str(self.lhs)
        if self.is_compound_quotient:
            ret += '/='
        elif self.is_compound_product:
            ret += '*='
        elif self.is_compound_minus:
            ret += '-='
        elif self.is_compound_sum:
            ret += '+='
        else:
            ret += '='
        ret += str(self.rhs)
        return ret

    def equals(self, other):
        """
        The equals operation.
        :param other: a different object.
        :type other: object
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(other, ASTAssignment):
            return False
        return (self.get_variable().equals(other.get_variable()) and
                self.is_compound_quotient == other.is_compound_quotient and
                self.is_compound_product == other.is_compound_product and
                self.is_compound_minus == other.is_compound_minus and
                self.is_compound_sum == other.is_compound_sum and
                self.is_direct_assignment == other.is_direct_assignment and
                self.get_expression().equals(other.get_expression()))

    def deconstructCompoundAssignment(self):
        """
        From lhs and rhs it constructs a new expression which corresponds to direct assignment.
        E.g.: a += b*c -> a = a + b*c
        :return: the rhs for an equivalent direct assignment.
        :rtype: ASTExpression
        """
        from pynestml.visitors.ASTSymbolTableVisitor import ASTSymbolTableVisitor
        # TODO: get rid of this through polymorphism?
        assert not self.is_direct_assignment, "Can only be invoked on a compound assignment."

        operator = self.extractOperatorFromCompoundAssignment()
        lhs_variable = self.getLhsVariableAsExpression()
        rhs_in_brackets = self.getBracketedRhsExpression()
        result = self.constructEquivalentDirectAssignmentRhs(operator, lhs_variable, rhs_in_brackets)
        # create symbols for the new Expression:
        ASTSymbolTableVisitor.visit_expression(result)
        return result

    def getLhsVariableAsExpression(self):
        from pynestml.meta_model.ASTNodeFactory import ASTNodeFactory
        # TODO: maybe calculate new source positions exactly?
        result = ASTNodeFactory.create_ast_simple_expression(variable=self.get_variable(),
                                                             source_position=self.get_variable().get_source_position())
        result.update_scope(self.get_scope())
        return result

    def extractOperatorFromCompoundAssignment(self):
        from pynestml.meta_model.ASTNodeFactory import ASTNodeFactory
        assert not self.is_direct_assignment
        # TODO: maybe calculate new source positions exactly?
        if self.is_compound_minus:
            result = ASTNodeFactory.create_ast_arithmetic_operator(is_minus_op=True,
                                                                   source_position=self.get_source_position())
        if self.is_compound_product:
            result = ASTNodeFactory.create_ast_arithmetic_operator(is_times_op=True,
                                                                   source_position=self.get_source_position())
        if self.is_compound_quotient:
            result = ASTNodeFactory.create_ast_arithmetic_operator(is_div_op=True,
                                                                   source_position=self.get_source_position())
        if self.is_compound_sum:
            result = ASTNodeFactory.create_ast_arithmetic_operator(is_plus_op=True,
                                                                   source_position=self.get_source_position())
        result.update_scope(self.get_scope())
        return result

    def getBracketedRhsExpression(self):
        from pynestml.meta_model.ASTNodeFactory import ASTNodeFactory
        # TODO: maybe calculate new source positions exactly?
        result = ASTNodeFactory.create_ast_expression(is_encapsulated=True,
                                                      expression=self.get_expression(),
                                                      source_position=self.get_expression().get_source_position())
        result.updateScope(self.get_scope())
        return result

    def constructEquivalentDirectAssignmentRhs(self, _operator, _lhsVariable, _rhsInBrackets):
        from pynestml.meta_model.ASTNodeFactory import ASTNodeFactory
        # TODO: maybe calculate new source positions exactly?
        result = ASTNodeFactory.create_ast_compound_expression(lhs=_lhsVariable, binary_operator=_operator,
                                                               rhs=_rhsInBrackets,
                                                               source_position=self.get_source_position())
        result.update_scope(self.get_scope())
        return result

    def resolveLhsVariableSymbol(self):
        return self.get_variable().resolveInOwnScope()
