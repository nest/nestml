#
# ASTCoCoVisitor.py
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


class ASTCoCoVisitor:
    """
    This visitor is used to visit each node of the ast and ensure certain properties.
    """

    @classmethod
    def visitArithmeticOperator(cls, _ast=None, _coco=None):
        """
        Visits a single arithmetic operator and checks the CoCo for this node.
        :param _ast: an arithmetic operator
        :type _ast: ASTArithmeticOperator
        :param _coco: a single coco method object to check.
        :type _coco: CoCo
        """
        assert (_ast is not None and isinstance(_ast, ASTArithmeticOperator.ASTArithmeticOperator)), \
            '(PyNestML.CoCo.Visitor) No or wrong type of arithmetic operator provided!'
        _coco(_ast)
        return

    @classmethod
    def visitAssignment(cls, _ast=None, _coco=None):
        """
        Visits a single assignment an checks the CoCo for this node.
        :param _ast: a single assignment object.
        :type _ast: ASTAssignment
        :param _coco: a single coco method object to check.
        :type _coco: CoCo
        """
        assert (_ast is not None and isinstance(_ast, ASTAssignment.ASTAssignment)), \
            '(PyNestML.CoCo.Visitor) No or wrong type of assignment provided!'
        _coco(_ast)
        cls.visitVariable(_ast.getVariable(), _coco)
        cls.visitExpression(_ast.getExpression(), _coco)
        return

    @classmethod
    def visitBitOperator(cls, _ast=None, _coco=None):
        """
        Visits a single bit-operator and checks the CoCo for this node.
        :param _ast: a single bit-operator.
        :type _ast: ASTBitOperator
        :param _coco: a single coco method object to check.
        :type _coco: CoCo
        """
        assert (_ast is not None and isinstance(_ast, ASTBitOperator.ASTBitOperator)), \
            '(PyNestML.CoCo.Visitor) No or wrong type of bit-operator provided!'
        _coco(_ast)
        return

    @classmethod
    def visitBlock(cls, _ast=None, _coco=None):
        """
        Visits a single block and checks the CoCo for this node.
        :param _ast: a single block.
        :type _ast: ASTBlock
        :param _coco: a single coco method object to check.
        :type _coco: CoCo
        """
        assert (_ast is not None and isinstance(_ast, ASTBlock.ASTBlock)), \
            '(PyNestML.CoCo.Visitor) No or wrong type of block provided!'
        _coco(_ast)
        for stmt in _ast.getStmts():
            cls.visitStmt(stmt, _coco)
        return

    @classmethod
    def visitBlockWithVariables(cls, _ast=None, _coco=None):
        """
        Visits a single block of variables and checks the CoCo for this node.
        :param _ast: a single block of variables.
        :type _ast: ASTBlockWithVariables
        :param _coco: a single coco method object to check.
        :type _coco: CoCo
        """
        assert (_ast is not None and isinstance(_ast, ASTBlockWithVariables.ASTBlockWithVariables)), \
            '(PyNestML.CoCo.Visitor) No or wrong type of block with variables provided!'
        _coco(_ast)
        for decl in _ast.getDeclarations():
            cls.visitDeclaration(decl, _coco)
        return

    @classmethod
    def visitBody(cls, _ast=None, _coco=None):
        """
        Visits a single body and checks the CoCo for this node.
        :param _ast: a single body element.
        :type _ast: ASTBody
        :param _coco: a single coco method object to check.
        :type _coco: CoCo
        """
        assert (_ast is not None and isinstance(_ast, ASTBody.ASTBody)), \
            '(PyNestML.CoCo.Visitor) No or wrong type of body provided!'
        _coco(_ast)
        for decl in _ast.getBodyElements():
            if isinstance(decl, ASTBlockWithVariables.ASTBlockWithVariables):
                cls.visitBlockWithVariables(decl, _coco)
            elif isinstance(decl, ASTUpdateBlock.ASTUpdateBlock):
                cls.visitUpdateBlock(decl, _coco)
            elif isinstance(decl, ASTEquationsBlock.ASTEquationsBlock):
                cls.visitEquationsBlock(decl, _coco)
            elif isinstance(decl, ASTInputBlock.ASTInputBlock):
                cls.visitInputBlock(decl, _coco)
            elif isinstance(decl, ASTOutputBlock.ASTOutputBlock):
                cls.visitOutputBlock(decl, _coco)
            else:
                cls.visitFunction(decl, _coco)
        return

    @classmethod
    def visitComparisonOperator(cls, _ast=None, _coco=None):
        """
        Visits a single comparison operator and checks the CoCo for this node.
        :param _ast: a single comparison operator.
        :type _ast: ASTComparisonOperator
        :param _coco: a single coco method object to check.
        :type _coco: CoCo
        """
        assert (_ast is not None and isinstance(_ast, ASTComparisonOperator.ASTComparisonOperator)), \
            '(PyNestML.CoCo.Visitor) No or wrong type of comparison operator provided!'
        _coco(_ast)
        return

    @classmethod
    def visitCompoundStmt(cls, _ast=None, _coco=None):
        """
        Visits a single compound stmt and checks the CoCo for this node.
        :param _ast: a single compound statement.
        :type _ast: ASTCompoundStmt
        :param _coco: a single coco method object to check.
        :type _coco: CoCo
        """
        assert (_ast is not None and isinstance(_ast, ASTCompoundStmt.ASTCompoundStmt)), \
            '(PyNestML.CoCo.Visitor) No or wrong type of compound statement provided!'
        _coco(_ast)
        if _ast.isIfStmt():
            cls.visitIfStmt(_ast.getIfStmt(), _coco)
        elif _ast.isWhileStmt():
            cls.visitWhileStmt(_ast.getWhileStmt(), _coco)
        else:
            cls.visitForStmt(_ast.getForStmt(), _coco)
        return

    @classmethod
    def visitDatatype(cls, _ast=None, _coco=None):
        """
        Visits a single datatype and checks the CoCo for this node.
        :param _ast: a single data-type element.
        :type _ast: ASTDatatype
        :param _coco: a single coco method object to check.
        :type _coco: CoCo
        """
        assert (_ast is not None and isinstance(_ast, ASTDatatype.ASTDatatype)), \
            '(PyNestML.CoCo.Visitor) No or wrong type of datatype provided!'
        _coco(_ast)
        if _ast.isUnitType():
            cls.visitUnitType(_ast.getUnitType(), _coco)
        return

    @classmethod
    def visitDeclaration(cls, _ast=None, _coco=None):
        """
        Visits a single declaration and checks the CoCo for this node.
        :param _ast: a single declaration statement.
        :type _ast: ASTDeclaration
        :param _coco: a single coco method object to check.
        :type _coco: CoCo
        """
        assert (_ast is not None and isinstance(_ast, ASTDeclaration.ASTDeclaration)), \
            '(PyNestML.CoCo.Visitor) No or wrong type of declaration provided!'
        _coco(_ast)
        for var in _ast.getVariables():
            cls.visitVariable(var, _coco)
        cls.visitDatatype(_ast.getDataType(), _coco)
        if _ast.hasExpression():
            cls.visitExpression(_ast.getExpr(), _coco)
        if _ast.hasInvariant():
            cls.visitExpression(_ast.getInvariant(), _coco)
        return

    @classmethod
    def visitDerivative(cls, _ast=None, _coco=None):
        """
        Visits a single declaration and checks the CoCo for this node.
        :param _ast: a single derivative element.
        :type _ast: ASTDerivative
        :param _coco: a single coco method object to check.
        :type _coco: CoCo
        """
        assert (_ast is not None and isinstance(_ast, ASTDerivative.ASTDerivative)), \
            '(PyNestML.CoCo.Visitor) No or wrong type of derivative provided!'
        _coco(_ast)
        return

    @classmethod
    def visitElifClause(cls, _ast=None, _coco=None):
        """
        Visits a single elif-clause and checks the CoCo for this node.
        :param _ast: a elif-clause statement.
        :type _ast: ASTElifClause
        :param _coco: a single coco method object to check.
        :type _coco: CoCo
        """
        assert (_ast is not None and isinstance(_ast, ASTElifClause.ASTElifClause)), \
            '(PyNestML.CoCo.Visitor) No or wrong type of elif-clause provided!'
        _coco(_ast)
        cls.visitExpression(_ast.getCondition(), _coco)
        cls.visitBlock(_ast.getBlock(), _coco)
        return

    @classmethod
    def visitElseClause(cls, _ast=None, _coco=None):
        """
        Visits a single else-clause and checks the CoCo for this node.
        :param _ast: a single else-clause statement.
        :type _ast: ASTElseClause
        :param _coco: a single coco method object to check.
        :type _coco: CoCo
        """
        assert (_ast is not None and isinstance(_ast, ASTElseClause.ASTElseClause)), \
            '(PyNestML.CoCo.Visitor) No or wrong type of else-clause provided!'
        _coco(_ast)
        cls.visitBlock(_ast.getBlock(), _coco)
        pass

    @classmethod
    def visitEquationsBlock(cls, _ast=None, _coco=None):
        """
        Visits a single equations block and checks the CoCo for this node.
        :param _ast: a single equations block statement.
        :type _ast: ASTEquationsBlock
        :param _coco: a single coco method object to check.
        :type _coco: CoCo
        """
        assert (_ast is not None and isinstance(_ast, ASTEquationsBlock.ASTEquationsBlock)), \
            '(PyNestML.CoCo.Visitor) No or wrong type of equations block provided!'
        _coco(_ast)
        for decl in _ast.getDeclarations():
            if isinstance(decl, ASTOdeShape.ASTOdeShape):
                cls.visitOdeShape(decl, _coco)
            elif isinstance(decl, ASTOdeFunction.ASTOdeFunction):
                cls.visitOdeFunction(decl, _coco)
            else:
                cls.visitOdeEquation(decl, _coco)
        return

    @classmethod
    def visitExpression(cls, _ast=None, _coco=None):
        """
        Visits a single expression and checks the CoCo for this node.
        :param _ast: a single  expression.
        :type _ast: ASTExpression
        :param _coco: a single coco method object to check.
        :type _coco: CoCo
        """
        assert (_ast is not None and (isinstance(_ast, ASTExpression.ASTExpression)
                                      or isinstance(_ast, ASTSimpleExpression.ASTSimpleExpression))), \
            '(PyNestML.CoCo.Visitor) No or wrong type of expression provided!'
        _coco(_ast)
        if _ast.isSimpleExpression():
            cls.visitSimpleExpression(_ast.getExpression(), _coco)
        if _ast.isUnaryOperator():
            cls.visitUnaryOperator(_ast.getUnaryOperator(), _coco)
        if _ast.isCompoundExpression():
            cls.visitExpression(_ast.getLhs(), _coco)
            if isinstance(_ast.getBinaryOperator(), ASTBitOperator.ASTBitOperator):
                cls.visitBitOperator(_ast.getBinaryOperator(), _coco)
            elif isinstance(_ast.getBinaryOperator(), ASTComparisonOperator.ASTComparisonOperator):
                cls.visitComparisonOperator(_ast.getBinaryOperator(), _coco)
            elif isinstance(_ast.getBinaryOperator(), ASTLogicalOperator.ASTLogicalOperator):
                cls.visitLogicalOperator(_ast.getBinaryOperator(), _coco)
            else:
                cls.visitArithmeticOperator(_ast.getBinaryOperator(), _coco)
            cls.visitExpression(_ast.getRhs(), _coco)
        if _ast.isTernaryOperator():
            cls.visitExpression(_ast.getCondition(), _coco)
            cls.visitExpression(_ast.getIfTrue(), _coco)
            cls.visitExpression(_ast.getIfNot(), _coco)
        return

    @classmethod
    def visitForStmt(cls, _ast=None, _coco=None):
        """
        Visits a single for statement and checks the CoCo for this node.
        :param _ast: a single  for-statement.
        :type _ast: ASTForStmt
        :param _coco: a single coco method object to check.
        :type _coco: CoCo
        """
        assert (_ast is not None and isinstance(_ast, ASTForStmt.ASTForStmt)), \
            '(PyNestML.CoCo.Visitor) No or wrong type of for-statement provided!'
        _coco(_ast)
        cls.visitExpression(_ast.getFrom())
        cls.visitExpression(_ast.getTo())
        cls.visitBlock(_ast.getBlock())
        return

    @classmethod
    def visitFunction(cls, _ast=None, _coco=None):
        """
        Visits a single function and checks the CoCo for this node.
        :param _ast: a single  function.
        :type _ast: ASTFunction
        :param _coco: a single coco method object to check.
        :type _coco: CoCo
        """
        assert (_ast is not None and isinstance(_ast, ASTFunction.ASTFunction)), \
            '(PyNestML.CoCo.Visitor) No or wrong type of function block provided!'
        _coco(_ast)
        for arg in _ast.getParameters().getParametersList():
            cls.visitDatatype(arg.getDataType(), _coco)
        if _ast.hasReturnType():
            cls.visitDatatype(_ast.getReturnType(), _coco)
        cls.visitBlock(_ast.getBlock(), _coco)
        pass

    @classmethod
    def visitFunctionCall(cls, _ast=None, _coco=None):
        """
        Visits a single function and checks the CoCo for this node.
        :param _ast: a single  function.
        :type _ast: ASTFunction
        :param _coco: a single coco method object to check.
        :type _coco: CoCo
        """
        assert (_ast is not None and isinstance(_ast, ASTFunctionCall.ASTFunctionCall)), \
            '(PyNestML.CoCo.Visitor) No or wrong type of function call provided!'
        _coco(_ast)
        if _ast.hasArgs():
            for arg in _ast.getArgs():
                cls.visitExpression(arg, _coco)
        return

    @classmethod
    def visitIfClause(cls, _ast=None, _coco=None):
        """
        Visits a single if-clause and checks the CoCo for this node.
        :param _ast: a if-clause.
        :type _ast: ASTIfClause
        :param _coco: a single coco method object to check.
        :type _coco: CoCo
        """
        assert (_ast is not None and isinstance(_ast, ASTIfClause.ASTIfClause)), \
            '(PyNestML.CoCo.Visitor) No or wrong type of if-clause provided!'
        _coco(_ast)
        cls.visitExpression(_ast.getCondition(), _coco)
        cls.visitBlock(_ast.getBlock(), _coco)
        return

    @classmethod
    def visitIfStmt(cls, _ast=None, _coco=None):
        """
        Visits a single if-stmt and checks the CoCo for this node.
        :param _ast: a if-stmt.
        :type _ast: ASTIfStmt
        :param _coco: a single coco method object to check.
        :type _coco: CoCo
        """
        assert (_ast is not None and isinstance(_ast, ASTIfStmt.ASTIfStmt)), \
            '(PyNestML.CoCo.Visitor) No or wrong type of if-statement provided!'
        _coco(_ast)
        cls.visitIfClause(_ast.getIfClause(), _coco)
        if _ast.hasElifClauses():
            for elifC in _ast.getElifClauses():
                cls.visitElifClause(elifC, _coco)
        if _ast.hasElseClause():
            cls.visitElseClause(_ast.getElseClause(), _coco)
        return

    @classmethod
    def visitInputBlock(cls, _ast=None, _coco=None):
        """
        Visits a single input-block and checks the CoCo for this node.
        :param _ast: a singe input-block.
        :type _ast: ASTInputBlock
        :param _coco: a single coco method object to check.
        :type _coco: CoCo
        """
        assert (_ast is not None and isinstance(_ast, ASTInputBlock.ASTInputBlock)), \
            '(PyNestML.CoCo.Visitor) No or wrong type of input-block provided!'
        _coco(_ast)
        for line in _ast.getInputLines():
            cls.visitInputLine(line, _coco)
        return

    @classmethod
    def visitInputLine(cls, _ast=None, _coco=None):
        """
        Visits a single input-line and checks the CoCo for this node.
        :param _ast: a singe input-line.
        :type _ast: ASTInputLine
        :param _coco: a single coco method object to check.
        :type _coco: CoCo
        """
        assert (_ast is not None and isinstance(_ast, ASTInputLine.ASTInputLine)), \
            '(PyNestML.CoCo.Visitor) No or wrong type of input-line provided!'
        _coco(_ast)
        if _ast.hasInputTypes():
            for tyPe in _ast.getInputTypes():
                cls.visitInputType(tyPe, _coco)
        return

    @classmethod
    def visitInputType(cls, _ast=None, _coco=None):
        """
        Visits a single input-type and checks the CoCo for this node.
        :param _ast: a singe input-type.
        :type _ast: ASTInputType
        :param _coco: a single coco method object to check.
        :type _coco: CoCo
        """
        assert (_ast is not None and isinstance(_ast, ASTInputType.ASTInputType)), \
            '(PyNestML.CoCo.Visitor) No or wrong type of input-type provided!'
        _coco(_ast)
        return

    @classmethod
    def visitLogicalOperator(cls, _ast=None, _coco=None):
        """
        Visits a single logical-operator and checks the CoCo for this node.
        :param _ast: a singe logical-operator.
        :type _ast: ASTLogicalOperator
        :param _coco: a single coco method object to check.
        :type _coco: CoCo
        """
        assert (_ast is not None and isinstance(_ast, ASTLogicalOperator.ASTLogicalOperator)), \
            '(PyNestML.CoCo.Visitor) No or wrong type of logical-operator provided!'
        _coco(_ast)
        return

    @classmethod
    def visitNestmlCompilationUnit(cls, _ast=None, _coco=None):
        """
        Visits a single compilation unit and checks the CoCo for this node.
        :param _ast: a singe logical-operator.
        :type _ast: ASTNESTMLCompilationUnit
        :param _coco: a single coco method object to check.
        :type _coco: CoCo
        """
        assert (_ast is not None and isinstance(_ast, ASTNESTMLCompilationUnit.ASTNESTMLCompilationUnit)), \
            '(PyNestML.CoCo.Visitor) No or wrong type of compilation unit provided!'
        _coco(_ast)
        for neuron in _ast.getNeuronList():
            cls.visitNeuron(neuron, _coco)
        return

    @classmethod
    def visitNeuron(cls, _ast=None, _coco=None):
        """
        Visits a single neuron and checks the CoCo for this node.
        :param _ast: a singe neuron.
        :type _ast: ASTNeuron
        :param _coco: a single coco method object to check.
        :type _coco: CoCo
        """
        assert (_ast is not None and isinstance(_ast, ASTNeuron.ASTNeuron)), \
            '(PyNestML.CoCo.Visitor) No or wrong type of neuron provided!'
        _coco(_ast)
        cls.visitBody(_ast.getBody(), _coco)
        return

    @classmethod
    def visitOdeEquation(cls, _ast=None, _coco=None):
        """
        Visits a single ode equation and checks the CoCo for this node.
        :param _ast: a singe ode equation.
        :type _ast: ASTOdeEquation
        :param _coco: a single coco method object to check.
        :type _coco: CoCo
        """
        assert (_ast is not None and isinstance(_ast, ASTOdeEquation.ASTOdeEquation)), \
            '(PyNestML.CoCo.Visitor) No or wrong type of ode-equation provided!'
        _coco(_ast)
        cls.visitDerivative(_ast.getLhs(), _coco)
        cls.visitExpression(_ast.getRhs(), _coco)
        return

    @classmethod
    def visitOdeFunction(cls, _ast=None, _coco=None):
        """
        Visits a single ode function and checks the CoCo for this node.
        :param _ast: a singe ode function.
        :type _ast: ASTOdeFunction
        :param _coco: a single coco method object to check.
        :type _coco: CoCo
        """
        assert (_ast is not None and isinstance(_ast, ASTOdeFunction.ASTOdeFunction)), \
            '(PyNestML.CoCo.Visitor) No or wrong type of ode-function provided!'
        _coco(_ast)
        cls.visitDatatype(_ast.getDataType(), _coco)
        cls.visitExpression(_ast.getExpression(), _coco)
        return

    @classmethod
    def visitOdeShape(cls, _ast=None, _coco=None):
        """
        Visits a single ode shape and checks the CoCo for this node.
        :param _ast: a singe ode shape.
        :type _ast: ASTOdeFunction
        :param _coco: a single coco method object to check.
        :type _coco: CoCo
        """
        assert (_ast is not None and isinstance(_ast, ASTOdeShape.ASTOdeShape)), \
            '(PyNestML.CoCo.Visitor) No or wrong type of ode-shape provided!'
        _coco(_ast)
        cls.visitVariable(_ast.getVariable(), _coco)
        cls.visitExpression(_ast.getExpression(), _coco)
        return

    @classmethod
    def visitOutputBlock(cls, _ast=None, _coco=None):
        """
        Visits a single output block and checks the CoCo for this node.
        :param _ast: a singe output block.
        :type _ast: ASTOutputBlock
        :param _coco: a single coco method object to check.
        :type _coco: CoCo
        """
        assert (_ast is not None and isinstance(_ast, ASTOutputBlock.ASTOutputBlock)), \
            '(PyNestML.CoCo.Visitor) No or wrong type of output-block provided!'
        _coco(_ast)
        return

    @classmethod
    def visitParameter(cls, _ast=None, _coco=None):
        """
        Visits a single parameter and checks the CoCo for this node.
        :param _ast: a singe parameter.
        :type _ast: ASTParameter
        :param _coco: a single coco method object to check.
        :type _coco: CoCo
        """
        assert (_ast is not None and isinstance(_ast, ASTParameter.ASTParameter)), \
            '(PyNestML.CoCo.Visitor) No or wrong type of parameter provided!'
        _coco(_ast)
        cls.visitDatatype(_ast.getDataType(), _coco)
        return

    @classmethod
    def visitParameters(cls, _ast=None, _coco=None):
        """
        Visits a single parameter and checks the CoCo for this node.
        :param _ast: a singe parameter.
        :type _ast: ASTParameter
        :param _coco: a single coco method object to check.
        :type _coco: CoCo
        """
        assert (_ast is not None and isinstance(_ast, ASTParameters.ASTParameters)), \
            '(PyNestML.CoCo.Visitor) No or wrong type of parameters provided!'
        _coco(_ast)
        for par in _ast.getParametersList():
            cls.visitParameter(par)
        return

    @classmethod
    def visitReturnStmt(cls, _ast=None, _coco=None):
        """
        Visits a single return statement and checks the CoCo for this node.
        :param _ast: a single return statement.
        :type _ast: ASTReturnStmt
        :param _coco: a single coco method object to check.
        :type _coco: CoCo
        """
        assert (_ast is not None and isinstance(_ast, ASTReturnStmt.ASTReturnStmt)), \
            '(PyNestML.CoCo.Visitor) No or wrong type of return statement provided!'
        _coco(_ast)
        if _ast.hasExpr():
            cls.visitExpression(_ast.getExpr(), _coco)
        return

    @classmethod
    def visitSimpleExpression(cls, _ast=None, _coco=None):
        """
        Visits a single simple expression and checks the CoCo for this node.
        :param _ast: a single simple expression.
        :type _ast: ASTSimpleExpression
        :param _coco: a single coco method object to check.
        :type _coco: CoCo
        """
        assert (_ast is not None and isinstance(_ast, ASTSimpleExpression.ASTSimpleExpression)), \
            '(PyNestML.CoCo.Visitor) No or wrong type of simple expression provided!'
        _coco(_ast)
        if _ast.isFunctionCall():
            cls.visitFunctionCall(_ast.getFunctionCall(), _coco)
        elif _ast.isVariable():
            cls.visitVariable(_ast.getVariable(), _coco)
        return

    @classmethod
    def visitSmallStmt(cls, _ast=None, _coco=None):
        """
        Visits a single small statement and checks the CoCo for this node.
        :param _ast: a single small statement.
        :type _ast: ASTSmallStatement
        :param _coco: a single coco method object to check.
        :type _coco: CoCo
        """
        assert (_ast is not None and isinstance(_ast, ASTSmallStmt.ASTSmallStmt)), \
            '(PyNestML.CoCo.Visitor) No or wrong type of small statement provided!'
        _coco(_ast)
        if _ast.isDeclaration():
            cls.visitDeclaration(_ast.getDeclaration(), _coco)
        elif _ast.isAssignment():
            cls.visitAssignment(_ast.getAssignment(), _coco)
        elif _ast.isFunctionCall():
            cls.visitFunctionCall(_ast.getFunctionCall(), _coco)
        elif _ast.isReturnStmt():
            cls.visitReturnStmt(_ast.getReturnStmt(), _coco)
        return

    @classmethod
    def visitStmt(cls, _ast=None, _coco=None):
        """
        Visits a single statement and checks the CoCo for this node.
        :param _ast: a single statement.
        :type _ast: ASTStmt
        :param _coco: a single coco method object to check.
        :type _coco: CoCo
        """
        assert (_ast is not None and isinstance(_ast, ASTStmt.ASTStmt)), \
            '(PyNestML.CoCo.Visitor) No or wrong type of statement provided!'
        _coco(_ast)
        if _ast.isSmallStmt():
            cls.visitSmallStmt(_ast.getSmallStmt(), _coco)
        else:
            cls.visitCompoundStmt(_ast.getCompoundStmt(), _coco)
        return

    @classmethod
    def visitUnaryOperator(cls, _ast=None, _coco=None):
        """
        Visits a single unary operator and checks the CoCo for this node.
        :param _ast: a single unary operator.
        :type _ast: ASTUnaryOperator
        :param _coco: a single coco method object to check.
        :type _coco: CoCo
        """
        assert (_ast is not None and isinstance(_ast, ASTUnaryOperator.ASTUnaryOperator)), \
            '(PyNestML.CoCo.Visitor) No or wrong type of unary-operator provided!'
        _coco(_ast)
        return

    @classmethod
    def visitUnitType(cls, _ast=None, _coco=None):
        """
        Visits a single unit-type and checks the CoCo for this node.
        :param _ast: a single unit-type.
        :type _ast: ASTUnitType
        :param _coco: a single coco method object to check.
        :type _coco: CoCo
        """
        assert (_ast is not None and isinstance(_ast, ASTUnitType.ASTUnitType)), \
            '(PyNestML.CoCo.Visitor) No or wrong type of unit-type provided!'
        _coco(_ast)
        if _ast.isPowerExpression():
            cls.visitUnitType(_ast.getBase(), _coco)
        elif _ast.isEncapsulated():
            cls.visitUnitType(_ast.getCompoundUnit(), _coco)
        elif _ast.isDiv() or _ast.isTimes():
            if isinstance(_ast.getLhs(), ASTUnitType.ASTUnitType):  # regard that lhs can be a numeric Or a unit-type
                cls.visitUnitType(_ast.getLhs(), _coco)
            cls.visitUnitType(_ast.getRhs(), _coco)
        return

    @classmethod
    def visitUpdateBlock(cls, _ast=None, _coco=None):
        """
        Visits a single update-block and checks the CoCo for this node.
        :param _ast: a single update-block.
        :type _ast: ASTUpdateBlock
        :param _coco: a single coco method object to check.
        :type _coco: CoCo
        """
        assert (_ast is not None and isinstance(_ast, ASTUpdateBlock.ASTUpdateBlock)), \
            '(PyNestML.CoCo.Visitor) No or wrong type of update-block provided!'
        _coco(_ast)
        cls.visitBlock(_ast.getBlock(), _coco)
        return

    @classmethod
    def visitVariable(cls, _ast=None, _coco=None):
        """
        Visits a single variable and checks the CoCo for this node.
        :param _ast: a single variable.
        :type _ast: ASTVariable
        :param _coco: a single coco method object to check.
        :type _coco: CoCo
        """
        assert (_ast is not None and isinstance(_ast, ASTVariable.ASTVariable)), \
            '(PyNestML.CoCo.Visitor) No or wrong type of variable provided!'
        _coco(_ast)
        return

    @classmethod
    def visitWhileStmt(cls, _ast=None, _coco=None):
        """
        Visits a single while statement and checks the CoCo for this node.
        :param _ast: a while statement.
        :type _ast: ASTWhileStmt
        :param _coco: a single coco method object to check.
        :type _coco: CoCo
        """
        assert (_ast is not None and isinstance(_ast, ASTWhileStmt.ASTWhileStmt)), \
            '(PyNestML.CoCo.Visitor) No or wrong type of while-statement provided!'
        _coco(_ast)
        cls.visitExpression(_ast.getCondition(), _coco)
        cls.visitBlock(_ast.getBlock(), _coco)
        return
