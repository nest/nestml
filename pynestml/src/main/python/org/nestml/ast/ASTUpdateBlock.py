"""
/*
 *  ASTDynamics.py
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


class ASTDynamics(ASTElement):
    """
    This class is used to store dynamic blocks.
    ASTDynamics a special function definition:
      update:
        if r == 0: # not refractory
          integrate(V)
        end
      end
     @attribute block Implementation of the dynamics.
   
    Grammar:
        dynamics:
            'update'
            BLOCK_OPEN
              block
            BLOCK_CLOSE;
    """
    __block = None

    def __init__(self, _block=None, _sourcePosition=None):
        """
        Standard constructor.
        :param _block: a block of definitions.
        :type _block: ASTBlock
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        """
        super(ASTDynamics, self).__init__(_sourcePosition)
        assert (_block is not None)
        self.__block = _block

    @classmethod
    def makeASTDynamics(cls, _block=None, _sourcePosition=None):
        """
        Factory method of the ASTDynamics class.
        :param _block: a block of definitions.
        :type _block: ASTBlock
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        :return: a new ASTDynamics object.
        :rtype: ASTDynamics
        """
        return cls(_block, _sourcePosition)

    def getBlock(self):
        """
        Returns the block of definitions.
        :return: the block
        :rtype: ASTBlock
        """
        return self.__block

    def printAST(self):
        """
        Returns a string representation of a dynamics block.
        :return: a string representing the dynamics block.
        :rtype: str
        """
        return 'update:\n' + self.getBlock().printAST() + 'end'
