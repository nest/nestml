# -*- coding: utf-8 -*-
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

from typing import List, Optional

from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_parameter import ASTParameter
from pynestml.utils.port_signal_type import PortSignalType


class ASTOutputBlock(ASTNode):
    """
    This class is used to store output port declarations.
    ASTOutput represents the output block of the neuron:
        output:
            spike
      @attribute spike true if and only if the neuron has a spike output.
      @attribute continuous true if and only if the neuron has a continuous time output.
    Grammar:
        outputBlock: 'output' BLOCK_OPEN ('spike' | 'continuous') ;
    Attributes:
        type = None
    """

    def __init__(self, o_type, attributes: Optional[List[ASTParameter]], *args, **kwargs):
        """
        Standard constructor.

        Parameters for superclass (ASTNode) can be passed through :python:`*args` and :python:`**kwargs`.

        :param o_type: the type of the output port.
        :type o_type: PortSignalType
        """
        assert isinstance(o_type, PortSignalType)
        super(ASTOutputBlock, self).__init__(*args, **kwargs)
        self.type = o_type
        self.attributes = attributes

    def clone(self):
        """
        Return a clone ("deep copy") of this node.

        :return: new AST node instance
        :rtype: ASTOutputBlock
        """
        dup = ASTOutputBlock(o_type=self.type,
                             attributes=self.attributes,
                             # ASTNode common attributes:
                             source_position=self.source_position,
                             scope=self.scope,
                             comment=self.comment,
                             pre_comments=[s for s in self.pre_comments],
                             in_comment=self.in_comment,
                             implicit_conversion_factor=self.implicit_conversion_factor)

        return dup

    def is_spike(self) -> bool:
        """
        Returns whether it is a spike type port or not.
        :return: True if spike, otherwise False.
        """
        return self.type is PortSignalType.SPIKE

    def is_continuous(self) -> bool:
        """
        Returns whether it is a continuous time type or not.
        :return: True if continuous time, otherwise False.
        """
        return self.type is PortSignalType.CONTINUOUS

    def get_attributes(self) -> List[ASTParameter]:
        r"""
        Returns the attributes of this node, if any.
        :return: List of attributes of this node.
        """
        if self.attributes is None:
            return []

        return self.attributes

    def get_children(self) -> List[ASTNode]:
        r"""
        Returns the children of this node, if any.
        :return: List of children of this node.
        """
        return []

    def equals(self, other: ASTNode) -> bool:
        r"""
        The equality method.
        """
        if not isinstance(other, ASTOutputBlock):
            return False

        if bool(self.attributes) != bool(other.attributes):
            return False

        for attribute_self, attribute_other in zip(self.attributes, other.attributes):
            if not attribute_self.equals(attribute_other):
                return False

        return self.is_spike() == other.is_spike() and self.is_continuous() == other.is_continuous()
