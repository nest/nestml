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

from abc import ABCMeta, abstractmethod

from pynestml.codegeneration.printers.ast_printer import ASTPrinter
from pynestml.codegeneration.printers.variable_printer import VariablePrinter
from pynestml.meta_model.ast_function_call import ASTFunctionCall


class FunctionCallPrinter(ASTPrinter, metaclass=ABCMeta):
    r"""
    Converts fnuction calls to the executable platform dependent code.

    This class is used to transform only parts of the grammar and not NESTML as a whole.
    """

    @abstractmethod
    def print_function_call(self, node: ASTFunctionCall, prefix: str = ""):
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
