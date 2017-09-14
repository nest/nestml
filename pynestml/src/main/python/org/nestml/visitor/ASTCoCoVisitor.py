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


class ASTCoCoVisitor:
    """
    This visitor is used to visit each node of the ast and ensure certain properties.
    """

    @classmethod
    def visitArithmeticOperator(cls, _ast=None, _coco=None):
        """
        Todo
        :param _ast: 
        :type _ast: 
        :param _coco: 
        :type _coco: 
        :return: 
        :rtype: 
        """
        _coco(_ast)
        return


    @classmethod
    def visitAssignment(cls, _ast=None, _coco=None):
        """
        Todo
        :param _ast: 
        :type _ast: 
        :param _coco: 
        :type _coco: 
        :return: 
        :rtype: 
        """
        pass

    @classmethod
    def visitBitOperator(cls, _ast=None, _coco=None):
        """
        Todo
        :param _ast: 
        :type _ast: 
        :param _coco: 
        :type _coco: 
        :return: 
        :rtype: 
        """
        pass

    @classmethod
    def visitBlock(cls, _ast=None, _coco=None):
        """
        Todo
        :param _ast: 
        :type _ast: 
        :param _coco: 
        :type _coco: 
        :return: 
        :rtype: 
        """
        pass

    @classmethod
    def visitBlockWithVariables(cls, _ast=None, _coco=None):
        """
        Todo
        :param _ast: 
        :type _ast: 
        :param _coco: 
        :type _coco: 
        :return: 
        :rtype: 
        """
        pass

    @classmethod
    def visitBody(cls, _ast=None, _coco=None):
        """
        Todo
        :param _ast: 
        :type _ast: 
        :param _coco: 
        :type _coco: 
        :return: 
        :rtype: 
        """
        pass

    @classmethod
    def visitComparisonOperator(cls, _ast=None, _coco=None):
        """
        Todo
        :param _ast: 
        :type _ast: 
        :param _coco: 
        :type _coco: 
        :return: 
        :rtype: 
        """
        pass

    @classmethod
    def visitCompoundStmt(cls, _ast=None, _coco=None):
        """
        Todo
        :param _ast: 
        :type _ast: 
        :param _coco: 
        :type _coco: 
        :return: 
        :rtype: 
        """
        pass

    @classmethod
    def visitDatatype(cls, _ast=None, _coco=None):
        """
        Todo
        :param _ast: 
        :type _ast: 
        :param _coco: 
        :type _coco: 
        :return: 
        :rtype: 
        """
        pass

    @classmethod
    def visitDeclaration(cls, _ast=None, _coco=None):
        """
        Todo
        :param _ast: 
        :type _ast: 
        :param _coco: 
        :type _coco: 
        :return: 
        :rtype: 
        """
        pass

    @classmethod
    def visitDerivative(cls, _ast=None, _coco=None):
        """
        Todo
        :param _ast: 
        :type _ast: 
        :param _coco: 
        :type _coco: 
        :return: 
        :rtype: 
        """
        pass

    @classmethod
    def visitElifClause(cls, _ast=None, _coco=None):
        """
        Todo
        :param _ast: 
        :type _ast: 
        :param _coco: 
        :type _coco: 
        :return: 
        :rtype: 
        """
        pass

    @classmethod
    def visitElseClause(cls, _ast=None, _coco=None):
        """
        Todo
        :param _ast: 
        :type _ast: 
        :param _coco: 
        :type _coco: 
        :return: 
        :rtype: 
        """
        pass

    @classmethod
    def visitEquationsBlock(cls, _ast=None, _coco=None):
        """
        Todo
        :param _ast: 
        :type _ast: 
        :param _coco: 
        :type _coco: 
        :return: 
        :rtype: 
        """
        pass

    @classmethod
    def visitExpression(cls, _ast=None, _coco=None):
        """
        Todo
        :param _ast: 
        :type _ast: 
        :param _coco: 
        :type _coco: 
        :return: 
        :rtype: 
        """
        pass

    @classmethod
    def visitForStmt(cls, _ast=None, _coco=None):
        """
        Todo
        :param _ast: 
        :type _ast: 
        :param _coco: 
        :type _coco: 
        :return: 
        :rtype: 
        """
        pass

    @classmethod
    def visitFunction(cls, _ast=None, _coco=None):
        """
        Todo
        :param _ast: 
        :type _ast: 
        :param _coco: 
        :type _coco: 
        :return: 
        :rtype: 
        """
        pass

    @classmethod
    def visitFunctionCall(cls, _ast=None, _coco=None):
        """
        Todo
        :param _ast: 
        :type _ast: 
        :param _coco: 
        :type _coco: 
        :return: 
        :rtype: 
        """
        pass

    @classmethod
    def visitIfClause(cls, _ast=None, _coco=None):
        """
        Todo
        :param _ast: 
        :type _ast: 
        :param _coco: 
        :type _coco: 
        :return: 
        :rtype: 
        """
        pass

    @classmethod
    def visitIfStmt(cls, _ast=None, _coco=None):
        """
        Todo
        :param _ast: 
        :type _ast: 
        :param _coco: 
        :type _coco: 
        :return: 
        :rtype: 
        """
        pass

    @classmethod
    def visitInputBlock(cls, _ast=None, _coco=None):
        """
        Todo
        :param _ast: 
        :type _ast: 
        :param _coco: 
        :type _coco: 
        :return: 
        :rtype: 
        """
        pass

    @classmethod
    def visitInputLine(cls, _ast=None, _coco=None):
        """
        Todo
        :param _ast: 
        :type _ast: 
        :param _coco: 
        :type _coco: 
        :return: 
        :rtype: 
        """
        pass

    @classmethod
    def visitInputType(cls, _ast=None, _coco=None):
        """
        Todo
        :param _ast: 
        :type _ast: 
        :param _coco: 
        :type _coco: 
        :return: 
        :rtype: 
        """
        pass

    @classmethod
    def visitLogicalOperator(cls, _ast=None, _coco=None):
        """
        
        :param _ast: 
        :type _ast: 
        :param _coco: 
        :type _coco: 
        :return: 
        :rtype: 
        """
        pass

    @classmethod
    def visitNestmlCompilationUnit(cls, _ast=None, _coco=None):
        """
        
        :param _ast: 
        :type _ast: 
        :param _coco: 
        :type _coco: 
        :return: 
        :rtype: 
        """
        pass

    @classmethod
    def visitNeuron(cls, _ast=None, _coco=None):
        """
        
        :param _ast: 
        :type _ast: 
        :param _coco: 
        :type _coco: 
        :return: 
        :rtype: 
        """
        pass

    @classmethod
    def visitOdeEquation(cls, _ast=None, _coco=None):
        """
        
        :param _ast: 
        :type _ast: 
        :param _coco: 
        :type _coco: 
        :return: 
        :rtype: 
        """
        pass

    @classmethod
    def visitOdeFunction(cls, _ast=None, _coco=None):
        """
        
        :param _ast: 
        :type _ast: 
        :param _coco: 
        :type _coco: 
        :return: 
        :rtype: 
        """
        pass

    @classmethod
    def visitOdeShape(cls, _ast=None, _coco=None):
        """
        
        :param _ast: 
        :type _ast: 
        :param _coco: 
        :type _coco: 
        :return: 
        :rtype: 
        """
        pass

    @classmethod
    def visitOutputBlock(cls, _ast=None, _coco=None):
        """
        
        :param _ast: 
        :type _ast: 
        :param _coco: 
        :type _coco: 
        :return: 
        :rtype: 
        """
        pass

    @classmethod
    def visitParameter(cls, _ast=None, _coco=None):
        """
        
        :param _ast: 
        :type _ast: 
        :param _coco: 
        :type _coco: 
        :return: 
        :rtype: 
        """
        pass

    @classmethod
    def visitParameters(cls, _ast=None, _coco=None):
        """
        
        :param _ast: 
        :type _ast: 
        :param _coco: 
        :type _coco: 
        :return: 
        :rtype: 
        """
        pass

    @classmethod
    def visitReturnStmt(cls, _ast=None, _coco=None):
        """
        
        :param _ast: 
        :type _ast: 
        :param _coco: 
        :type _coco: 
        :return: 
        :rtype: 
        """
        pass

    @classmethod
    def visitSimpleExpression(cls, _ast=None, _coco=None):
        """
        
        :param _ast: 
        :type _ast: 
        :param _coco: 
        :type _coco: 
        :return: 
        :rtype: 
        """
        pass

    @classmethod
    def visitSmallStmt(cls, _ast=None, _coco=None):
        """
        
        :param _ast: 
        :type _ast: 
        :param _coco: 
        :type _coco: 
        :return: 
        :rtype: 
        """
        pass

    @classmethod
    def visitStmt(cls, _ast=None, _coco=None):
        """
        
        :param _ast: 
        :type _ast: 
        :param _coco: 
        :type _coco: 
        :return: 
        :rtype: 
        """
        pass

    @classmethod
    def visitUnaryOperator(cls, _ast=None, _coco=None):
        """
        
        :param _ast: 
        :type _ast: 
        :param _coco: 
        :type _coco: 
        :return: 
        :rtype: 
        """
        pass

    @classmethod
    def visitUnitType(cls, _ast=None, _coco=None):
        """
        
        :param _ast: 
        :type _ast: 
        :param _coco: 
        :type _coco: 
        :return: 
        :rtype: 
        """
        pass

    @classmethod
    def visitUpdateBlock(cls, _ast=None, _coco=None):
        """
        
        :param _ast: 
        :type _ast: 
        :param _coco: 
        :type _coco: 
        :return: 
        :rtype: 
        """
        pass

    @classmethod
    def visitVariable(cls, _ast=None, _coco=None):
        """
        
        :param _ast: 
        :type _ast: 
        :param _coco: 
        :type _coco: 
        :return: 
        :rtype: 
        """
        pass

    @classmethod
    def visitWhileStmt(cls, _ast=None, _coco=None):
        """
        
        :param _ast: 
        :type _ast: 
        :param _coco: 
        :type _coco: 
        :return: 
        :rtype: 
        """
        pass
