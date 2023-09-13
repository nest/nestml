# -*- coding: utf-8 -*-
#
# python_code_generator_utils.py
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

from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.symbols.variable_symbol import VariableSymbol
from pynestml.symbols.variable_symbol import BlockType


class PythonCodeGeneratorUtils:

    @classmethod
    def print_symbol_origin(cls, variable_symbol: VariableSymbol, variable: ASTVariable) -> str:
        """
        Returns a prefix corresponding to the origin of the variable symbol.
        :param variable_symbol: a single variable symbol.
        :return: the corresponding prefix
        """
        if variable_symbol.block_type in [BlockType.STATE, BlockType.EQUATION]:
            if "_is_numeric" in dir(variable) and variable._is_numeric:
                return 'self.S_.ode_state[self.S_.ode_state_variable_name_to_index["%s"]]'

            return 'self.S_.%s'

        if variable_symbol.block_type == BlockType.PARAMETERS:
            return 'self.P_.%s'

        if variable_symbol.block_type == BlockType.COMMON_PARAMETERS:
            return 'self.cp.%s'

        if variable_symbol.block_type == BlockType.INTERNALS:
            return 'self.V_.%s'

        if variable_symbol.block_type == BlockType.INPUT:
            return 'self.B_.%s'

        return ''
