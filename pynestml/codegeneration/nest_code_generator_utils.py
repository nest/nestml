# -*- coding: utf-8 -*-
#
# nest_code_generator_utils.py
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

from pynestml.symbols.variable_symbol import VariableSymbol
from pynestml.symbols.variable_symbol import BlockType

from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression

from collections import defaultdict


class NESTCodeGeneratorUtils:

    @classmethod
    def print_symbol_origin(cls, variable_symbol: VariableSymbol, numerical_state_symbols=None) -> str:
        """
        Returns a prefix corresponding to the origin of the variable symbol.
        :param variable_symbol: a single variable symbol.
        :return: the corresponding prefix
        """
        if variable_symbol.block_type in [BlockType.STATE, BlockType.EQUATION]:
            if numerical_state_symbols and variable_symbol.get_symbol_name() in numerical_state_symbols:
                return 'S_.ode_state[State_::%s]'

            return 'S_.%s'

        if variable_symbol.block_type == BlockType.PARAMETERS:
            return 'P_.%s'

        if variable_symbol.block_type == BlockType.COMMON_PARAMETERS:
            return 'cp.%s'

        if variable_symbol.block_type == BlockType.INTERNALS:
            return 'V_.%s'

        if variable_symbol.block_type == BlockType.INPUT:
            return 'B_.%s'

        return ''

    @classmethod
    def print_element(cls, name, element, rec_step):
        for indent in range(rec_step):
            print("----", end="")
        print(name + ": ", end="")
        if isinstance(element, defaultdict):
            print("\n", end="")
            cls.print_dictionary(element, rec_step + 1)
        else:
            if hasattr(element, 'name'):
                print(element.name, end="")
            elif isinstance(element, str):
                print(element, end="")
            elif isinstance(element, dict):
                print("\n", end="")
                cls.print_dictionary(element, rec_step + 1)
            elif isinstance(element, list):
                for index in range(len(element)):
                    print("\n", end="")
                    cls.print_element(str(index), element[index], rec_step + 1)
            elif isinstance(element, ASTExpression) or isinstance(element, ASTSimpleExpression):
                print(cls._ode_toolbox_printer.print(element), end="")

            print("(" + type(element).__name__ + ")", end="")

    @classmethod
    def print_dictionary(cls, dictionary, rec_step):
        for name, element in dictionary.items():
            cls.print_element(name, element, rec_step)
            print("\n", end="")
