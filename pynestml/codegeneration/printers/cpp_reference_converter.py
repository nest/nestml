# -*- coding: utf-8 -*-
#
# cpp_reference_converter.py
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

from typing import Union

from pynestml.codegeneration.printers.reference_converter import ReferenceConverter
from pynestml.meta_model.ast_arithmetic_operator import ASTArithmeticOperator
from pynestml.meta_model.ast_bit_operator import ASTBitOperator
from pynestml.meta_model.ast_comparison_operator import ASTComparisonOperator
from pynestml.meta_model.ast_logical_operator import ASTLogicalOperator
from pynestml.meta_model.ast_unary_operator import ASTUnaryOperator
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.symbols.variable_symbol import VariableSymbol


class CppReferenceConverter(ReferenceConverter):
    def convert_to_cpp_name(self, variable_name: str) -> str:
        """
        Converts a handed over name to the corresponding NEST/C++ naming guideline. This is chosen to be compatible with the naming strategy for ode-toolbox, such that the variable name in a NESTML statement like "G_ahp" += 1" will be converted into "G_ahp__d".

        :param variable_name: a single name.
        :return: a string representation
        """
        differential_order = variable_name.count("\"")
        if differential_order > 0:
            return variable_name.replace("\"", "").replace("$", "__DOLLAR") + "__" + "d" * differential_order

        return variable_name.replace("$", "__DOLLAR")

    def getter(self, variable_symbol: VariableSymbol) -> str:
        """
        Converts for a handed over symbol the corresponding name of the getter to a nest processable format.
        :param variable_symbol: a single variable symbol.
        :return: a string representation
        """
        return 'get_' + self.convert_to_cpp_name(variable_symbol.get_symbol_name())

    def setter(self, variable_symbol: VariableSymbol) -> str:
        """
        Converts for a handed over symbol the corresponding name of the setter to a nest processable format.
        :param variable_symbol: a single variable symbol.
        :return: a string representation
        """
        return 'set_' + self.convert_to_cpp_name(variable_symbol.get_symbol_name())

    def name(self, node: Union[VariableSymbol, ASTVariable]) -> str:
        """
        Returns for the handed over element the corresponding nest processable string.
        :param node: a single variable symbol or variable
        :return: a string representation
        """
        if isinstance(node, VariableSymbol):
            return self.convert_to_cpp_name(node.get_symbol_name())

        return self.convert_to_cpp_name(node.get_complete_name())

    def convert_constant(self, const: Union[str, float, int]) -> str:
        """
        Converts a single handed over constant.
        :param const: a constant as string, float or int.
        :return: a string representation
        """
        if const == 'inf':
            return 'std::numeric_limits<double_t>::infinity()'

        if const == 'true':
            return 'true'

        if const == 'false':
            return 'false'

        if isinstance(const, float) or isinstance(const, int):
            return str(const)

        return const

    def convert_unary_op(self, unary_operator: ASTUnaryOperator) -> str:
        """
        Converts a unary operator.
        :param unary_operator: an operator object
        :return: a string representation
        """
        if unary_operator.is_unary_plus:
            return '(' + '+' + '(%s)' + ')'

        if unary_operator.is_unary_minus:
            return '(' + '-' + '(%s)' + ')'

        if unary_operator.is_unary_tilde:
            return '(' + '~' + '(%s)' + ')'

        raise RuntimeError('Cannot determine unary operator!')

    def convert_encapsulated(self) -> str:
        """
        Converts the encapsulating parenthesis of an expression.
        :return: a string representation
        """
        return '(%s)'

    def convert_logical_not(self) -> str:
        """
        Converts a logical NOT operator.
        :return: a string representation
        """
        return '(' + '!' + '%s' + ')'

    def convert_logical_operator(self, op: ASTLogicalOperator) -> str:
        """
        Converts a logical operator.
        :param op: a logical operator object
        :return: a string representation
        """
        if op.is_logical_and:
            return '%s' + '&&' + '%s'

        if op.is_logical_or:
            return '%s' + '||' + '%s'

        raise RuntimeError('Cannot determine logical operator!')

    def convert_comparison_operator(self, op: ASTComparisonOperator) -> str:
        """
        Converts a comparison operator.
        :param op: a comparison operator object
        :return: a string representation
        """
        if op.is_lt:
            return '%s' + '<' + '%s'

        if op.is_le:
            return '%s' + '<=' + '%s'

        if op.is_eq:
            return '%s' + '==' + '%s'

        if op.is_ne or op.is_ne2:
            return '%s' + '!=' + '%s'

        if op.is_ge:
            return '%s' + '>=' + '%s'

        if op.is_gt:
            return '%s' + '>' + '%s'

        raise RuntimeError('Cannot determine comparison operator!')

    def convert_bit_operator(self, op: ASTBitOperator) -> str:
        """
        Converts a bit operator in NEST syntax.
        :param op: a bit operator object
        :return: a string representation
        """
        if op.is_bit_shift_left:
            return '%s' + '<<' '%s'

        if op.is_bit_shift_right:
            return '%s' + '>>' + '%s'

        if op.is_bit_and:
            return '%s' + '&' + '%s'

        if op.is_bit_or:
            return '%s' + '|' + '%s'

        if op.is_bit_xor:
            return '%s' + '^' + '%s'

        raise RuntimeError('Cannot determine bit operator!')

    def convert_arithmetic_operator(self, op: ASTArithmeticOperator) -> str:
        """
        Converts an arithmetic operator.
        :param op: an arithmetic operator object
        :return: a string representation
        """
        if op.is_plus_op:
            return '%s' + ' + ' + '%s'

        if op.is_minus_op:
            return '%s' + ' - ' + '%s'

        if op.is_times_op:
            return '%s' + ' * ' + '%s'

        if op.is_div_op:
            return '%s' + ' / ' + '%s'

        if op.is_modulo_op:
            return '%s' + ' %% ' + '%s'

        if op.is_pow_op:
            return 'pow' + '(%s, %s)'

        raise RuntimeError('Cannot determine arithmetic operator!')

    def convert_ternary_operator(self) -> str:
        """
        Converts a ternary operator.
        :return: a string representation
        """
        return '(' + '%s' + ') ? (' + '%s' + ') : (' + '%s' + ')'

    def convert_binary_op(self, binary_operator: Union[ASTArithmeticOperator, ASTBitOperator, ASTComparisonOperator, ASTLogicalOperator]) -> str:
        """
        Converts a binary operator.
        :param binary_operator: a binary operator object
        :return: a string representation
        """
        if isinstance(binary_operator, ASTArithmeticOperator):
            return self.convert_arithmetic_operator(binary_operator)

        if isinstance(binary_operator, ASTBitOperator):
            return self.convert_bit_operator(binary_operator)

        if isinstance(binary_operator, ASTComparisonOperator):
            return self.convert_comparison_operator(binary_operator)

        if isinstance(binary_operator, ASTLogicalOperator):
            return self.convert_logical_operator(binary_operator)

        raise RuntimeError('Cannot determine binary operator!')

    def buffer_value(self, variable_symbol: VariableSymbol) -> str:
        """
        Converts for a handed over symbol the corresponding name of the buffer to a nest processable format.
        :param variable_symbol: a single variable symbol.
        :return: the corresponding representation as a string
        """
        return variable_symbol.get_symbol_name() + '_grid_sum_'
