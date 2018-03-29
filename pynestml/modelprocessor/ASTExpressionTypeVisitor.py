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
from pynestml.modelprocessor.ASTSimpleExpression import ASTSimpleExpression
from pynestml.modelprocessor.ASTExpression import ASTExpression
from pynestml.modelprocessor.ASTVisitor import ASTVisitor
from pynestml.modelprocessor.BinaryLogicVisitor import BinaryLogicVisitor
from pynestml.modelprocessor.BooleanLiteralVisitor import BooleanLiteralVisitor
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
from pynestml.modelprocessor.VariableVisitor import VariableVisitor


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
    __noSemantics = ASTNoSemantics()
    __comparisonOperatorVisitor = ASTComparisonOperatorVisitor()
    __binaryLogicVisitor = BinaryLogicVisitor()
    __conditionVisitor = ASTConditionVisitor()
    __functionCallVisitor = ASTFunctionCallVisitor()
    __booleanLiteralVisitor = BooleanLiteralVisitor()
    __numericLiteralVisitor = ASTNumericLiteralVisitor()
    __stringLiteralVisitor = StringLiteralVisitor()
    __variableVisitor = VariableVisitor()
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
        self.getRealSelf().visit(_node)
        self.getRealSelf().endvisit(_node)
        return

    def traverseSimpleExpression(self, _node):
        """
        Traverses a simple expression and invokes required subroutines.
        :param _node: a single node.
        :type _node: ASTSimpleExpression
        """
        assert (_node is not None and isinstance(_node, ASTSimpleExpression)), \
            '(PyNestML.ExpressionTypeVisitor) No or wrong type of simple-expression provided (%s)!' % type(_node)
        # handle all simpleExpressions
        if isinstance(_node, ASTSimpleExpression):
            # simpleExpression = functionCall
            if _node.getFunctionCall() is not None:
                self.setRealSelf(self.__functionCallVisitor)
                return
            # simpleExpression =  (INTEGER|FLOAT) (variable)?
            if _node.getNumericLiteral() is not None or \
                    (_node.getNumericLiteral() is not None and _node.getVariable() is not None):
                self.setRealSelf(self.__numericLiteralVisitor)
                return
            # simpleExpression =  variable
            if _node.getVariable() is not None:
                self.setRealSelf(self.__variableVisitor)
                return
            # simpleExpression = BOOLEAN_LITERAL
            if _node.isBooleanTrue() or _node.isBooleanFalse():
                self.setRealSelf(self.__booleanLiteralVisitor)
                return
            # simpleExpression = isInf='inf'
            if _node.isInfLiteral():
                self.setRealSelf(self.__infVisitor)
                return
            # simpleExpression = string=STRING_LITERAL
            if _node.isString():
                self.setRealSelf(self.__stringLiteralVisitor)
                return

        return

    def traverseExpression(self, _node):
        """
        Traverses an expression and executes the required sub-routines.
        :param _node: a single ast node
        :type _node: ASTExpression
        """
        assert (_node is not None and isinstance(_node, ASTExpression)), \
            '(PyNestML.ExpressionTypeVisitor) No or wrong type of expression provided (%s)!' % type(_node)
        # Expr = unaryOperator term=expression
        if _node.getExpression() is not None and _node.getUnaryOperator() is not None:
            _node.getExpression().accept(self)
            self.setRealSelf(self.__unaryVisitor)
            return

        # Parentheses and logicalNot
        if _node.getExpression() is not None:
            _node.getExpression().accept(self)
            # Expr = leftParentheses='(' term=expression rightParentheses=')'
            if _node.isEncapsulated():
                self.setRealSelf(self.__parenthesesVisitor)
                return
            # Expr = logicalNot='not' term=expression
            if _node.isLogicalNot():
                self.setRealSelf(self.__logicalNotVisitor)
                return

        # Rules with binary operators
        if _node.getBinaryOperator() is not None:
            bin_op = _node.getBinaryOperator()
            # All these rules employ left and right side expressions.
            if _node.getLhs() is not None:
                _node.getLhs().accept(self)
            if _node.getRhs() is not None:
                _node.getRhs().accept(self)
            # Handle all Arithmetic Operators:
            if isinstance(bin_op, ASTArithmeticOperator.ASTArithmeticOperator):
                # Expr = <assoc=right> left=expression powOp='**' right=expression
                if bin_op.isPowOp():
                    self.setRealSelf(self.__powVisitor)
                    return
                # Expr = left=expression (timesOp='*' | divOp='/' | moduloOp='%') right=expression
                if bin_op.is_times_op or bin_op.is_div_op or bin_op.is_modulo_op:
                    self.setRealSelf(self.__dotOperatorVisitor)
                    return
                # Expr = left=expression (plusOp='+'  | minusOp='-') right=expression
                if bin_op.isPlusOp() or bin_op.isMinusOp():
                    self.setRealSelf(self.__lineOperatorVisitor)
                    return
            # handle all bitOperators:
            if isinstance(bin_op, ASTBitOperator.ASTBitOperator):
                # Expr = left=expression bitOperator right=expression
                self.setRealSelf(self.__noSemantics)  # TODO: implement something -> future work with more operators
                return
            # handle all comparison Operators:
            if isinstance(bin_op, ASTComparisonOperator.ASTComparisonOperator):
                # Expr = left=expression comparisonOperator right=expression
                self.setRealSelf(self.__comparisonOperatorVisitor)
                return
            # handle all logical Operators
            if isinstance(bin_op, ASTLogicalOperator.ASTLogicalOperator):
                # Expr = left=expression logicalOperator right=expression
                self.setRealSelf(self.__binaryLogicVisitor)
                return

        # Expr = condition=expression '?' ifTrue=expression ':' ifNot=expression
        if _node.getCondition() is not None and _node.getIfTrue() is not None and _node.getIfNot() is not None:
            _node.getCondition().accept(self)
            _node.getIfTrue().accept(self)
            _node.getIfNot().accept(self)
            self.setRealSelf(self.__conditionVisitor)
            return
