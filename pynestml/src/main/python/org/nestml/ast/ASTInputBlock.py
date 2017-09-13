"""
 /*
 *  ASTInputBlock.py
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


class ASTInputBlock(ASTElement):
    """
    This class is used to store blocks of input definitions.
    ASTInputBlock represents the input block:
        input:
          spikeBuffer   <- inhibitory excitatory spike
          currentBuffer <- current
        end

    @attribute inputLine set of input lines.
    Grammar:
          inputBlock: 'input'
            BLOCK_OPEN
              (inputLine | NEWLINE)*
            BLOCK_CLOSE;
    """
    __inputDefinitions = None

    def __init__(self, _inputDefinitions=list(), _sourcePosition=None):
        """
        Standard constructor.
        :param _inputDefinitions: 
        :type _inputDefinitions: list(ASTInputLine)
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        """
        assert (_inputDefinitions is not None and isinstance(_inputDefinitions, list)), \
            '(PyNestML.AST.Input) No or wrong type of input definitions provided!'
        super(ASTInputBlock, self).__init__(_sourcePosition)
        self.__inputDefinitions = _inputDefinitions

    @classmethod
    def makeASTInputBlock(cls, _inputDefinitions=list(), _sourcePosition=None):
        """
        Factory method of the ASTInputBlock class.
        :param _inputDefinitions: a list of input definitions.
        :type _inputDefinitions: list(ASTInputLine)
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        :return: a new ASTInputBlock object
        :rtype: ASTInputBlock
        """
        return cls(_inputDefinitions, _sourcePosition)

    def getInputLines(self):
        """
        Returns the list of input lines.
        :return: a list of input lines
        :rtype: list(ASTInputLine)
        """
        return self.__inputDefinitions

    def printAST(self):
        """
        Returns a string representation of the input block.
        :return: a string representation.
        :rtype: str
        """
        ret = 'input:\n'
        if self.getInputLines() is not None:
            for inputDef in self.getInputLines():
                ret += inputDef.printAST() + '\n'
        ret += 'end\n'
        return ret
