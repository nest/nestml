# -*- coding: utf-8 -*-
#
# syns_info_enricher.py
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

from _collections import defaultdict
import copy

from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_inline_expression import ASTInlineExpression
from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.symbols.symbol import SymbolKind
from pynestml.utils.model_parser import ModelParser
from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor
from pynestml.visitors.ast_visitor import ASTVisitor
import sympy

from pynestml.utils.mechs_info_enricher import MechsInfoEnricher


class SynsInfoEnricher(MechsInfoEnricher):
    """
    input: a neuron after ODE-toolbox transformations

    the kernel analysis solves all kernels at the same time
    this splits the variables on per kernel basis
    """

    def __init__(self, params):
        super(MechsInfoEnricher, self).__init__(params)

    @classmethod
    def enrich_mechanism_specific(cls, neuron, mechs_info):
        specific_enricher_visitor = SynsInfoEnricherVisitor()
        neuron.accept(specific_enricher_visitor)
        mechs_info = cls.transform_convolutions_analytic_solutions(neuron, mechs_info)
        mechs_info = cls.restore_order_internals(neuron, mechs_info)
        return mechs_info

    @classmethod
    def transform_convolutions_analytic_solutions(
            cls,
            neuron: ASTNeuron,
            cm_syns_info: dict):

        enriched_syns_info = copy.copy(cm_syns_info)
        for synapse_name, synapse_info in cm_syns_info.items():
            for convolution_name in synapse_info["convolutions"].keys():
                analytic_solution = enriched_syns_info[synapse_name][
                    "convolutions"][convolution_name]["analytic_solution"]
                analytic_solution_transformed = defaultdict(
                    lambda: defaultdict())

                for variable_name, expression_str in analytic_solution["initial_values"].items():
                    variable = neuron.get_equations_blocks()[0].get_scope().resolve_to_symbol(variable_name,
                                                                                              SymbolKind.VARIABLE)

                    expression = ModelParser.parse_expression(expression_str)
                    # pretend that update expressions are in "equations" block,
                    # which should always be present, as synapses have been
                    # defined to get here
                    expression.update_scope(neuron.get_equations_blocks()[0].get_scope())
                    expression.accept(ASTSymbolTableVisitor())

                    update_expr_str = analytic_solution["update_expressions"][variable_name]
                    update_expr_ast = ModelParser.parse_expression(
                        update_expr_str)
                    # pretend that update expressions are in "equations" block,
                    # which should always be present, as differential equations
                    # must have been defined to get here
                    update_expr_ast.update_scope(
                        neuron.get_equations_blocks()[0].get_scope())
                    update_expr_ast.accept(ASTSymbolTableVisitor())

                    analytic_solution_transformed['kernel_states'][variable_name] = {
                        "ASTVariable": variable,
                        "init_expression": expression,
                        "update_expression": update_expr_ast,
                    }

                for variable_name, expression_string in analytic_solution["propagators"].items(
                ):
                    variable = SynsInfoEnricherVisitor.internal_variable_name_to_variable[variable_name]
                    expression = ModelParser.parse_expression(
                        expression_string)
                    # pretend that update expressions are in "equations" block,
                    # which should always be present, as synapses have been
                    # defined to get here
                    expression.update_scope(
                        neuron.get_equations_blocks()[0].get_scope())
                    expression.accept(ASTSymbolTableVisitor())
                    analytic_solution_transformed['propagators'][variable_name] = {
                        "ASTVariable": variable, "init_expression": expression, }

                enriched_syns_info[synapse_name]["convolutions"][convolution_name]["analytic_solution"] = \
                    analytic_solution_transformed

            # only one buffer allowed, so allow direct access
            # to it instead of a list
            if "buffer_name" not in enriched_syns_info[synapse_name]:
                buffers_used = list(
                    enriched_syns_info[synapse_name]["buffers_used"])
                del enriched_syns_info[synapse_name]["buffers_used"]
                enriched_syns_info[synapse_name]["buffer_name"] = buffers_used[0]

            inline_expression_name = enriched_syns_info[synapse_name]["root_expression"].variable_name
            enriched_syns_info[synapse_name]["root_expression"] = \
                SynsInfoEnricherVisitor.inline_name_to_transformed_inline[inline_expression_name]
            enriched_syns_info[synapse_name]["inline_expression_d"] = \
                cls.compute_expression_derivative(
                    enriched_syns_info[synapse_name]["root_expression"])

            # now also identify analytic helper variables such as __h
            enriched_syns_info[synapse_name]["analytic_helpers"] = cls.get_analytic_helper_variable_declarations(
                enriched_syns_info[synapse_name])

        return enriched_syns_info

    @classmethod
    def restore_order_internals(cls, neuron: ASTNeuron, cm_syns_info: dict):
        """orders user defined internals
        back to the order they were originally defined
        this is important if one such variable uses another
        user needs to have control over the order
        assign each variable a rank
        that corresponds to the order in
        SynsInfoEnricher.declarations_ordered"""
        variable_name_to_order = {}
        for index, declaration in enumerate(
                SynsInfoEnricherVisitor.declarations_ordered):
            variable_name = declaration.get_variables()[0].get_name()
            variable_name_to_order[variable_name] = index

        enriched_syns_info = copy.copy(cm_syns_info)
        for synapse_name, synapse_info in cm_syns_info.items():
            user_internals = enriched_syns_info[synapse_name]["internals_used_declared"]
            user_internals_sorted = sorted(
                user_internals.items(), key=lambda x: variable_name_to_order[x[0]])
            enriched_syns_info[synapse_name]["internals_used_declared"] = user_internals_sorted

        return enriched_syns_info

    @classmethod
    def compute_expression_derivative(
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
    def get_variable_names_used(cls, node) -> set:
        variable_names_extractor = ASTUsedVariableNamesExtractor(node)
        return variable_names_extractor.variable_names

    @classmethod
    def get_all_synapse_variables(cls, single_synapse_info):
        """returns all variable names referenced by the synapse inline
        and by the analytical solution
        assumes that the model has already been transformed"""

        # get all variables from transformed inline
        inline_variables = cls.get_variable_names_used(
            single_synapse_info["root_expression"])

        analytic_solution_vars = set()
        # get all variables from transformed analytic solution
        for convolution_name, convolution_info in single_synapse_info["convolutions"].items(
        ):
            analytic_sol = convolution_info["analytic_solution"]
            # get variables from init and update expressions
            # for each kernel
            for kernel_var_name, kernel_info in analytic_sol["kernel_states"].items(
            ):
                analytic_solution_vars.add(kernel_var_name)

                update_vars = cls.get_variable_names_used(
                    kernel_info["update_expression"])
                init_vars = cls.get_variable_names_used(
                    kernel_info["init_expression"])

                analytic_solution_vars.update(update_vars)
                analytic_solution_vars.update(init_vars)

            # get variables from init expressions
            # for each propagator
            # include propagator variable itself
            for propagator_var_name, propagator_info in analytic_sol["propagators"].items(
            ):
                analytic_solution_vars.add(propagator_var_name)

                init_vars = cls.get_variable_names_used(
                    propagator_info["init_expression"])

                analytic_solution_vars.update(init_vars)

        return analytic_solution_vars.union(inline_variables)

    @classmethod
    def get_new_variables_after_transformation(cls, single_synapse_info):
        return cls.get_all_synapse_variables(single_synapse_info).difference(
            single_synapse_info["total_used_declared"])

    @classmethod
    def get_analytic_helper_variable_names(cls, single_synapse_info):
        """get new variables that only occur on the right hand side of analytic solution Expressions
        but for wich analytic solution does not offer any values
        this can isolate out additional variables that suddenly appear such as __h
        whose initial values are not inlcuded in the output of analytic solver"""

        analytic_lhs_vars = set()

        for convolution_name, convolution_info in single_synapse_info["convolutions"].items(
        ):
            analytic_sol = convolution_info["analytic_solution"]

            # get variables representing convolutions by kernel
            for kernel_var_name, kernel_info in analytic_sol["kernel_states"].items(
            ):
                analytic_lhs_vars.add(kernel_var_name)

            # get propagator variable names
            for propagator_var_name, propagator_info in analytic_sol["propagators"].items(
            ):
                analytic_lhs_vars.add(propagator_var_name)

        return cls.get_new_variables_after_transformation(
            single_synapse_info).symmetric_difference(analytic_lhs_vars)

    @classmethod
    def get_analytic_helper_variable_declarations(cls, single_synapse_info):
        variable_names = cls.get_analytic_helper_variable_names(
            single_synapse_info)
        result = dict()
        for variable_name in variable_names:
            if variable_name not in SynsInfoEnricherVisitor.internal_variable_name_to_variable:
                continue
            variable = SynsInfoEnricherVisitor.internal_variable_name_to_variable[variable_name]
            expression = SynsInfoEnricherVisitor.variables_to_internal_declarations[variable]
            result[variable_name] = {
                "ASTVariable": variable,
                "init_expression": expression,
            }
            if expression.is_function_call() and expression.get_function_call(
            ).callee_name == PredefinedFunctions.TIME_RESOLUTION:
                result[variable_name]["is_time_resolution"] = True
            else:
                result[variable_name]["is_time_resolution"] = False

        return result


class SynsInfoEnricherVisitor(ASTVisitor):
    variables_to_internal_declarations = {}
    internal_variable_name_to_variable = {}
    inline_name_to_transformed_inline = {}

    # assuming depth first traversal
    # collect declaratins in the order
    # in which they were present in the neuron
    declarations_ordered = []

    def __init__(self):
        super(SynsInfoEnricherVisitor, self).__init__()

        self.inside_parameter_block = False
        self.inside_state_block = False
        self.inside_internals_block = False
        self.inside_inline_expression = False
        self.inside_inline_expression = False
        self.inside_declaration = False
        self.inside_simple_expression = False

    def visit_inline_expression(self, node):
        self.inside_inline_expression = True
        inline_name = node.variable_name
        SynsInfoEnricherVisitor.inline_name_to_transformed_inline[inline_name] = node

    def endvisit_inline_expression(self, node):
        self.inside_inline_expression = False

    def visit_block_with_variables(self, node):
        if node.is_state:
            self.inside_state_block = True
        if node.is_parameters:
            self.inside_parameter_block = True
        if node.is_internals:
            self.inside_internals_block = True

    def endvisit_block_with_variables(self, node):
        if node.is_state:
            self.inside_state_block = False
        if node.is_parameters:
            self.inside_parameter_block = False
        if node.is_internals:
            self.inside_internals_block = False

    def visit_simple_expression(self, node):
        self.inside_simple_expression = True

    def endvisit_simple_expression(self, node):
        self.inside_simple_expression = False

    def visit_declaration(self, node):
        self.declarations_ordered.append(node)
        self.inside_declaration = True
        if self.inside_internals_block:
            variable = node.get_variables()[0]
            expression = node.get_expression()
            SynsInfoEnricherVisitor.variables_to_internal_declarations[variable] = expression
            SynsInfoEnricherVisitor.internal_variable_name_to_variable[variable.get_name(
            )] = variable

    def endvisit_declaration(self, node):
        self.inside_declaration = False


class ASTUsedVariableNamesExtractor(ASTVisitor):
    def __init__(self, node):
        super(ASTUsedVariableNamesExtractor, self).__init__()
        self.variable_names = set()
        node.accept(self)

    def visit_variable(self, node):
        self.variable_names.add(node.get_name())
