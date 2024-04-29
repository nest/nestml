# -*- coding: utf-8 -*-
#
# mechs_info_enricher.py
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

from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.meta_model.ast_declaration import ASTDeclaration
from pynestml.meta_model.ast_small_stmt import ASTSmallStmt
from pynestml.meta_model.ast_compound_stmt import ASTCompoundStmt
from pynestml.meta_model.ast_stmt import ASTStmt
from pynestml.utils.model_parser import ModelParser
from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor
from pynestml.symbols.symbol import SymbolKind
from pynestml.visitors.ast_visitor import ASTVisitor
from pynestml.symbols.predefined_functions import PredefinedFunctions
from collections import defaultdict
from pynestml.utils.ast_utils import ASTUtils

import sympy


class MechsInfoEnricher:
    """
    Adds information collection that can't be done in the processing class since that is used in the cocos.
    Here we use the ModelParser which would lead to a cyclic dependency.
    """

    def __init__(self):
        pass

    @classmethod
    def enrich_with_additional_info(cls, neuron: ASTNeuron, mechs_info: dict):
        mechs_info = cls.transform_ode_solutions(neuron, mechs_info)
        #cls.common_subexpression_elimination(mechs_info)
        mechs_info = cls.enrich_mechanism_specific(neuron, mechs_info)
        return mechs_info

    @classmethod
    def transform_ode_solutions(cls, neuron, mechs_info):
        for mechanism_name, mechanism_info in mechs_info.items():
            for ode_var_name, ode_info in mechanism_info["ODEs"].items():
                mechanism_info["ODEs"][ode_var_name]["transformed_solutions"] = list()

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

                        update_expr_str = ode_info["ode_toolbox_output"][ode_solution_index]["update_expressions"][
                            variable_name]
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
                    for variable_name, rhs_str in ode_info["ode_toolbox_output"][ode_solution_index]["propagators"].items():
                        prop_variable = neuron.get_equations_blocks()[0].get_scope().resolve_to_symbol(variable_name,
                                                                                                       SymbolKind.VARIABLE)
                        if prop_variable is None:
                            ASTUtils.add_declarations_to_internals(
                                neuron, ode_info["ode_toolbox_output"][ode_solution_index]["propagators"])
                            prop_variable = neuron.get_equations_blocks()[0].get_scope().resolve_to_symbol(
                                variable_name,
                                SymbolKind.VARIABLE)

                        expression = ModelParser.parse_expression(rhs_str)
                        # pretend that update expressions are in "equations" block,
                        # which should always be present, as synapses have been
                        # defined to get here
                        expression.update_scope(
                            neuron.get_equations_blocks()[0].get_scope())
                        expression.accept(ASTSymbolTableVisitor())

                        solution_transformed["propagators"][variable_name] = {
                            "ASTVariable": prop_variable, "init_expression": expression, }
                        expression_variable_collector = ASTEnricherInfoCollectorVisitor()
                        expression.accept(expression_variable_collector)

                        neuron_internal_declaration_collector = ASTEnricherInfoCollectorVisitor()
                        neuron.accept(neuron_internal_declaration_collector)

                        for variable in expression_variable_collector.all_variables:
                            for internal_declaration in neuron_internal_declaration_collector.internal_declarations:
                                if variable.get_name() == internal_declaration.get_variables()[0].get_name() \
                                        and internal_declaration.get_expression().is_function_call() \
                                        and internal_declaration.get_expression().get_function_call().callee_name == \
                                        PredefinedFunctions.TIME_RESOLUTION:
                                    mechanism_info["time_resolution_var"] = variable

                    mechanism_info["ODEs"][ode_var_name]["transformed_solutions"].append(solution_transformed)

        return mechs_info

    @classmethod
    def common_subexpression_elimination(cls, mechs_info):
        for mechanism_name, mechanism_info in mechs_info.items():
            for function in mechanism_info["Functions"]:
                print(function.name)
                function_expression_collector = ASTEnricherInfoExpressionCollectorVisitor()
                function.accept(function_expression_collector)
                for index in range(len(function_expression_collector.expressions)):
                    exp_index = len(function_expression_collector.expressions)-index-1
                    expression = function_expression_collector.expressions[exp_index]
                    expr_str = str(expression)
                    print(expr_str)
                    try:
                        sympy_expr = sympy.parsing.sympy_parser.parse_expr(expr_str)
                        #cse_sympy_expression = sympy.simplify(sympy_expr)
                        cse_sympy_expression = sympy.cse(sympy_expr, optimizations=[])
                        print(str(cse_sympy_expression))
                        cse_expression = ModelParser.parse_expression(str(cse_sympy_expression[1][0]))
                        #cse_expression = ModelParser.parse_expression(str(cse_sympy_expression[0]))
                        cse_expression.update_scope(expression.get_scope())
                        cse_expression.accept(ASTSymbolTableVisitor())
                        function_expression_collector.expressions[
                            exp_index].is_encapsulated = cse_expression.is_encapsulated
                        function_expression_collector.expressions[
                            exp_index].is_logical_not = cse_expression.is_logical_not
                        function_expression_collector.expressions[
                            exp_index].unary_operator = cse_expression.unary_operator
                        function_expression_collector.expressions[
                            exp_index].expression = cse_expression.expression
                        function_expression_collector.expressions[
                            exp_index].lhs = cse_expression.lhs
                        function_expression_collector.expressions[
                            exp_index].binary_operator = cse_expression.binary_operator
                        function_expression_collector.expressions[
                            exp_index].rhs = cse_expression.rhs
                        function_expression_collector.expressions[
                            exp_index].condition = cse_expression.condition
                        function_expression_collector.expressions[
                            exp_index].if_true = cse_expression.if_true
                        function_expression_collector.expressions[
                            exp_index].if_not = cse_expression.if_not
                        function_expression_collector.expressions[
                            exp_index].has_delay = cse_expression.has_delay

                        for substitution in cse_sympy_expression[0][::-1]:
                            substitution_str = str(substitution[0]) + " real = " + str(substitution[1])
                            sub_expression = ModelParser.parse_stmt(substitution_str)
                            sub_expression.update_scope(expression.get_scope())
                            sub_expression.accept(ASTSymbolTableVisitor())
                            function_expression_collector.blocks[exp_index].stmts.insert(0, sub_expression)
                    except:
                        print("expression failed to be simplified")
                function.accept(ASTSymbolTableVisitor())




    @classmethod
    def enrich_mechanism_specific(cls, neuron, mechs_info):
        return mechs_info


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


class ASTEnricherInfoExpressionCollectorVisitor(ASTVisitor):

    def __init__(self):
        super(ASTEnricherInfoExpressionCollectorVisitor, self).__init__()
        self.expressions = list()
        self.blocks = list()
        self.inside_expression = False
        self.expression_depth = 0
        self.block_traversal_list = list()
        self.inside_block = False

    def visit_expression(self, node):
        self.inside_expression = True
        self.expression_depth += 1
        if self.expression_depth == 1:
            self.expressions.append(node)
            self.blocks.append(self.block_traversal_list[-1])

    def endvisit_expression(self, node):
        self.inside_expression = False
        self.expression_depth -= 1

    def visit_block(self, node):
        self.inside_block = True
        self.block_traversal_list.append(node)

    def endvisit_block(self, node):
        self.inside_block = False
        self.block_traversal_list.pop()
