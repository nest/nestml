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


from pynestml.modelprocessor import ASTArithmeticOperator, ASTBitOperator, ASTComparisonOperator, ASTLogicalOperator
from pynestml.modelprocessor.ASTSimpleExpression import ASTSimpleExpression
from pynestml.modelprocessor.ASTExpression import ASTExpression
from pynestml.modelprocessor.ASTVisitor import ASTVisitor
from pynestml.modelprocessor.ASTBinaryLogicVisitor import ASTBinaryLogicVisitor
from pynestml.modelprocessor.ASTBooleanLiteralVisitor import ASTBooleanLiteralVisitor
from pynestml.modelprocessor.ASTComparisonOperatorVisitor import ASTComparisonOperatorVisitor
from pynestml.modelprocessor.ASTConditionVisitor import ASTConditionVisitor
from pynestml.modelprocessor.ASTDotOperatorVisitor import ASTDotOperatorVisitor
from pynestml.modelprocessor.ASTFunctionCallVisitor import ASTFunctionCallVisitor
from pynestml.modelprocessor.ASTInfVisitor import ASTInfVisitor
from pynestml.modelprocessor.ASTLineOperationVisitor import ASTLineOperatorVisitor
from pynestml.modelprocessor.ASTLogicalNotVisitor import ASTLogicalNotVisitor
from pynestml.modelprocessor.ASTNoSemantics import ASTNoSemantics
from pynestml.modelprocessor.ASTNumericLiteralVisitor import ASTNumericLiteralVisitor
from pynestml.modelprocessor.ASTParenthesesVisitor import ASTParenthesesVisitor
from pynestml.modelprocessor.ASTPowerVisitor import ASTPowerVisitor
from pynestml.modelprocessor.ASTStringLiteralVisitor import StringLiteralVisitor
from pynestml.modelprocessor.ASTUnaryVisitor import ASTUnaryVisitor
from pynestml.modelprocessor.ASTVariableVisitor import ASTVariableVisitor


class ASTExpressionTypeVisitor(ASTVisitor):
    """
    This is the main visitor as used to derive the type of an rhs. By using different sub-visitors and
    real-self it is possible to adapt to different types of sub-expressions.
    """

    __unaryVisitor = ASTUnaryVisitor()
    __powVisitor = ASTPowerVisitor()
    __parenthesesVisitor = ASTParenthesesVisitor()
    __logicalNotVisitor = ASTLogicalNotVisitor()
    __dotOperatorVisitor = ASTDotOperatorVisitor()
    __lineOperatorVisitor = ASTLineOperatorVisitor()
    __noSemantics = ASTNoSemantics()
    __comparisonOperatorVisitor = ASTComparisonOperatorVisitor()
    __binaryLogicVisitor = ASTBinaryLogicVisitor()
    __conditionVisitor = ASTConditionVisitor()
    __functionCallVisitor = ASTFunctionCallVisitor()
    __booleanLiteralVisitor = ASTBooleanLiteralVisitor()
    __numericLiteralVisitor = ASTNumericLiteralVisitor()
    __stringLiteralVisitor = StringLiteralVisitor()
    __variableVisitor = ASTVariableVisitor()
    __infVisitor = ASTInfVisitor()

    def handle(self, _node):
        """
        Handles the handed over node and executes the required sub routines.
        :param _node: a ast node.
        :type _node: AST_
        """
        assert (_node is not None), \
            '(PyNestML.Visitor.ExpressionTypeVisitor) No ast node provided (%s)!' % type(_node)
        self.traverse(_node)
        self.get_real_self().visit(_node)
        self.get_real_self().endvisit(_node)
        return

    def traverse_simple_expression(self, node):
        """
        Traverses a simple rhs and invokes required subroutines.
        :param node: a single node.
        :type node: ASTSimpleExpression
        """
        assert (node is not None and isinstance(node, ASTSimpleExpression)), \
            '(PyNestML.ExpressionTypeVisitor) No or wrong type of simple-rhs provided (%s)!' % type(node)
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

    def traverse_expression(self, node):
        """
        Traverses an rhs and executes the required sub-routines.
        :param node: a single ast node
        :type node: ASTExpression
        """
        assert (node is not None and isinstance(node, ASTExpression)), \
            '(PyNestML.ExpressionTypeVisitor) No or wrong type of rhs provided (%s)!' % type(node)
        # Expr = unaryOperator term=rhs
        if node.get_expression() is not None and node.get_unary_operator() is not None:
            node.get_expression().accept(self)
            self.set_real_self(self.__unaryVisitor)
            return

        # Parentheses and logicalNot
        if node.get_expression() is not None:
            node.get_expression().accept(self)
            # Expr = leftParentheses='(' term=rhs rightParentheses=')'
            if node.is_encapsulated:
                self.set_real_self(self.__parenthesesVisitor)
                return
            # Expr = logicalNot='not' term=rhs
            if node.isLogicalNot():
                self.set_real_self(self.__logicalNotVisitor)
                return

        # Rules with binary operators
        if node.get_binary_operator() is not None:
            bin_op = node.get_binary_operator()
            # All these rules employ left and right side expressions.
            if node.get_lhs() is not None:
                node.get_lhs().accept(self)
            if node.get_rhs() is not None:
                node.get_rhs().accept(self)
            # Handle all Arithmetic Operators:
            if isinstance(bin_op, ASTArithmeticOperator.ASTArithmeticOperator):
                # Expr = <assoc=right> left=rhs powOp='**' right=rhs
                if bin_op.is_pow_op:
                    self.set_real_self(self.__powVisitor)
                    return
                # Expr = left=rhs (timesOp='*' | divOp='/' | moduloOp='%') right=rhs
                if bin_op.is_times_op or bin_op.is_div_op or bin_op.is_modulo_op:
                    self.set_real_self(self.__dotOperatorVisitor)
                    return
                # Expr = left=rhs (plusOp='+'  | minusOp='-') right=rhs
                if bin_op.is_plus_op or bin_op.is_minus_op:
                    self.set_real_self(self.__lineOperatorVisitor)
                    return
            # handle all bitOperators:
            if isinstance(bin_op, ASTBitOperator.ASTBitOperator):
                # Expr = left=rhs bitOperator right=rhs
                self.set_real_self(self.__noSemantics)  # TODO: implement something -> future work with more operators
                return
            # handle all comparison Operators:
            if isinstance(bin_op, ASTComparisonOperator.ASTComparisonOperator):
                # Expr = left=rhs comparisonOperator right=rhs
                self.set_real_self(self.__comparisonOperatorVisitor)
                return
            # handle all logical Operators
            if isinstance(bin_op, ASTLogicalOperator.ASTLogicalOperator):
                # Expr = left=rhs logicalOperator right=rhs
                self.set_real_self(self.__binaryLogicVisitor)
                return

        # Expr = condition=rhs '?' ifTrue=rhs ':' ifNot=rhs
        if node.get_condition() is not None and node.get_if_true() is not None and node.get_if_not() is not None:
            node.get_condition().accept(self)
            node.get_if_true().accept(self)
            node.get_if_not().accept(self)
            self.set_real_self(self.__conditionVisitor)
            return
