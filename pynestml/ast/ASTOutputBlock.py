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
from pynestml.ast.ASTNode import ASTNode
from pynestml.ast.ASTSignalType import ASTSignalType
from pynestml.ast.ASTSourceLocation import ASTSourceLocation


class ASTOutputBlock(ASTNode):
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

    def __init__(self, type, source_position):
        # type: (ASTSignalType,ASTSourceLocation) -> None
        """
        Standard constructor.
        :param type: the type of the output buffer.
        :type type: SignalType
        :param source_position: the position of this element in the source file.
        :type source_position: ASTSourceLocation.
        """
        super(ASTOutputBlock, self).__init__(source_position)
        self.__type = type

    def is_spike(self):
        """
        Returns whether it is a spike buffer or not.
        :return: True if spike, otherwise False.
        :rtype: bool
        """
        return self.__type is ASTSignalType.SPIKE

    def is_current(self):
        """
        Returns whether it is a current buffer or not.
        :return: True if current, otherwise False.
        :rtype: bool
        """
        return self.__type is ASTSignalType.CURRENT

    def get_parent(self, ast=None):
        """
        Indicates whether a this node contains the handed over node.
        :param ast: an arbitrary ast node.
        :type ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        return None

    def __str__(self):
        """
        Returns a string representation of the output declaration.
        :return: a string representation
        :rtype: str
        """
        return 'output: ' + ('spike' if self.is_spike() else 'current') + '\n'

    def equals(self, other=None):
        """
        The equals method.
        :param other: a different object.
        :type other: object
        :return: True if equals, otherwise False.
        :rtype: bool
        """
        if not isinstance(other, ASTOutputBlock):
            return False
        return self.is_spike() == other.is_spike() and self.is_current() == other.is_current()
