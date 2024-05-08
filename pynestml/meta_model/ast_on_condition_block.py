# -*- coding: utf-8 -*-
#
# ast_on_condition_block.py
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

from typing import Any, List, Optional, Mapping

from pynestml.meta_model.ast_block import ASTBlock
from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_node import ASTNode


class ASTOnConditionBlock(ASTNode):
    r"""
    This class is used to store a declaration of an onCondition block
    """

    def __init__(self, block: ASTBlock, cond_expr: ASTExpression, const_parameters: Optional[Mapping] = None, *args, **kwargs):
        r"""
        Standard constructor.
        :param block: a block of definitions.
        :param source_position: the position of this element in the source file.
        """
        super(ASTOnConditionBlock, self).__init__(*args, **kwargs)
        self.block = block
        self.cond_expr = cond_expr
        self.const_parameters = const_parameters
        if self.const_parameters is None:
            self.const_parameters = {}

    def clone(self) -> ASTOnConditionBlock:
        r"""
        Return a clone ("deep copy") of this node.

        :return: new AST node instance
        """
        dup = ASTOnConditionBlock(block=self.block.clone(),
                                  cond_expr=self.cond_expr,
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

    def get_cond_expr(self) -> str:
        r"""
        Returns the conditional expression
        :return: the conditional expression
        """
        return self.cond_expr

    def get_children(self) -> List[ASTNode]:
        r"""
        Returns the children of this node, if any.
        :return: List of children of this node.
        """
        children = []
        if self.cond_expr:
            children.append(self.cond_expr)

        if self.get_block():
            children.append(self.get_block())

        return children

    def equals(self, other: ASTNode) -> bool:
        r"""
        The equality method.
        """
        if not isinstance(other, ASTOnConditionBlock):
            return False

        return self.get_block().equals(other.get_block()) and self.cond_expr == other.cond_expr
