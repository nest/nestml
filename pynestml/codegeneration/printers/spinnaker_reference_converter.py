# -*- coding: utf-8 -*-
#
# spinnaker_reference_converter.py
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

from pynestml.codegeneration.printers.cpp_reference_converter import CppReferenceConverter
from pynestml.codegeneration.printers.base_reference_converter import BaseReferenceConverter
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

class SpinnakerReferenceConverter(CppReferenceConverter):
    """
    Reference converter for the SpiNNaker target
    """
    def name(self, node: Union[VariableSymbol, ASTVariable]) -> str:
        return super().name(node)

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
            return 'neuron->this_h'

        if function_name == PredefinedFunctions.TIME_STEPS:
            raise Exception("time_steps() function not yet implemented")

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
            return 'send_spike(timer_count, time, neuron_index)'

        if function_name == PredefinedFunctions.PRINT:
            return 'std::cout << {!s}'

        if function_name == PredefinedFunctions.PRINTLN:
            return 'std::cout << {!s} << std::endl'

        if function_name == PredefinedFunctions.DELIVER_SPIKE:
            raise Exception("deliver_spike() function not yet implemented")

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
        if variable.get_name() == PredefinedVariables.E_CONSTANT:
            return "numerics::e"

        symbol = variable.get_scope().resolve_to_symbol(variable.get_complete_name(), SymbolKind.VARIABLE)
        if symbol is None:
            # test if variable name can be resolved to a type
            if PredefinedUnits.is_unit(variable.get_complete_name()):
                return str(UnitConverter.get_factor(PredefinedUnits.get_unit(variable.get_complete_name()).get_unit()))

            code, message = Messages.get_could_not_resolve(variable.get_name())
            Logger.log_message(log_level=LoggingLevel.ERROR, code=code, message=message,
                               error_position=variable.get_source_position())
            return ""

        vector_param = ""
        if symbol.has_vector_parameter():
            vector_param = "[" + variable.get_vector_parameter() + "]"

        # if symbol.is_local():
        #     return variable.get_name() + vector_param

        if symbol.is_buffer():
            if isinstance(symbol.get_type_symbol(), UnitTypeSymbol):
                units_conversion_factor = UnitConverter.get_factor(symbol.get_type_symbol().unit.unit)
            else:
                units_conversion_factor = 1
            s = ""
            if not units_conversion_factor == 1:
                s += "(" + str(units_conversion_factor) + " * "
            s += self.print_origin(symbol, prefix=prefix) + self.buffer_value(symbol)
            s += vector_param
            if not units_conversion_factor == 1:
                s += ")"
            return s

        if symbol.is_inline_expression:
            return self.getter(symbol) + "()" + vector_param

        assert not symbol.is_kernel(), "SpiNNaker reference converter cannot print kernel; kernel should have been " \
                                       "converted during code generation code generation "

        if symbol.is_state() or symbol.is_inline_expression:
            return self.getter(symbol) + "()" + vector_param

        variable_name = self.convert_to_cpp_name(variable.get_complete_name())
        if symbol.is_local():
            return variable_name + vector_param

        return self.print_origin(symbol, prefix=prefix) + \
            self.name(symbol) + vector_param


    def print_origin(self, variable_symbol: VariableSymbol, prefix: str = '') -> str:
        """
        Returns a prefix corresponding to the origin of the variable symbol.
        :param variable_symbol: a single variable symbol.
        :return: the corresponding prefix
        """
        
        return ""
