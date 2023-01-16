# -*- coding: utf-8 -*-
#
# chan_info_enricher.py
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

import copy
from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_inline_expression import ASTInlineExpression
from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.utils.model_parser import ModelParser
from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor
import sympy
from collections import defaultdict
from pynestml.symbols.symbol import SymbolKind
from pynestml.visitors.ast_visitor import ASTVisitor
from pynestml.symbols.predefined_functions import PredefinedFunctions


class ChanInfoEnricher():

    """
    Adds derivative of inline expression to chan_info
    This needs to be done used from within nest_codegenerator
    because the import of ModelParser will otherwise cause
    a circular dependency when this is used
    inside CmProcessing

    input:

        {
        "Na":
        {
            "ASTInlineExpression": ASTInlineExpression,
            "channel_parameters":
            {
                "gbar": {
                            "expected_name": "gbar_Na",
                            "parameter_block_variable": ASTVariable,
                            "rhs_expression": ASTSimpleExpression or ASTExpression
                        },
                "e":  {
                            "expected_name": "e_Na",
                            "parameter_block_variable": ASTVariable,
                            "rhs_expression": ASTSimpleExpression or ASTExpression
                        }
            }
            "gating_variables":
            {
                "m":
                {
                    "ASTVariable": ASTVariable,
                    "state_variable": ASTVariable,
                    "expected_functions":
                    {
                        "tau":  {
                                    "ASTFunction": ASTFunction,
                                    "function_name": str,
                                    "result_variable_name": str,
                                    "rhs_expression": ASTSimpleExpression or ASTExpression
                                },
                        "inf":  {
                                    "ASTFunction": ASTFunction,
                                    "function_name": str,
                                    "result_variable_name": str,
                                    "rhs_expression": ASTSimpleExpression or ASTExpression
                                }
                    }
                },
                "h":
                {
                    "ASTVariable": ASTVariable,
                    "state_variable": ASTVariable,
                    "expected_functions":
                    {
                        "tau":  {
                                    "ASTFunction": ASTFunction,
                                    "function_name": str,
                                    "result_variable_name": str,
                                    "rhs_expression": ASTSimpleExpression or ASTExpression
                                },
                        "inf":  {
                                    "ASTFunction": ASTFunction,
                                    "function_name": str,
                                    "result_variable_name": str,
                                    "rhs_expression": ASTSimpleExpression or ASTExpression
                                }
                    }
                },
                ...
            }
        },
        "K":
        {
            ...
        }
    }

    output:

        {
        "Na":
        {
            "ASTInlineExpression": ASTInlineExpression,
            "inline_derivative": ASTInlineExpression,
            "channel_parameters":
            {
                "gbar": {
                            "expected_name": "gbar_Na",
                            "parameter_block_variable": ASTVariable,
                            "rhs_expression": ASTSimpleExpression or ASTExpression
                        },
                "e":  {
                            "expected_name": "e_Na",
                            "parameter_block_variable": ASTVariable,
                            "rhs_expression": ASTSimpleExpression or ASTExpression
                        }
            }
            "gating_variables":
            {
                "m":
                {
                    "ASTVariable": ASTVariable,
                    "state_variable": ASTVariable,
                    "expected_functions":
                    {
                        "tau":  {
                                    "ASTFunction": ASTFunction,
                                    "function_name": str,
                                    "result_variable_name": str,
                                    "rhs_expression": ASTSimpleExpression or ASTExpression
                                },
                        "inf":  {
                                    "ASTFunction": ASTFunction,
                                    "function_name": str,
                                    "result_variable_name": str,
                                    "rhs_expression": ASTSimpleExpression or ASTExpression
                                }
                    }
                },
                "h":
                {
                    "ASTVariable": ASTVariable,
                    "state_variable": ASTVariable,
                    "expected_functions":
                    {
                        "tau":  {
                                    "ASTFunction": ASTFunction,
                                    "function_name": str,
                                    "result_variable_name": str,
                                    "rhs_expression": ASTSimpleExpression or ASTExpression
                                },
                        "inf":  {
                                    "ASTFunction": ASTFunction,
                                    "function_name": str,
                                    "result_variable_name": str,
                                    "rhs_expression": ASTSimpleExpression or ASTExpression
                                }
                    }
                },
                ...
            }
        },
        "K":
        {
            ...
        }
    }

"""

    @classmethod
    def enrich_with_additional_info(cls, neuron: ASTNeuron, chan_info: dict):
        chan_info_copy = copy.copy(chan_info)
        for ion_channel_name, ion_channel_info in chan_info_copy.items():
            chan_info[ion_channel_name]["inline_derivative"] = cls.computeExpressionDerivative(
                chan_info[ion_channel_name]["RootInlineExpression"])
            chan_info[ion_channel_name] = cls.transform_ode_solution(neuron, ion_channel_info)
        return chan_info

    @classmethod
    def computeExpressionDerivative(
            cls, inline_expression: ASTInlineExpression) -> ASTExpression:
        expr_str = str(inline_expression.get_expression())
        sympy_expr = sympy.parsing.sympy_parser.parse_expr(expr_str)
        sympy_expr = sympy.diff(sympy_expr, "v_comp")

        ast_expression_d = ModelParser.parse_expression(str(sympy_expr))
        # copy scope of the original inline_expression into the the derivative
        ast_expression_d.update_scope(inline_expression.get_scope())
        ast_expression_d.accept(ASTSymbolTableVisitor())

        return ast_expression_d

    @classmethod
    def transform_ode_solution(cls, neuron, channel_info):
        for ode_var_name, ode_info in channel_info["ODEs"].items():
            channel_info["ODEs"][ode_var_name]["transformed_solutions"] = list()

            for ode_solution_index in range(len(ode_info["ode_toolbox_output"])):
                solution_transformed = defaultdict()
                solution_transformed["states"] = defaultdict()
                solution_transformed["propagators"] = defaultdict()

                for variable_name, rhs_str in ode_info["ode_toolbox_output"][ode_solution_index]["initial_values"].items():
                    variable = neuron.get_equations_blocks()[0].get_scope().resolve_to_symbol(variable_name,
                                                                                              SymbolKind.VARIABLE)

                    expression = ModelParser.parse_expression(rhs_str)
                    # pretend that update expressions are in "equations" block,
                    # which should always be present, as synapses have been
                    # defined to get here
                    expression.update_scope(neuron.get_equations_blocks()[0].get_scope())
                    expression.accept(ASTSymbolTableVisitor())

                    update_expr_str = ode_info["ode_toolbox_output"][ode_solution_index]["update_expressions"][variable_name]
                    update_expr_ast = ModelParser.parse_expression(
                        update_expr_str)
                    # pretend that update expressions are in "equations" block,
                    # which should always be present, as differential equations
                    # must have been defined to get here
                    update_expr_ast.update_scope(
                        neuron.get_equations_blocks()[0].get_scope())
                    update_expr_ast.accept(ASTSymbolTableVisitor())

                    solution_transformed["states"][variable_name] = {
                        "ASTVariable": variable,
                        "init_expression": expression,
                        "update_expression": update_expr_ast,
                    }
                for variable_name, rhs_str in ode_info["ode_toolbox_output"][ode_solution_index]["propagators"].items(
                ):
                    variable = neuron.get_equations_blocks()[0].get_scope().resolve_to_symbol(variable_name,
                                                                                              SymbolKind.VARIABLE)

                    expression = ModelParser.parse_expression(rhs_str)
                    # pretend that update expressions are in "equations" block,
                    # which should always be present, as synapses have been
                    # defined to get here
                    expression.update_scope(
                        neuron.get_equations_blocks()[0].get_scope())
                    expression.accept(ASTSymbolTableVisitor())

                    solution_transformed["propagators"][variable_name] = {
                        "ASTVariable": variable, "init_expression": expression, }
                    expression_variable_collector = ASTEnricherInfoCollectorVisitor()
                    expression.accept(expression_variable_collector)
                    print("TRV: " + PredefinedFunctions.TIME_RESOLUTION)
                    for variable in expression_variable_collector.all_variables:
                        for internal_declaration in expression_variable_collector.internal_declarations:
                            if variable.get_name() == internal_declaration.get_lhs.get_name() \
                                    and internal_declaration.get_expression().is_function_call() \
                                    and internal_declaration.get_expression().callee_name == PredefinedFunctions.TIME_RESOLUTION:
                                channel_info["time_resolution_var"] = variable()        #not so sensible (predefined) :D

                channel_info["ODEs"][ode_var_name]["transformed_solutions"].append(solution_transformed)

        return channel_info

class ASTEnricherInfoCollectorVisitor(ASTVisitor):
    def __init__(self):
        super(ASTEnricherInfoCollectorVisitor, self).__init__()
        self.inside_variable = False
        self.inside_block_with_variables = False
        self.all_states = list()
        self.all_parameters = list()
        self.inside_states_block = False
        self.inside_parameters_block = False
        self.all_variables = list()
        self.inside_internals_block = False
        self.inside_declaration = False
        self.internal_declarations = list()

    def visit_block_with_variables(self, node):
        self.inside_block_with_variables = True
        if node.is_state:
            self.inside_states_block = True
        if node.is_parameters:
            self.inside_parameters_block = True
        if node.is_internals:
            self.inside_internals_block = True

    def endvisit_block_with_variables(self, node):
        self.inside_states_block = False
        self.inside_parameters_block = False
        self.inside_block_with_variables = False
        self.inside_internals_block = False

    def visit_variable(self, node):
        self.inside_variable = True
        self.all_variables.append(node.clone())
        if self.inside_states_block:
            self.all_states.append(node.clone())
        if self.inside_parameters_block:
            self.all_parameters.append(node.clone())

    def endvisit_variable(self, node):
        self.inside_variable = False

    def visit_declaration(self, node):
        self.inside_declaration = True
        if self.inside_internals_block:
            self.internal_declarations.append(node)

    def endvisit_declaration(self, node):
        self.inside_declaration = False