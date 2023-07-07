# -*- coding: utf-8 -*-
#
# variable_printer.py
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

from abc import ABCMeta, abstractmethod

from pynestml.codegeneration.printers.ast_printer import ASTPrinter
from pynestml.codegeneration.printers.expression_printer import ExpressionPrinter
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.meta_model.ast_node import ASTNode


class VariablePrinter(ASTPrinter, metaclass=ABCMeta):
    r"""
    Converts variables to the executable platform dependent code.

    This class is used to transform only parts of the grammar and not NESTML as a whole.
    """

    def __init__(self, expression_printer: ExpressionPrinter):
        self._expression_printer = expression_printer
        self.array_index = "0"
        self.print_as_arrays = False

    def set_array_index(self, index):
        self.array_index = index

    def array_printing_toggle(self, array_printing=None):
        if array_printing is None:
            self.print_as_arrays = not self.print_as_arrays
        else:
            self.print_as_arrays = array_printing

    def print(self, node: ASTNode) -> str:
        assert isinstance(node, ASTVariable)

        return self.print_variable(node)

    @abstractmethod
    def print_variable(self, node: ASTVariable) -> str:
        """Print a variable.

        Parameters
        ----------
        node
            The node to print.

        Returns
        -------
        s
            The string representation.
        """
        raise
