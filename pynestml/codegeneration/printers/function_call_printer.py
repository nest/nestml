# -*- coding: utf-8 -*-
#
# function_call_printer.py
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

from typing import TYPE_CHECKING, Optional, Type

from abc import ABCMeta, abstractmethod

from pynestml.codegeneration.printers.ast_printer import ASTPrinter
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.meta_model.ast_node import ASTNode


if TYPE_CHECKING:
    from pynestml.codegeneration.printers.expression_printer import ExpressionPrinter    # avoided circular import by using ``from __future__ import annotations``
    from pynestml.codegeneration.unit_converter import UnitConverter


class FunctionCallPrinter(ASTPrinter, metaclass=ABCMeta):
    r"""
    Converts function calls to the executable platform dependent code.

    This class is used to transform only parts of the grammar and not NESTML as a whole.

    The ``unit_converter`` determines the system of physical units of the target platform; it is used, for instance, to print the unit of a variable in a ``print()`` statement. By default, the units used by NEST are assumed.
    """

    def __init__(self, expression_printer: ExpressionPrinter, unit_converter: Optional[Type[UnitConverter]] = None):
        self._expression_printer = expression_printer
        if unit_converter is None:
            from pynestml.codegeneration.nest_unit_converter import NESTUnitConverter
            unit_converter = NESTUnitConverter
        self._unit_converter = unit_converter

    @abstractmethod
    def print_function_call(self, node: ASTFunctionCall) -> str:
        """Print a function call.

        Parameters
        ----------
        node
            The node to print.

        Returns
        -------
        s
            The string representation.
        """
        return ""

    def print(self, node: ASTNode) -> str:
        assert isinstance(node, ASTFunctionCall)
        return self.print_function_call(node)
