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

from pynestml.codegeneration.i_reference_converter import IReferenceConverter
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.utils.ast_utils import ASTUtils


class NestMLReferenceConverter(IReferenceConverter):
    """
    This converter preserves the initial NestML syntax.
    """

    def convert_unary_op(self, ast_unary_operator):
        """
        Returns the same string.
        :param ast_unary_operator: a single unary operator string.
        :type ast_unary_operator: ast_unary_operator
        :return: the same string
        :rtype: str
        """
        return str(ast_unary_operator) + '%s'

    def convert_name_reference(self, ast_variable, prefix=''):
        """
        Returns the same string
        :param ast_variable: a single variable
        :type ast_variable: ASTVariable
        :return: the same string
        :rtype: str
        """
        return prefix + ast_variable.get_complete_name()

    def convert_function_call(self, function_call, prefix=''):
        """Return the function call in NESTML syntax.

        Parameters
        ----------
        function_call : ASTFunctionCall
            The function call node to convert.
        prefix : str
            The prefix argument is not relevant for rendering NESTML syntax and will be ignored.

        Returns
        -------
        s : str
            The function call string in NESTML syntax.
        """
        result = function_call.get_name()
        if ASTUtils.needs_arguments(function_call):
            n_args = len(function_call.get_args())
            result += '(' + ', '.join(['{!s}' for _ in range(n_args)]) + ')'
        else:
            result += '()'
        return result

    def convert_binary_op(self, ast_binary_operator):
        """
        Returns the same binary operator back.
        :param ast_binary_operator:  a single binary operator
        :type ast_binary_operator: str
        :return: the same binary operator
        :rtype: str
        """
        return '%s' + str(ast_binary_operator) + '%s'

    def convert_constant(self, constant_name):
        """
        Returns the same string back.
        :param constant_name: a constant name
        :type constant_name: str
        :return: the same string
        :rtype: str
        """
        return constant_name

    def convert_ternary_operator(self):
        """
        Converts the ternary operator to its initial kernel.
        :return: a string representation
        :rtype: str
        """
        return '(' + '%s' + ')?(' + '%s' + '):(' + '%s' + ')'

    def convert_logical_operator(self, op):
        return str(op)

    def convert_arithmetic_operator(self, op):
        return str(op)

    def convert_encapsulated(self):
        return '(%s)'

    def convert_comparison_operator(self, op):
        return str(op)

    def convert_logical_not(self):
        return 'not'

    def convert_bit_operator(self, op):
        return str(op)
