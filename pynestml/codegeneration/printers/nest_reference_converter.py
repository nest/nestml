# -*- coding: utf-8 -*-
#
# nest_reference_converter.py
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

import re

from pynestml.codegeneration.printers.cpp_reference_converter import CppReferenceConverter
from pynestml.codegeneration.printers.unit_converter import UnitConverter
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.meta_model.ast_external_variable import ASTExternalVariable
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.symbol_table.scope import Scope
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


class NESTReferenceConverter(CppReferenceConverter):
    r"""
    Reference converter for C++ syntax and using the NEST API.
    """

    def convert_function_call(self, function_call: ASTFunctionCall, prefix: str = '') -> str:
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
        function_name = function_call.get_name()

        if function_name == 'and':
            return '&&'

        if function_name == 'or':
            return '||'

        if function_name == PredefinedFunctions.TIME_RESOLUTION:
            # context dependent; we assume the template contains the necessary definitions
            return '__resolution'

        if function_name == PredefinedFunctions.TIME_STEPS:
            return 'nest::Time(nest::Time::ms((double) ({!s}))).get_steps()'

        if function_name == PredefinedFunctions.CLIP:
            # warning: the arguments of this function must swapped and
            # are therefore [v_max, v_min, v], hence its structure
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

        if function_name == PredefinedFunctions.RANDOM_NORMAL:
            return '(({!s}) + ({!s}) * ' + prefix + 'normal_dev_( nest::get_vp_specific_rng( ' + prefix + 'get_thread() ) ))'

        if function_name == PredefinedFunctions.RANDOM_UNIFORM:
            return '(({!s}) + ({!s}) * nest::get_vp_specific_rng( ' + prefix + 'get_thread() )->drand())'

        if function_name == PredefinedFunctions.EMIT_SPIKE:
            return 'set_spiketime(nest::Time::step(origin.get_steps()+lag+1));\n' \
                   'nest::SpikeEvent se;\n' \
                   'nest::kernel().event_delivery_manager.send(*this, se, lag)'

        if function_name == PredefinedFunctions.PRINT:
            return 'std::cout << {!s}'

        if function_name == PredefinedFunctions.PRINTLN:
            return 'std::cout << {!s} << std::endl'

        if function_name == PredefinedFunctions.DELIVER_SPIKE:
            return '''
        set_delay( {1!s} );
        const long __delay_steps = nest::Time::delay_ms_to_steps( get_delay() );
        set_delay_steps(__delay_steps);
        e.set_receiver( *__target );
  e.set_weight( {0!s} );
  // use accessor functions (inherited from Connection< >) to obtain delay in steps and rport
  e.set_delay_steps( get_delay_steps() );
  e.set_rport( get_rport() );
e();
'''

        # suppress prefix for misc. predefined functions
        # check if function is "predefined" purely based on the name, as we don't have access to the function symbol here
        function_is_predefined = PredefinedFunctions.get_function(function_name)
        if function_is_predefined:
            prefix = ''

        if ASTUtils.needs_arguments(function_call):
            n_args = len(function_call.get_args())
            return prefix + function_name + '(' + ', '.join(['{!s}' for _ in range(n_args)]) + ')'
        return prefix + function_name + '()'

    def convert_name_reference(self, variable: ASTVariable, prefix: str = '') -> str:
        """
        Converts a single variable to nest processable format.
        :param variable: a single variable.
        :return: a nest processable format.
        """
        if isinstance(variable, ASTExternalVariable):
            _name = str(variable)
            if variable.get_alternate_name():
                # the disadvantage of this approach is that the time the value is to be obtained is not explicitly specified, so we will actually get the value at the end of the min_delay timestep
                return "((POST_NEURON_TYPE*)(__target))->get_" + variable.get_alternate_name() + "()"

            return "((POST_NEURON_TYPE*)(__target))->get_" + _name + "(_tr_t)"

        if variable.get_name() == PredefinedVariables.E_CONSTANT:
            return 'numerics::e'

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

        assert not symbol.is_kernel(), "NEST reference converter cannot print kernel; kernel should have been converted during code generation"

        if symbol.is_state():
            temp = ""
            temp += self.getter(symbol) + "()"
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

    def __get_unit_name(self, variable: ASTVariable):
        assert variable.get_scope() is not None, "Undeclared variable: " + variable.get_complete_name()

        variable_name = self.convert_to_cpp_name(variable.get_complete_name())
        symbol = variable.get_scope().resolve_to_symbol(variable_name, SymbolKind.VARIABLE)
        if isinstance(symbol.get_type_symbol(), UnitTypeSymbol):
            return symbol.get_type_symbol().unit.unit.to_string()

        return ''

    def convert_print_statement(self, function_call: ASTFunctionCall) -> str:
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
            return fun_left(left) + self.convert_name_reference(ast_var) + fun_right(right)

        return '"' + stmt + '"'  # format bare string in C++ (add double quotes)

    def print_origin(self, variable_symbol: VariableSymbol, prefix: str = '') -> str:
        """
        Returns a prefix corresponding to the origin of the variable symbol.
        :param variable_symbol: a single variable symbol.
        :return: the corresponding prefix
        """
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
