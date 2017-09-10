"""
/*
 *  ASTCompound_Stmt.py
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
from pynestml.src.main.python.org.nestml.ast.ASTElement import ASTElement


class ASTCompound_Stmt(ASTElement):
    """
    This class is used to store compound statements.
    Grammar:
        compound_Stmt : if_Stmt
                | for_Stmt
                | while_Stmt;
    """
    __if_stmt = None
    __while_stmt = None
    __for_stmt = None

    def __init__(self, _if_stmt=None, _while_stmt=None, _for_stmt=None, _sourcePosition=None):
        """
        Standard constructor.
        :param _if_stmt: a if statement object
        :type _if_stmt: ASTIF_Stmt
        :param _while_stmt: a while statement object
        :type _while_stmt: ASTWHILE_Stmt
        :param _for_stmt: a for statement object
        :type _for_stmt: ASTFOR_Stmt
        :param _sourcePosition: The source position of the assignment
        :type _sourcePosition: ASTSourcePosition
        """
        super(ASTCompound_Stmt, self).__init__(_sourcePosition)
        self.__if_stmt = _if_stmt
        self.__while_stmt = _while_stmt
        self.__for_stmt = _for_stmt

    @classmethod
    def makeASTCompound_Stmt(cls, _if_stmt=None, _while_stmt=None,
                             _for_stmt=None, _sourcePosition=None):
        """
        Factory method of the ASTCompound_Stmt class.
        :param _if_stmt: a if statement object
        :type _if_stmt: ASTIF_Stmt
        :param _while_stmt: a while statement object
        :type _while_stmt: ASTWHILE_Stmt
        :param _for_stmt: a for statement object
        :type _for_stmt: ASTFOR_Stmt
        :param _sourcePosition: The source position of the assignment
        :type _sourcePosition: ASTSourcePosition
        :return: a new compound_stmt object
        :rtype: ASTCompound_Stmt
        """
        return cls(_if_stmt, _while_stmt, _for_stmt, _sourcePosition)

    def isIfStmt(self):
        """
        Returns whether it is an "if" statement or not.
        :return: True if if stmt, False else.
        :rtype: bool
        """
        return self.__if_stmt is not None

    def getIfStmt(self):
        """
        Returns the "if" statement.
        :return: the "if" statement.
        :rtype: ASTIF_Stmt
        """
        return self.__if_stmt

    def isWhileStmt(self):
        """
        Returns whether it is an "while" statement or not.
        :return: True if "while" stmt, False else.
        :rtype: bool
        """
        return self.__while_stmt is not None

    def getWhileStmt(self):
        """
        Returns the while statement.
        :return: the while statement.
        :rtype: ASTWHILE_Stmt
        """
        return self.__while_stmt

    def isForStmt(self):
        """
        Returns whether it is an "for" statement or not.
        :return: True if "for" stmt, False else.
        :rtype: bool
        """
        return self.__for_stmt is not None

    def getForStmt(self):
        """
        Returns the for statement.
        :return: the for statement.
        :rtype: ASTFOR_Stmt
        """
        return self.__for_stmt

    def printAST(self):
        """
        Returns a string representation of the compound statement.
        :return: a string representing the compound statement.
        :rtype: str
        """
        if self.isIfStmt():
            return self.getIfStmt().printAST()
        elif self.isForStmt():
            return self.getForStmt().printAST()
        elif self.isWhileStmt():
            return self.getWhileStmt().printAST()
        else:
            return '(NESTML.AST.PRINT) Unknown compound statement element.'
