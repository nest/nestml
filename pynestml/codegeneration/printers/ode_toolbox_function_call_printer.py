# -*- coding: utf-8 -*-
#
# ode_toolbox_function_call_printer.py
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

from typing import Tuple

from pynestml.codegeneration.printers.function_call_printer import FunctionCallPrinter
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.utils.ast_utils import ASTUtils
from pynestml.meta_model.ast_node import ASTNode


class ODEToolboxFunctionCallPrinter(FunctionCallPrinter):
    r"""
    Printer for ASTFunctionCall in sympy syntax.
    """

    def print(self, node: ASTNode) -> str:
        assert isinstance(node, ASTFunctionCall)

        return self.print_function_call(node)

    def print_function_call(self, function_call: ASTFunctionCall) -> str:
        """Print a function call, including bracketed arguments list.

        Parameters
        ----------
        node
            The function call node to print.

        Returns
        -------
        s
            The function call string.
        """
        assert isinstance(function_call, ASTFunctionCall)

        function_name = self._print_function_call_format_string(function_call)
        if ASTUtils.needs_arguments(function_call):
            return function_name.format(*self._print_function_call_argument_list(function_call))

        return function_name

    def _print_function_call_format_string(self, function_call: ASTFunctionCall) -> str:
        r"""
        Converts a single handed over function call to C++ NEST API syntax.

        Parameters
        ----------
        function_call
            The function call node to convert.

        Returns
        -------
        s
            The function call string in C++ syntax.
        """
        function_name = function_call.get_name()

        if function_name == PredefinedFunctions.CLIP:
            # the arguments of this function must be swapped and are therefore [v_max, v_min, v]
            return 'min({2!s}, max({1!s}, {0!s}))'

        if function_name == PredefinedFunctions.MAX:
            return 'max({!s}, {!s})'

        if function_name == PredefinedFunctions.MIN:
            return 'min({!s}, {!s})'

        if function_name == PredefinedFunctions.EXP:
            return 'exp({!s})'

        if function_name == PredefinedFunctions.LN:
            return 'log({!s})'

        if function_name == PredefinedFunctions.LOG10:
            return 'log10({!s})'

        if function_name == PredefinedFunctions.COSH:
            return 'cosh({!s})'

        if function_name == PredefinedFunctions.SINH:
            return 'sinh({!s})'

        if function_name == PredefinedFunctions.TANH:
            return 'tanh({!s})'

        if function_name == PredefinedFunctions.ERF:
            return 'erf({!s})'

        if function_name == PredefinedFunctions.ERFC:
            return 'erfc({!s})'

        if function_name == PredefinedFunctions.EXPM1:
            return 'expm1({!s})'

        if function_name == PredefinedFunctions.POW:
            return '{!s}**{!s}'

        if ASTUtils.needs_arguments(function_call):
            n_args = len(function_call.get_args())
            return function_name + '(' + ', '.join(['{!s}' for _ in range(n_args)]) + ')'

        return function_name + '()'

    def _print_function_call_argument_list(self, function_call: ASTFunctionCall) -> Tuple[str, ...]:
        ret = []

        for arg in function_call.get_args():
            ret.append(self._expression_printer.print(arg))

        return tuple(ret)
