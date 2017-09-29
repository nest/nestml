#
# ExpressionTypeVisitor.py
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


from pynestml.src.main.python.org.nestml.ast import ASTArithmeticOperator, ASTBitOperator, ASTComparisonOperator, \
    ASTLogicalOperator
from pynestml.src.main.python.org.nestml.visitor.NESTMLVisitor import NESTMLVisitor
from pynestml.src.main.python.org.nestml.visitor.expression_visitor.BinaryLogicVisitor import BinaryLogicVisitor
from pynestml.src.main.python.org.nestml.visitor.expression_visitor.BooleanLiteralVisitor import BooleanLiteralVisitor
from pynestml.src.main.python.org.nestml.visitor.expression_visitor.ComparisonOperatorVisitor import \
    ComparisonOperatorVisitor
from pynestml.src.main.python.org.nestml.visitor.expression_visitor.ConditionVisitor import ConditionVisitor
from pynestml.src.main.python.org.nestml.visitor.expression_visitor.DotOperatorVisitor import DotOperatorVisitor
from pynestml.src.main.python.org.nestml.visitor.expression_visitor.FunctionCallVisitor import FunctionCallVisitor
from pynestml.src.main.python.org.nestml.visitor.expression_visitor.InfVisitor import InfVisitor
from pynestml.src.main.python.org.nestml.visitor.expression_visitor.LineOperationVisitor import LineOperatorVisitor
from pynestml.src.main.python.org.nestml.visitor.expression_visitor.LogicalNotVisitor import LogicalNotVisitor
from pynestml.src.main.python.org.nestml.visitor.expression_visitor.NoSemantics import NoSemantics
from pynestml.src.main.python.org.nestml.visitor.expression_visitor.NumericLiteralVisitor import NumericLiteralVisitor
from pynestml.src.main.python.org.nestml.visitor.expression_visitor.ParenthesesVisitor import ParenthesesVisitor
from pynestml.src.main.python.org.nestml.visitor.expression_visitor.PowVisitor import PowVisitor
from pynestml.src.main.python.org.nestml.visitor.expression_visitor.StringLiteralVisitor import StringLiteralVisitor
from pynestml.src.main.python.org.nestml.visitor.expression_visitor.UnaryVisitor import UnaryVisitor
from pynestml.src.main.python.org.nestml.visitor.expression_visitor.VariableVisitor import VariableVisitor


class ExpressionTypeVisitor(NESTMLVisitor):
    __unaryVisitor = UnaryVisitor()
    __powVisitor  = PowVisitor()
    __parenthesesVisitor = ParenthesesVisitor()
    __logicalNotVisitor = LogicalNotVisitor()
    __dotOperatorVisitor = DotOperatorVisitor()
    __lineOperatorVisitor = LineOperatorVisitor()
    __noSemantics = NoSemantics()
    __comparisonOperatorVisitor = ComparisonOperatorVisitor()
    __binaryLogicVisitor = BinaryLogicVisitor()
    __conditionVisitor = ConditionVisitor()
    __functionCallVisitor = FunctionCallVisitor()
    __booleanLiteralVisitor = BooleanLiteralVisitor()
    __numericLiteralVisitor = NumericLiteralVisitor()
    __stringLiteralVisitor = StringLiteralVisitor()
    __variableVisitor = VariableVisitor()
    __infVisitor = InfVisitor()

    def handle(self,_node):
        self.traverse(_node)
        self.getRealSelf().visit(_node)
        self.getRealSelf().endVisit(_node)
        return


    def traverseExpression(self, _node):
        #Expr = unaryOperator term=expression
        if _node.getExpression() is not None and _node.getUnaryOperator() is not None:
            _node.getExpression().accept(self)
            self.setRealSelf(self.__unaryVisitor)
            return

        #Parentheses and logicalNot
        if _node.getExpression() is not None and not _node.isSimpleExpression():
            _node.getExpression().accept(self)
            #Expr = leftParentheses='(' term=expression rightParentheses=')'
            if _node.hasLeftParentheses() and _node.hasRightParentheses():
                self.setRealSelf(self.__parenthesesVisitor)
                return
            #Expr = logicalNot='not' term=expression
            if _node.isLogicalNot():
                self.setRealSelf(self.__logicalNotVisitor)
                return

        #Rules with binary operators
        if _node.getBinaryOperator() is not None:
            binOp = _node.getBinaryOperator()
            # All these rules employ left and right side expressions.
            if _node.getLeft() is not None:
                _node.getLeft().accept(self)
            if _node.getRight() is not None:
                _node.getRight().accept(self)
            #Handle all Arithmetic Operators:
            if isinstance(binOp,ASTArithmeticOperator.ASTArithmeticOperator):
                #Expr = <assoc=right> left=expression powOp='**' right=expression
                if binOp.isPowOp():
                    self.setRealSelf(self.__powVisitor)
                    return
                # Expr = left=expression (timesOp='*' | divOp='/' | moduloOp='%') right=expression
                if binOp.isTimesOp() or binOp.isDivOp() or binOp.isModuloOp():
                    self.setRealSelf(self.__dotOperatorVisitor)
                    return
                #Expr = left=expression (plusOp='+'  | minusOp='-') right=expression
                if binOp.isPlusOp() or binOp.isMinusOp():
                    self.setRealSelf(self.__lineOperatorVisitor)
                    return
            #handle all bitOperators:
            if isinstance(binOp,ASTBitOperator.ASTBitOperator):
                #Expr = left=expression bitOperator right=expression
                self.setRealSelf(self.__noSemantics) #TODO: implement something
                return
            #handle all comparison Operators:
            if isinstance(binOp,ASTComparisonOperator.ASTComparisonOperator):
                #Expr = left=expression comparisonOperator right=expression
               self.setRealSelf(self.__comparisonOperatorVisitor)
               return
            #handle all logical Operators
            if isinstance(binOp,ASTLogicalOperator.ASTLogicalOperator):
                #Expr = left=expression logicalOperator right=expression
                self.setRealSelf(self.__binaryLogicVisitor)
                return

        #Expr = condition=expression '?' ifTrue=expression ':' ifNot=expression
        if _node.getCondition() is not None and _node.getIfTrue() is not None and _node.getIfNot() is not None:
            _node.getCondition().accept(self)
            _node.getIfTrue().accept(self)
            _node.getIfNot().accept(self)
            self.setRealSelf(self.__conditionVisitor)
            return

        # handle all simpleexpressions
        if _node.isSimpleExpression():
            #simpleExpression = functionCall
            simpEx = _node.getExpression()
            if simpEx.getFunctionCall() is not None:
                self.setRealSelf(self.__functionCallVisitor)
                return
            # simpleExpression =  (INTEGER|FLOAT) (variable)?
            if simpEx.getNumericLiteral() is not None or \
                    (simpEx.getNumericLiteral() is not None and simpEx.getVariable() is not None):
                self.setRealSelf(self.__numericLiteralVisitor)
                return
            #simpleExpression =  variable
            if simpEx.getVariable() is not None:
                self.setRealSelf(self.__variableVisitor)
                return
            #simpleExpression = BOOLEAN_LITERAL
            if simpEx.isBooleanTrue() or simpEx.isBooleanFalse():
                self.setRealSelf(self.__booleanLiteralVisitor)
                return
            #simpleExpression = isInf='inf'
            if simpEx.isInfLiteral():
                self.setRealSelf(self.__infVisitor)
                return
            #simpleExpression = string=STRING_LITERAL
            if simpEx.isString():
                self.setRealSelf(self.__stringLiteralVisitor)
                return
