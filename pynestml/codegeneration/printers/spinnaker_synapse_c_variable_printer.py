# -*- coding: utf-8 -*-
#
# spinnaker_c_variable_printer.py
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

from pynestml.utils.ast_utils import ASTUtils

from pynestml.codegeneration.nest_unit_converter import NESTUnitConverter
from pynestml.codegeneration.printers.cpp_variable_printer import CppVariablePrinter
from pynestml.codegeneration.printers.expression_printer import ExpressionPrinter
from pynestml.codegeneration.printers.spinnaker_c_variable_printer import SpinnakerCVariablePrinter
from pynestml.codegeneration.spinnaker_code_generator_utils import SPINNAKERCodeGeneratorUtils
from pynestml.meta_model.ast_external_variable import ASTExternalVariable
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.symbols.predefined_units import PredefinedUnits
from pynestml.symbols.predefined_variables import PredefinedVariables
from pynestml.symbols.symbol import SymbolKind
from pynestml.symbols.unit_type_symbol import UnitTypeSymbol
from pynestml.symbols.variable_symbol import BlockType
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages


class SpinnakerSynapseCVariablePrinter(SpinnakerCVariablePrinter):
    r"""
    Variable printer for C syntax and the Spinnaker API -- for synapses
    """

    def _print(self, variable: ASTVariable, symbol, with_origin: bool = True) -> str:
        assert all([isinstance(s, str) for s in self._state_symbols])

        variable_name = CppVariablePrinter._print_cpp_name(variable.get_complete_name())

        if symbol.is_local():
            return variable_name

        if variable.is_delay_variable():
            return self._print_delay_variable(variable)

        if with_origin:
            return SPINNAKERCodeGeneratorUtils.print_symbol_origin(symbol, numerical_state_symbols=self._state_symbols, for_synapse=True) % variable_name

        return variable_name
