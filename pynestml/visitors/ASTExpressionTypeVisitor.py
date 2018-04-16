#
# ASTExpressionTypeVisitor.py
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


from pynestml.meta_model import ASTArithmeticOperator, ASTBitOperator, ASTComparisonOperator, ASTLogicalOperator
from pynestml.meta_model.ASTExpression import ASTExpression
from pynestml.meta_model.ASTSimpleExpression import ASTSimpleExpression
from pynestml.visitors.ASTBinaryLogicVisitor import ASTBinaryLogicVisitor
from pynestml.visitors.ASTBooleanLiteralVisitor import ASTBooleanLiteralVisitor
from pynestml.visitors.ASTComparisonOperatorVisitor import ASTComparisonOperatorVisitor
from pynestml.visitors.ASTConditionVisitor import ASTConditionVisitor
from pynestml.visitors.ASTDotOperatorVisitor import ASTDotOperatorVisitor
from pynestml.visitors.ASTFunctionCallVisitor import ASTFunctionCallVisitor
from pynestml.visitors.ASTInfVisitor import ASTInfVisitor
from pynestml.visitors.ASTLineOperationVisitor import ASTLineOperatorVisitor
from pynestml.visitors.ASTLogicalNotVisitor import ASTLogicalNotVisitor
from pynestml.visitors.ASTNoSemanticsVisitor import ASTNoSemanticsVisitor
from pynestml.visitors.ASTNumericLiteralVisitor import ASTNumericLiteralVisitor
from pynestml.visitors.ASTParenthesesVisitor import ASTParenthesesVisitor
from pynestml.visitors.ASTPowerVisitor import ASTPowerVisitor
from pynestml.visitors.ASTStringLiteralVisitor import ASTStringLiteralVisitor
from pynestml.visitors.ASTUnaryVisitor import ASTUnaryVisitor
from pynestml.visitors.ASTVariableVisitor import ASTVariableVisitor
from pynestml.visitors.ASTVisitor import ASTVisitor


class ASTExpressionTypeVisitor(ASTVisitor):
    """
    This is the main visitor as used to derive the type of an expression. By using different sub-visitors and
    real-self it is possible to adapt to different types of sub-expressions.
    """

    __unaryVisitor = ASTUnaryVisitor()
    __powVisitor = ASTPowerVisitor()
    __parenthesesVisitor = ASTParenthesesVisitor()
    __logicalNotVisitor = ASTLogicalNotVisitor()
    __dotOperatorVisitor = ASTDotOperatorVisitor()
    __lineOperatorVisitor = ASTLineOperatorVisitor()
    __noSemantics = ASTNoSemanticsVisitor()
    __comparisonOperatorVisitor = ASTComparisonOperatorVisitor()
    __binaryLogicVisitor = ASTBinaryLogicVisitor()
    __conditionVisitor = ASTConditionVisitor()
    __functionCallVisitor = ASTFunctionCallVisitor()
    __booleanLiteralVisitor = ASTBooleanLiteralVisitor()
    __numericLiteralVisitor = ASTNumericLiteralVisitor()
    __stringLiteralVisitor = ASTStringLiteralVisitor()
    __variableVisitor = ASTVariableVisitor()
    __infVisitor = ASTInfVisitor()

    def handle(self, _node):
        """
        Handles the handed over node and executes the required sub routines.
        :param _node: a meta_model node.
        :type _node: AST_
        """
        self.traverse(_node)
        self.get_real_self().visit(_node)
        self.get_real_self().endvisit(_node)

    def traverse_simple_expression(self, node):
        """
        Traverses a simple expression and invokes required subroutines.
        :param node: a single node.
        :type node: ASTSimpleExpression
        """
        assert (node is not None and isinstance(node, ASTSimpleExpression)), \
            '(PyNestML.ASTExpressionTypeVisitor) No or wrong type of simple-expression provided (%s)!' % type(node)
        # handle all simpleExpressions
        if isinstance(node, ASTSimpleExpression):
            # simpleExpression = functionCall
            if node.get_function_call() is not None:
                self.set_real_self(self.__functionCallVisitor)
                return
            # simpleExpression =  (INTEGER|FLOAT) (variable)?
            if node.get_numeric_literal() is not None or \
                    (node.get_numeric_literal() is not None and node.get_variable() is not None):
                self.set_real_self(self.__numericLiteralVisitor)
                return
            # simpleExpression =  variable
            if node.get_variable() is not None:
                self.set_real_self(self.__variableVisitor)
                return
            # simpleExpression = BOOLEAN_LITERAL
            if node.is_boolean_true() or node.is_boolean_false():
                self.set_real_self(self.__booleanLiteralVisitor)
                return
            # simpleExpression = isInf='inf'
            if node.is_inf_literal():
                self.set_real_self(self.__infVisitor)
                return
            # simpleExpression = string=STRING_LITERAL
            if node.is_string():
                self.set_real_self(self.__stringLiteralVisitor)
                return

        return

    def traverse_expression(self, _node):
        """
        Traverses an expression and executes the required sub-routines.
        :param _node: a single meta_model node
        :type _node: ASTExpression
        """
        assert (_node is not None and isinstance(_node, ASTExpression)), \
            '(PyNestML.ASTExpressionTypeVisitor) No or wrong type of expression provided (%s)!' % type(_node)
        # Expr = unaryOperator term=expression
        if _node.get_expression() is not None and _node.get_unary_operator() is not None:
            _node.get_expression().accept(self)
            self.set_real_self(self.__unaryVisitor)
            return

        # Parentheses and logicalNot
        if _node.get_expression() is not None:
            _node.get_expression().accept(self)
            # Expr = leftParentheses='(' term=expression rightParentheses=')'
            if _node.is_encapsulated:
                self.set_real_self(self.__parenthesesVisitor)
                return
            # Expr = logicalNot='not' term=expression
            if _node.is_logical_not:
                self.set_real_self(self.__logicalNotVisitor)
                return

        # Rules with binary operators
        if _node.get_binary_operator() is not None:
            bin_op = _node.get_binary_operator()
            # All these rules employ left and right side expressions.
            if _node.get_lhs() is not None:
                _node.get_lhs().accept(self)
            if _node.get_rhs() is not None:
                _node.get_rhs().accept(self)
            # Handle all Arithmetic Operators:
            if isinstance(bin_op, ASTArithmeticOperator.ASTArithmeticOperator):
                # Expr = <assoc=right> left=expression powOp='**' right=expression
                if bin_op.is_pow_op:
                    self.set_real_self(self.__powVisitor)
                    return
                # Expr = left=expression (timesOp='*' | divOp='/' | moduloOp='%') right=expression
                if bin_op.is_times_op or bin_op.is_div_op or bin_op.is_modulo_op:
                    self.set_real_self(self.__dotOperatorVisitor)
                    return
                # Expr = left=expression (plusOp='+'  | minusOp='-') right=expression
                if bin_op.is_plus_op or bin_op.is_minus_op:
                    self.set_real_self(self.__lineOperatorVisitor)
                    return
            # handle all bitOperators:
            if isinstance(bin_op, ASTBitOperator.ASTBitOperator):
                # Expr = left=expression bitOperator right=expression
                self.set_real_self(self.__noSemantics)  # TODO: implement something -> future work with more operators
                return
            # handle all comparison Operators:
            if isinstance(bin_op, ASTComparisonOperator.ASTComparisonOperator):
                # Expr = left=expression comparisonOperator right=expression
                self.set_real_self(self.__comparisonOperatorVisitor)
                return
            # handle all logical Operators
            if isinstance(bin_op, ASTLogicalOperator.ASTLogicalOperator):
                # Expr = left=expression logicalOperator right=expression
                self.set_real_self(self.__binaryLogicVisitor)
                return

        # Expr = condition=expression '?' ifTrue=expression ':' ifNot=expression
        if _node.get_condition() is not None and _node.get_if_true() is not None and _node.get_if_not() is not None:
            _node.get_condition().accept(self)
            _node.get_if_true().accept(self)
            _node.get_if_not().accept(self)
            self.set_real_self(self.__conditionVisitor)
            return
