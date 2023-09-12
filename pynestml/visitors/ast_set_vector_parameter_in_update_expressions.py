# -*- coding: utf-8 -*-
#
# ast_set_vector_parameter_in_update_expressions.py
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
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.visitors.ast_visitor import ASTVisitor


class ASTSetVectorParameterInUpdateExpressionVisitor(ASTVisitor):
    """
    Sets the vector parameter in the update expression to the value that was originally provided in the ODE in the equations block.
    """

    def __init__(self, var: ASTVariable):
        super(ASTSetVectorParameterInUpdateExpressionVisitor, self).__init__()
        self.var = var

    def visit_variable(self, node: ASTVariable):
        """
        Set the vector parameter if present.
        :param node: variable in the expression
        """
        if node.get_name() == self.var.get_name():
            node.set_vector_parameter(self.var.get_vector_parameter())
