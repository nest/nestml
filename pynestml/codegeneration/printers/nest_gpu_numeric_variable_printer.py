# -*- coding: utf-8 -*-
#
# nest_gpu_numeric_variable_printer.py
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

from pynestml.codegeneration.nest_unit_converter import NESTUnitConverter
from pynestml.codegeneration.printers.cpp_variable_printer import CppVariablePrinter
from pynestml.codegeneration.printers.expression_printer import ExpressionPrinter
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.symbols.predefined_units import PredefinedUnits
from pynestml.symbols.predefined_variables import PredefinedVariables
from pynestml.symbols.symbol import SymbolKind
from pynestml.symbols.unit_type_symbol import UnitTypeSymbol
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages


class NESTGPUNumericVariablePrinter(CppVariablePrinter):
    """
    Variable printer for numeric (RK5) solver syntax for the NEST-GPU target
    """
    
    def __init__(self, expression_printer: ExpressionPrinter, with_origin: bool = True, with_vector_parameter: bool = True) -> None:
        super().__init__(expression_printer)
        self.with_origin = with_origin
        self.with_vector_parameter = with_vector_parameter

    def print_variable(self, variable: ASTVariable) -> str:
        """
        Converts a single name reference to a format that supports APIs from RK5 numeric solver in NEST-GPU
        """
        assert isinstance(variable, ASTVariable)

        if variable.get_name() == PredefinedVariables.E_CONSTANT:
            return "M_E"
        
        symbol = variable.get_scope().resolve_to_symbol(variable.get_complete_name(), SymbolKind.VARIABLE)
        if symbol is None:
            # test if variable name can be resolved to a type
            if PredefinedUnits.is_unit(variable.get_complete_name()):
                return str(NESTUnitConverter.get_factor(PredefinedUnits.get_unit(variable.get_complete_name()).get_unit()))

            code, message = Messages.get_could_not_resolve(variable.get_name())
            Logger.log_message(log_level=LoggingLevel.ERROR, code=code, message=message,
                               error_position=variable.get_source_position())
            return ""

        if symbol.is_buffer():
            if isinstance(symbol.get_type_symbol(), UnitTypeSymbol):
                units_conversion_factor = NESTUnitConverter.get_factor(symbol.get_type_symbol().unit.unit)
            else:
                units_conversion_factor = 1
            s = ""
            if not units_conversion_factor == 1:
                s += "(" + str(units_conversion_factor) + " * "
            s += self._print(variable, symbol, with_origin=self.with_origin)
            if not units_conversion_factor == 1:
                s += ")"
            return s

        if symbol.is_inline_expression:
            # there might not be a corresponding defined state variable; insist on calling the getter function
            return "get_" + self._print(variable, symbol, with_origin=False) + "()"

        assert not symbol.is_kernel(), "Cannot print kernel; kernel should have been converted during code generation"

        if symbol.is_state() or symbol.is_inline_expression:
            return self._print(variable, symbol, with_origin=self.with_origin)

        return self._print(variable, symbol, with_origin=self.with_origin)

    def _print(self, variable: ASTVariable, symbol, with_origin: bool = True) -> str:
        var_cpp_name = CppVariablePrinter._print_cpp_name(variable.get_complete_name())

        if symbol.is_local():
            return var_cpp_name
        
        if symbol.is_state() and not symbol.is_inline_expression:
            return "y[i_" + var_cpp_name + "]"
        
        if symbol.is_parameters() or symbol.is_internals() or symbol.is_continuous_input_port():
            return "param[i_" + var_cpp_name + "]"
        
        if symbol.is_spike_input_port():
            return "y[N_SCAL_VAR + i_" + symbol.get_symbol_name() + "]"

        raise Exception("Unknown node type: " + symbol.get_symbol_name())
