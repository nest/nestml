"""
/*
 *  ASTEquations.py
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


class ASTEquations(ASTElement):
    """
    This class is used to store an equations block.
    ASTEquations a special function definition:
       equations:
         G = (e/tau_syn) * t * exp(-1/tau_syn*t)
         V' = -1/Tau * V + 1/C_m * (I_sum(G, spikes) + I_e + currents)
       end
     @attribute odeDeclaration Block with equations and differential equations.
     Grammar:
          equations:
            'equations'
            BLOCK_OPEN
              odeDeclaration
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
        assert (_block is not None)
        super(ASTEquations, self).__init__(_sourcePosition)
        self.__block = _block

    @classmethod
    def makeASTEquations(cls, _block=None, _sourcePosition=None):
        """
        Factory method of the ASTEquations class.
        :param _block: a block of definitions.
        :type _block: ASTBlock
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        :return: a new ASTEquations object.
        :rtype: ASTEquations
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
        Returns a string representation of the equations block.
        :return: a string representing an equations block.
        :rtype: str
        """
        return 'equations:\n' + self.getBlock().printAST() + 'end'
