# -*- coding: utf-8 -*-
#
# python_function_call_printer.py
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

import re

from pynestml.codegeneration.printers.function_call_printer import FunctionCallPrinter
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.symbol_table.scope import Scope
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.utils.ast_utils import ASTUtils
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_variable import ASTVariable


class PythonFunctionCallPrinter(FunctionCallPrinter):
    r"""
    Printer for ASTFunctionCall in Python syntax.
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
            if function_call.get_name() == PredefinedFunctions.PRINT or function_call.get_name() == PredefinedFunctions.PRINTLN:
                return function_name.format(self._print_print_statement(function_call))

            return function_name.format(*self._print_function_call_argument_list(function_call))

        return function_name

    def _print_function_call_argument_list(self, function_call: ASTFunctionCall) -> Tuple[str, ...]:
        ret = []

        for arg in function_call.get_args():
            ret.append(self._expression_printer.print(arg))

        return tuple(ret)

    def _print_print_statement(self, function_call: ASTFunctionCall) -> str:
        r"""
        A wrapper function to convert arguments of a print or println functions
        :param function_call: print function call
        :return: the converted print string with corresponding variables, if any
        """
        stmt = function_call.get_args()[0].get_string()
        stmt = stmt[stmt.index("\"") + 1: stmt.rindex("\"")]  # Remove the double quotes from the string
        scope = function_call.get_scope()
        return self.__convert_print_statement_str(stmt, scope)

    def __convert_print_statement_str(self, stmt: str, scope: Scope) -> str:
        r"""
        Converts the string argument of the print or println function to Python format
        Variables are resolved to Python format and printed with physical units as mentioned in model, separated by a space

        .. code-block:: nestml

            println("Hello World")

        .. code-block:: Python

            print("Hello World")

        .. code-block:: nestml

            println("Membrane potential = {V_m}")

        .. code-block:: Python

            print("Membrane potential = " + str(V_m) + " mV")

        :param stmt: argument to the print or println function
        :param scope: scope of the variables in the argument, if any
        :return: the converted string
        """
        pattern = re.compile(r"\{[a-zA-Z_][a-zA-Z0-9_]*\}")  # Match the variables enclosed within "{ }"
        match = pattern.search(stmt)
        if match:
            var_name = match.group(0)[match.group(0).find("{") + 1:match.group(0).find("}")]
            left, right = stmt.split(match.group(0), 1)  # Split on the first occurrence of a variable
            fun_left = (lambda lhs: self.__convert_print_statement_str(lhs, scope) + " + " if lhs else "")
            fun_right = (lambda rhs: " + " + self.__convert_print_statement_str(rhs, scope) if rhs else "")
            ast_var = ASTVariable(var_name, scope=scope)
            right = " " + ASTUtils.get_unit_name(ast_var) + right  # concatenate unit separated by a space with the right part of the string
            return fun_left(left) + self._expression_printer.print(ast_var) + fun_right(right)

        return "\"" + stmt + "\""  # format bare string in Python (add double quotes)

    def _print_function_call_format_string(self, function_call: ASTFunctionCall) -> str:
        """
        Converts a single handed over function call to Python syntax.

        Parameters
        ----------
        function_call
            The function call node to convert.

        Returns
        -------
        s
            The function call string in Python syntax.
        """
        if function_call.get_name() == PredefinedFunctions.TIME_STEPS:
            return "steps({!s}, self._timestep)"

        if function_call.get_name() == PredefinedFunctions.TIME_RESOLUTION:
            return "self._timestep"

        if function_call.get_name() == PredefinedFunctions.EMIT_SPIKE:
            return "self.emit_spike(origin)"

        s = function_call.get_name()

        s += "("
        if ASTUtils.needs_arguments(function_call):
            n_args = len(function_call.get_args())
            s += ", ".join(["{!s}" for _ in range(n_args)])

        s += ")"

        return s
