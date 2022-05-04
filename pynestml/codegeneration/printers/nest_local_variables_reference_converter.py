# -*- coding: utf-8 -*-
#
# nest_local_variables_reference_converter.py
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
from pynestml.codegeneration.printers.nest_reference_converter import NESTReferenceConverter
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


class NESTLocalVariablesReferenceConverter(NESTReferenceConverter):
    r"""
    Reference converter that converts state variables into names rather than getter method calls.
    """

    def convert_name_reference(self, variable: ASTVariable, prefix: str = '', with_origins=True) -> str:
        """
        Converts a single variable to nest processable format.
        :param variable: a single variable.
        :return: a nest processable format.
        """
        symbol = variable.get_scope().resolve_to_symbol(variable.get_complete_name(), SymbolKind.VARIABLE)
        if symbol is not None:
            if symbol.is_state():
                temp = ""
                temp += self.convert_to_cpp_name(symbol.get_symbol_name())
                temp += ('[' + variable.get_vector_parameter() + ']' if symbol.has_vector_parameter() else '')
                return temp

        return super().convert_name_reference(variable, prefix, with_origins)
