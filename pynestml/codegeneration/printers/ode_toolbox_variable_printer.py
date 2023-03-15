# -*- coding: utf-8 -*-
#
# ode_toolbox_variable_printer.py
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

from pynestml.codegeneration.printers.variable_printer import VariablePrinter
from pynestml.meta_model.ast_variable import ASTVariable


class ODEToolboxVariablePrinter(VariablePrinter):
    r"""
    Convert into a format accepted by ODE-toolbox as input.
    """

    def print_variable(self, node: ASTVariable) -> str:
        """
        Print variable.
        :param node: the node to print
        :return: string representation
        """
        return node.get_complete_name().replace("$", "__DOLLAR")
