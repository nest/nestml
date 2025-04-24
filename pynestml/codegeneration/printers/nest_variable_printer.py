# -*- coding: utf-8 -*-
#
# nest_variable_printer.py
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

from __future__ import annotations

from typing import Dict, Optional

from pynestml.codegeneration.nest_code_generator_utils import NESTCodeGeneratorUtils
from pynestml.codegeneration.printers.cpp_variable_printer import CppVariablePrinter
from pynestml.codegeneration.printers.expression_printer import ExpressionPrinter
from pynestml.codegeneration.nest_unit_converter import NESTUnitConverter
from pynestml.meta_model.ast_external_variable import ASTExternalVariable
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.symbols.predefined_units import PredefinedUnits
from pynestml.symbols.predefined_variables import PredefinedVariables
from pynestml.symbols.symbol import SymbolKind
from pynestml.symbols.unit_type_symbol import UnitTypeSymbol
from pynestml.symbols.variable_symbol import BlockType
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages


class NESTVariablePrinter(CppVariablePrinter):
    r"""
    Variable printer for C++ syntax and the NEST API.
    """

    def __init__(self, expression_printer: ExpressionPrinter, with_origin: bool = True, with_vector_parameter: bool = True, enforce_getter: bool = True, variables_special_cases: Optional[Dict[str, str]] = None) -> None:
        super().__init__(expression_printer)
        self.with_origin = with_origin
        self.with_vector_parameter = with_vector_parameter
        self.enforce_getter = enforce_getter
        self.variables_special_cases = variables_special_cases
        self.cpp_variable_suffix = ""
        # self.postsynaptic_getter_string_ = "start->get_%s()"   # XXX: TODO: see https://github.com/nest/nestml/issues/1163
        # self.postsynaptic_getter_string_ = "((post_neuron_t*)(__target))->get_%s(t_hist_entry_ms)"
        self.postsynaptic_getter_string_ = "((post_neuron_t*)(__target))->get_%s(get_t())"

    def set_getter_string(self, s):
        self.postsynaptic_getter_string_ = s
        return ""

    def print_variable(self, variable: ASTVariable) -> str:
        """
        Converts a single variable to nest processable format.
        :param variable: a single variable.
        :return: a nest processable format.
        """
        assert isinstance(variable, ASTVariable)

        # print special cases such as synaptic delay variable
        if self.variables_special_cases and variable.get_name() in self.variables_special_cases.keys():
            return self.variables_special_cases[variable.get_name()]

        # print external variables (such as a variable in the synapse that needs to call the getter method on the postsynaptic partner)
        if isinstance(variable, ASTExternalVariable):
            _name = str(variable)
            if variable.get_alternate_name():
                if not variable._altscope:
                    # get the value from the postsynaptic partner continuous-time buffer (for post_connected_continuous_input_ports); this has been buffered in a local temp variable starting with "__"
                    return variable.get_alternate_name()

                # get the value from the postsynaptic partner (without time specified)
                # the disadvantage of this approach is that the time the value is to be obtained is not explicitly specified, so we will actually get the value at the end of the min_delay timestep
                return "((post_neuron_t*)(__target))->get_" + variable.get_alternate_name() + "()"

            # grab the value from the postsynaptic spiking history buffer
            return self.postsynaptic_getter_string_ % _name

        if variable.get_name() == PredefinedVariables.E_CONSTANT:
            return "numerics::e"    # from nest::

        if variable.get_name() == PredefinedVariables.PI_CONSTANT:
            return "numerics::pi"    # from nest::

        if variable.get_name() == PredefinedVariables.TIME_CONSTANT:
            return "get_t()"

        symbol = variable.get_scope().resolve_to_symbol(variable.get_complete_name(), SymbolKind.VARIABLE)

        if symbol is None:
            # test if variable name can be resolved to a type
            if PredefinedUnits.is_unit(variable.get_complete_name()):
                return str(NESTUnitConverter.get_factor(PredefinedUnits.get_unit(variable.get_complete_name()).get_unit()))

            code, message = Messages.get_could_not_resolve(variable.get_name())
            Logger.log_message(log_level=LoggingLevel.ERROR, code=code, message=message,
                               error_position=variable.get_source_position())
            return ""

        vector_param = ""
        if self.with_vector_parameter and symbol.has_vector_parameter():
            vector_param = "[" + self._expression_printer.print(variable.get_vector_parameter()) + "]"

        if symbol.is_buffer():
            if isinstance(symbol.get_type_symbol(), UnitTypeSymbol):
                units_conversion_factor = NESTUnitConverter.get_factor(symbol.get_type_symbol().unit.unit)
            else:
                units_conversion_factor = 1
            s = ""
            if not units_conversion_factor == 1:
                s += "(" + str(units_conversion_factor) + " * "
            if self.cpp_variable_suffix == "":
                s += "B_."
            s += self._print_buffer_value(variable)
            if not units_conversion_factor == 1:
                s += ")"
            return s

        if symbol.is_inline_expression:
            # there might not be a corresponding defined state variable; insist on calling the getter function
            if self.enforce_getter:
                return "get_" + self._print(variable, symbol, with_origin=False) + vector_param + "()" + self.cpp_variable_suffix
            # modification to not enforce getter function:
            else:
                return self._print(variable, symbol, with_origin=False) + self.cpp_variable_suffix

        assert not symbol.is_kernel(), "Cannot print kernel; kernel should have been converted during code generation"

        if symbol.is_state() or symbol.is_inline_expression:
            return self._print(variable, symbol, with_origin=self.with_origin) + vector_param + self.cpp_variable_suffix

        return self._print(variable, symbol, with_origin=self.with_origin) + vector_param + self.cpp_variable_suffix

    def _print_delay_variable(self, variable: ASTVariable) -> str:
        """
        Converts a delay variable to NEST processable format
        :param variable:
        :return:
        """
        symbol = variable.get_scope().resolve_to_symbol(variable.get_complete_name(), SymbolKind.VARIABLE)
        if symbol and symbol.is_state() and symbol.has_delay_parameter():
            return "get_delayed_" + variable.get_name() + "()"

        return ""

    def _print_buffer_value(self, variable: ASTVariable) -> str:
        """
        Converts for a handed over symbol the corresponding name of the buffer to a nest processable format.
        :param variable: a single variable symbol.
        :return: the corresponding representation as a string
        """
        variable_symbol = variable.get_scope().resolve_to_symbol(variable.get_complete_name(), SymbolKind.VARIABLE)
        if variable_symbol.is_spike_input_port():
            var_name = variable_symbol.get_symbol_name().upper()
            if variable.has_vector_parameter():
                if variable.get_vector_parameter().is_variable():
                    # the enum corresponding to the first input port in a vector of input ports will have the _0 suffixed to the enum's name.
                    var_name += "_0 + " + variable.get_vector_parameter().get_variable().get_name()
                else:
                    var_name += "_" + str(variable.get_vector_parameter())
            return "spike_inputs_grid_sum_[" + var_name + " - MIN_SPIKE_RECEPTOR]"

        if self.cpp_variable_suffix:
            return variable_symbol.get_symbol_name() + self.cpp_variable_suffix

        return variable_symbol.get_symbol_name() + '_grid_sum_'

    def _print(self, variable: ASTVariable, symbol, with_origin: bool = True) -> str:
        variable_name = CppVariablePrinter._print_cpp_name(variable.get_complete_name())

        if symbol.is_local():
            return variable_name

        if variable.is_delay_variable():
            return self._print_delay_variable(variable)

        if with_origin:
            return NESTCodeGeneratorUtils.print_symbol_origin(symbol, variable) % variable_name

        return variable_name
