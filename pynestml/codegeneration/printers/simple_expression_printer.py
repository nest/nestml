# -*- coding: utf-8 -*-
#
# simple_expression_printer.py
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

from typing import TYPE_CHECKING, Optional

from abc import ABCMeta, abstractmethod

from pynestml.codegeneration.printers.ast_printer import ASTPrinter
from pynestml.codegeneration.printers.constant_printer import ConstantPrinter
from pynestml.codegeneration.printers.function_call_printer import FunctionCallPrinter
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression


if TYPE_CHECKING:
    from pynestml.codegeneration.printers.variable_printer import VariablePrinter


class SimpleExpressionPrinter(ASTPrinter, metaclass=ABCMeta):
    r"""
    Converts expressions to the executable platform dependent code.

    This class is used to transform only parts of the grammar and not NESTML as a whole.
    """

    def __init__(self,
                 variable_printer: VariablePrinter,
                 constant_printer: ConstantPrinter,
                 function_call_printer: FunctionCallPrinter):
        self._variable_printer = variable_printer
        self._constant_printer = constant_printer
        self._function_call_printer = function_call_printer

    def get_implicit_conversion_factor(self, node: ASTNode) -> Optional[float]:
        r"""
        Gives the implicit conversion factor of the given node (see ASTNode.set_implicit_conversion_factor()) that applies to the values as this printer prints them.

        :param node: an expression node
        :return: the factor, or None if the node has no factor
        """
        return node.get_implicit_conversion_factor()

    @abstractmethod
    def print_simple_expression(self, node: ASTSimpleExpression) -> str:
        """Print a simple expression.

        Parameters
        ----------
        node
            The expression node to print.

        Returns
        -------
        s
            The expression string.
        """
        raise Exception("Cannot call abstract method")
