#
# ASTInputBlock.py
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

from pynestml.modelprocessor.ASTNode import ASTElement
from pynestml.modelprocessor.ASTInputLine import ASTInputLine


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
            '(PyNestML.AST.Input) No or wrong type of input definitions provided (%s)!' % type(_inputDefinitions)
        for definition in _inputDefinitions:
            assert (definition is not None and isinstance(definition, ASTInputLine)), \
                '(PyNestML.AST.Input) No or wrong type of input definition provided (%s)!' % type(definition)
        super(ASTInputBlock, self).__init__(_sourcePosition)
        self.__inputDefinitions = _inputDefinitions
        return

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

    def getParent(self, _ast=None):
        """
        Indicates whether a this node contains the handed over node.
        :param _ast: an arbitrary ast node.
        :type _ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        for line in self.getInputLines():
            if line is _ast:
                return self
            elif line.getParent(_ast) is not None:
                return line.getParent(_ast)
        return None

    def __str__(self):
        """
        Returns a string representation of the input block.
        :return: a string representation.
        :rtype: str
        """
        ret = 'input:\n'
        if self.getInputLines() is not None:
            for inputDef in self.getInputLines():
                ret += str(inputDef) + '\n'
        ret += 'end\n'
        return ret

    def equals(self, _other=None):
        """
        The equals method.
        :param _other: a different object.
        :type _other:  object
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(_other, ASTInputBlock):
            return False
        if len(self.getInputLines()) != len(_other.getInputLines()):
            return False
        myInputLines = self.getInputLines()
        yourInputLines = _other.getInputLines()
        for i in range(0, len(myInputLines)):
            if not myInputLines[i].equals(yourInputLines[i]):
                return False
        return True
