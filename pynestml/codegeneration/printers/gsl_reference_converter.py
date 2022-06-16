# -*- coding: utf-8 -*-
#
# gsl_reference_converter.py
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

from pynestml.codegeneration.printers.cpp_reference_converter import CppReferenceConverter
from pynestml.codegeneration.printers.unit_converter import UnitConverter
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.symbols.predefined_units import PredefinedUnits
from pynestml.symbols.predefined_variables import PredefinedVariables
from pynestml.symbols.symbol import SymbolKind
from pynestml.symbols.unit_type_symbol import UnitTypeSymbol
from pynestml.symbols.variable_symbol import VariableSymbol
from pynestml.utils.ast_utils import ASTUtils
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages


class GSLReferenceConverter(CppReferenceConverter):
    r"""
    Reference converter for C++ syntax and using the GSL (GNU Scientific Library) API.
    """
    maximal_exponent = 10.

    def __init__(self, is_upper_bound=False):
        """
        Standard constructor.
        :param is_upper_bound: Indicates whether an upper bound for the exponent shall be used.
        :type is_upper_bound: bool
        """
        self.is_upper_bound = is_upper_bound

    def convert_name_reference(self, variable: ASTVariable, prefix: str = '') -> str:
        """
        Converts a single name reference to a gsl processable format.
        :param ast_variable: a single variable
        :return: a gsl processable format of the variable
        """

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

        if symbol.is_state():
            return self.name(symbol)

        if symbol.is_buffer():
            if isinstance(symbol.get_type_symbol(), UnitTypeSymbol):
                units_conversion_factor = UnitConverter.get_factor(symbol.get_type_symbol().unit.unit)
            else:
                units_conversion_factor = 1
            s = ""
            if not units_conversion_factor == 1:
                s += "(" + str(units_conversion_factor) + " * "
            s += prefix + 'B_.' + self.buffer_value(symbol)
            if symbol.has_vector_parameter():
                s += '[i]'
            if not units_conversion_factor == 1:
                s += ")"
            return s

        variable_name = self.convert_to_cpp_name(variable.get_name())

        if symbol.is_local() or symbol.is_inline_expression:
            return variable_name

        if symbol.has_vector_parameter():
            return prefix + 'get_' + variable_name + '()[i]'

        return prefix + 'get_' + variable_name + '()'

    def convert_function_call(self, function_call: ASTFunctionCall, prefix: str = '') -> str:
        """Convert a single function call to C++ GSL API syntax.

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

        if function_name == PredefinedFunctions.TIME_RESOLUTION:
            # context dependent; we assume the template contains the necessary definitions
            return '__resolution'

        if function_name == PredefinedFunctions.TIME_STEPS:
            return 'nest::Time(nest::Time::ms((double) {!s})).get_steps()'

        if function_name == PredefinedFunctions.MAX:
            return 'std::max({!s}, {!s})'

        if function_name == PredefinedFunctions.MIN:
            return 'std::min({!s}, {!s})'

        if function_name == PredefinedFunctions.CLIP:
            # warning: the arguments of this function have been swapped and
            # are therefore [v_max, v_min, v], hence its structure
            return 'std::min({2!s}, std::max({1!s}, {0!s}))'

        if function_name == PredefinedFunctions.EXP:
            if self.is_upper_bound:
                return 'std::exp(std::min({!s},' + str(self.maximal_exponent) + '))'
            else:
                return 'std::exp({!s})'

        if function_name == PredefinedFunctions.COSH:
            if self.is_upper_bound:
                return 'std::cosh(std::min(std::abs({!s}),' + str(self.maximal_exponent) + '))'
            else:
                return 'std::cosh({!s})'

        if function_name == PredefinedFunctions.SINH:
            if self.is_upper_bound:
                return 'std::sinh(({!s} > 0 ? 1 : -1)*std::min(std::abs({!s}),' + str(self.maximal_exponent) + '))'
            else:
                return 'std::sinh({!s})'

        if function_name == PredefinedFunctions.TANH:
            return 'std::tanh({!s})'

        if function_name == PredefinedFunctions.LN:
            return 'std::log({!s})'

        if function_name == PredefinedFunctions.LOG10:
            return 'std::log10({!s})'

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

        if function_name == PredefinedFunctions.DELIVER_SPIKE:
            return '''set_delay( {1!s} );
const long __delay_steps = nest::Time::delay_ms_to_steps( get_delay() );
set_delay_steps(__delay_steps);
e.set_receiver( *__target );
e.set_weight( {0!s} );
// use accessor functions (inherited from Connection< >) to obtain delay in steps and rport
e.set_delay_steps( get_delay_steps() );
e.set_rport( get_rport() );
e();'''

        # suppress prefix for misc. predefined functions
        # check if function is "predefined" purely based on the name, as we don't have access to the function symbol here
        function_is_predefined = PredefinedFunctions.get_function(function_name)
        if function_is_predefined:
            prefix = ''

        if ASTUtils.needs_arguments(function_call):
            n_args = len(function_call.get_args())
            return prefix + function_name + '(' + ', '.join(['{!s}' for _ in range(n_args)]) + ')'

        return prefix + function_name + '()'

    def array_index(self, symbol: VariableSymbol) -> str:
        """
        Transforms the haded over symbol to a GSL processable format.
        :param symbol: a single variable symbol
        :return: the corresponding string format
        """
        return 'State_::' + self.convert_to_cpp_name(symbol.get_symbol_name())

    def name(self, symbol: VariableSymbol) -> str:
        """
        Transforms the given symbol to a format that can be processed by GSL.
        :param symbol: a single variable symbol
        :return: the corresponding string format
        """
        if symbol.is_state() and not symbol.is_inline_expression:
            return 'ode_state[State_::' + self.convert_to_cpp_name(symbol.get_symbol_name()) + ']'

        return super().name(symbol)
