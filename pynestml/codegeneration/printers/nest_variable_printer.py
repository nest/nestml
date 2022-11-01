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

from pynestml.codegeneration.printers.cpp_variable_printer import CppVariablePrinter
from pynestml.codegeneration.printers.nest_cpp_variable_getter_printer import NESTCppVariableGetterPrinter
from pynestml.codegeneration.printers.unit_converter import UnitConverter
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.meta_model.ast_external_variable import ASTExternalVariable
from pynestml.meta_model.ast_function_call import ASTFunctionCall
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


class NESTVariablePrinter(CppVariablePrinter):
    r"""
    Reference converter for C++ syntax and using the NEST API.
    """

    def print_variable(self, node: ASTVariable) -> str:
        import pdb;pdb.set_trace()
        symbol = node.get_scope().resolve_to_symbol(node.lhs.get_complete_name(), SymbolKind.VARIABLE)
        ret = self.print_origin(symbol) + node.name
        for i in range(1, node.differential_order + 1):
            ret += "__d"
        return ret

    def print_variable(self, variable: ASTVariable, prefix: str = '') -> str:
        """
        Converts a single variable to nest processable format.
        :param variable: a single variable.
        :return: a nest processable format.
        """
        import pdb;pdb.set_trace()
        if isinstance(variable, ASTExternalVariable):
            _name = str(variable)
            if variable.get_alternate_name():
                # the disadvantage of this approach is that the time the value is to be obtained is not explicitly specified, so we will actually get the value at the end of the min_delay timestep
                return "((POST_NEURON_TYPE*)(__target))->get_" + variable.get_alternate_name() + "()"

            return "((POST_NEURON_TYPE*)(__target))->get_" + _name + "(_tr_t)"

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
            vector_param = "[" + self.print_vector_parameter_name_reference(variable) + "]"

        if symbol.is_buffer():
            if isinstance(symbol.get_type_symbol(), UnitTypeSymbol):
                units_conversion_factor = UnitConverter.get_factor(symbol.get_type_symbol().unit.unit)
            else:
                units_conversion_factor = 1
            s = ""
            if not units_conversion_factor == 1:
                s += "(" + str(units_conversion_factor) + " * "
            s += self.print_origin(symbol, prefix=prefix) + self.print_variable(symbol) + "_grid_sum_"
            s += vector_param
            if not units_conversion_factor == 1:
                s += ")"
            return s

        if symbol.is_inline_expression:
            return NESTCppVariableGetterPrinter().print(variable) + "()" + vector_param

        assert not symbol.is_kernel(), "NEST reference converter cannot print kernel; kernel should have been " \
                                       "converted during code generation code generation "

        if symbol.is_state() or symbol.is_inline_expression:
            return NESTCppVariableGetterPrinter().print(variable) + "()" + vector_param

        variable_name = self.print_cpp_name(variable.get_complete_name())
        if symbol.is_local():
            return variable_name + vector_param

        return self.print_origin(symbol, prefix=prefix) + \
            self.name(symbol) + vector_param

    def print_delay_variable(self, variable: ASTVariable, prefix=''):
        """
        Converts a delay variable to NEST processable format
        :param variable:
        :return:
        """
        symbol = variable.get_scope().resolve_to_symbol(variable.get_complete_name(), SymbolKind.VARIABLE)
        if symbol:
            if symbol.is_state() and symbol.has_delay_parameter():
                return "get_delayed_" + variable.get_name() + "()"
        return ""

    def print_vector_parameter_name_reference(self, variable: ASTVariable) -> str:
        """
        Converts the vector parameter into NEST processable format
        :param variable:
        :return:
        """
        vector_parameter = variable.get_vector_parameter()
        vector_parameter_var = ASTVariable(vector_parameter, scope=variable.get_scope())

        symbol = vector_parameter_var.get_scope().resolve_to_symbol(vector_parameter_var.get_complete_name(),
                                                                    SymbolKind.VARIABLE)
        if symbol is not None:
            if symbol.block_type == BlockType.STATE:
                return NESTCppVariableGetterPrinter().print(variable) + "()"

            if symbol.block_type == BlockType.LOCAL:
                return symbol.get_symbol_name()

            return self.print_origin(symbol)

        return vector_parameter

    def __get_unit_name(self, variable: ASTVariable):
        assert variable.get_scope() is not None, "Undeclared variable: " + variable.get_complete_name()

        variable_name = self.print_cpp_name(variable.get_complete_name())
        symbol = variable.get_scope().resolve_to_symbol(variable_name, SymbolKind.VARIABLE)
        if isinstance(symbol.get_type_symbol(), UnitTypeSymbol):
            return symbol.get_type_symbol().unit.unit.to_string()

        return ''

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
