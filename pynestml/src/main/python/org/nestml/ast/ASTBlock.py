#
# ASTBlock.py
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


from pynestml.src.main.python.org.nestml.ast.ASTElement import ASTElement


class ASTBlock(ASTElement):
    """
    This class is used to store a single block of declarations, i.e., statements.
    Grammar:
        block : ( stmt | NEWLINE )*;
    """
    __stmts = None

    def __init__(self, _stmts=list(), _sourcePosition=None):
        """
        Standard constructor.
        :param _stmts: a list of statements 
        :type _stmts: list(ASTStmt)
        :param _sourcePosition: the position of this element
        :type _sourcePosition: ASTSourcePosition
        """
        super(ASTBlock, self).__init__(_sourcePosition)
        self.__stmts = _stmts

    @classmethod
    def makeASTBlock(cls, _stmts=list(), _sourcePosition=None):
        """
        Factory method of ASTBlock.
        :param _stmts: a list of statements 
        :type _stmts: list(ASTStmt)
        :param _sourcePosition: the position of this element
        :type _sourcePosition: ASTSourcePosition
        :return a new block element
        :rtype ASTBlock 
        """
        return cls(_stmts, _sourcePosition)

    def getStmts(self):
        """
        Returns the list of statements.
        :return: list of stmts.
        :rtype: list(ASTStmt)
        """
        return self.__stmts

    def addStmt(self, _stmt=None):
        """
        Adds a single statement to the list of statements.
        :param _stmt: a statement
        :type _stmt: ASTStmt
        :return: no value returned
        :rtype: None
        """
        self.__stmts.append(_stmt)

    def deleteStmt(self, _stmt=None):
        """
        Deletes the handed over statement.
        :param _stmt: 
        :type _stmt: 
        :return: True if deleted, otherwise False.
        :rtype: bool
        """
        self.__stmts.remove(_stmt)

    def printAST(self):
        """
        Returns the raw representation of the block as a string.
        :return: a string representation
        :rtype: str
        """
        ret = ''
        for stmt in self.__stmts:
            ret += stmt.printAST()
            ret += '\n'
        return ret
