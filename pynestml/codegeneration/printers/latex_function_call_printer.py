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

from typing import Optional, Tuple

import re

from pynestml.codegeneration.printers.function_call_printer import FunctionCallPrinter
from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_expression_node import ASTExpressionNode
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.symbol_table.scope import Scope
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.utils.ast_utils import ASTUtils
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_variable import ASTVariable


class LatexFunctionCallPrinter(FunctionCallPrinter):
    r"""
    Printer for ASTFunctionCall in LaTeX syntax.
    """

    def _print_function_call(self, node: ASTFunctionCall, prefix: str = '') -> str:
        """
        Converts a single handed over function call to C++ NEST API syntax.

        Parameters
        ----------
        function_call
            The function call node to convert.
        prefix
            Optional string that will be prefixed to the function call. For example, to refer to a function call in the class "node", use a prefix equal to "node." or "node->".

            Predefined functions will not be prefixed.

        Returns
        -------
        s
            The function call string in C++ syntax.
        """
        function_name = node.get_name()

        if function_name == PredefinedFunctions.TIME_RESOLUTION:
            # context dependent; we assume the template contains the necessary definitions
            return '\Delta{}t'

        if function_name == PredefinedFunctions.TIME_STEPS:
            return '\text{steps}'

        if function_name == PredefinedFunctions.RANDOM_NORMAL:
            return '\mathcal{N}({!s}, {!s}'

        if function_name == PredefinedFunctions.RANDOM_UNIFORM:
            return '\mathcal{U}({!s}, {!s}'

        if function_name == PredefinedFunctions.EMIT_SPIKE:
            return '\text{spike}'

        if function_name == PredefinedFunctions.DELIVER_SPIKE:
            return '\text{deliver\_spike}'

        return "\text{" + function_name + "}"

    def print_function_call(self, function_call: ASTFunctionCall, prefix: str = "") -> str:
        function_name = self._print_function_name(function_call, prefix)
        if ASTUtils.needs_arguments(function_call):
            return function_name % self._print_function_call_argument_list(function_call)

        return function_name

    def _print_function_call_argument_list(self, function_call: ASTFunctionCall) -> Tuple[str, ...]:
        ret = []
        for arg in function_call.get_args():
            ret.append(self.print_expression(arg))

        return tuple(ret)
