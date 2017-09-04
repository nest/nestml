"""
/*
 *  ASTStmt.py
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
from pynestml.src.main.python.org.nestml.ast.ASTSmall_Stmt import ASTSmall_Stmt
from pynestml.src.main.python.org.nestml.ast.ASTCompound_Stmt import ASTCompound_Stmt
from pynestml.src.main.python.org.nestml.ast.ASTElement import ASTElement


class ASTStmt(ASTElement):
    """
    This class is used to store a single statement.
    """
    __small_statement = None
    __compound_statement = None

    def __init__(self, _small_statement=None, _compound_statement=None, _sourcePosition=None):
        """
        Standard constructor.
        :param _small_statement: a small statement
        :type _small_statement: ASTSmall_Stmt 
        :param _compound_statement: a compound statement
        :type _compound_statement: ASTCompound_Stmt
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        """
        assert (_small_statement is None or _compound_statement is None), \
            '(PyNESTML.AST.Stmt) Type of statement not clear.'
        assert (_small_statement is None or isinstance(_small_statement, ASTSmall_Stmt)), \
            '(PyNESTML.AST.Stmt) Not a small statement provided.'
        assert (_compound_statement is None or isinstance(_compound_statement, ASTCompound_Stmt)), \
            '(PyNESTML.AST.Stmt) Not a compound statement provided.'
        super(ASTStmt, self).__init__(_sourcePosition)
        self.__small_statement = _small_statement
        self.__compound_statement = _compound_statement

    @classmethod
    def makeASTStmt(cls, _small_statement=None, _compound_statement=None, _sourcePosition=None):
        """
        Factory method of the ASTStmt class.
        :param _small_statement: a small statement.
        :type _small_statement: ASTSmall_Stmt
        :param _compound_statement: a compound statement
        :type _compound_statement: ASTCompound_Stmt
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        :return: a new ASTStmt object
        :rtype: ASTStmt
        """
        return cls(_small_statement, _compound_statement, _sourcePosition)

    def isSmallStmt(self):
        """
        Returns whether it is a small statement or not.
        :return: True if small stmt, False else.
        :rtype: bool
        """
        return self.__small_statement is not None

    def getSmallStmt(self):
        """
        Returns the small statement.
        :return: the small statement.
        :rtype: ASTSmall_Stmt
        """
        return self.__small_statement

    def isCompoundStmt(self):
        """
        Returns whether it is a compound statement or not.
        :return: True if compound stmt, False else.
        :rtype: bool
        """
        return self.__compound_statement is not None

    def getCompoundStmt(self):
        """
        Returns the compound statement.
        :return: the compound statement.
        :rtype: ASTCompound_Stmt
        """
        return self.__compound_statement

    def printAST(self):
        """
        Returns a string representation of the statement.
        :return: a string representation.
        :rtype: str
        """
        if self.isSmallStmt():
            return self.getSmallStmt().printAST()
        else:
            return self.getCompoundStmt().printAST()
