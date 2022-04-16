# -*- coding: utf-8 -*-
#
# expression_printer.py
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

from abc import ABCMeta, abstractmethod

from pynestml.codegeneration.printers.reference_converter import ReferenceConverter
from pynestml.meta_model.ast_expression_node import ASTExpressionNode


class ExpressionPrinter(metaclass=ABCMeta):
    r"""
    Converts expressions to the executable platform dependent code.

    This class is used to transform only parts of the grammar and not NESTML as a whole.
    """

    def __init__(self, reference_converter: ReferenceConverter):
        self.reference_converter = reference_converter

    @abstractmethod
    def print_expression(self, node: ASTExpressionNode, prefix: str = ""):
        """Print an expression.

        Parameters
        ----------
        node : ASTExpressionNode
            The expression node to print.
        prefix : str
            *See documentation for the function print_function_call().*

        Returns
        -------
        s : str
            The expression string.
        """
        pass
