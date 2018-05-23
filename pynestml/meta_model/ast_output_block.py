#
# ast_output_block.py
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
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_signal_type import ASTSignalType
from pynestml.meta_model.ast_source_location import ASTSourceLocation


class ASTOutputBlock(ASTNode):
    """
    This class is used to store output buffer declarations.
    ASTOutput represents the output block of the neuron:
        output: spike
      @attribute spike true iff the neuron has a spike output.
      @attribute current true iff. the neuron is a current output.
    Grammar:
        outputBlock: 'output' BLOCK_OPEN ('spike' | 'current') ;
    Attributes:
        type = None
    """

    def __init__(self, o_type, source_position):
        # type: (ASTSignalType,ASTSourceLocation) -> None
        """
        Standard constructor.
        :param o_type: the type of the output buffer.
        :type o_type: SignalType
        :param source_position: the position of this element in the source file.
        :type source_position: ASTSourceLocation.
        """
        super(ASTOutputBlock, self).__init__(source_position)
        self.type = o_type

    def is_spike(self):
        """
        Returns whether it is a spike buffer or not.
        :return: True if spike, otherwise False.
        :rtype: bool
        """
        return self.type is ASTSignalType.SPIKE

    def is_current(self):
        """
        Returns whether it is a current buffer or not.
        :return: True if current, otherwise False.
        :rtype: bool
        """
        return self.type is ASTSignalType.CURRENT

    def get_parent(self, ast):
        """
        Indicates whether a this node contains the handed over node.
        :param ast: an arbitrary meta_model node.
        :type ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        return None

    def equals(self, other):
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
