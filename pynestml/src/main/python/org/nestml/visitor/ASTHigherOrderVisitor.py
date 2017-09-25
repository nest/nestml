#
# ASTHigherOrderVisitor.py
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


class ASTHigherOrderVisitor:
    """
    This visitor is used to visit each node of the ast and and preform an arbitrary on it..
    """

    @classmethod
    def visitArithmeticOperator(cls, _ast=None, _func=None):
        """
        Visits a single arithmetic operator and executes the operation this node.
        :param _ast: an arithmetic operator
        :type _ast: ASTArithmeticOperator
        :param _func: a single single function.
        :type _func: fun
        """
        assert (_ast is not None and isinstance(_ast, ASTArithmeticOperator.ASTArithmeticOperator)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of arithmetic operator provided (%s)!' % type(_ast)
        assert (_func is not None and callable(_func)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function provided (%s)!' % type(_func)
        _func(_ast)
        return

    @classmethod
    def visitAssignment(cls, _ast=None, _func=None):
        """
        Visits a single assignment and executes the operation this node.
        :param _ast: a single assignment object.
        :type _ast: ASTAssignment
        :param _func: a single single function.
        :type _func: fun
        """
        assert (_ast is not None and isinstance(_ast, ASTAssignment.ASTAssignment)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of assignment provided (%s)!' % type(_ast)
        assert (_func is not None and callable(_func)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function provided (%s)!' % type(_func)
        _func(_ast)
        cls.visitVariable(_ast.getVariable(), _func)
        cls.visitExpression(_ast.getExpression(), _func)
        return

    @classmethod
    def visitBitOperator(cls, _ast=None, _func=None):
        """
        Visits a single bit-operator and executes the operation this node.
        :param _ast: a single bit-operator.
        :type _ast: ASTBitOperator
        :param _func: a single single function.
        :type _func: fun
        """
        assert (_ast is not None and isinstance(_ast, ASTBitOperator.ASTBitOperator)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of bit-operator provided (%s)!' % type(_ast)
        assert (_func is not None and callable(_func)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function provided (%s)!' % type(_func)
        _func(_ast)
        return

    @classmethod
    def visitBlock(cls, _ast=None, _func=None):
        """
        Visits a single block and executes the operation this node.
        :param _ast: a single block.
        :type _ast: ASTBlock
        :param _func: a single single function.
        :type _func: fun
        """
        assert (_ast is not None and isinstance(_ast, ASTBlock.ASTBlock)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of block provided (%s)!' % type(_ast)
        assert (_func is not None and callable(_func)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function provided (%s)!' % type(_func)
        _func(_ast)
        for stmt in _ast.getStmts():
            if isinstance(stmt, ASTSmallStmt.ASTSmallStmt):
                cls.visitSmallStmt(stmt, _func)
            elif isinstance(stmt, ASTCompoundStmt.ASTCompoundStmt):
                cls.visitCompoundStmt(stmt, _func)
        return

    @classmethod
    def visitBlockWithVariables(cls, _ast=None, _func=None):
        """
        Visits a single block of variables and executes the operation this node.
        :param _ast: a single block of variables.
        :type _ast: ASTBlockWithVariables
        :param _func: a single single function.
        :type _func: fun
        """
        assert (_ast is not None and isinstance(_ast, ASTBlockWithVariables.ASTBlockWithVariables)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of block with variables provided (%s)!' % type(_ast)
        assert (_func is not None and callable(_func)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function provided (%s)!' % type(_func)
        _func(_ast)
        for decl in _ast.getDeclarations():
            cls.visitDeclaration(decl, _func)
        return

    @classmethod
    def visitBody(cls, _ast=None, _func=None):
        """
        Visits a single body and executes the operation this node.
        :param _ast: a single body element.
        :type _ast: ASTBody
        :param _func: a single single function.
        :type _func: fun
        """
        assert (_ast is not None and isinstance(_ast, ASTBody.ASTBody)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of body provided (%s)!' % type(_ast)
        assert (_func is not None and callable(_func)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function provided (%s)!' % type(_func)
        _func(_ast)
        for decl in _ast.getBodyElements():
            if isinstance(decl, ASTBlockWithVariables.ASTBlockWithVariables):
                cls.visitBlockWithVariables(decl, _func)
            elif isinstance(decl, ASTUpdateBlock.ASTUpdateBlock):
                cls.visitUpdateBlock(decl, _func)
            elif isinstance(decl, ASTEquationsBlock.ASTEquationsBlock):
                cls.visitEquationsBlock(decl, _func)
            elif isinstance(decl, ASTInputBlock.ASTInputBlock):
                cls.visitInputBlock(decl, _func)
            elif isinstance(decl, ASTOutputBlock.ASTOutputBlock):
                cls.visitOutputBlock(decl, _func)
            else:
                cls.visitFunction(decl, _func)
        return

    @classmethod
    def visitComparisonOperator(cls, _ast=None, _func=None):
        """
        Visits a single comparison operator and executes the operation this node.
        :param _ast: a single comparison operator.
        :type _ast: ASTComparisonOperator
        :param _func: a single single function.
        :type _func: fun
        """
        assert (_ast is not None and isinstance(_ast, ASTComparisonOperator.ASTComparisonOperator)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of comparison operator provided (%s)!' % type(_ast)
        assert (_func is not None and callable(_func)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function provided (%s)!' % type(_func)
        _func(_ast)
        return

    @classmethod
    def visitCompoundStmt(cls, _ast=None, _func=None):
        """
        Visits a single compound stmt and executes the operation this node.
        :param _ast: a single compound statement.
        :type _ast: ASTCompoundStmt
        :param _func: a single single function.
        :type _func: fun
        """
        assert (_ast is not None and isinstance(_ast, ASTCompoundStmt.ASTCompoundStmt)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of compound statement provided (%s)!' % type(_ast)
        assert (_func is not None and callable(_func)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function provided (%s)!' % type(_func)
        _func(_ast)
        if _ast.isIfStmt():
            cls.visitIfStmt(_ast.getIfStmt(), _func)
        elif _ast.isWhileStmt():
            cls.visitWhileStmt(_ast.getWhileStmt(), _func)
        else:
            cls.visitForStmt(_ast.getForStmt(), _func)
        return

    @classmethod
    def visitDatatype(cls, _ast=None, _func=None):
        """
        Visits a single datatype and executes the operation this node.
        :param _ast: a single data-type element.
        :type _ast: ASTDatatype
        :param _func: a single single function.
        :type _func: fun
        """
        assert (_ast is not None and isinstance(_ast, ASTDatatype.ASTDatatype)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of datatype provided (%s)!' % type(_ast)
        assert (_func is not None and callable(_func)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function provided (%s)!' % type(_func)
        _func(_ast)
        if _ast.isUnitType():
            cls.visitUnitType(_ast.getUnitType(), _func)
        return

    @classmethod
    def visitDeclaration(cls, _ast=None, _func=None):
        """
        Visits a single declaration and executes the operation this node.
        :param _ast: a single declaration statement.
        :type _ast: ASTDeclaration
        :param _func: a single single function.
        :type _func: fun
        """
        assert (_ast is not None and isinstance(_ast, ASTDeclaration.ASTDeclaration)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of declaration provided (%s)!' % type(_ast)
        assert (_func is not None and callable(_func)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function provided (%s)!' % type(_func)
        _func(_ast)
        for var in _ast.getVariables():
            cls.visitVariable(var, _func)
        cls.visitDatatype(_ast.getDataType(), _func)
        if _ast.hasExpression():
            cls.visitExpression(_ast.getExpr(), _func)
        if _ast.hasInvariant():
            cls.visitExpression(_ast.getInvariant(), _func)
        return

    @classmethod
    def visitElifClause(cls, _ast=None, _func=None):
        """
        Visits a single elif-clause and executes the operation this node.
        :param _ast: a elif-clause statement.
        :type _ast: ASTElifClause
        :param _func: a single single function.
        :type _func: fun
        """
        assert (_ast is not None and isinstance(_ast, ASTElifClause.ASTElifClause)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of elif-clause provided (%s)!' % type(_ast)
        assert (_func is not None and callable(_func)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function provided (%s)!' % type(_func)
        _func(_ast)
        cls.visitExpression(_ast.getCondition(), _func)
        cls.visitBlock(_ast.getBlock(), _func)
        return

    @classmethod
    def visitElseClause(cls, _ast=None, _func=None):
        """
        Visits a single else-clause and executes the operation this node.
        :param _ast: a single else-clause statement.
        :type _ast: ASTElseClause
        :param _func: a single single function.
        :type _func: fun
        """
        assert (_ast is not None and isinstance(_ast, ASTElseClause.ASTElseClause)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of else-clause provided (%s)!' % type(_ast)
        assert (_func is not None and callable(_func)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function provided (%s)!' % type(_func)
        _func(_ast)
        cls.visitBlock(_ast.getBlock(), _func)
        pass

    @classmethod
    def visitEquationsBlock(cls, _ast=None, _func=None):
        """
        Visits a single equations block and executes the operation this node.
        :param _ast: a single equations block statement.
        :type _ast: ASTEquationsBlock
        :param _func: a single single function.
        :type _func: fun
        """
        assert (_ast is not None and isinstance(_ast, ASTEquationsBlock.ASTEquationsBlock)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of equations block provided (%s)!' % type(_ast)
        assert (_func is not None and callable(_func)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function provided (%s)!' % type(_func)
        _func(_ast)
        for decl in _ast.getDeclarations():
            if isinstance(decl, ASTOdeShape.ASTOdeShape):
                cls.visitOdeShape(decl, _func)
            elif isinstance(decl, ASTOdeFunction.ASTOdeFunction):
                cls.visitOdeFunction(decl, _func)
            else:
                cls.visitOdeEquation(decl, _func)
        return

    @classmethod
    def visitExpression(cls, _ast=None, _func=None):
        """
        Visits a single expression and executes the operation this node.
        :param _ast: a single  expression.
        :type _ast: ASTExpression
        :param _func: a single single function.
        :type _func: fun
        """
        assert (_ast is not None and (isinstance(_ast, ASTExpression.ASTExpression)
                                      or isinstance(_ast, ASTSimpleExpression.ASTSimpleExpression))), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of expression provided (%s)!' % type(_ast)
        assert (_func is not None and callable(_func)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function provided (%s)!' % type(_func)
        _func(_ast)
        if _ast.isSimpleExpression():
            cls.visitSimpleExpression(_ast.getExpression(), _func)
        if _ast.isUnaryOperator():
            cls.visitUnaryOperator(_ast.getUnaryOperator(), _func)
        if _ast.isCompoundExpression():
            cls.visitExpression(_ast.getLhs(), _func)
            if isinstance(_ast.getBinaryOperator(), ASTBitOperator.ASTBitOperator):
                cls.visitBitOperator(_ast.getBinaryOperator(), _func)
            elif isinstance(_ast.getBinaryOperator(), ASTComparisonOperator.ASTComparisonOperator):
                cls.visitComparisonOperator(_ast.getBinaryOperator(), _func)
            elif isinstance(_ast.getBinaryOperator(), ASTLogicalOperator.ASTLogicalOperator):
                cls.visitLogicalOperator(_ast.getBinaryOperator(), _func)
            else:
                cls.visitArithmeticOperator(_ast.getBinaryOperator(), _func)
            cls.visitExpression(_ast.getRhs(), _func)
        if _ast.isTernaryOperator():
            cls.visitExpression(_ast.getCondition(), _func)
            cls.visitExpression(_ast.getIfTrue(), _func)
            cls.visitExpression(_ast.getIfNot(), _func)
        return

    @classmethod
    def visitForStmt(cls, _ast=None, _func=None):
        """
        Visits a single for statement and executes the operation this node.
        :param _ast: a single  for-statement.
        :type _ast: ASTForStmt
        :param _func: a single single function.
        :type _func: fun
        """
        assert (_ast is not None and isinstance(_ast, ASTForStmt.ASTForStmt)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of for-statement provided (%s)!' % type(_ast)
        assert (_func is not None and callable(_func)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function provided (%s)!' % type(_func)
        _func(_ast)
        cls.visitExpression(_ast.getFrom())
        cls.visitExpression(_ast.getTo())
        cls.visitBlock(_ast.getBlock())
        return

    @classmethod
    def visitFunction(cls, _ast=None, _func=None):
        """
        Visits a single function and executes the operation this node.
        :param _ast: a single  function.
        :type _ast: ASTFunction
        :param _func: a single single function.
        :type _func: fun
        """
        assert (_ast is not None and isinstance(_ast, ASTFunction.ASTFunction)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function block provided (%s)!' % type(_ast)
        assert (_func is not None and callable(_func)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function provided (%s)!' % type(_func)
        _func(_ast)
        for arg in _ast.getParameters():
            cls.visitDatatype(arg.getDataType(), _func)
        if _ast.hasReturnType():
            cls.visitDatatype(_ast.getReturnType(), _func)
        cls.visitBlock(_ast.getBlock(), _func)
        pass

    @classmethod
    def visitFunctionCall(cls, _ast=None, _func=None):
        """
        Visits a single function and executes the operation this node.
        :param _ast: a single  function.
        :type _ast: ASTFunction
        :param _func: a single single function.
        :type _func: fun
        """
        assert (_ast is not None and isinstance(_ast, ASTFunctionCall.ASTFunctionCall)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function call provided (%s)!' % type(_ast)
        assert (_func is not None and callable(_func)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function provided (%s)!' % type(_func)
        _func(_ast)
        if _ast.hasArgs():
            for arg in _ast.getArgs():
                cls.visitExpression(arg, _func)
        return

    @classmethod
    def visitIfClause(cls, _ast=None, _func=None):
        """
        Visits a single if-clause and executes the operation this node.
        :param _ast: a if-clause.
        :type _ast: ASTIfClause
        :param _func: a single single function.
        :type _func: fun
        """
        assert (_ast is not None and isinstance(_ast, ASTIfClause.ASTIfClause)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of if-clause provided (%s)!' % type(_ast)
        assert (_func is not None and callable(_func)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function provided (%s)!' % type(_func)
        _func(_ast)
        cls.visitExpression(_ast.getCondition(), _func)
        cls.visitBlock(_ast.getBlock(), _func)
        return

    @classmethod
    def visitIfStmt(cls, _ast=None, _func=None):
        """
        Visits a single if-stmt and executes the operation this node.
        :param _ast: a if-stmt.
        :type _ast: ASTIfStmt
        :param _func: a single single function.
        :type _func: fun
        """
        assert (_ast is not None and isinstance(_ast, ASTIfStmt.ASTIfStmt)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of if-statement provided (%s)!' % type(_ast)
        assert (_func is not None and callable(_func)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function provided (%s)!' % type(_func)
        _func(_ast)
        cls.visitIfClause(_ast.getIfClause(), _func)
        if _ast.hasElifClauses():
            for elifC in _ast.getElifClauses():
                cls.visitElifClause(elifC, _func)
        if _ast.hasElseClause():
            cls.visitElseClause(_ast.getElseClause(), _func)
        return

    @classmethod
    def visitInputBlock(cls, _ast=None, _func=None):
        """
        Visits a single input-block and executes the operation this node.
        :param _ast: a singe input-block.
        :type _ast: ASTInputBlock
        :param _func: a single single function.
        :type _func: fun
        """
        assert (_ast is not None and isinstance(_ast, ASTInputBlock.ASTInputBlock)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of input-block provided (%s)!' % type(_ast)
        assert (_func is not None and callable(_func)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function provided (%s)!' % type(_func)
        _func(_ast)
        for line in _ast.getInputLines():
            cls.visitInputLine(line, _func)
        return

    @classmethod
    def visitInputLine(cls, _ast=None, _func=None):
        """
        Visits a single input-line and executes the operation this node.
        :param _ast: a singe input-line.
        :type _ast: ASTInputLine
        :param _func: a single single function.
        :type _func: fun
        """
        assert (_ast is not None and isinstance(_ast, ASTInputLine.ASTInputLine)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of input-line provided (%s)!' % type(_ast)
        assert (_func is not None and callable(_func)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function provided (%s)!' % type(_func)
        _func(_ast)
        if _ast.hasInputTypes():
            for tyPe in _ast.getInputTypes():
                cls.visitInputType(tyPe, _func)
        return

    @classmethod
    def visitInputType(cls, _ast=None, _func=None):
        """
        Visits a single input-type and executes the operation this node.
        :param _ast: a singe input-type.
        :type _ast: ASTInputType
        :param _func: a single single function.
        :type _func: fun
        """
        assert (_ast is not None and isinstance(_ast, ASTInputType.ASTInputType)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of input-type provided (%s)!' % type(_ast)
        assert (_func is not None and callable(_func)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function provided (%s)!' % type(_func)
        _func(_ast)
        return

    @classmethod
    def visitLogicalOperator(cls, _ast=None, _func=None):
        """
        Visits a single logical-operator and executes the operation this node.
        :param _ast: a singe logical-operator.
        :type _ast: ASTLogicalOperator
        :param _func: a single single function.
        :type _func: fun
        """
        assert (_ast is not None and isinstance(_ast, ASTLogicalOperator.ASTLogicalOperator)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of logical-operator provided (%s)!' % type(_ast)
        assert (_func is not None and callable(_func)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function provided (%s)!' % type(_func)
        _func(_ast)
        return

    @classmethod
    def visitNestmlCompilationUnit(cls, _ast=None, _func=None):
        """
        Visits a single compilation unit and executes the operation this node.
        :param _ast: a singe logical-operator.
        :type _ast: ASTNESTMLCompilationUnit
        :param _func: a single single function.
        :type _func: fun
        """
        assert (_ast is not None and isinstance(_ast, ASTNESTMLCompilationUnit.ASTNESTMLCompilationUnit)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of compilation unit provided (%s)!' % type(_ast)
        assert (_func is not None and callable(_func)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function provided (%s)!' % type(_func)
        _func(_ast)
        for neuron in _ast.getNeuronList():
            cls.visitNeuron(neuron, _func)
        return

    @classmethod
    def visitNeuron(cls, _ast=None, _func=None):
        """
        Visits a single neuron and executes the operation this node.
        :param _ast: a singe neuron.
        :type _ast: ASTNeuron
        :param _func: a single single function.
        :type _func: fun
        """
        assert (_ast is not None and isinstance(_ast, ASTNeuron.ASTNeuron)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of neuron provided (%s)!' % type(_ast)
        assert (_func is not None and callable(_func)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function provided (%s)!' % type(_func)
        _func(_ast)
        cls.visitBody(_ast.getBody(), _func)
        return

    @classmethod
    def visitOdeEquation(cls, _ast=None, _func=None):
        """
        Visits a single ode equation and executes the operation this node.
        :param _ast: a singe ode equation.
        :type _ast: ASTOdeEquation
        :param _func: a single single function.
        :type _func: fun
        """
        assert (_ast is not None and isinstance(_ast, ASTOdeEquation.ASTOdeEquation)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of ode-equation provided (%s)!' % type(_ast)
        assert (_func is not None and callable(_func)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function provided (%s)!' % type(_func)
        _func(_ast)
        cls.visitVariable(_ast.getLhs(), _func)
        cls.visitExpression(_ast.getRhs(), _func)
        return

    @classmethod
    def visitOdeFunction(cls, _ast=None, _func=None):
        """
        Visits a single ode function and executes the operation this node.
        :param _ast: a singe ode function.
        :type _ast: ASTOdeFunction
        :param _func: a single single function.
        :type _func: fun
        """
        assert (_ast is not None and isinstance(_ast, ASTOdeFunction.ASTOdeFunction)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of ode-function provided (%s)!' % type(_ast)
        assert (_func is not None and callable(_func)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function provided (%s)!' % type(_func)
        _func(_ast)
        cls.visitDatatype(_ast.getDataType(), _func)
        cls.visitExpression(_ast.getExpression(), _func)
        return

    @classmethod
    def visitOdeShape(cls, _ast=None, _func=None):
        """
        Visits a single ode shape and executes the operation this node.
        :param _ast: a singe ode shape.
        :type _ast: ASTOdeFunction
        :param _func: a single single function.
        :type _func: fun
        """
        assert (_ast is not None and isinstance(_ast, ASTOdeShape.ASTOdeShape)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of ode-shape provided (%s)!' % type(_ast)
        assert (_func is not None and callable(_func)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function provided (%s)!' % type(_func)
        _func(_ast)
        cls.visitVariable(_ast.getVariable(), _func)
        cls.visitExpression(_ast.getExpression(), _func)
        return

    @classmethod
    def visitOutputBlock(cls, _ast=None, _func=None):
        """
        Visits a single output block and executes the operation this node.
        :param _ast: a singe output block.
        :type _ast: ASTOutputBlock
        :param _func: a single single function.
        :type _func: fun
        """
        assert (_ast is not None and isinstance(_ast, ASTOutputBlock.ASTOutputBlock)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of output-block provided (%s)!' % type(_ast)
        assert (_func is not None and callable(_func)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function provided (%s)!' % type(_func)
        _func(_ast)
        return

    @classmethod
    def visitParameter(cls, _ast=None, _func=None):
        """
        Visits a single parameter and executes the operation this node.
        :param _ast: a singe parameter.
        :type _ast: ASTParameter
        :param _func: a single single function.
        :type _func: fun
        """
        assert (_ast is not None and isinstance(_ast, ASTParameter.ASTParameter)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of parameter provided (%s)!' % type(_ast)
        assert (_func is not None and callable(_func)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function provided (%s)!' % type(_func)
        _func(_ast)
        cls.visitDatatype(_ast.getDataType(), _func)
        return

    @classmethod
    def visitReturnStmt(cls, _ast=None, _func=None):
        """
        Visits a single return statement and executes the operation this node.
        :param _ast: a single return statement.
        :type _ast: ASTReturnStmt
        :param _func: a single single function.
        :type _func: fun
        """
        assert (_ast is not None and isinstance(_ast, ASTReturnStmt.ASTReturnStmt)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of return statement provided (%s)!' % type(_ast)
        assert (_func is not None and callable(_func)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function provided (%s)!' % type(_func)
        _func(_ast)
        if _ast.hasExpr():
            cls.visitExpression(_ast.getExpr(), _func)
        return

    @classmethod
    def visitSimpleExpression(cls, _ast=None, _func=None):
        """
        Visits a single simple expression and executes the operation this node.
        :param _ast: a single simple expression.
        :type _ast: ASTSimpleExpression
        :param _func: a single single function.
        :type _func: fun
        """
        assert (_ast is not None and isinstance(_ast, ASTSimpleExpression.ASTSimpleExpression)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of simple expression provided (%s)!' % type(_ast)
        assert (_func is not None and callable(_func)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function provided (%s)!' % type(_func)
        _func(_ast)
        if _ast.isFunctionCall():
            cls.visitFunctionCall(_ast.getFunctionCall(), _func)
        elif _ast.isVariable():
            cls.visitVariable(_ast.getVariable(), _func)
        return

    @classmethod
    def visitSmallStmt(cls, _ast=None, _func=None):
        """
        Visits a single small statement and executes the operation this node.
        :param _ast: a single small statement.
        :type _ast: ASTSmallStatement
        :param _func: a single single function.
        :type _func: fun
        """
        assert (_ast is not None and isinstance(_ast, ASTSmallStmt.ASTSmallStmt)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of small statement provided (%s)!' % type(_ast)
        assert (_func is not None and callable(_func)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function provided (%s)!' % type(_func)
        _func(_ast)
        if _ast.isDeclaration():
            cls.visitDeclaration(_ast.getDeclaration(), _func)
        elif _ast.isAssignment():
            cls.visitAssignment(_ast.getAssignment(), _func)
        elif _ast.isFunctionCall():
            cls.visitFunctionCall(_ast.getFunctionCall(), _func)
        elif _ast.isReturnStmt():
            cls.visitReturnStmt(_ast.getReturnStmt(), _func)
        return

    @classmethod
    def visitUnaryOperator(cls, _ast=None, _func=None):
        """
        Visits a single unary operator and executes the operation this node.
        :param _ast: a single unary operator.
        :type _ast: ASTUnaryOperator
        :param _func: a single single function.
        :type _func: fun
        """
        assert (_ast is not None and isinstance(_ast, ASTUnaryOperator.ASTUnaryOperator)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of unary-operator provided (%s)!' % type(_ast)
        assert (_func is not None and callable(_func)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function provided (%s)!' % type(_func)
        _func(_ast)
        return

    @classmethod
    def visitUnitType(cls, _ast=None, _func=None):
        """
        Visits a single unit-type and executes the operation this node.
        :param _ast: a single unit-type.
        :type _ast: ASTUnitType
        :param _func: a single single function.
        :type _func: fun
        """
        assert (_ast is not None and isinstance(_ast, ASTUnitType.ASTUnitType)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of unit-type provided (%s)!' % type(_ast)
        assert (_func is not None and callable(_func)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function provided (%s)!' % type(_func)
        _func(_ast)
        if _ast.isPowerExpression():
            cls.visitUnitType(_ast.getBase(), _func)
        elif _ast.isEncapsulated():
            cls.visitUnitType(_ast.getCompoundUnit(), _func)
        elif _ast.isDiv() or _ast.isTimes():
            if isinstance(_ast.getLhs(), ASTUnitType.ASTUnitType):  # regard that lhs can be a numeric Or a unit-type
                cls.visitUnitType(_ast.getLhs(), _func)
            cls.visitUnitType(_ast.getRhs(), _func)
        return

    @classmethod
    def visitUpdateBlock(cls, _ast=None, _func=None):
        """
        Visits a single update-block and executes the operation this node.
        :param _ast: a single update-block.
        :type _ast: ASTUpdateBlock
        :param _func: a single single function.
        :type _func: fun
        """
        assert (_ast is not None and isinstance(_ast, ASTUpdateBlock.ASTUpdateBlock)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of update-block provided (%s)!' % type(_ast)
        assert (_func is not None and callable(_func)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function provided (%s)!' % type(_func)
        _func(_ast)
        cls.visitBlock(_ast.getBlock(), _func)
        return

    @classmethod
    def visitVariable(cls, _ast=None, _func=None):
        """
        Visits a single variable and executes the operation this node.
        :param _ast: a single variable.
        :type _ast: ASTVariable
        :param _func: a single single function.
        :type _func: fun
        """
        assert (_ast is not None and isinstance(_ast, ASTVariable.ASTVariable)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of variable provided (%s)!' % type(_ast)
        assert (_func is not None and callable(_func)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function provided (%s)!' % type(_func)
        _func(_ast)
        return

    @classmethod
    def visitWhileStmt(cls, _ast=None, _func=None):
        """
        Visits a single while statement and executes the operation this node.
        :param _ast: a while statement.
        :type _ast: ASTWhileStmt
        :param _func: a single single function.
        :type _func: fun
        """
        assert (_ast is not None and isinstance(_ast, ASTWhileStmt.ASTWhileStmt)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of while-statement provided (%s)!' % type(_ast)
        assert (_func is not None and callable(_func)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function provided (%s)!' % type(_func)
        _func(_ast)
        cls.visitExpression(_ast.getCondition(), _func)
        cls.visitBlock(_ast.getBlock(), _func)
        return
