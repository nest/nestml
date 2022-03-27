# -*- coding: utf-8 -*-
#
# nestml_reference_converter.py
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

from pynestml.codegeneration.printers.reference_converter import ReferenceConverter
from pynestml.meta_model.ast_unary_operator import ASTUnaryOperator
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.utils.ast_utils import ASTUtils


class NestMLReferenceConverter(ReferenceConverter):
    """
    This converter preserves the initial NestML syntax.
    """

    def convert_unary_op(self, ast_unary_operator: ASTUnaryOperator) -> str:
        """
        Returns the same string.
        :param ast_unary_operator: a single unary operator string.
        :return: the same string
        """
        return str(ast_unary_operator) + '%s'

    def convert_name_reference(self, ast_variable: ASTVariable, prefix='') -> str:
        """
        Returns the same string
        :param ast_variable: a single variable
        :return: the same string
        """
        return prefix + ast_variable.get_complete_name()

    def convert_function_call(self, function_call: ASTFunctionCall, prefix: str= '') -> str:
        """Return the function call in NESTML syntax.

        Parameters
        ----------
        function_call
            The function call node to convert.
        prefix
            The prefix argument is not relevant for rendering NESTML syntax and will be ignored.

        Returns
        -------
        s
            The function call string in NESTML syntax.
        """
        result = function_call.get_name()
        if ASTUtils.needs_arguments(function_call):
            n_args = len(function_call.get_args())
            result += '(' + ', '.join(['{!s}' for _ in range(n_args)]) + ')'
        else:
            result += '()'
        return result

    def convert_binary_op(self, ast_binary_operator) -> str:
        """
        Returns the same binary operator back.
        :param ast_binary_operator:  a single binary operator
        :return: the same binary operator
        """
        return '%s' + str(ast_binary_operator) + '%s'

    def convert_constant(self, constant_name: str) -> str:
        """
        Returns the same string back.
        :param constant_name: a constant name
        :return: the same string
        """
        return constant_name

    def convert_ternary_operator(self) -> str:
        """
        Converts the ternary operator to its initial kernel.
        :return: a string representation
        """
        return '(' + '%s' + ')?(' + '%s' + '):(' + '%s' + ')'

    def convert_logical_operator(self, op) -> str:
        return str(op)

    def convert_arithmetic_operator(self, op) -> str:
        return str(op)

    def convert_encapsulated(self) -> str:
        return '(%s)'

    def convert_comparison_operator(self, op) -> str:
        return str(op)

    def convert_logical_not(self) -> str:
        return 'not'

    def convert_bit_operator(self, op) -> str:
        return str(op)
