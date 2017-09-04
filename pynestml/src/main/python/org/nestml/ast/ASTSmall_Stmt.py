"""
/*
 *  ASTSmall_Stmt.py
 *
 *  This file is part of NEST.
 *
 *  Copyright (C) 2004 The NEST Initiative
 *
 *  NEST is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  NEST is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with NEST.  If not, see <http://www.gnu.org/licenses/>.
 *
 */
@author kperun
"""
from pynestml.src.main.python.org.nestml.ast.ASTAssignment import ASTAssignment
from pynestml.src.main.python.org.nestml.ast.ASTFunctionCall import ASTFunctionCall
from pynestml.src.main.python.org.nestml.ast.ASTReturnStmt import ASTReturnStmt
from pynestml.src.main.python.org.nestml.ast.ASTDeclaration import ASTDeclaration
from pynestml.src.main.python.org.nestml.ast.ASTElement import ASTElement


class ASTSmall_Stmt(ASTElement):
    """
    This class is used to store small statements, e.g., a declaration.
    Grammar:
        small_Stmt : assignment
                 | functionCall
                 | declaration
                 | returnStmt;
    """
    __assignment = None
    __functionCall = None
    __declaration = None
    __returnStmt = None

    def __init__(self, _assignment=None, _functionCall=None, _declaration=None, _returnStmt=None,
                 _sourcePosition=None):
        """
        Standard constructor.
        :param _assignment: an ast-assignment object.
        :type _assignment: ASTAssignment
        :param _functionCall: an ast-function call object.
        :type _functionCall: ASTFunctionCall
        :param _declaration: an ast-declaration object.
        :type _declaration: ASTDeclaration
        :param _returnStmt: an ast-return statement object.
        :type _returnStmt: ASTReturnStmt
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        """
        assert (_assignment is None or isinstance(_assignment, ASTAssignment)), \
            '(PyNESTML.AST) Not an assignment provided.'
        assert (_functionCall is None or isinstance(_functionCall, ASTFunctionCall)), \
            '(PyNESTML.AST) Not a function call provided.'
        assert (_declaration is None or isinstance(_declaration, ASTDeclaration)), \
            '(PyNESTML.AST) Not a declaration provided.'
        assert (_returnStmt is None or isinstance(_returnStmt, ASTReturnStmt)), \
            '(PyNESTML.AST) Not a return statement provided.'
        super(ASTSmall_Stmt, self).__init__(_sourcePosition)
        self.__assignment = _assignment
        self.__functionCall = _functionCall
        self.__declaration = _declaration
        self.__returnStmt = _returnStmt

    @classmethod
    def makeASTSmall_Stmt(cls, _assignment=None, _functionCall=None, _declaration=None,
                          _returnStmt=None, _sourcePosition=None):
        """
        Factory method of the ASTSmall_Stmt class.
        :param _assignment: an ast-assignment object.
        :type _assignment: ASTAssignment
        :param _functionCall: an ast-function call object.
        :type _functionCall: ASTFunctionCall
        :param _declaration: an ast-declaration object.
        :type _declaration: ASTDeclaration
        :param _returnStmt: an ast-return statement object.
        :type _returnStmt: ASTReturnStmt
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        :return: a new ASTSmall_Stmt object. 
        :rtype: ASTSmall_Stmt
        """
        return cls(_assignment, _functionCall, _declaration, _returnStmt, _sourcePosition)

    def isAssignment(self):
        """
        Returns whether it is an assignment statement or not.
        :return: True if assignment, False else.
        :rtype: bool
        """
        return self.__assignment is not None

    def getAssignment(self):
        """
        Returns the assignment.
        :return: the assignment statement.
        :rtype: ASTAssignment
        """
        return self.__assignment

    def isFunctionCall(self):
        """
        Returns whether it is an function call or not.
        :return: True if function call, False else.
        :rtype: bool
        """
        return self.__functionCall is not None

    def getFunctionCall(self):
        """
        Returns the function call.
        :return: the function call statement.
        :rtype: ASTFunctionCall
        """
        return self.__functionCall

    def isDeclaration(self):
        """
        Returns whether it is a declaration statement or not.
        :return: True if declaration, False else.
        :rtype: bool
        """
        return self.__declaration is not None

    def getDeclaration(self):
        """
        Returns the assignment.
        :return: the declaration statement.
        :rtype: ASTDeclaration
        """
        return self.__declaration

    def isReturnStmt(self):
        """
        Returns whether it is a return statement or not.
        :return: True if return stmt, False else.
        :rtype: bool
        """
        return self.__returnStmt is not None

    def getReturnStmt(self):
        """
        Returns the return statement.
        :return: the return statement.
        :rtype: ASTReturn_Stmt
        """
        return self.__returnStmt

    def printAST(self):
        """
        Returns a string representation of the small statement.
        :return: a string representation.
        :rtype: str
        """
        if self.isAssignment():
            return self.getAssignment().printAST()
        elif self.isFunctionCall():
            return self.getFunctionCall().printAST()
        elif self.isDeclaration():
            return self.getDeclaration().printAST()
        else:
            return self.getReturnStmt().printAST()
