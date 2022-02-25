# -*- coding: utf-8 -*-
#
# python_standalone_reference_converter.py
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

from pynestml.codegeneration.base_reference_converter import BaseReferenceConverter
from pynestml.codegeneration.base_reference_converter import BaseReferenceConverter
from pynestml.codegeneration.reference_converter import ReferenceConverter
from pynestml.codegeneration.unit_converter import UnitConverter
from pynestml.meta_model.ast_arithmetic_operator import ASTArithmeticOperator
from pynestml.meta_model.ast_bit_operator import ASTBitOperator
from pynestml.meta_model.ast_comparison_operator import ASTComparisonOperator
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.meta_model.ast_logical_operator import ASTLogicalOperator
from pynestml.meta_model.ast_unary_operator import ASTUnaryOperator
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.meta_model.ast_external_variable import ASTExternalVariable
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.symbols.predefined_units import PredefinedUnits
from pynestml.symbols.predefined_variables import PredefinedVariables
from pynestml.symbols.symbol import SymbolKind
from pynestml.symbols.unit_type_symbol import UnitTypeSymbol
from pynestml.symbols.variable_symbol import BlockType
from pynestml.symbols.variable_symbol import VariableSymbol
from pynestml.utils.ast_utils import ASTUtils
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages
from pynestml.codegeneration.reference_converter import ReferenceConverter
from pynestml.meta_model.ast_external_variable import ASTExternalVariable
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.symbols.variable_symbol import BlockType
from pynestml.symbols.variable_symbol import VariableSymbol
from pynestml.utils.ast_utils import ASTUtils


class PythonStandaloneReferenceConverter(BaseReferenceConverter):
    r"""
    Convert to Python syntax.
    """

    def convert_unary_op(self, ast_unary_operator) -> str:
        """
        Returns the same string.
        :param ast_unary_operator: a single unary operator string.
        :type ast_unary_operator: ast_unary_operator
        :return: the same string
        :rtype: str
        """
        return str(ast_unary_operator) + '%s'

    def convert_name_reference(self, ast_variable, prefix='') -> str:
        """
        Returns the same string
        :param ast_variable: a single variable
        :type ast_variable: ASTVariable
        :return: the same string
        :rtype: str
        """
        return prefix + ast_variable.get_complete_name()

    def convert_function_call(self, function_call, prefix='') -> str:
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

    def convert_binary_op(self, ast_binary_operator) -> str:
        """
        Returns the same binary operator back.
        :param ast_binary_operator:  a single binary operator
        :type ast_binary_operator: str
        :return: the same binary operator
        :rtype: str
        """
        return '%s' + str(ast_binary_operator) + '%s'

    def convert_constant(self, constant_name: str) -> str:
        """
        Returns the same string back.
        :param constant_name: a constant name
        :return: the same string
        """
        if constant_name == 'true':
            return 'True'

        if constant_name == 'false':
            return 'False'

        return constant_name

    def convert_ternary_operator(self) -> str:
        """
        Converts the ternary operator to its initial kernel.
        :return: a string representation
        :rtype: str
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

    def print_origin(self, variable_symbol, prefix='') -> str:
        """
        Returns a prefix corresponding to the origin of the variable symbol.
        :param variable_symbol: a single variable symbol.
        :type variable_symbol: VariableSymbol
        :return: the corresponding prefix
        """
        assert isinstance(variable_symbol, VariableSymbol), \
            '(PyNestML.CodeGenerator.Printer) No or wrong type of variable symbol provided (%s)!' % type(
                variable_symbol)

        if prefix == '':
            prefix = 'self.'
        print("abc Printing " +prefix+ str(variable_symbol.name))

        if variable_symbol.block_type == BlockType.STATE:
            return prefix + 'S_.'

        if variable_symbol.block_type == BlockType.EQUATION:
            return prefix + 'S_.'

        if variable_symbol.block_type == BlockType.PARAMETERS:
            return prefix + 'P_.'

        if variable_symbol.block_type == BlockType.COMMON_PARAMETERS:
            return prefix + 'cp.'

        if variable_symbol.block_type == BlockType.INTERNALS:
            return prefix + 'V_.'

        if variable_symbol.block_type == BlockType.INPUT:
            return prefix + 'B_.'

        return ''

    def array_index(self, symbol) -> str:
        """
        Transforms the haded over symbol to a GSL processable format.
        :param symbol: a single variable symbol
        :type symbol: VariableSymbol
        :return: the corresponding string format
        :rtype: str
        """
        return 'State_.' + self.convert_to_cpp_name(symbol.get_symbol_name())

    def convert_name_reference(self, variable: ASTVariable, prefix='') -> str:
        """
        Converts a single variable to nest processable format.
        :param variable: a single variable.
        :type variable: ASTVariable
        :return: a nest processable format.
        """
        if isinstance(variable, ASTExternalVariable):
            _name = str(variable)
            if variable.get_alternate_name():
                # the disadvantage of this approach is that the time the value is to be obtained is not explicitly specified, so we will actually get the value at the end of the min_delay timestep
                return "((POST_NEURON_TYPE*)(__target))->get_" + variable.get_alternate_name() + "()"

            return "((POST_NEURON_TYPE*)(__target))->get_" + _name + "(_tr_t)"

        if variable.get_name() == PredefinedVariables.E_CONSTANT:
            return 'math.e'

        symbol = variable.get_scope().resolve_to_symbol(variable.get_complete_name(), SymbolKind.VARIABLE)
        if symbol is None:
            # test if variable name can be resolved to a type
            if PredefinedUnits.is_unit(variable.get_complete_name()):
                return str(UnitConverter.get_factor(PredefinedUnits.get_unit(variable.get_complete_name()).get_unit()))

            code, message = Messages.get_could_not_resolve(variable.get_name())
            Logger.log_message(log_level=LoggingLevel.ERROR, code=code, message=message,
                               error_position=variable.get_source_position())
            return ''

        if symbol.is_local():
            return variable.get_name() + ('[' + variable.get_vector_parameter() + ']' if symbol.has_vector_parameter() else '')

        if symbol.is_buffer():
            if isinstance(symbol.get_type_symbol(), UnitTypeSymbol):
                units_conversion_factor = UnitConverter.get_factor(symbol.get_type_symbol().unit.unit)
            else:
                units_conversion_factor = 1
            s = ""
            if not units_conversion_factor == 1:
                s += "(" + str(units_conversion_factor) + " * "
            s += self.print_origin(symbol, prefix=prefix) + self.buffer_value(symbol)
            if symbol.has_vector_parameter():
                s += '[' + variable.get_vector_parameter() + ']'
            if not units_conversion_factor == 1:
                s += ")"
            return s

        if symbol.is_inline_expression:
            return 'get_' + variable.get_name() + '()' + ('[i]' if symbol.has_vector_parameter() else '')

        if symbol.is_kernel():
            assert False, "Reference converter cannot print kernel; kernel should have been converted during code generation"

        if symbol.is_state():
            temp = ""
            temp += "self." + self.getter(symbol) + "()"
            temp += ('[' + variable.get_vector_parameter() + ']' if symbol.has_vector_parameter() else '')
            return temp

        variable_name = self.convert_to_cpp_name(variable.get_complete_name())
        if symbol.is_local():
            return variable_name + ('[i]' if symbol.has_vector_parameter() else '')

        if symbol.is_inline_expression:
            return 'get_' + variable_name + '()' + ('[i]' if symbol.has_vector_parameter() else '')

        return self.print_origin(symbol, prefix=prefix) + \
            self.name(symbol) + \
            ('[' + variable.get_vector_parameter() + ']' if symbol.has_vector_parameter() else '')

    def buffer_value(self, variable_symbol: VariableSymbol) -> str:
        """
        Converts for a handed over symbol the corresponding name of the buffer to a nest processable format.
        :param variable_symbol: a single variable symbol.
        :return: the corresponding representation as a string
        """
        return variable_symbol.get_symbol_name() + '_grid_sum_'
