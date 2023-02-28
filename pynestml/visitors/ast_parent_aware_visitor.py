# -*- coding: utf-8 -*-
#
# ast_parent_aware_visitor.py
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
from pynestml.utils.stack import Stack
from pynestml.visitors.ast_visitor import ASTVisitor


class ASTParentAwareVisitor(ASTVisitor):
    """
    The parent aware visitor storing a trace. This visitor enables a given visitor to inspect the corresponding
    parent node.
    Attributes:
        parents type(Stack): A stack containing the predecessor of this node.
    """

    def __init__(self):
        super(ASTParentAwareVisitor, self).__init__()
        self.parents = Stack()

    def handle(self, _node):
        self.visit(_node)
        self.parents.push(_node)
        self.traverse(_node)
        self.parents.pop()
        self.endvisit(_node)
        return
