# -*- coding: utf-8 -*-
#
# ast_parent_visitor.py
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
from pynestml.visitors.ast_visitor import ASTVisitor


class ASTParentVisitor(ASTVisitor):
    r"""
    For each node in the AST, assign its ``parent_`` attribute; in other words, make the AST a doubly-linked tree.
    """

    def __init__(self):
        super(ASTParentVisitor, self).__init__()

    def visit(self, node: ASTNode):
        r"""Set ``parent_`` property on all children to refer back to this node."""
        children = node.get_children()
        for child in children:
            child.parent_ = node
