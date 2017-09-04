"""
/*
 *  ASTWHILE_Stmt.py  
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
from pynestml.src.main.python.org.nestml.ast.ASTExpression import ASTExpression
from pynestml.src.main.python.org.nestml.ast.ASTBlock import ASTBlock
from pynestml.src.main.python.org.nestml.ast.ASTElement import ASTElement


class ASTWHILE_Stmt(ASTElement):
    """
    This class is used to store a new while-block.
    Grammar:
        while_Stmt : 'while' expr BLOCK_OPEN block BLOCK_CLOSE;
    """
    __condition = None
    __block = None

    def __init__(self, _condition=None, _block=None, _sourcePosition=None):
        """
        Standard constructor.
        :param _condition: the condition of the block.
        :type _condition: ASTExpression
        :param _block: a block of statements.
        :type _block: ASTBlock
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        """
        assert (_condition is not None and isinstance(_condition, ASTExpression)), \
            '(PyNESTML.AST.While-Stmt) Handed over object not an expression.'
        assert (_block is not None and isinstance(_block, ASTBlock)), \
            '(PyNESTML.While-Stmt) Handed over object not a block.'
        super(ASTWHILE_Stmt, self).__init__(_sourcePosition)
        self.__block = _block
        self.__condition = _condition

    @classmethod
    def makeASTWHILE_Stmt(cls, _condition=None, _block=None, _sourcePosition=None):
        """
        The factory method of the ASTWHILE_Stmt class.
        :param _condition: the condition of the block.
        :type _condition: ASTExpression
        :param _block: a block of statements.
        :type _block: ASTBlock
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        :return: a new block
        :rtype: ASTWHILE_Stmt
        """
        return cls(_condition, _block, _sourcePosition)

    def getCondition(self):
        """
        Returns the condition of the block.
        :return: the condition.
        :rtype: ASTExpression
        """
        return self.__condition

    def getBlock(self):
        """
        Returns the block of statements.
        :return: the block of statements.
        :rtype: ASTBlock
        """
        return self.__block

    def printAST(self):
        """
        Returns a string representation of the while statement.
        :return: a string representation.
        :rtype: str
        """
        return 'while ' + self.getCondition().printAST() + ':\n' + self.getBlock().printAST() + '\nend'
