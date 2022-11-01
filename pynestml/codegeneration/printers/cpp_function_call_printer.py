# -*- coding: utf-8 -*-
#
# cpp_simple_expression_printer.py
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


class CppFunctionCallPrinter(FunctionCallPrinter):
    r"""
    Printer for ASTFunctionCall in C++ syntax.
    """

    def print_function_call(self, function_call: ASTFunctionCall, prefix: str = "") -> str:
        """Print a function call, including bracketed arguments list.

        Parameters
        ----------
        node
            The function call node to print.
        prefix
            Optional string that will be prefixed to the function call. For example, to refer to a function call in the class "node", use a prefix equal to "node." or "node->".

            Predefined functions will not be prefixed.

        Returns
        -------
        s
            The function call string.
        """
        function_name = self._print_function_call(function_call, prefix=prefix)
        if ASTUtils.needs_arguments(function_call):
            if function_call.get_name() == PredefinedFunctions.PRINT or function_call.get_name() == PredefinedFunctions.PRINTLN:
                return function_name.format(self._print_print_statement(function_call))

            return function_name.format(*self.print_function_call_argument_list(function_call, prefix=prefix))

        return function_name

    def _print_function_call(self, function_call: ASTFunctionCall, prefix: str = "") -> str:
        r"""
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
        function_name = function_call.get_name()

        if function_name == 'and':
            return '&&'

        if function_name == 'or':
            return '||'

        if function_name == PredefinedFunctions.CLIP:
            # the arguments of this function must be swapped and are therefore [v_max, v_min, v]
            return 'std::min({2!s}, std::max({1!s}, {0!s}))'

        if function_name == PredefinedFunctions.MAX:
            return 'std::max({!s}, {!s})'

        if function_name == PredefinedFunctions.MIN:
            return 'std::min({!s}, {!s})'

        if function_name == PredefinedFunctions.EXP:
            return 'std::exp({!s})'

        if function_name == PredefinedFunctions.LN:
            return 'std::log({!s})'

        if function_name == PredefinedFunctions.LOG10:
            return 'std::log10({!s})'

        if function_name == PredefinedFunctions.COSH:
            return 'std::cosh({!s})'

        if function_name == PredefinedFunctions.SINH:
            return 'std::sinh({!s})'

        if function_name == PredefinedFunctions.TANH:
            return 'std::tanh({!s})'

        if function_name == PredefinedFunctions.EXPM1:
            return 'numerics::expm1({!s})'

        if function_name == PredefinedFunctions.PRINT:
            return 'std::cout << {!s}'

        if function_name == PredefinedFunctions.PRINTLN:
            return 'std::cout << {!s} << std::endl'

        # suppress prefix for misc. predefined functions
        # check if function is "predefined" purely based on the name, as we don't have access to the function symbol here
        function_is_predefined = PredefinedFunctions.get_function(function_name)
        if function_is_predefined:
            prefix = ''

        if ASTUtils.needs_arguments(function_call):
            n_args = len(function_call.get_args())
            return prefix + function_name + '(' + ', '.join(['{!s}' for _ in range(n_args)]) + ')'

        return prefix + function_name + '()'

    def print_function_call_argument_list(self, function_call: ASTFunctionCall, prefix: str="") -> Tuple[str, ...]:
        ret = []

        for arg in function_call.get_args():
            ret.append(self.print_expression(arg, prefix=prefix))

        return tuple(ret)

    def _print_print_statement(self, function_call: ASTFunctionCall) -> str:
        r"""
        A wrapper function to convert arguments of a print or println functions
        :param function_call: print function call
        :return: the converted print string with corresponding variables, if any
        """
        stmt = function_call.get_args()[0].get_string()
        stmt = stmt[stmt.index('"') + 1: stmt.rindex('"')]  # Remove the double quotes from the string
        scope = function_call.get_scope()
        return self.__convert_print_statement_str(stmt, scope)

    def __convert_print_statement_str(self, stmt: str, scope: Scope) -> str:
        r"""
        Converts the string argument of the print or println function to NEST processable format
        Variables are resolved to NEST processable format and printed with physical units as mentioned in model, separated by a space

        .. code-block:: nestml

            print("Hello World")

        .. code-block:: C++

            std::cout << "Hello World";

        .. code-block:: nestml

            print("Membrane potential = {V_m}")

        .. code-block:: C++

            std::cout << "Membrane potential = " << V_m << " mV";

        :param stmt: argument to the print or println function
        :param scope: scope of the variables in the argument, if any
        :return: the converted string to NEST
        """
        pattern = re.compile(r'\{[a-zA-Z_][a-zA-Z0-9_]*\}')  # Match the variables enclosed within '{ }'
        match = pattern.search(stmt)
        if match:
            var_name = match.group(0)[match.group(0).find('{') + 1:match.group(0).find('}')]
            left, right = stmt.split(match.group(0), 1)  # Split on the first occurrence of a variable
            fun_left = (lambda l: self.__convert_print_statement_str(l, scope) + ' << ' if l else '')
            fun_right = (lambda r: ' << ' + self.__convert_print_statement_str(r, scope) if r else '')
            ast_var = ASTVariable(var_name, scope=scope)
            right = ' ' + self.__get_unit_name(ast_var) + right  # concatenate unit separated by a space with the right part of the string
            return fun_left(left) + self.print_variable(ast_var) + fun_right(right)

        return '"' + stmt + '"'  # format bare string in C++ (add double quotes)
