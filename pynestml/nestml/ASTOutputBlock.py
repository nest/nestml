#
# ASTOutputBlock.py
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


from pynestml.nestml.ASTElement import ASTElement
from enum import Enum


class ASTOutputBlock(ASTElement):
    """
    This class is used to store output buffer declarations.
    ASTOutput represents the output block of the neuron:
        output: spike
      @attribute spike true iff the neuron has a spike output.
      @attribute current true iff. the neuron is a current output.
    Grammar:
        outputBlock: 'output' BLOCK_OPEN ('spike' | 'current') ;
    """
    __type = None

    def __init__(self, _type=None, _sourcePosition=None):
        """
        Standard constructor.
        :param _type: the type of the output buffer.
        :type _type: SignalType
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        """
        assert (_type is SignalType.SPIKE or _type is SignalType.CURRENT), \
            '(PyNestML.AST.OutputBlock) No or wrong type specification buffer provided (%s)!' % type(_type)
        super(ASTOutputBlock, self).__init__(_sourcePosition)
        self.__type = _type

    @classmethod
    def makeASTOutputBlock(cls, _type=None, _sourcePosition=None):
        """
        Factory method of the ASTOutputBlock class.
        :param _type: the type of the output buffer.
        :type _type: SignalType
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        :return: a new ASTOutputBlock object
        :rtype: ASTOutputBlock
        """
        return cls(_type, _sourcePosition)

    def isSpike(self):
        """
        Returns whether it is a spike buffer or not.
        :return: True if spike, otherwise False.
        :rtype: bool
        """
        return self.__type is SignalType.SPIKE

    def isCurrent(self):
        """
        Returns whether it is a current buffer or not.
        :return: True if current, otherwise False.
        :rtype: bool
        """
        return self.__type is SignalType.CURRENT

    def getParent(self, _ast=None):
        """
        Indicates whether a this node contains the handed over node.
        :param _ast: an arbitrary ast node.
        :type _ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        return None

    def printAST(self):
        """
        Returns a string representation of the output declaration.
        :return: a string representation
        :rtype: str
        """
        return 'output: ' + ('spike' if self.isSpike() else 'current') + '\n'

    def equals(self, _other=None):
        """
        The equals method.
        :param _other: a different object.
        :type _other: object
        :return: True if equals, otherwise False.
        :rtype: bool
        """
        if not isinstance(_other, ASTOutputBlock):
            return False
        return self.isSpike() == _other.isSpike() and self.isCurrent() == _other.isCurrent()


class SignalType(Enum):
    """
    This enum is used to describe the type of the emitted signal. 
    """
    SPIKE = 1
    CURRENT = 2
