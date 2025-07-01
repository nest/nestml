# -*- coding: utf-8 -*-
#
# spinnaker_code_generator_utils.py
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
from pynestml.meta_model.ast_model import ASTModel
from pynestml.symbols.variable_symbol import VariableSymbol
from pynestml.symbols.variable_symbol import BlockType




class SPINNAKER2CodeGeneratorUtils:

    @classmethod
    def print_symbol_origin(cls, variable_symbol: VariableSymbol, numerical_state_symbols=None) -> str:
        """
        Returns a prefix corresponding to the origin of the variable symbol.
        :param variable_symbol: a single variable symbol.
        :return: the corresponding prefix
        """
        if variable_symbol.block_type in [BlockType.STATE, BlockType.EQUATION]:
            if numerical_state_symbols and variable_symbol.get_symbol_name() in numerical_state_symbols:
                return  'NUMERICAL STATE SYMBOL'  #'S_.ode_state[State_::%s]'

            return 'state->%s'

        if variable_symbol.block_type == BlockType.PARAMETERS:
            return 'neuron_params->%s'

        if variable_symbol.block_type == BlockType.COMMON_PARAMETERS:
            return 'neuron_params->%s'

        if variable_symbol.block_type == BlockType.INTERNALS:  # and not variable_symbol.name == "__h":
            return 'neuron_params->%s'


        if variable_symbol.block_type == BlockType.INPUT:
            return 'input->%s'

        return ''

    # @classmethod
    # def get_propagators_as_python_expression(cls, propagators:dict) -> dict:
    #     import math
    #
    #     # Define supported math functions and constants
    #     safe_dict = {
    #         # Basic math functions
    #         'exp': math.exp,
    #         'ln': math.log,
    #         'log10': math.log10,
    #         'pow': math.pow,
    #         'sqrt': math.sqrt,
    #         # Trigonometric functions
    #         'sin': math.sin,
    #         'cos': math.cos,
    #         'tan': math.tan,
    #         'asin': math.asin,
    #         'acos': math.acos,
    #         'atan': math.atan,
    #         'atan2': math.atan2,
    #         # Hyperbolic functions
    #         'sinh': math.sinh,
    #         'cosh': math.cosh,
    #         'tanh': math.tanh,
    #         # Math functions
    #         'abs': abs,
    #         'ceil': math.ceil,
    #         'floor': math.floor,
    #         'round': round,
    #         'erf': math.erf,
    #         'erfc': math.erfc,
    #         # Constants
    #         'e': math.e,
    #         'pi': math.pi,
    #         'inf': float('inf'),
    #         '__h': '__h',
    #     }
    #
    #     propagators_as_python_expressions = dict()
    #     for key, expression in propagators.items():
    #                      # Remove all function names from the expression before checking the pattern
    #         result = eval(expression, {"__builtins__": {}}, safe_dict)
    #         propagators_as_python_expressions[key] = result
    #     pass
