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
from pynestml.modelprocessor.ASTArithmeticOperator import ASTArithmeticOperator
from pynestml.modelprocessor.ASTAssignment import ASTAssignment
from pynestml.modelprocessor.ASTBitOperator import ASTBitOperator
from pynestml.modelprocessor.ASTBlock import ASTBlock
from pynestml.modelprocessor.ASTBlockWithVariables import ASTBlockWithVariables
from pynestml.modelprocessor.ASTBody import ASTBody
from pynestml.modelprocessor.ASTComparisonOperator import ASTComparisonOperator
from pynestml.modelprocessor.ASTCompoundStmt import ASTCompoundStmt
from pynestml.modelprocessor.ASTDatatype import ASTDatatype
from pynestml.modelprocessor.ASTDeclaration import ASTDeclaration
from pynestml.modelprocessor.ASTElifClause import ASTElifClause
from pynestml.modelprocessor.ASTElseClause import ASTElseClause
from pynestml.modelprocessor.ASTEquationsBlock import ASTEquationsBlock
from pynestml.modelprocessor.ASTExpression import ASTExpression
from pynestml.modelprocessor.ASTForStmt import ASTForStmt
from pynestml.modelprocessor.ASTFunction import ASTFunction
from pynestml.modelprocessor.ASTFunctionCall import ASTFunctionCall
from pynestml.modelprocessor.ASTIfClause import ASTIfClause
from pynestml.modelprocessor.ASTIfStmt import ASTIfStmt
from pynestml.modelprocessor.ASTInputBlock import ASTInputBlock
from pynestml.modelprocessor.ASTInputLine import ASTInputLine
from pynestml.modelprocessor.ASTInputType import ASTInputType
from pynestml.modelprocessor.ASTLogicalOperator import ASTLogicalOperator
from pynestml.modelprocessor.ASTNESTMLCompilationUnit import ASTNESTMLCompilationUnit
from pynestml.modelprocessor.ASTNeuron import ASTNeuron
from pynestml.modelprocessor.ASTOdeEquation import ASTOdeEquation
from pynestml.modelprocessor.ASTOdeFunction import ASTOdeFunction
from pynestml.modelprocessor.ASTOdeShape import ASTOdeShape
from pynestml.modelprocessor.ASTOutputBlock import ASTOutputBlock
from pynestml.modelprocessor.ASTParameter import ASTParameter
from pynestml.modelprocessor.ASTReturnStmt import ASTReturnStmt
from pynestml.modelprocessor.ASTSimpleExpression import ASTSimpleExpression
from pynestml.modelprocessor.ASTSmallStmt import ASTSmallStmt
from pynestml.modelprocessor.ASTUnaryOperator import ASTUnaryOperator
from pynestml.modelprocessor.ASTUnitType import ASTUnitType
from pynestml.modelprocessor.ASTUpdateBlock import ASTUpdateBlock
from pynestml.modelprocessor.ASTVariable import ASTVariable
from pynestml.modelprocessor.ASTWhileStmt import ASTWhileStmt


class ASTHigherOrderVisitor(object):
    """
    This visitor is used to visit each node of the ast and and preform an arbitrary on it..
    """

    @classmethod
    def visit(cls, _node=None, _func=None):
        """
        Dispatcher for visitor pattern.
        :param _node: The ASTElement to visit
        :type _node:  ASTElement or inherited
        :param _func: a single callable object
        :type _func: callable
        """
        if isinstance(_node, ASTArithmeticOperator):
            cls.visitArithmeticOperator(_node, _func)
            return
        if isinstance(_node, ASTAssignment):
            cls.visitAssignment(_node, _func)
            return
        if isinstance(_node, ASTBitOperator):
            cls.visitBitOperator(_node, _func)
            return
        if isinstance(_node, ASTBlock):
            cls.visitBlock(_node, _func)
            return
        if isinstance(_node, ASTBlockWithVariables):
            cls.visitBlockWithVariables(_node, _func)
            return
        if isinstance(_node, ASTBody):
            cls.visitBody(_node, _func)
            return
        if isinstance(_node, ASTComparisonOperator):
            cls.visitComparisonOperator(_node, _func)
            return
        if isinstance(_node, ASTCompoundStmt):
            cls.visitCompoundStmt(_node, _func)
            return
        if isinstance(_node, ASTDatatype):
            cls.visitDatatype(_node, _func)
            return
        if isinstance(_node, ASTDeclaration):
            cls.visitDeclaration(_node, _func)
            return
        if isinstance(_node, ASTElifClause):
            cls.visitElifClause(_node, _func)
            return
        if isinstance(_node, ASTElseClause):
            cls.visitElseClause(_node, _func)
            return
        if isinstance(_node, ASTEquationsBlock):
            cls.visitEquationsBlock(_node, _func)
            return
        if isinstance(_node, ASTExpression):
            cls.visitExpression(_node, _func)
            return
        if isinstance(_node, ASTForStmt):
            cls.visitForStmt(_node, _func)
            return
        if isinstance(_node, ASTFunction):
            cls.visitFunction(_node, _func)
            return
        if isinstance(_node, ASTFunctionCall):
            cls.visitFunctionCall(_node, _func)
            return
        if isinstance(_node, ASTIfClause):
            cls.visitIfClause(_node, _func)
            return
        if isinstance(_node, ASTIfStmt):
            cls.visitIfStmt(_node, _func)
            return
        if isinstance(_node, ASTInputBlock):
            cls.visitInputBlock(_node, _func)
            return
        if isinstance(_node, ASTInputLine):
            cls.visitInputLine(_node, _func)
            return
        if isinstance(_node, ASTInputType):
            cls.visitInputType(_node, _func)
            return
        if isinstance(_node, ASTLogicalOperator):
            cls.visitLogicalOperator(_node, _func)
            return
        if isinstance(_node, ASTNESTMLCompilationUnit):
            cls.visitCompilationUnit(_node, _func)
            return
        if isinstance(_node, ASTNeuron):
            cls.visitNeuron(_node, _func)
            return
        if isinstance(_node, ASTOdeEquation):
            cls.visitOdeEquation(_node, _func)
            return
        if isinstance(_node, ASTOdeFunction):
            cls.visitOdeFunction(_node, _func)
            return
        if isinstance(_node, ASTOdeShape):
            cls.visitOdeShape(_node, _func)
            return
        if isinstance(_node, ASTOutputBlock):
            cls.visitOutputBlock(_node, _func)
            return
        if isinstance(_node, ASTParameter):
            cls.visitParameter(_node, _func)
            return
        if isinstance(_node, ASTReturnStmt):
            cls.visitReturnStmt(_node, _func)
            return
        if isinstance(_node, ASTSimpleExpression):
            cls.visitSimpleExpression(_node, _func)
            return
        if isinstance(_node, ASTSmallStmt):
            cls.visitSmallStmt(_node, _func)
            return
        if isinstance(_node, ASTUnaryOperator):
            cls.visitUnaryOperator(_node, _func)
            return
        if isinstance(_node, ASTUnitType):
            cls.visitUnitType(_node, _func)
            return
        if isinstance(_node, ASTUpdateBlock):
            cls.visitUpdateBlock(_node, _func)
            return
        if isinstance(_node, ASTVariable):
            cls.visitVariable(_node, _func)
            return
        if isinstance(_node, ASTWhileStmt):
            cls.visitWhileStmt(_node, _func)
            return
        return

    @classmethod
    def visitCompilationUnit(cls, _ast=None, _func=None):
        """
        Visits a single compilation unit and executes the operation on this node.
        :param _ast: a single node
        :type _ast: ASTNESTMLCompilationUnit
        :param _func: a single function
        :type _func: fun
        """
        assert (_ast is not None and isinstance(_ast, ASTNESTMLCompilationUnit)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of compilation unit provided (%s)!' % type(_ast)
        assert (_func is not None and callable(_func)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function provided (%s)!' % type(_func)
        _func(_ast)
        for neuron in _ast.getNeuronList():
            cls.visit(neuron, _func)
        return

    @classmethod
    def visitArithmeticOperator(cls, _ast=None, _func=None):
        """
        Visits a single arithmetic operator and executes the operation this node.
        :param _ast: an arithmetic operator
        :type _ast: ASTArithmeticOperator
        :param _func: a single single function.
        :type _func: fun
        """
        assert (_ast is not None and isinstance(_ast, ASTArithmeticOperator)), \
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
        from pynestml.modelprocessor.ASTAssignment import ASTAssignment
        assert (_ast is not None and isinstance(_ast, ASTAssignment)), \
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
        from pynestml.modelprocessor.ASTBitOperator import ASTBitOperator
        assert (_ast is not None and isinstance(_ast, ASTBitOperator)), \
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
        from pynestml.modelprocessor.ASTBlock import ASTBlock
        from pynestml.modelprocessor.ASTSmallStmt import ASTSmallStmt
        from pynestml.modelprocessor.ASTCompoundStmt import ASTCompoundStmt
        assert (_ast is not None and isinstance(_ast, ASTBlock)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of block provided (%s)!' % type(_ast)
        assert (_func is not None and callable(_func)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function provided (%s)!' % type(_func)
        _func(_ast)
        for stmt in _ast.getStmts():
            if isinstance(stmt, ASTSmallStmt):
                cls.visitSmallStmt(stmt, _func)
            elif isinstance(stmt, ASTCompoundStmt):
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
        from pynestml.modelprocessor.ASTBlockWithVariables import ASTBlockWithVariables
        assert (_ast is not None and isinstance(_ast, ASTBlockWithVariables)), \
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
        from pynestml.modelprocessor.ASTBody import ASTBody
        assert (_ast is not None and isinstance(_ast, ASTBody)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of body provided (%s)!' % type(_ast)
        assert (_func is not None and callable(_func)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function provided (%s)!' % type(_func)
        _func(_ast)
        from pynestml.modelprocessor.ASTBlockWithVariables import ASTBlockWithVariables
        from pynestml.modelprocessor.ASTUpdateBlock import ASTUpdateBlock
        from pynestml.modelprocessor.ASTEquationsBlock import ASTEquationsBlock
        from pynestml.modelprocessor.ASTInputBlock import ASTInputBlock
        from pynestml.modelprocessor.ASTOutputBlock import ASTOutputBlock
        for decl in _ast.getBodyElements():
            if isinstance(decl, ASTBlockWithVariables):
                cls.visitBlockWithVariables(decl, _func)
            elif isinstance(decl, ASTUpdateBlock):
                cls.visitUpdateBlock(decl, _func)
            elif isinstance(decl, ASTEquationsBlock):
                cls.visitEquationsBlock(decl, _func)
            elif isinstance(decl, ASTInputBlock):
                cls.visitInputBlock(decl, _func)
            elif isinstance(decl, ASTOutputBlock):
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
        from pynestml.modelprocessor.ASTComparisonOperator import ASTComparisonOperator
        assert (_ast is not None and isinstance(_ast, ASTComparisonOperator)), \
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
        from pynestml.modelprocessor.ASTCompoundStmt import ASTCompoundStmt
        assert (_ast is not None and isinstance(_ast, ASTCompoundStmt)), \
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
        from pynestml.modelprocessor.ASTDatatype import ASTDatatype
        assert (_ast is not None and isinstance(_ast, ASTDatatype)), \
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
        from pynestml.modelprocessor.ASTDeclaration import ASTDeclaration
        assert (_ast is not None and isinstance(_ast, ASTDeclaration)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of declaration provided (%s)!' % type(_ast)
        assert (_func is not None and callable(_func)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function provided (%s)!' % type(_func)
        _func(_ast)
        for var in _ast.getVariables():
            cls.visitVariable(var, _func)
        cls.visitDatatype(_ast.getDataType(), _func)
        if _ast.hasExpression():
            cls.visitExpression(_ast.getExpression(), _func)
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
        from pynestml.modelprocessor.ASTElifClause import ASTElifClause
        assert (_ast is not None and isinstance(_ast, ASTElifClause)), \
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
        from pynestml.modelprocessor.ASTElseClause import ASTElseClause
        assert (_ast is not None and isinstance(_ast, ASTElseClause)), \
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
        from pynestml.modelprocessor.ASTEquationsBlock import ASTEquationsBlock
        assert (_ast is not None and isinstance(_ast, ASTEquationsBlock)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of equations block provided (%s)!' % type(_ast)
        assert (_func is not None and callable(_func)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function provided (%s)!' % type(_func)
        _func(_ast)
        from pynestml.modelprocessor.ASTOdeShape import ASTOdeShape
        from pynestml.modelprocessor.ASTOdeFunction import ASTOdeFunction
        for decl in _ast.getDeclarations():
            if isinstance(decl, ASTOdeShape):
                cls.visitOdeShape(decl, _func)
            elif isinstance(decl, ASTOdeFunction):
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
        from pynestml.modelprocessor.ASTExpression import ASTExpression
        from pynestml.modelprocessor.ASTSimpleExpression import ASTSimpleExpression
        from pynestml.modelprocessor.ASTBitOperator import ASTBitOperator
        from pynestml.modelprocessor.ASTComparisonOperator import ASTComparisonOperator
        from pynestml.modelprocessor.ASTLogicalOperator import ASTLogicalOperator
        assert (_ast is not None and (isinstance(_ast, ASTExpression) or isinstance(_ast, ASTSimpleExpression))), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of expression provided (%s)!' % type(_ast)
        assert (_func is not None and callable(_func)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function provided (%s)!' % type(_func)
        if isinstance(_ast, ASTSimpleExpression):
            cls.visitSimpleExpression(_ast, _func)
            return
        _func(_ast)
        if _ast.isEncapsulated():
            cls.visitExpression(_ast.getExpression(), _func)
        if _ast.isUnaryOperator():
            cls.visitUnaryOperator(_ast.getUnaryOperator(), _func)
            cls.visitExpression(_ast.getExpression(), _func)
        if _ast.isLogicalNot():
            cls.visitExpression(_ast.getExpression(), _func)
        if _ast.isCompoundExpression():
            cls.visitExpression(_ast.getLhs(), _func)
            if isinstance(_ast.getBinaryOperator(), ASTBitOperator):
                cls.visitBitOperator(_ast.getBinaryOperator(), _func)
            elif isinstance(_ast.getBinaryOperator(), ASTComparisonOperator):
                cls.visitComparisonOperator(_ast.getBinaryOperator(), _func)
            elif isinstance(_ast.getBinaryOperator(), ASTLogicalOperator):
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
        from pynestml.modelprocessor.ASTForStmt import ASTForStmt
        assert (_ast is not None and isinstance(_ast, ASTForStmt)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of for-statement provided (%s)!' % type(_ast)
        assert (_func is not None and callable(_func)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function provided (%s)!' % type(_func)
        _func(_ast)
        cls.visitExpression(_ast.getFrom(), _func)
        cls.visitExpression(_ast.getTo(), _func)
        cls.visitBlock(_ast.getBlock(), _func)
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
        from pynestml.modelprocessor.ASTFunction import ASTFunction
        assert (_ast is not None and isinstance(_ast, ASTFunction)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function block provided (%s)!' % type(_ast)
        assert (_func is not None and callable(_func)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function provided (%s)!' % type(_func)
        _func(_ast)
        for arg in _ast.getParameters():
            cls.visitDatatype(arg.getDataType(), _func)
        if _ast.hasReturnType():
            cls.visitDatatype(_ast.get_return_data_type(), _func)
        cls.visitBlock(_ast.getBlock(), _func)
        pass

    @classmethod
    def visitFunctionCall(cls, _ast=None, _func=None):
        """
        Visits a single function and executes the operation this node.
        :param _ast: a single  function.
        :type _ast: ASTFunctionCall
        :param _func: a single single function.
        :type _func: fun
        """
        from pynestml.modelprocessor.ASTFunctionCall import ASTFunctionCall
        assert (_ast is not None and isinstance(_ast, ASTFunctionCall)), \
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
        from pynestml.modelprocessor.ASTIfClause import ASTIfClause
        assert (_ast is not None and isinstance(_ast, ASTIfClause)), \
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
        from pynestml.modelprocessor.ASTIfStmt import ASTIfStmt
        assert (_ast is not None and isinstance(_ast, ASTIfStmt)), \
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
        from pynestml.modelprocessor.ASTInputBlock import ASTInputBlock
        assert (_ast is not None and isinstance(_ast, ASTInputBlock)), \
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
        from pynestml.modelprocessor.ASTInputLine import ASTInputLine
        assert (_ast is not None and isinstance(_ast, ASTInputLine)), \
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
        from pynestml.modelprocessor.ASTInputType import ASTInputType
        assert (_ast is not None and isinstance(_ast, ASTInputType)), \
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
        from pynestml.modelprocessor.ASTLogicalOperator import ASTLogicalOperator
        assert (_ast is not None and isinstance(_ast, ASTLogicalOperator)), \
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
        from pynestml.modelprocessor.ASTNESTMLCompilationUnit import ASTNESTMLCompilationUnit
        assert (_ast is not None and isinstance(_ast, ASTNESTMLCompilationUnit)), \
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
        from pynestml.modelprocessor.ASTNeuron import ASTNeuron
        assert (_ast is not None and isinstance(_ast, ASTNeuron)), \
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
        from pynestml.modelprocessor.ASTOdeEquation import ASTOdeEquation
        assert (_ast is not None and isinstance(_ast, ASTOdeEquation)), \
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
        from pynestml.modelprocessor.ASTOdeFunction import ASTOdeFunction
        assert (_ast is not None and isinstance(_ast, ASTOdeFunction)), \
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
        :type _ast: ASTOdeShape
        :param _func: a single single function.
        :type _func: fun
        """
        from pynestml.modelprocessor.ASTOdeShape import ASTOdeShape
        assert (_ast is not None and isinstance(_ast, ASTOdeShape)), \
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
        from pynestml.modelprocessor.ASTOutputBlock import ASTOutputBlock
        assert (_ast is not None and isinstance(_ast, ASTOutputBlock)), \
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
        from pynestml.modelprocessor.ASTParameter import ASTParameter
        assert (_ast is not None and isinstance(_ast, ASTParameter)), \
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
        from pynestml.modelprocessor.ASTReturnStmt import ASTReturnStmt
        assert (_ast is not None and isinstance(_ast, ASTReturnStmt)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of return statement provided (%s)!' % type(_ast)
        assert (_func is not None and callable(_func)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function provided (%s)!' % type(_func)
        _func(_ast)
        if _ast.hasExpression():
            cls.visitExpression(_ast.getExpression(), _func)
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
        from pynestml.modelprocessor.ASTSimpleExpression import ASTSimpleExpression
        assert (_ast is not None and isinstance(_ast, ASTSimpleExpression)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of simple expression provided (%s)!' % type(_ast)
        assert (_func is not None and callable(_func)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function provided (%s)!' % type(_func)
        _func(_ast)
        if _ast.isFunctionCall():
            cls.visitFunctionCall(_ast.getFunctionCall(), _func)
        elif _ast.isVariable() or _ast.hasUnit():
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
        from pynestml.modelprocessor.ASTSmallStmt import ASTSmallStmt
        assert (_ast is not None and isinstance(_ast, ASTSmallStmt)), \
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
        from pynestml.modelprocessor.ASTUnaryOperator import ASTUnaryOperator
        assert (_ast is not None and isinstance(_ast, ASTUnaryOperator)), \
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
        from pynestml.modelprocessor.ASTUnitType import ASTUnitType
        assert (_ast is not None and isinstance(_ast, ASTUnitType)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of unit-type provided (%s)!' % type(_ast)
        assert (_func is not None and callable(_func)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function provided (%s)!' % type(_func)
        _func(_ast)
        if _ast.isPowerExpression():
            cls.visitUnitType(_ast.getBase(), _func)
        elif _ast.isEncapsulated():
            cls.visitUnitType(_ast.getCompoundUnit(), _func)
        elif _ast.isDiv() or _ast.isTimes():
            if isinstance(_ast.getLhs(), ASTUnitType):  # regard that lhs can be a numeric Or a unit-type
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
        from pynestml.modelprocessor.ASTUpdateBlock import ASTUpdateBlock
        assert (_ast is not None and isinstance(_ast, ASTUpdateBlock)), \
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
        from pynestml.modelprocessor.ASTVariable import ASTVariable
        assert (_ast is not None and isinstance(_ast, ASTVariable)), \
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
        from pynestml.modelprocessor.ASTWhileStmt import ASTWhileStmt
        assert (_ast is not None and isinstance(_ast, ASTWhileStmt)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of while-statement provided (%s)!' % type(_ast)
        assert (_func is not None and callable(_func)), \
            '(PyNestML.Visitor.HigherOrder) No or wrong type of function provided (%s)!' % type(_func)
        _func(_ast)
        cls.visitExpression(_ast.getCondition(), _func)
        cls.visitBlock(_ast.getBlock(), _func)
        return

    def traverse(self, _ast=None,_visitOp=None, _traverseOp=None, _endvisitOp=None):
        """
        Dispatcher for traverse method.
        :param _ast: The ASTElement to visit
        :type _ast: Inherited from ASTElement
        :param _visitOp: The operation executed on visiting
        :type _visitOp: callable
        :param _traverseOp: the traverse routine
        :type _traverseOp: callable
        :param _endvisitOp: the operation called on end visit
        :type _endvisitOp: callable
        """
        # custom traverse available, then use it
        if _traverseOp is not None:
            _traverseOp(_ast, _visitOp, _traverseOp, _endvisitOp)
        if isinstance(_ast, ASTArithmeticOperator):
            self.traverseArithmeticOperator(_ast)
            return
        if isinstance(_ast, ASTAssignment):
            self.traverseAssignment(_ast)
            return
        if isinstance(_ast, ASTBitOperator):
            self.traverseBitOperator(_ast)
            return
        if isinstance(_ast, ASTBlock):
            self.traverseBlock(_ast)
            return
        if isinstance(_ast, ASTBlockWithVariables):
            self.traverseBlockWithVariables(_ast)
            return
        if isinstance(_ast, ASTBody):
            self.traverseBody(_ast)
            return
        if isinstance(_ast, ASTComparisonOperator):
            self.traverseComparisonOperator(_ast)
            return
        if isinstance(_ast, ASTCompoundStmt):
            self.traverseCompoundStmt(_ast)
            return
        if isinstance(_ast, ASTDatatype):
            self.traverseDatatype(_ast)
            return
        if isinstance(_ast, ASTDeclaration):
            self.traverseDeclaration(_ast)
            return
        if isinstance(_ast, ASTElifClause):
            self.traverseElifClause(_ast)
            return
        if isinstance(_ast, ASTElseClause):
            self.traverseElseClause(_ast)
            return
        if isinstance(_ast, ASTEquationsBlock):
            self.traverseEquationsBlock(_ast)
            return
        if isinstance(_ast, ASTExpression):
            self.traverseExpression(_ast)
            return
        if isinstance(_ast, ASTForStmt):
            self.traverseForStmt(_ast)
            return
        if isinstance(_ast, ASTFunction):
            self.traverseFunction(_ast)
            return
        if isinstance(_ast, ASTFunctionCall):
            self.traverseFunctionCall(_ast)
            return
        if isinstance(_ast, ASTIfClause):
            self.traverseIfClause(_ast)
            return
        if isinstance(_ast, ASTIfStmt):
            self.traverseIfStmt(_ast)
            return
        if isinstance(_ast, ASTInputBlock):
            self.traverseInputBlock(_ast)
            return
        if isinstance(_ast, ASTInputLine):
            self.traverseInputLine(_ast)
            return
        if isinstance(_ast, ASTInputType):
            self.traverseInputType(_ast)
            return
        if isinstance(_ast, ASTLogicalOperator):
            self.traverseLogicalOperator(_ast)
            return
        if isinstance(_ast, ASTNESTMLCompilationUnit):
            self.traverseCompilationUnit(_ast)
            return
        if isinstance(_ast, ASTNeuron):
            self.traverseNeuron(_ast)
            return
        if isinstance(_ast, ASTOdeEquation):
            self.traverseOdeEquation(_ast)
            return
        if isinstance(_ast, ASTOdeFunction):
            self.traverseOdeFunction(_ast)
            return
        if isinstance(_ast, ASTOdeShape):
            self.traverseOdeShape(_ast)
            return
        if isinstance(_ast, ASTOutputBlock):
            self.traverseOutputBlock(_ast)
            return
        if isinstance(_ast, ASTParameter):
            self.traverseParameter(_ast)
            return
        if isinstance(_ast, ASTReturnStmt):
            self.traverseReturnStmt(_ast)
            return
        if isinstance(_ast, ASTSimpleExpression):
            self.traverseSimpleExpression(_ast)
            return
        if isinstance(_ast, ASTSmallStmt):
            self.traverseSmallStmt(_ast)
            return
        if isinstance(_ast, ASTUnaryOperator):
            self.traverseUnaryOperator(_ast)
            return
        if isinstance(_ast, ASTUnitType):
            self.traverseUnitType(_ast)
            return
        if isinstance(_ast, ASTUpdateBlock):
            self.traverseUpdateBlock(_ast)
            return
        if isinstance(_ast, ASTVariable):
            self.traverseVariable(_ast)
            return
        if isinstance(_ast, ASTWhileStmt):
            self.traverseWhileStmt(_ast)
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
        if _node.getExpression() is not None:
            _node.getExpression().accept(self.getRealSelf())
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
        if _node.get_rhs() is not None:
            _node.get_rhs().accept(self.getRealSelf())
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
        if _node.get_return_data_type() is not None:
            _node.get_return_data_type().accept(self.getRealSelf())
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
        if _node.get_rhs() is not None:
            _node.get_rhs().accept(self.getRealSelf())
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
        if _node.getExpression() is not None:
            _node.getExpression().accept(self.getRealSelf())
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
        if _node.get_rhs() is not None:
            _node.get_rhs().accept(self.getRealSelf())
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