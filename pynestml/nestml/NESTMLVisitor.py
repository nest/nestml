#
# NESTMLVisitor.py
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

from pynestml.nestml.ASTArithmeticOperator import ASTArithmeticOperator
from pynestml.nestml.ASTAssignment import ASTAssignment
from pynestml.nestml.ASTBitOperator import ASTBitOperator
from pynestml.nestml.ASTBlock import ASTBlock
from pynestml.nestml.ASTBlockWithVariables import ASTBlockWithVariables
from pynestml.nestml.ASTBody import ASTBody
from pynestml.nestml.ASTComparisonOperator import ASTComparisonOperator
from pynestml.nestml.ASTCompoundStmt import ASTCompoundStmt
from pynestml.nestml.ASTDatatype import ASTDatatype
from pynestml.nestml.ASTDeclaration import ASTDeclaration
from pynestml.nestml.ASTElifClause import ASTElifClause
from pynestml.nestml.ASTElseClause import ASTElseClause
from pynestml.nestml.ASTEquationsBlock import ASTEquationsBlock
from pynestml.nestml.ASTExpression import ASTExpression
from pynestml.nestml.ASTForStmt import ASTForStmt
from pynestml.nestml.ASTFunction import ASTFunction
from pynestml.nestml.ASTFunctionCall import ASTFunctionCall
from pynestml.nestml.ASTIfClause import ASTIfClause
from pynestml.nestml.ASTIfStmt import ASTIfStmt
from pynestml.nestml.ASTInputBlock import ASTInputBlock
from pynestml.nestml.ASTInputLine import ASTInputLine
from pynestml.nestml.ASTInputType import ASTInputType
from pynestml.nestml.ASTLogicalOperator import ASTLogicalOperator
from pynestml.nestml.ASTNESTMLCompilationUnit import ASTNESTMLCompilationUnit
from pynestml.nestml.ASTNeuron import ASTNeuron
from pynestml.nestml.ASTOdeEquation import ASTOdeEquation
from pynestml.nestml.ASTOdeFunction import ASTOdeFunction
from pynestml.nestml.ASTOdeShape import ASTOdeShape
from pynestml.nestml.ASTOutputBlock import ASTOutputBlock
from pynestml.nestml.ASTParameter import ASTParameter
from pynestml.nestml.ASTReturnStmt import ASTReturnStmt
from pynestml.nestml.ASTSimpleExpression import ASTSimpleExpression
from pynestml.nestml.ASTSmallStmt import ASTSmallStmt
from pynestml.nestml.ASTUnaryOperator import ASTUnaryOperator
from pynestml.nestml.ASTUnitType import ASTUnitType
from pynestml.nestml.ASTUpdateBlock import ASTUpdateBlock
from pynestml.nestml.ASTVariable import ASTVariable
from pynestml.nestml.ASTWhileStmt import ASTWhileStmt


class NESTMLVisitor(object):
    """
    This class represents a standard implementation of a visitor as used to create concrete instances.
                 
    """

    __realSelf = None

    def __init__(self):
        self.__realSelf = self
        return

    def visitCompilationUnit(self, _compilationUnit=None):
        """
        Visits a single compilation unit, thus all neurons.
        :param _compilationUnit: a single compilation unit.
        :type _compilationUnit: ASTNESTMLCompilationUnit
        """
        return

    def visitNeuron(self, _neuron=None):
        """
        Used to visit a single neuron.
        :return: a single neuron.
        :rtype: ASTNeuron
        """
        return

    def visitBody(self, _body=None):
        """
        Used to visit a single neuron body.
        :param _body: a single body element.
        :type _body: ASTBody
        """
        return

    def visitFunction(self, _block=None):
        """
        Used to visit a single function block.
        :param _block: a function block object.
        :type _block: ASTFunction
        """
        return

    def visitUpdateBlock(self, _block=None):
        """
        Used to visit a single update block.
        :param _block: an update block object. 
        :type _block: ASTDynamics
        """
        return

    def visitBlock(self, _block=None):
        """
        Used to visit a single block of statements.
        :param _block: a block object.
        :type _block: ASTBlock
        """
        return

    def visitSmallStmt(self, _stmt=None):
        """
        Used to visit a single small statement.
        :param _stmt: a single small statement.
        :type _stmt: ASTSmallStatement
        """
        return

    def visitCompoundStmt(self, _stmt=None):
        """
        Used to visit a single compound statement.
        :param _stmt: a single compound statement.
        :type _stmt: ASTCompoundStatement
        """
        return

    def visitAssignment(self, _assignment=None):
        """
        Used to visit a single assignment.
        :param _assignment: an assignment object.
        :type _assignment: ASTAssignment
        """
        return

    def visitFunctionCall(self, _functionCall=None):
        """
        Private method: Used to visit a single function call and update its corresponding scope.
        :param _functionCall: a function call object.
        :type _functionCall: ASTFunctionCall
        """
        return

    def visitDeclaration(self, _declaration=None):
        """
        Used to visit a single declaration.
        :param _declaration: a declaration object.
        :type _declaration: ASTDeclaration
        """
        return

    def visitReturnStmt(self, _returnStmt=None):
        """
        Used to visit a single return statement.
        :param _returnStmt: a return statement object.
        :type _returnStmt: ASTReturnStmt
        """
        return

    def visitIfStmt(self, _ifStmt=None):
        """
        Used to visit a single if-statement.
        :param _ifStmt: an if-statement object.
        :type _ifStmt: ASTIfStmt
        """
        return

    def visitIfClause(self, _ifClause=None):
        """
        Used to visit a single if-clause.
        :param _ifClause: an if clause.
        :type _ifClause: ASTIfClause
        """
        return

    def visitElifClause(self, _elifClause=None):
        """
        Used to visit a single elif-clause.
        :param _elifClause: an elif clause.
        :type _elifClause: ASTElifClause
        """
        return

    def visitElseClause(self, _elseClause=None):
        """
        Used to visit a single else-clause.
        :param _elseClause: an else clause.
        :type _elseClause: ASTElseClause
        """
        return

    def visitForStmt(self, _forStmt=None):
        """
        Private method: Used to visit a single for-stmt.
        :param _forStmt: a for-statement. 
        :type _forStmt: ASTForStmt
        """
        return

    def visitWhileStmt(self, _whileStmt=None):
        """
        Used to visit a single while-stmt.
        :param _whileStmt: a while-statement.
        :type _whileStmt: ASTWhileStmt
        """
        return

    def visitDatatype(self, _dataType=None):
        """
        Used to visit a single data-type. 
        :param _dataType: a data-type.
        :type _dataType: ASTDataType
        """
        return

    def visitUnitType(self, _unitType=None):
        """
        Used to visit a single unit-type.
        :param _unitType: a unit type.
        :type _unitType: ASTUnitType
        """
        return

    def visitExpression(self, _expr=None):
        """
        Used to visit a single expression.
        :param _expr: an expression.
        :type _expr: ASTExpression
        """
        return

    def visitSimpleExpression(self, _expr=None):
        """
        Used to visit a single simple expression.
        :param _expr: a simple expression. 
        :type _expr: ASTSimpleExpression
        """
        return

    def visitUnaryOperator(self, _unaryOp=None):
        """
        Used to visit a single unary operator.
        :param _unaryOp: a single unary operator. 
        :type _unaryOp: ASTUnaryOperator
        """
        return

    def visitBitOperator(self, _bitOp=None):
        """
        Used to visit a single unary operator.
        :param _bitOp: a single bit operator. 
        :type _bitOp: ASTBitOperator
        """
        return

    def visitComparisonOperator(self, _comparisonOp=None):
        """
        Used to visit a single comparison operator.
        :param _comparisonOp: a single comparison operator.
        :type _comparisonOp: ASTComparisonOperator
        """
        return

    def visitLogicalOperator(self, _logicalOp=None):
        """
        Used to visit a single logical operator.
        :param _logicalOp: a single logical operator.
        :type _logicalOp: ASTLogicalOperator
        """
        return

    def visitVariable(self, _variable=None):
        """
        Used to visit a single variable.
        :param _variable: a single variable.
        :type _variable: ASTVariable
        """
        return

    def visitOdeFunction(self, _odeFunction=None):
        """
        Used to visit a single ode-function.
        :param _odeFunction: a single ode-function.
        :type _odeFunction: ASTOdeFunction
        """
        return

    def visitOdeShape(self, _odeShape=None):
        """
        Used to visit a single ode-shape.
        :param _odeShape: a single ode-shape.
        :type _odeShape: ASTOdeShape
        """
        return

    def visitOdeEquation(self, _equation=None):
        """
        Used to visit a single ode-equation.
        :param _equation: a single ode-equation.
        :type _equation: ASTOdeEquation
        """
        return

    def visitBlockWithVariables(self, _block=None):
        """
        Used to visit a single block of variables.
        :param _block: a block with declared variables.
        :type _block: ASTBlockWithVariables
        """
        return

    def visitEquationsBlock(self, _block=None):
        """
        Used to visit a single equations block.
        :param _block: a single equations block.
        :type _block: ASTEquationsBlock
        """
        return

    def visitInputBlock(self, _block=None):
        """
        Used to visit a single input block.
        :param _block: a single input block.
        :type _block: ASTInputBlock
        """
        return

    def visitOutputBlock(self, _block=None):
        """
        Used to visit a single output block.
        :param _block: a single output block. 
        :type _block: ASTOutputBlock
        """
        return

    def visitInputLine(self, _line=None):
        """
        Used to visit a single input line.
        :param _line: a single input line.
        :type _line: ASTInputLine
        """
        return

    def visitInputType(self, _type=None):
        """
        Used to visit a single input type.
        :param _type: a single input-type.
        :type _type: ASTInputType
        """
        return

    def visitArithmeticOperator(self, _arithmeticOp=None):
        """
        Used to visit a single arithmetic operator.
        :param _arithmeticOp: a single arithmetic operator.
        :type _arithmeticOp: ASTArithmeticOperator
        """
        return

    def visitParameter(self, _parameter=None):
        """
        Used to visit a single parameter.
        :param _parameter: a single parameter.
        :type _parameter: ASTParameter
        """
        return

    def endvisitCompilationUnit(self, _compilationUnit=None):
        """
        Visits a single compilation unit, thus all neurons.
        :param _compilationUnit: a single compilation unit.
        :type _compilationUnit: ASTNESTMLCompilationUnit
        """
        return

    def endvisitNeuron(self, _neuron=None):
        """
        Used to endvisit a single neuron.
        :return: a single neuron.
        :rtype: ASTNeuron
        """
        return

    def endvisitBody(self, _body=None):
        """
        Used to endvisit a single neuron body.
        :param _body: a single body element.
        :type _body: ASTBody
        """
        return

    def endvisitFunction(self, _block=None):
        """
        Used to endvisit a single function block.
        :param _block: a function block object.
        :type _block: ASTFunction
        """
        return

    def endvisitUpdateBlock(self, _block=None):
        """
        Used to endvisit a single update block.
        :param _block: an update block object. 
        :type _block: ASTDynamics
        """
        return

    def endvisitBlock(self, _block=None):
        """
        Used to endvisit a single block of statements.
        :param _block: a block object.
        :type _block: ASTBlock
        """
        return

    def endvisitSmallStmt(self, _stmt=None):
        """
        Used to endvisit a single small statement.
        :param _stmt: a single small statement.
        :type _stmt: ASTSmallStatement
        """
        return

    def endvisitCompoundStmt(self, _stmt=None):
        """
        Used to endvisit a single compound statement.
        :param _stmt: a single compound statement.
        :type _stmt: ASTCompoundStatement
        """
        return

    def endvisitAssignment(self, _assignment=None):
        """
        Used to endvisit a single assignment.
        :param _assignment: an assignment object.
        :type _assignment: ASTAssignment
        """
        return

    def endvisitFunctionCall(self, _functionCall=None):
        """
        Private method: Used to endvisit a single function call and update its corresponding scope.
        :param _functionCall: a function call object.
        :type _functionCall: ASTFunctionCall
        """
        return

    def endvisitDeclaration(self, _declaration=None):
        """
        Used to endvisit a single declaration.
        :param _declaration: a declaration object.
        :type _declaration: ASTDeclaration
        """
        return

    def endvisitReturnStmt(self, _returnStmt=None):
        """
        Used to endvisit a single return statement.
        :param _returnStmt: a return statement object.
        :type _returnStmt: ASTReturnStmt
        """
        return

    def endvisitIfStmt(self, _ifStmt=None):
        """
        Used to endvisit a single if-statement.
        :param _ifStmt: an if-statement object.
        :type _ifStmt: ASTIfStmt
        """
        return

    def endvisitIfClause(self, _ifClause=None):
        """
        Used to endvisit a single if-clause.
        :param _ifClause: an if clause.
        :type _ifClause: ASTIfClause
        """
        return

    def endvisitElifClause(self, _elifClause=None):
        """
        Used to endvisit a single elif-clause.
        :param _elifClause: an elif clause.
        :type _elifClause: ASTElifClause
        """
        return

    def endvisitElseClause(self, _elseClause=None):
        """
        Used to endvisit a single else-clause.
        :param _elseClause: an else clause.
        :type _elseClause: ASTElseClause
        """
        return

    def endvisitForStmt(self, _forStmt=None):
        """
        Private method: Used to endvisit a single for-stmt.
        :param _forStmt: a for-statement. 
        :type _forStmt: ASTForStmt
        """
        return

    def endvisitWhileStmt(self, _whileStmt=None):
        """
        Used to endvisit a single while-stmt.
        :param _whileStmt: a while-statement.
        :type _whileStmt: ASTWhileStmt
        """
        return

    def endvisitDatatype(self, _dataType=None):
        """
        Used to endvisit a single data-type. 
        :param _dataType: a data-type.
        :type _dataType: ASTDataType
        """
        return

    def endvisitUnitType(self, _unitType=None):
        """
        Used to endvisit a single unit-type.
        :param _unitType: a unit type.
        :type _unitType: ASTUnitType
        """
        return

    def endvisitExpression(self, _expr=None):
        """
        Used to endvisit a single expression.
        :param _expr: an expression.
        :type _expr: ASTExpression
        """
        return

    def endvisitSimpleExpression(self, _expr=None):
        """
        Used to endvisit a single simple expression.
        :param _expr: a simple expression. 
        :type _expr: ASTSimpleExpression
        """
        return

    def endvisitUnaryOperator(self, _unaryOp=None):
        """
        Used to endvisit a single unary operator.
        :param _unaryOp: a single unary operator. 
        :type _unaryOp: ASTUnaryOperator
        """
        return

    def endvisitBitOperator(self, _bitOp=None):
        """
        Used to endvisit a single unary operator.
        :param _bitOp: a single bit operator. 
        :type _bitOp: ASTBitOperator
        """
        return

    def endvisitComparisonOperator(self, _comparisonOp=None):
        """
        Used to endvisit a single comparison operator.
        :param _comparisonOp: a single comparison operator.
        :type _comparisonOp: ASTComparisonOperator
        """
        return

    def endvisitLogicalOperator(self, _logicalOp=None):
        """
        Used to endvisit a single logical operator.
        :param _logicalOp: a single logical operator.
        :type _logicalOp: ASTLogicalOperator
        """
        return

    def endvisitVariable(self, _variable=None):
        """
        Used to endvisit a single variable.
        :param _variable: a single variable.
        :type _variable: ASTVariable
        """
        return

    def endvisitOdeFunction(self, _odeFunction=None):
        """
        Used to endvisit a single ode-function.
        :param _odeFunction: a single ode-function.
        :type _odeFunction: ASTOdeFunction
        """
        return

    def endvisitOdeShape(self, _odeShape=None):
        """
        Used to endvisit a single ode-shape.
        :param _odeShape: a single ode-shape.
        :type _odeShape: ASTOdeShape
        """
        return

    def endvisitOdeEquation(self, _equation=None):
        """
        Used to endvisit a single ode-equation.
        :param _equation: a single ode-equation.
        :type _equation: ASTOdeEquation
        """
        return

    def endvisitBlockWithVariables(self, _block=None):
        """
        Used to endvisit a single block of variables.
        :param _block: a block with declared variables.
        :type _block: ASTBlockWithVariables
        """
        return

    def endvisitEquationsBlock(self, _block=None):
        """
        Used to endvisit a single equations block.
        :param _block: a single equations block.
        :type _block: ASTEquationsBlock
        """
        return

    def endvisitInputBlock(self, _block=None):
        """
        Used to endvisit a single input block.
        :param _block: a single input block.
        :type _block: ASTInputBlock
        """
        return

    def endvisitOutputBlock(self, _block=None):
        """
        Used to endvisit a single output block.
        :param _block: a single output block. 
        :type _block: ASTOutputBlock
        """
        return

    def endvisitInputLine(self, _line=None):
        """
        Used to endvisit a single input line.
        :param _line: a single input line.
        :type _line: ASTInputLine
        """
        return

    def endvisitInputType(self, _type=None):
        """
        Used to endvisit a single input type.
        :param _type: a single input-type.
        :type _type: ASTInputType
        """
        return

    def endvisitArithmeticOperator(self, _arithmeticOp=None):
        """
        Used to endvisit a single arithmetic operator.
        :param _arithmeticOp: a single arithmetic operator.
        :type _arithmeticOp: ASTArithmeticOperator
        """
        return

    def endvisitParameter(self, _parameter=None):
        """
        Used to endvisit a single parameter.
        :param _parameter: a single parameter.
        :type _parameter: ASTParameter
        """
        return

    def setRealSelf(self, _visitor):
        assert (_visitor is not None and isinstance(_visitor, NESTMLVisitor))
        self.__realSelf = _visitor
        return

    def getRealSelf(self):
        return self.__realSelf

    def handle(self, _node):
        self.getRealSelf().visit(_node)
        self.getRealSelf().traverse(_node)
        self.getRealSelf().endvisit(_node)
        return

    def visit(self, _node):
        """
        Dispatcher for visitor pattern.
        :param _node: The ASTElement to visit
        :type _node:  ASTElement or inherited
        """
        if isinstance(_node, ASTArithmeticOperator):
            self.visitArithmeticOperator(_node)
            return
        if isinstance(_node, ASTAssignment):
            self.visitAssignment(_node)
            return
        if isinstance(_node, ASTBitOperator):
            self.visitBitOperator(_node)
            return
        if isinstance(_node, ASTBlock):
            self.visitBlock(_node)
            return
        if isinstance(_node, ASTBlockWithVariables):
            self.visitBlockWithVariables(_node)
            return
        if isinstance(_node, ASTBody):
            self.visitBody(_node)
            return
        if isinstance(_node, ASTComparisonOperator):
            self.visitComparisonOperator(_node)
            return
        if isinstance(_node, ASTCompoundStmt):
            self.visitCompoundStmt(_node)
            return
        if isinstance(_node, ASTDatatype):
            self.visitDatatype(_node)
            return
        if isinstance(_node, ASTDeclaration):
            self.visitDeclaration(_node)
            return
        if isinstance(_node, ASTElifClause):
            self.visitElifClause(_node)
            return
        if isinstance(_node, ASTElseClause):
            self.visitElseClause(_node)
            return
        if isinstance(_node, ASTEquationsBlock):
            self.visitEquationsBlock(_node)
            return
        if isinstance(_node, ASTExpression):
            self.visitExpression(_node)
            return
        if isinstance(_node, ASTForStmt):
            self.visitForStmt(_node)
            return
        if isinstance(_node, ASTFunction):
            self.visitFunction(_node)
            return
        if isinstance(_node, ASTFunctionCall):
            self.visitFunctionCall(_node)
            return
        if isinstance(_node, ASTIfClause):
            self.visitIfClause(_node)
            return
        if isinstance(_node, ASTIfStmt):
            self.visitIfStmt(_node)
            return
        if isinstance(_node, ASTInputBlock):
            self.visitInputBlock(_node)
            return
        if isinstance(_node, ASTInputLine):
            self.visitInputLine(_node)
            return
        if isinstance(_node, ASTInputType):
            self.visitInputType(_node)
            return
        if isinstance(_node, ASTLogicalOperator):
            self.visitLogicalOperator(_node)
            return
        if isinstance(_node, ASTNESTMLCompilationUnit):
            self.visitCompilationUnit(_node)
            return
        if isinstance(_node, ASTNeuron):
            self.visitNeuron(_node)
            return
        if isinstance(_node, ASTOdeEquation):
            self.visitOdeEquation(_node)
            return
        if isinstance(_node, ASTOdeFunction):
            self.visitOdeFunction(_node)
            return
        if isinstance(_node, ASTOdeShape):
            self.visitOdeShape(_node)
            return
        if isinstance(_node, ASTOutputBlock):
            self.visitOutputBlock(_node)
            return
        if isinstance(_node, ASTParameter):
            self.visitParameter(_node)
            return
        if isinstance(_node, ASTReturnStmt):
            self.visitReturnStmt(_node)
            return
        if isinstance(_node, ASTSimpleExpression):
            self.visitSimpleExpression(_node)
            return
        if isinstance(_node, ASTSmallStmt):
            self.visitSmallStmt(_node)
            return
        if isinstance(_node, ASTUnaryOperator):
            self.visitUnaryOperator(_node)
            return
        if isinstance(_node, ASTUnitType):
            self.visitUnitType(_node)
            return
        if isinstance(_node, ASTUpdateBlock):
            self.visitUpdateBlock(_node)
            return
        if isinstance(_node, ASTVariable):
            self.visitVariable(_node)
            return
        if isinstance(_node, ASTWhileStmt):
            self.visitWhileStmt(_node)
            return
        return

    def traverse(self, _node):
        """
        Dispatcher for traverse method.
        :param _node: The ASTElement to visit
        :type _node: Inherited from ASTElement
        """
        if isinstance(_node, ASTArithmeticOperator):
            self.traverseArithmeticOperator(_node)
            return
        if isinstance(_node, ASTAssignment):
            self.traverseAssignment(_node)
            return
        if isinstance(_node, ASTBitOperator):
            self.traverseBitOperator(_node)
            return
        if isinstance(_node, ASTBlock):
            self.traverseBlock(_node)
            return
        if isinstance(_node, ASTBlockWithVariables):
            self.traverseBlockWithVariables(_node)
            return
        if isinstance(_node, ASTBody):
            self.traverseBody(_node)
            return
        if isinstance(_node, ASTComparisonOperator):
            self.traverseComparisonOperator(_node)
            return
        if isinstance(_node, ASTCompoundStmt):
            self.traverseCompoundStmt(_node)
            return
        if isinstance(_node, ASTDatatype):
            self.traverseDatatype(_node)
            return
        if isinstance(_node, ASTDeclaration):
            self.traverseDeclaration(_node)
            return
        if isinstance(_node, ASTElifClause):
            self.traverseElifClause(_node)
            return
        if isinstance(_node, ASTElseClause):
            self.traverseElseClause(_node)
            return
        if isinstance(_node, ASTEquationsBlock):
            self.traverseEquationsBlock(_node)
            return
        if isinstance(_node, ASTExpression):
            self.traverseExpression(_node)
            return
        if isinstance(_node, ASTForStmt):
            self.traverseForStmt(_node)
            return
        if isinstance(_node, ASTFunction):
            self.traverseFunction(_node)
            return
        if isinstance(_node, ASTFunctionCall):
            self.traverseFunctionCall(_node)
            return
        if isinstance(_node, ASTIfClause):
            self.traverseIfClause(_node)
            return
        if isinstance(_node, ASTIfStmt):
            self.traverseIfStmt(_node)
            return
        if isinstance(_node, ASTInputBlock):
            self.traverseInputBlock(_node)
            return
        if isinstance(_node, ASTInputLine):
            self.traverseInputLine(_node)
            return
        if isinstance(_node, ASTInputType):
            self.traverseInputType(_node)
            return
        if isinstance(_node, ASTLogicalOperator):
            self.traverseLogicalOperator(_node)
            return
        if isinstance(_node, ASTNESTMLCompilationUnit):
            self.traverseCompilationUnit(_node)
            return
        if isinstance(_node, ASTNeuron):
            self.traverseNeuron(_node)
            return
        if isinstance(_node, ASTOdeEquation):
            self.traverseOdeEquation(_node)
            return
        if isinstance(_node, ASTOdeFunction):
            self.traverseOdeFunction(_node)
            return
        if isinstance(_node, ASTOdeShape):
            self.traverseOdeShape(_node)
            return
        if isinstance(_node, ASTOutputBlock):
            self.traverseOutputBlock(_node)
            return
        if isinstance(_node, ASTParameter):
            self.traverseParameter(_node)
            return
        if isinstance(_node, ASTReturnStmt):
            self.traverseReturnStmt(_node)
            return
        if isinstance(_node, ASTSimpleExpression):
            self.traverseSimpleExpression(_node)
            return
        if isinstance(_node, ASTSmallStmt):
            self.traverseSmallStmt(_node)
            return
        if isinstance(_node, ASTUnaryOperator):
            self.traverseUnaryOperator(_node)
            return
        if isinstance(_node, ASTUnitType):
            self.traverseUnitType(_node)
            return
        if isinstance(_node, ASTUpdateBlock):
            self.traverseUpdateBlock(_node)
            return
        if isinstance(_node, ASTVariable):
            self.traverseVariable(_node)
            return
        if isinstance(_node, ASTWhileStmt):
            self.traverseWhileStmt(_node)
            return
        return

    def endvisit(self, _node):
        """
        Dispatcher for endvisit.
        :param _node: The ASTElement to endvisit
        :type _node:  ASTElement or inherited
        """
        if isinstance(_node, ASTArithmeticOperator):
            self.endvisitArithmeticOperator(_node)
            return
        if isinstance(_node, ASTAssignment):
            self.endvisitAssignment(_node)
            return
        if isinstance(_node, ASTBitOperator):
            self.endvisitBitOperator(_node)
            return
        if isinstance(_node, ASTBlock):
            self.endvisitBlock(_node)
            return
        if isinstance(_node, ASTBlockWithVariables):
            self.endvisitBlockWithVariables(_node)
            return
        if isinstance(_node, ASTBody):
            self.endvisitBody(_node)
            return
        if isinstance(_node, ASTComparisonOperator):
            self.endvisitComparisonOperator()
            return
        if isinstance(_node, ASTCompoundStmt):
            self.endvisitCompoundStmt(_node)
            return
        if isinstance(_node, ASTDatatype):
            self.endvisitDatatype(_node)
            return
        if isinstance(_node, ASTDeclaration):
            self.endvisitDeclaration(_node)
            return
        if isinstance(_node, ASTElifClause):
            self.endvisitElifClause(_node)
            return
        if isinstance(_node, ASTElseClause):
            self.endvisitElseClause(_node)
            return
        if isinstance(_node, ASTEquationsBlock):
            self.endvisitEquationsBlock(_node)
            return
        if isinstance(_node, ASTExpression):
            self.endvisitExpression(_node)
            return
        if isinstance(_node, ASTForStmt):
            self.endvisitForStmt(_node)
            return
        if isinstance(_node, ASTFunction):
            self.endvisitFunction(_node)
            return
        if isinstance(_node, ASTFunctionCall):
            self.endvisitFunctionCall(_node)
            return
        if isinstance(_node, ASTIfClause):
            self.endvisitIfClause(_node)
            return
        if isinstance(_node, ASTIfStmt):
            self.endvisitIfStmt(_node)
            return
        if isinstance(_node, ASTInputBlock):
            self.endvisitInputBlock(_node)
            return
        if isinstance(_node, ASTInputLine):
            self.endvisitInputLine(_node)
            return
        if isinstance(_node, ASTInputType):
            self.endvisitInputType(_node)
            return
        if isinstance(_node, ASTLogicalOperator):
            self.endvisitLogicalOperator(_node)
            return
        if isinstance(_node, ASTNESTMLCompilationUnit):
            self.endvisitCompilationUnit(_node)
            return
        if isinstance(_node, ASTNeuron):
            self.endvisitNeuron(_node)
            return
        if isinstance(_node, ASTOdeEquation):
            self.endvisitOdeEquation(_node)
            return
        if isinstance(_node, ASTOdeFunction):
            self.endvisitOdeFunction(_node)
            return
        if isinstance(_node, ASTOdeShape):
            self.endvisitOdeShape(_node)
            return
        if isinstance(_node, ASTOutputBlock):
            self.endvisitOutputBlock(_node)
            return
        if isinstance(_node, ASTParameter):
            self.endvisitParameter(_node)
            return
        if isinstance(_node, ASTReturnStmt):
            self.endvisitReturnStmt(_node)
            return
        if isinstance(_node, ASTSimpleExpression):
            self.endvisitSimpleExpression(_node)
            return
        if isinstance(_node, ASTSmallStmt):
            self.endvisitSmallStmt(_node)
            return
        if isinstance(_node, ASTUnaryOperator):
            self.endvisitUnaryOperator(_node)
            return
        if isinstance(_node, ASTUnitType):
            self.endvisitUnitType(_node)
            return
        if isinstance(_node, ASTUpdateBlock):
            self.endvisitUpdateBlock(_node)
            return
        if isinstance(_node, ASTVariable):
            self.endvisitVariable(_node)
            return
        if isinstance(_node, ASTWhileStmt):
            self.endvisitWhileStmt(_node)
            return
        return

    def traverseArithmeticOperator(self, _node):
        return

    def traverseAssignment(self, _node):
        if _node.getVariable() is not None:
            _node.getVariable().accept(self.getRealSelf())
        if _node.getExpression() is not None:
            _node.getExpression().accept(self.getRealSelf())
        return

    def traverseBitOperator(self, _node):
        return

    def traverseBlock(self, _node):
        if _node.getStmts() is not None:
            for subnode in _node.getStmts():
                subnode.accept(self.getRealSelf())
        return

    def traverseBlockWithVariables(self, _node):
        if _node.getDeclarations() is not None:
            for subnode in _node.getDeclarations():
                subnode.accept(self.getRealSelf())
        return

    def traverseBody(self, _node):
        if _node.getBodyElements() is not None:
            for subnode in _node.getBodyElements():
                subnode.accept(self.getRealSelf())
        return

    def traverseComparisonOperator(self, _node):
        return

    def traverseCompoundStmt(self, _node):
        if _node.getIfStmt() is not None:
            _node.getIfStmt().accept(self.getRealSelf())
        if _node.getWhileStmt() is not None:
            _node.getWhileStmt().accept(self.getRealSelf())
        if _node.getForStmt() is not None:
            _node.getForStmt().accept(self.getRealSelf())
        return

    def traverseDatatype(self, _node):
        if _node.getUnitType() is not None:
            _node.getUnitType().accept(self.getRealSelf())
        return

    def traverseDeclaration(self, _node):
        if _node.getVariables() is not None:
            for subnode in _node.getVariables():
                subnode.accept(self.getRealSelf())
        if _node.getDataType() is not None:
            _node.getDataType().accept(self.getRealSelf())
        if _node.getExpr() is not None:
            _node.getExpr().accept(self.getRealSelf())
        if _node.getInvariant() is not None:
            _node.getInvariant().accept(self.getRealSelf())
        return

    def traverseElifClause(self, _node):
        if _node.getCondition() is not None:
            _node.getCondition().accept(self.getRealSelf())
        if _node.getBlock() is not None:
            _node.getBlock().accept(self.getRealSelf())
        return

    def traverseElseClause(self, _node):
        if _node.getBlock() is not None:
            _node.getBlock().accept(self.getRealSelf())
        return

    def traverseEquationsBlock(self, _node):
        if _node.getDeclarations() is not None:
            for subnode in _node.getDeclarations():
                subnode.accept(self.getRealSelf())
        return

    def traverseExpression(self, _node):
        if _node.getExpression() is not None:
            _node.getExpression().accept(self.getRealSelf())
        if _node.getUnaryOperator() is not None:
            _node.getUnaryOperator().accept(self.getRealSelf())
        if _node.getLhs() is not None:
            _node.getLhs().accept(self.getRealSelf())
        if _node.getRhs() is not None:
            _node.getRhs().accept(self.getRealSelf())
        if _node.getBinaryOperator() is not None:
            _node.getBinaryOperator().accept(self.getRealSelf())
        if _node.getCondition() is not None:
            _node.getCondition().accept(self.getRealSelf())
        if _node.getIfTrue() is not None:
            _node.getIfTrue().accept(self.getRealSelf())
        if _node.getIfNot() is not None:
            _node.getIfNot().accept(self.getRealSelf())
        return

    def traverseForStmt(self, _node):
        if _node.getFrom() is not None:
            _node.getFrom().accept(self.getRealSelf())
        if _node.getTo() is not None:
            _node.getTo().accept(self.getRealSelf())
        if _node.getBlock() is not None:
            _node.getBlock().accept(self.getRealSelf())
        return

    def traverseFunction(self, _node):
        if _node.getParameters() is not None:
            for subnode in _node.getParameters():
                subnode.accept(self.getRealSelf())
        if _node.getReturnType() is not None:
            _node.getReturnType().accept(self.getRealSelf())
        if _node.getBlock() is not None:
            _node.getBlock().accept(self.getRealSelf())
        return

    def traverseFunctionCall(self, _node):
        if _node.getArgs() is not None:
            for subnode in _node.getArgs():
                subnode.accept(self.getRealSelf())
        return

    def traverseIfClause(self, _node):
        if _node.getCondition() is not None:
            _node.getCondition().accept(self.getRealSelf())
        if _node.getBlock() is not None:
            _node.getBlock().accept(self.getRealSelf())
        return

    def traverseIfStmt(self, _node):
        if _node.getIfClause() is not None:
            _node.getIfClause().accept(self.getRealSelf())
        for elifClause in _node.getElifClauses():
            elifClause.accept(self.getRealSelf())
        if _node.getElseClause() is not None:
            _node.getElseClause().accept(self.getRealSelf())
        return

    def traverseInputBlock(self, _node):
        if _node.getInputLines() is not None:
            for subnode in _node.getInputLines():
                subnode.accept(self.getRealSelf())
        return

    def traverseInputLine(self, _node):
        if _node.getInputTypes() is not None:
            for subnode in _node.getInputTypes():
                subnode.accept(self.getRealSelf())
        return

    def traverseInputType(self, _node):
        return

    def traverseLogicalOperator(self, _node):
        return

    def traverseCompilationUnit(self, _node):
        if _node.getNeuronList() is not None:
            for subnode in _node.getNeuronList():
                subnode.accept(self.getRealSelf())
        return

    def traverseNeuron(self, _node):
        if _node.getBody() is not None:
            _node.getBody().accept(self.getRealSelf())
        return

    def traverseOdeEquation(self, _node):
        if _node.getLhs() is not None:
            _node.getLhs().accept(self.getRealSelf())
        if _node.getRhs() is not None:
            _node.getRhs().accept(self.getRealSelf())
        return

    def traverseOdeFunction(self, _node):
        if _node.getDataType() is not None:
            _node.getDataType().accept(self.getRealSelf())
        if _node.getExpression() is not None:
            _node.getExpression().accept(self.getRealSelf())
        return

    def traverseOdeShape(self, _node):
        if _node.getVariable() is not None:
            _node.getVariable().accept(self.getRealSelf())
        if _node.getExpression() is not None:
            _node.getExpression().accept(self.getRealSelf())
        return

    def traverseOutputBlock(self, _node):
        return

    def traverseParameter(self, _node):
        if _node.getDataType() is not None:
            _node.getDataType().accept(self.getRealSelf())
        return

    def traverseReturnStmt(self, _node):
        if _node.getExpr() is not None:
            _node.getExpr().accept(self.getRealSelf())
        return

    def traverseSimpleExpression(self, _node):
        if _node.getFunctionCall() is not None:
            _node.getFunctionCall().accept(self.getRealSelf())
        if _node.getVariable() is not None:
            _node.getVariable().accept(self.getRealSelf())
        return

    def traverseSmallStmt(self, _node):
        if _node.getAssignment() is not None:
            _node.getAssignment().accept(self.getRealSelf())
        if _node.getFunctionCall() is not None:
            _node.getFunctionCall().accept(self.getRealSelf())
        if _node.getDeclaration() is not None:
            _node.getDeclaration().accept(self.getRealSelf())
        if _node.getReturnStmt() is not None:
            _node.getReturnStmt().accept(self.getRealSelf())
        return

    def traverseUnaryOperator(self, _node):
        return

    def traverseUnitType(self, _node):
        if _node.getBase() is not None:
            _node.getBase().accept(self.getRealSelf())
        if _node.getLhs() is not None:
            if isinstance(_node.getLhs(), ASTUnitType):
                _node.getLhs().accept(self.getRealSelf())
        if _node.getRhs() is not None:
            _node.getRhs().accept(self.getRealSelf())
        if _node.getCompoundUnit() is not None:
            _node.getCompoundUnit().accept(self.getRealSelf())
        return

    def traverseUpdateBlock(self, _node):
        if _node.getBlock() is not None:
            _node.getBlock().accept(self.getRealSelf())
        return

    def traverseVariable(self, node):
        return

    def traverseWhileStmt(self, _node):
        if _node.getCondition() is not None:
            _node.getCondition().accept(self.getRealSelf())
        if _node.getBlock() is not None:
            _node.getBlock().accept(self.getRealSelf())
        return
