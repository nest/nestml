# -*- coding: utf-8 -*-
#
# ast_on_receive_block.py
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

from __future__ import annotations

from typing import Any, Optional, Mapping

from pynestml.meta_model.ast_block import ASTBlock
from pynestml.meta_model.ast_node import ASTNode


class ASTOnReceiveBlock(ASTNode):
    r"""
    This class is used to store a declaration of an onReceive block, for example:

    .. code-block:: nestml

       onReceive(pre_spikes):
           pre_tr += 1

    """

    def __init__(self, block: ASTBlock, port_name: str, const_parameters: Optional[Mapping] = None, *args, **kwargs):
        r"""
        Standard constructor.
        :param block: a block of definitions.
        :param source_position: the position of this element in the source file.
        """
        super(ASTOnReceiveBlock, self).__init__(*args, **kwargs)
        self.block = block
        self.port_name = port_name
        self.const_parameters = const_parameters
        if self.const_parameters is None:
            self.const_parameters = {}

    def clone(self) -> ASTOnReceiveBlock:
        r"""
        Return a clone ("deep copy") of this node.

        :return: new AST node instance
        """
        dup = ASTOnReceiveBlock(block=self.block.clone(),
                                port_name=self.port_name,
                                const_parameters=self.const_parameters,
                                # ASTNode common attributes:
                                source_position=self.source_position,
                                scope=self.scope,
                                comment=self.comment,
                                pre_comments=[s for s in self.pre_comments],
                                in_comment=self.in_comment,
                                implicit_conversion_factor=self.implicit_conversion_factor)

        return dup

    def get_const_parameters(self):
        return self.const_parameters

    def get_block(self) -> ASTBlock:
        r"""
        Returns the block of definitions.
        :return: the block
        """
        return self.block

    def get_port_name(self) -> str:
        r"""
        Returns the port name.
        :return: the port name
        """
        return self.port_name

    def get_parent(self, ast: ASTNode) -> Optional[ASTNode]:
        r"""
        Indicates whether a this node contains the handed over node.
        :param ast: an arbitrary meta_model node.
        :return: AST if this or one of the child nodes contains the handed over element.
        """
        if self.get_block() is ast:
            return self

        if self.get_block().get_parent(ast) is not None:
            return self.get_block().get_parent(ast)

        return None

    def equals(self, other: Any) -> bool:
        r"""
        The equals method.
        :param other: a different object.
        :return: True if equal, otherwise False.
        """
        if not isinstance(other, ASTOnReceiveBlock):
            return False
        return self.get_block().equals(other.get_block()) and self.port_name == other.port_name
