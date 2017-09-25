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
from pynestml.src.main.python.org.nestml.ast import *


class NESTMLVisitor(object):
    """
    This class represents a standard implementation of a visitor as used to create concrete instances.
                 
    """

    @classmethod
    def visitCompilationUnit(cls, _compilationUnit=None):
        """
        Visits a single compilation unit, thus all neurons.
        :param _compilationUnit: a single compilation unit.
        :type _compilationUnit: ASTNESTMLCompilationUnit
        """
        assert (_compilationUnit is not None and isinstance(_compilationUnit, ASTNESTMLCompilationUnit)), \
            '(PyNestML.Visitor) No or wrong type of compilation unit provided (%s)!' % type(_compilationUnit)
        for neuron in _compilationUnit.getNeuronList():
            cls.visitNeuron(neuron)
        return

    @classmethod
    def visitNeuron(cls, _neuron=None):
        """
        Used to visit a single neuron.
        :return: a single neuron.
        :rtype: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron.ASTNeuron)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of neuron provided (%s)!' % type(_neuron)
        cls.visitBody(_neuron.getBody())
        return

    @classmethod
    def visitBody(cls, _body=None):
        """
        Used to visit a single neuron body.
        :param _body: a single body element.
        :type _body: ASTBody
        """
        for bodyElement in _body.getBodyElements():
            if isinstance(bodyElement, ASTBlockWithVariables.ASTBlockWithVariables):
                cls.visitBlockWithVariable(bodyElement)
            elif isinstance(bodyElement, ASTUpdateBlock.ASTUpdateBlock):
                cls.visitUpdateBlock(bodyElement)
            elif isinstance(bodyElement, ASTEquationsBlock.ASTEquationsBlock):
                cls.visitEquationsBlock(bodyElement)
            elif isinstance(bodyElement, ASTInputBlock.ASTInputBlock):
                cls.visitInputBlock(bodyElement)
            elif isinstance(bodyElement, ASTOutputBlock.ASTOutputBlock):
                cls.visitOutputBlock(bodyElement)
            elif isinstance(bodyElement, ASTFunction.ASTFunction):
                cls.visitFunctionBlock(bodyElement)
        return

    @classmethod
    def visitFunctionBlock(cls, _block=None):
        """
        Used to visit a single function block.
        :param _block: a function block object.
        :type _block: ASTFunction
        """
        assert (_block is not None and isinstance(_block, ASTFunction.ASTFunction)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of function block provided (%s)!' % type(_block)
        for arg in _block.getParameters():
            cls.visitDataType(arg.getDataType())
        if _block.hasReturnType():
            cls.visitDataType(_block.getReturnType())
        cls.visitBlock(_block.getBlock())
        return

    @classmethod
    def visitUpdateBlock(cls, _block=None):
        """
        Used to visit a single update block.
        :param _block: an update block object. 
        :type _block: ASTDynamics
        """
        assert (_block is not None and isinstance(_block, ASTUpdateBlock.ASTUpdateBlock)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of update-block provided (%s)!' % type(_block)
        cls.visitBlock(_block.getBlock())
        return

    @classmethod
    def visitBlock(cls, _block=None):
        """
        Used to visit a single block of statements.
        :param _block: a block object.
        :type _block: ASTBlock
        """
        assert (_block is not None and isinstance(_block, ASTBlock.ASTBlock)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of block provided %s!' % type(_block)
        for stmt in _block.getStmts():
            if isinstance(stmt, ASTSmallStmt.ASTSmallStmt):
                cls.visitSmallStmt(stmt)
            elif isinstance(stmt, ASTCompoundStmt.ASTCompoundStmt):
                cls.visitCompoundStmt(stmt)
        return

    @classmethod
    def visitSmallStmt(cls, _stmt=None):
        """
        Used to visit a single small statement.
        :param _stmt: a single small statement.
        :type _stmt: ASTSmallStatement
        """
        assert (_stmt is not None and isinstance(_stmt, ASTSmallStmt.ASTSmallStmt)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of small statement provided (%s)!' % type(_stmt)
        if _stmt.isDeclaration():
            cls.visitDeclaration(_stmt.getDeclaration())
        elif _stmt.isAssignment():
            cls.visitAssignment(_stmt.getAssignment())
        elif _stmt.isFunctionCall():
            cls.visitFunctionCall(_stmt.getFunctionCall())
        elif _stmt.isReturnStmt():
            cls.visitReturnStmt(_stmt.getReturnStmt())
        return

    @classmethod
    def visitCompoundStmt(cls, _stmt=None):
        """
        Used to visit a single compound statement.
        :param _stmt: a single compound statement.
        :type _stmt: ASTCompoundStatement
        """
        assert (_stmt is not None and isinstance(_stmt, ASTCompoundStmt.ASTCompoundStmt)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of compound statement provided!'
        if _stmt.isIfStmt():
            cls.visitIfStmt(_stmt.getIfStmt())
        elif _stmt.isWhileStmt():
            cls.visitWhileStmt(_stmt.getWhileStmt())
        else:
            cls.visitForStmt(_stmt.getForStmt())
        return

    @classmethod
    def visitAssignment(cls, _assignment=None):
        """
        Used to visit a single assignment.
        :param _assignment: an assignment object.
        :type _assignment: ASTAssignment
        """
        assert (_assignment is not None and isinstance(_assignment, ASTAssignment.ASTAssignment)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of assignment provided (%s)!' % type(_assignment)
        cls.visitVariable(_assignment.getVariable())
        cls.visitExpression(_assignment.getExpression())
        return

    @classmethod
    def visitFunctionCall(cls, _functionCall=None):
        """
        Private method: Used to visit a single function call and update its corresponding scope.
        :param _functionCall: a function call object.
        :type _functionCall: ASTFunctionCall
        """
        assert (_functionCall is not None and isinstance(_functionCall, ASTFunctionCall.ASTFunctionCall)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of function call provided (%s)!' % type(_functionCall)
        for arg in _functionCall.getArgs():
            cls.visitExpression(arg)
        return

    @classmethod
    def visitDeclaration(cls, _declaration=None):
        """
        Used to visit a single declaration.
        :param _declaration: a declaration object.
        :type _declaration: ASTDeclaration
        """
        assert (_declaration is not None and isinstance(_declaration, ASTDeclaration.ASTDeclaration)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong typ of declaration provided (%s)!' % type(_declaration)
        for var in _declaration.getVariables():  # for all variables declared create a new symbol
            cls.visitVariable(var)
        cls.visitDataType(_declaration.getDataType())
        if _declaration.hasExpression():
            cls.visitExpression(_declaration.getExpr())
        if _declaration.hasInvariant():
            cls.visitExpression(_declaration.getInvariant())
        return

    @classmethod
    def visitReturnStmt(cls, _returnStmt=None):
        """
        Used to visit a single return statement.
        :param _returnStmt: a return statement object.
        :type _returnStmt: ASTReturnStmt
        """
        assert (_returnStmt is not None and isinstance(_returnStmt, ASTReturnStmt.ASTReturnStmt)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of return statement provided (%s)!' % type(_returnStmt)
        if _returnStmt.hasExpr():
            cls.visitExpression(_returnStmt.getExpr())
        return

    @classmethod
    def visitIfStmt(cls, _ifStmt=None):
        """
        Used to visit a single if-statement.
        :param _ifStmt: an if-statement object.
        :type _ifStmt: ASTIfStmt
        """
        assert (_ifStmt is not None and isinstance(_ifStmt, ASTIfStmt.ASTIfStmt)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of if-statement provided (%s)!' % type(_ifStmt)
        cls.visitIfClause(_ifStmt.getIfClause())
        for elIf in _ifStmt.getElifClauses():
            cls.visitElifClause(elIf)
        if _ifStmt.hasElseClause():
            cls.visitElseClause(_ifStmt.getElseClause())
        return

    @classmethod
    def visitIfClause(cls, _ifClause=None):
        """
        Used to visit a single if-clause.
        :param _ifClause: an if clause.
        :type _ifClause: ASTIfClause
        """
        assert (_ifClause is not None and isinstance(_ifClause, ASTIfClause.ASTIfClause)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of if-clause handed over (%s)!' % type(_ifClause)
        cls.visitExpression(_ifClause.getCondition())
        cls.visitBlock(_ifClause.getBlock())
        return

    @classmethod
    def visitElifClause(cls, _elifClause=None):
        """
        Used to visit a single elif-clause.
        :param _elifClause: an elif clause.
        :type _elifClause: ASTElifClause
        """
        assert (_elifClause is not None and isinstance(_elifClause, ASTElifClause.ASTElifClause)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of elif-clause handed over (%s)!' % type(_elifClause)
        cls.visitExpression(_elifClause.getCondition())
        cls.visitBlock(_elifClause.getBlock())
        return

    @classmethod
    def visitElseClause(cls, _elseClause=None):
        """
        Used to visit a single else-clause.
        :param _elseClause: an else clause.
        :type _elseClause: ASTElseClause
        """
        assert (_elseClause is not None and isinstance(_elseClause, ASTElseClause.ASTElseClause)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of else-clause handed over (%s)!' % type(_elseClause)
        cls.visitBlock(_elseClause.getBlock())
        return

    @classmethod
    def visitForStmt(cls, _forStmt=None):
        """
        Private method: Used to visit a single for-stmt.
        :param _forStmt: a for-statement. 
        :type _forStmt: ASTForStmt
        """
        assert (_forStmt is not None and isinstance(_forStmt, ASTForStmt.ASTForStmt)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of for-statement provided (%s)!' % type(_forStmt)
        cls.visitExpression(_forStmt.getFrom())
        cls.visitExpression(_forStmt.getTo())
        cls.visitBlock(_forStmt.getBlock())
        return

    @classmethod
    def visitWhileStmt(cls, _whileStmt=None):
        """
        Used to visit a single while-stmt.
        :param _whileStmt: a while-statement.
        :type _whileStmt: ASTWhileStmt
        """
        assert (_whileStmt is not None and isinstance(_whileStmt, ASTWhileStmt.ASTWhileStmt)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of while-statement provided (%s)!' % type(_whileStmt)
        cls.visitExpression(_whileStmt.getCondition())
        cls.visitBlock(_whileStmt.getBlock())
        return

    @classmethod
    def visitDataType(cls, _dataType=None):
        """
        Used to visit a single data-type. 
        :param _dataType: a data-type.
        :type _dataType: ASTDataType
        """
        assert (_dataType is not None and isinstance(_dataType, ASTDatatype.ASTDatatype)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of data-type provided (%s)!' % type(_dataType)
        if _dataType.isUnitType():
            return cls.visitUnitType(_dataType.getUnitType())
        # besides updating the scope no operations are required, since no type symbols are added to the scope.
        else:
            return

    @classmethod
    def visitUnitType(cls, _unitType=None):
        """
        Used to visit a single unit-type.
        :param _unitType: a unit type.
        :type _unitType: ASTUnitType
        """
        assert (_unitType is not None and isinstance(_unitType, ASTUnitType.ASTUnitType)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of unit-typ provided (%s)!' % type(_unitType)
        if _unitType.isPowerExpression():
            cls.visitUnitType(_unitType.getBase())
        elif _unitType.isEncapsulated():
            cls.visitUnitType(_unitType.getCompoundUnit())
        elif _unitType.isDiv() or _unitType.isTimes():
            if isinstance(_unitType.getLhs(), ASTUnitType.ASTUnitType):  # lhs can be a numeric Or a unit-type
                cls.visitUnitType(_unitType.getLhs())
            cls.visitUnitType(_unitType.getRhs())
        return

    @classmethod
    def visitExpression(cls, _expr=None):
        """
        Used to visit a single expression.
        :param _expr: an expression.
        :type _expr: ASTExpression
        """
        assert (_expr is not None and (isinstance(_expr, ASTExpression.ASTExpression)
                                       or isinstance(_expr, ASTSimpleExpression.ASTSimpleExpression))), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of expression handed over(%s)!' % type(_expr)
        if _expr.isSimpleExpression():
            cls.visitSimpleExpression(_expr.getExpression())
        if _expr.isLogicalNot():
            cls.visitExpression(_expr.getExpression())
        if _expr.isUnaryOperator():
            cls.visitUnaryOperator(_expr.getUnaryOperator())
            cls.visitExpression(_expr.getExpression())
        if _expr.isCompoundExpression():
            cls.visitExpression(_expr.getLhs())
            if isinstance(_expr.getBinaryOperator(), ASTBitOperator.ASTBitOperator):
                cls.visitBitOperator(_expr.getBinaryOperator())
            elif isinstance(_expr.getBinaryOperator(), ASTComparisonOperator.ASTComparisonOperator):
                cls.visitComparisonOperator(_expr.getBinaryOperator())
            elif isinstance(_expr.getBinaryOperator(), ASTLogicalOperator.ASTLogicalOperator):
                cls.visitLogicalOperator(_expr.getBinaryOperator())
            else:
                cls.visitArithmeticOperator(_expr.getBinaryOperator())
            cls.visitExpression(_expr.getRhs())
        if _expr.isTernaryOperator():
            cls.visitExpression(_expr.getCondition())
            cls.visitExpression(_expr.getIfTrue())
            cls.visitExpression(_expr.getIfNot())
        return

    @classmethod
    def visitSimpleExpression(cls, _expr=None):
        """
        Used to visit a single simple expression.
        :param _expr: a simple expression. 
        :type _expr: ASTSimpleExpression
        """
        assert (_expr is not None and isinstance(_expr, ASTSimpleExpression.ASTSimpleExpression)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of simple expression provided (%s)!' % type(_expr)
        if _expr.isFunctionCall():
            cls.visitFunctionCall(_expr.getFunctionCall())
        elif _expr.isVariable() or _expr.hasUnit():
            cls.visitVariable(_expr.getVariable())
        return

    @classmethod
    def visitUnaryOperator(cls, _unaryOp=None):
        """
        Used to visit a single unary operator.
        :param _unaryOp: a single unary operator. 
        :type _unaryOp: ASTUnaryOperator
        """
        assert (_unaryOp is not None and isinstance(_unaryOp, ASTUnaryOperator.ASTUnaryOperator)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of unary operator provided (%s)!' % type(_unaryOp)
        return

    @classmethod
    def visitBitOperator(cls, _bitOp=None):
        """
        Used to visit a single unary operator.
        :param _bitOp: a single bit operator. 
        :type _bitOp: ASTBitOperator
        """
        assert (_bitOp is not None and isinstance(_bitOp, ASTBitOperator.ASTBitOperator)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of bit operator provided (%s)!' % type(_bitOp)
        return

    @classmethod
    def visitComparisonOperator(cls, _comparisonOp=None):
        """
        Used to visit a single comparison operator.
        :param _comparisonOp: a single comparison operator.
        :type _comparisonOp: ASTComparisonOperator
        """
        assert (_comparisonOp is not None and isinstance(_comparisonOp, ASTComparisonOperator.ASTComparisonOperator)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of comparison operator provided (%s)!' % type(
                _comparisonOp)
        return

    @classmethod
    def visitLogicalOperator(cls, _logicalOp=None):
        """
        Used to visit a single logical operator.
        :param _logicalOp: a single logical operator.
        :type _logicalOp: ASTLogicalOperator
        """
        assert (_logicalOp is not None and isinstance(_logicalOp, ASTLogicalOperator.ASTLogicalOperator)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of logical operator provided (%s)!' % type(_logicalOp)
        return

    @classmethod
    def visitVariable(cls, _variable=None):
        """
        Used to visit a single variable.
        :param _variable: a single variable.
        :type _variable: ASTVariable
        """
        assert (_variable is not None and isinstance(_variable, ASTVariable.ASTVariable)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of variable provided (%s)!' % type(_variable)
        return

    @classmethod
    def visitOdeFunction(cls, _odeFunction=None):
        """
        Used to visit a single ode-function.
        :param _odeFunction: a single ode-function.
        :type _odeFunction: ASTOdeFunction
        """
        assert (_odeFunction is not None and isinstance(_odeFunction, ASTOdeFunction.ASTOdeFunction)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of ode-function provided (%s)!' % type(_odeFunction)
        cls.visitDataType(_odeFunction.getDataType())
        cls.visitExpression(_odeFunction.getExpression())
        return

    @classmethod
    def visitOdeShape(cls, _odeShape=None):
        """
        Used to visit a single ode-shape.
        :param _odeShape: a single ode-shape.
        :type _odeShape: ASTOdeShape
        """
        assert (_odeShape is not None and isinstance(_odeShape, ASTOdeShape.ASTOdeShape)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of ode-shape provided (%s)!' % type(_odeShape)
        cls.visitVariable(_odeShape.getVariable())
        cls.visitExpression(_odeShape.getExpression())
        return

    @classmethod
    def visitOdeEquation(cls, _equation=None):
        """
        Used to visit a single ode-equation.
        :param _equation: a single ode-equation.
        :type _equation: ASTOdeEquation
        """
        assert (_equation is not None and isinstance(_equation, ASTOdeEquation.ASTOdeEquation)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of ode-equation handed over (%s)!' % type(_equation)
        cls.visitVariable(_equation.getLhs())
        cls.visitExpression(_equation.getRhs())
        return

    @classmethod
    def visitBlockWithVariable(cls, _block=None):
        """
        Used to visit a single block of variables.
        :param _block: a block with declared variables.
        :type _block: ASTBlockWithVariables
        """
        assert (_block is not None and isinstance(_block, ASTBlockWithVariables.ASTBlockWithVariables)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of block with variables provided!'
        for decl in _block.getDeclarations():
            cls.visitDeclaration(decl)
        return

    @classmethod
    def visitEquationsBlock(cls, _block=None):
        """
        Used to visit a single equations block.
        :param _block: a single equations block.
        :type _block: ASTEquationsBlock
        """
        assert (_block is not None and isinstance(_block, ASTEquationsBlock.ASTEquationsBlock)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of equations block provided (%s)!' % type(_block)
        for decl in _block.getDeclarations():
            if isinstance(decl, ASTOdeFunction.ASTOdeFunction):
                cls.visitOdeFunction(decl)
            elif isinstance(decl, ASTOdeShape.ASTOdeShape):
                cls.visitOdeShape(decl)
            else:
                cls.visitOdeEquation(decl)
        return

    @classmethod
    def visitInputBlock(cls, _block=None):
        """
        Used to visit a single input block.
        :param _block: a single input block.
        :type _block: ASTInputBlock
        """
        assert (_block is not None and isinstance(_block, ASTInputBlock.ASTInputBlock)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of input-block provided (%s)!' % type(_block)
        for line in _block.getInputLines():
            cls.visitInputLine(line)
        return

    @classmethod
    def visitOutputBlock(cls, _block=None):
        """
        Used to visit a single output block.
        :param _block: a single output block. 
        :type _block: ASTOutputBlock
        """
        assert (_block is not None and isinstance(_block, ASTOutputBlock.ASTOutputBlock)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of output-block provided (%s)!' % type(_block)
        return

    @classmethod
    def visitInputLine(cls, _line=None):
        """
        Used to visit a single input line.
        :param _line: a single input line.
        :type _line: ASTInputLine
        """
        assert (_line is not None and isinstance(_line, ASTInputLine.ASTInputLine)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of input-line provided (%s)!' % type(_line)
        for inputType in _line.getInputTypes():
            cls.visitInputType(inputType)
        return

    @classmethod
    def visitInputType(cls, _type=None):
        """
        Used to visit a single input type.
        :param _type: a single input-type.
        :type _type: ASTInputType
        """
        assert (_type is not None and isinstance(_type, ASTInputType.ASTInputType)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of input-type provided (%s)!' % type(_type)
        return

    @classmethod
    def visitArithmeticOperator(cls, _arithmeticOp=None):
        """
        Used to visit a single arithmetic operator.
        :param _arithmeticOp: a single arithmetic operator.
        :type _arithmeticOp: ASTArithmeticOperator
        """
        assert (_arithmeticOp is not None and isinstance(_arithmeticOp, ASTArithmeticOperator.ASTArithmeticOperator)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of arithmetic operator provided (%s)!' % type(
                _arithmeticOp)
        return

    @classmethod
    def visitParameter(cls, _parameter=None):
        """
        Used to visit a single parameter.
        :param _parameter: a single parameter.
        :type _parameter: ASTParameter
        """
        assert (_parameter is not None and isinstance(_parameter, ASTParameter.ASTParameter)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of parameter provided (%s)!' % type(
                _parameter)
        cls.visitDataType(_parameter.getDataType())
        return
