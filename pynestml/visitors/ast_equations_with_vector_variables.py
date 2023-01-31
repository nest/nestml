# -*- coding: utf-8 -*-
#
# ast_equations_with_vector_variables.py
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
from pynestml.meta_model.ast_ode_equation import ASTOdeEquation
from pynestml.visitors.ast_visitor import ASTVisitor


class ASTEquationsWithVectorVariablesVisitor(ASTVisitor):
    """
    A visitor that collects all the equations that contain vector variables.
    """

    def __init__(self):
        super(ASTEquationsWithVectorVariablesVisitor, self).__init__()
        self.equations = list()

    def visit_ode_equation(self, node: ASTOdeEquation):
        rhs = node.get_rhs()
        for var in rhs.get_variables():
            if var.get_vector_parameter() and node not in self.equations:
                self.equations.append(node)
