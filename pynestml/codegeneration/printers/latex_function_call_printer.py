# -*- coding: utf-8 -*-
#
# latex_function_call_printer.py
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
from pynestml.meta_model.ast_node import ASTNode
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.utils.ast_utils import ASTUtils


class LatexFunctionCallPrinter(FunctionCallPrinter):
    r"""
    Printer for ASTFunctionCall in LaTeX syntax.
    """

    def print(self, node: ASTNode) -> str:
        assert isinstance(node, ASTFunctionCall)

        return self.print_function_call(node)

    def _print_function_call(self, node: ASTFunctionCall) -> str:
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
        function_name = node.get_name()

        if function_name == PredefinedFunctions.TIME_RESOLUTION:
            # context dependent; we assume the template contains the necessary definitions
            return r'\Delta{}t'

        if function_name == PredefinedFunctions.TIME_STEPS:
            return r'\text{steps}'

        if function_name == PredefinedFunctions.RANDOM_NORMAL:
            return r'\mathcal{N}({!s}, {!s}'

        if function_name == PredefinedFunctions.RANDOM_UNIFORM:
            return r'\mathcal{U}({!s}, {!s}'

        if function_name == PredefinedFunctions.EMIT_SPIKE:
            return r'\text{spike}'

        if function_name == PredefinedFunctions.DELIVER_SPIKE:
            return r'\text{deliver\_spike}'

        return r"\text{" + function_name + r"}"

    def print_function_call(self, function_call: ASTFunctionCall) -> str:
        result = self._print_function_call(function_call)

        if ASTUtils.needs_arguments(function_call):
            n_args = len(function_call.get_args())
            result += '(' + ', '.join(['%s' for _ in range(n_args)]) + ')'
        else:
            result += '()'

        return result % self._print_function_call_argument_list(function_call)

    def _print_function_call_argument_list(self, function_call: ASTFunctionCall) -> Tuple[str, ...]:
        ret = []
        for arg in function_call.get_args():
            ret.append(self._expression_printer.print(arg))

        return tuple(ret)
