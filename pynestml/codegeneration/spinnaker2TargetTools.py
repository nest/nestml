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
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_model import ASTModel

from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.symbols.variable_symbol import VariableSymbol
from pynestml.symbols.variable_symbol import BlockType


class Spinnaker2TargetTools:
    @classmethod
    def get_propagators_as_math_expressions(cls, neuron:ASTNode, parameters:dict) -> dict:
        propagators_as_math_expressions = {}
        propagator_expressions = neuron.analytic_solver["propagators"]
        for propagator_expression in propagator_expressions:
            # propagator_expressions[propagator_expression] = propagator_expressions[propagator_expression].replace(
            #     '__h', str(1))
            # for symbol, value in parameters.items():
            #     propagator_expressions[propagator_expression] = propagator_expressions[propagator_expression].replace(symbol, str(value))
            #     propagators_as_math_expressions.update({propagator_expression: propagator_expressions[propagator_expression]})
            propagators_as_math_expressions[propagator_expression] = propagator_expressions[propagator_expression]
        return propagators_as_math_expressions