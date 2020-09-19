# -*- coding: utf-8 -*-
#
# ast_higher_order_visitor.py
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
from pynestml.visitors.ast_visitor import ASTVisitor


class ASTHigherOrderVisitor(ASTVisitor):
    """
    This visitor is used to visit each node of the meta_model and and preform an arbitrary on it..
    """

    def __init__(self, visit_funcs=list(), endvisit_funcs=list()):
        self.visit_funcs = list()
        self.endvisit_funcs = list()
        super(ASTHigherOrderVisitor, self).__init__()
        # check if a list of funcs is handed over or not
        if isinstance(visit_funcs, list):
            self.visit_funcs.extend(visit_funcs)
        elif callable(visit_funcs):
            self.visit_funcs.append(visit_funcs)
        # analogously for end visit funcs
        if isinstance(endvisit_funcs, list):
            self.endvisit_funcs.extend(endvisit_funcs)
        elif callable(endvisit_funcs):
            self.endvisit_funcs.append(endvisit_funcs)

    def visit(self, node):
        for fun in self.visit_funcs:
            fun(node)

    def endvisit(self, node):
        for fun in self.endvisit_funcs:
            fun(node)
