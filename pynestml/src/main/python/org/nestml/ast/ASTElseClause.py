"""
/*
 *  ASTElseClause.py
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


class ASTElseClause(ASTElement):
    """
    This class is used to store a single else-clause.
    Grammar:
        elseClause : 'else' BLOCK_OPEN block;
    """
    __block = None

    def __init__(self, _block=None, _sourcePosition=None):
        """
        Standard constructor.
        :param _block: a block of statements.
        :type _block: ASTBlock
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        """
        super(ASTElseClause, self).__init__(_sourcePosition)
        self.__block = _block

    @classmethod
    def makeASTElseClause(cls, _block=None, _sourcePosition=None):
        """
        The factory method of the ASTElseClause class.
        :param _block: a block of statements.
        :type _block: ASTBlock
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        :return: a new block
        :rtype: ASTElseClause
        """
        return cls(_block, _sourcePosition)

    def getBlock(self):
        """
        Returns the block of statements.
        :return: the block of statements.
        :rtype: ASTBlock
        """
        return self.__block

    def printAST(self):
        """
        Returns a string representation of the else clause.
        :return: a string representation of the else clause.
        :rtype: str
        """
        return 'else:\n' + self.getBlock().printAST()
