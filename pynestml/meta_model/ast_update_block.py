# -*- coding: utf-8 -*-
#
# ast_update_block.py
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

from typing import List

from pynestml.meta_model.ast_stmts_body import ASTStmtsBody
from pynestml.meta_model.ast_node import ASTNode


class ASTUpdateBlock(ASTNode):
    r"""
    The ``update`` block in the model.
    """

    def __init__(self, stmts_body: ASTStmtsBody, *args, **kwargs):
        """
        Standard constructor.

        Parameters for superclass (ASTNode) can be passed through :python:`*args` and :python:`**kwargs`.

        :param block: a block of definitions.
        """
        super(ASTUpdateBlock, self).__init__(*args, **kwargs)
        assert isinstance(stmts_body, ASTStmtsBody)
        self.stmts_body = stmts_body

    def clone(self):
        """
        Return a clone ("deep copy") of this node.

        :return: new AST node instance
        :rtype: ASTUpdateBlock
        """
        dup = ASTUpdateBlock(stmts_body=self.stmts_body.clone(),
                             # ASTNode common attributes:
                             source_position=self.source_position,
                             scope=self.scope,
                             comment=self.comment,
                             pre_comments=[s for s in self.pre_comments],
                             in_comment=self.in_comment,
                             implicit_conversion_factor=self.implicit_conversion_factor)

        return dup

    def get_stmts_body(self) -> ASTStmtsBody:
        """
        Returns the body of statements.
        :return: the statements body
        """
        return self.stmts_body

    def get_children(self) -> List[ASTNode]:
        r"""
        Returns the children of this node, if any.
        :return: List of children of this node.
        """
        return [self.get_stmts_body()]

    def equals(self, other: ASTNode) -> bool:
        r"""
        The equality method.
        """
        if not isinstance(other, ASTUpdateBlock):
            return False

        return self.get_stmts_body().equals(other.get_stmts_body())
