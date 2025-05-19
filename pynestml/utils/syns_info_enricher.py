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
import copy
from collections import defaultdict

import sympy
from pynestml.cocos.co_cos_manager import CoCosManager

from pynestml.symbol_table.symbol_table import SymbolTable

from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_inline_expression import ASTInlineExpression
from pynestml.meta_model.ast_model import ASTModel
from pynestml.visitors.ast_parent_visitor import ASTParentVisitor
from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor
from pynestml.utils.ast_utils import ASTUtils
from pynestml.visitors.ast_visitor import ASTVisitor
from pynestml.utils.model_parser import ModelParser
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.symbols.symbol import SymbolKind

from collections import defaultdict


class SynsInfoEnricher:
    """
    Adds information collection that can't be done in the processing class since that is used in the cocos.
    Here we use the ModelParser which would lead to a cyclic dependency.

    Additionally we require information about the paired synapses mechanism to confirm what dependencies are actually existent in the synapse.
    """

    def __init__(self):
        pass

    @classmethod
    def enrich_with_additional_info(cls, synapse: ASTModel, syns_info: dict, chan_info: dict, recs_info: dict,
                                    conc_info: dict, con_in_info: dict):
        specific_enricher_visitor = SynsInfoEnricherVisitor()

        cls.add_propagators_to_internals(synapse, syns_info)
        synapse.accept(specific_enricher_visitor)

        synapse_info = syns_info[synapse.get_name()]
        synapse_info = cls.transform_ode_solutions(synapse, synapse_info)
        synapse_info = cls.confirm_dependencies(synapse_info, chan_info, recs_info, conc_info, con_in_info)
        synapse_info = cls.extract_infunction_declarations(synapse_info)

        synapse_info = cls.transform_convolutions_analytic_solutions(synapse, synapse_info)
        syns_info[synapse.get_name()] = synapse_info

        return syns_info

    @classmethod
    def add_propagators_to_internals(cls, neuron, mechs_info):
        for mechanism_name, mechanism_info in mechs_info.items():
            for ode_var_name, ode_info in mechanism_info["ODEs"].items():
                for ode_solution_index in range(len(ode_info["ode_toolbox_output"])):
                    for variable_name, rhs_str in ode_info["ode_toolbox_output"][ode_solution_index]["propagators"].items():
                        ASTUtils.add_declaration_to_internals(neuron, variable_name, rhs_str)

            if "convolutions" in mechanism_info:
                for convolution_name, convolution_info in mechanism_info["convolutions"].items():
                    for variable_name, rhs_str in convolution_info["analytic_solution"]["propagators"].items():
                        ASTUtils.add_declaration_to_internals(neuron, variable_name, rhs_str)

        SymbolTable.delete_model_scope(neuron.get_name())
        symbol_table_visitor = ASTSymbolTableVisitor()
        neuron.accept(symbol_table_visitor)
        CoCosManager.check_cocos(neuron, after_ast_rewrite=True)
        SymbolTable.add_model_scope(neuron.get_name(), neuron.get_scope())

    @classmethod
    def transform_ode_solutions(cls, synapse, syns_info):
        for ode_var_name, ode_info in syns_info["ODEs"].items():
            syns_info["ODEs"][ode_var_name]["transformed_solutions"] = list()

            for ode_solution_index in range(len(ode_info["ode_toolbox_output"])):
                solution_transformed = defaultdict()
                solution_transformed["states"] = defaultdict()
                solution_transformed["propagators"] = defaultdict()

                for variable_name, rhs_str in ode_info["ode_toolbox_output"][ode_solution_index]["initial_values"].items():
                    variable = synapse.get_equations_blocks()[0].get_scope().resolve_to_symbol(variable_name,
                                                                                               SymbolKind.VARIABLE)

                    expression = ModelParser.parse_expression(rhs_str)
                    # pretend that update expressions are in "equations" block,
                    # which should always be present, as synapses have been
                    # defined to get here
                    expression.update_scope(synapse.get_equations_blocks()[0].get_scope())
                    expression.accept(ASTSymbolTableVisitor())

                    update_expr_str = ode_info["ode_toolbox_output"][ode_solution_index]["update_expressions"][
                        variable_name]
                    update_expr_ast = ModelParser.parse_expression(
                        update_expr_str)
                    # pretend that update expressions are in "equations" block,
                    # which should always be present, as differential equations
                    # must have been defined to get here
                    update_expr_ast.update_scope(
                        synapse.get_equations_blocks()[0].get_scope())
                    update_expr_ast.accept(ASTSymbolTableVisitor())

                    solution_transformed["states"][variable_name] = {
                        "ASTVariable": variable,
                        "init_expression": expression,
                        "update_expression": update_expr_ast,
                    }
                for variable_name, rhs_str in ode_info["ode_toolbox_output"][ode_solution_index]["propagators"].items():
                    prop_variable = synapse.get_internals_blocks()[0].get_scope().resolve_to_symbol(variable_name, SymbolKind.VARIABLE)
                    if prop_variable is None:
                        ASTUtils.add_declarations_to_internals(
                            synapse, ode_info["ode_toolbox_output"][ode_solution_index]["propagators"])
                        prop_variable = synapse.get_internals_blocks()[0].get_scope().resolve_to_symbol(
                            variable_name,
                            SymbolKind.VARIABLE)

                    expression = ModelParser.parse_expression(rhs_str)
                    # pretend that update expressions are in "equations" block,
                    # which should always be present, as synapses have been
                    # defined to get here
                    expression.update_scope(
                        synapse.get_equations_blocks()[0].get_scope())
                    expression.accept(ASTSymbolTableVisitor())

                    solution_transformed["propagators"][variable_name] = {
                        "ASTVariable": prop_variable, "init_expression": expression, }
                    expression_variable_collector = ASTEnricherInfoCollectorVisitor()
                    expression.accept(expression_variable_collector)

                    synapse_internal_declaration_collector = ASTEnricherInfoCollectorVisitor()
                    synapse.accept(synapse_internal_declaration_collector)

                    for variable in expression_variable_collector.all_variables:
                        for internal_declaration in synapse_internal_declaration_collector.internal_declarations:
                            if variable.get_name() == internal_declaration.get_variables()[0].get_name() \
                                    and internal_declaration.get_expression().is_function_call() \
                                    and internal_declaration.get_expression().get_function_call().callee_name == \
                                    PredefinedFunctions.TIME_RESOLUTION:
                                syns_info["time_resolution_var"] = variable

                syns_info["ODEs"][ode_var_name]["transformed_solutions"].append(solution_transformed)

        synapse.accept(ASTParentVisitor())

        return syns_info

    @classmethod
    def confirm_dependencies(cls, syns_info: dict, chan_info: dict, recs_info: dict, conc_info: dict,
                             con_in_info: dict):
        actual_dependencies = dict()
        chan_deps = list()
        rec_deps = list()
        conc_deps = list()
        con_in_deps = list()
        for pot_dep, dep_info in syns_info["PotentialDependencies"].items():
            for channel_name, channel_info in chan_info.items():
                if pot_dep == channel_name:
                    chan_deps.append(channel_info["root_expression"])
            for receptor_name, receptor_info in recs_info.items():
                if pot_dep == receptor_name:
                    rec_deps.append(receptor_info["root_expression"])
            for concentration_name, concentration_info in conc_info.items():
                if pot_dep == concentration_name:
                    conc_deps.append(concentration_info["root_expression"])
            for continuous_name, continuous_info in con_in_info.items():
                if pot_dep == continuous_name:
                    con_in_deps.append(continuous_info["root_expression"])

        actual_dependencies["channels"] = chan_deps
        actual_dependencies["receptors"] = rec_deps
        actual_dependencies["concentrations"] = conc_deps
        actual_dependencies["continuous"] = con_in_deps
        syns_info["Dependencies"] = actual_dependencies
        return syns_info

    @classmethod
    def extract_infunction_declarations(cls, syn_info):
        pre_spike_function = syn_info["PreSpikeFunction"]
        post_spike_function = syn_info["PostSpikeFunction"]
        update_block = syn_info["UpdateBlock"]
        # general_functions = syn_info["Functions"]
        declaration_visitor = ASTDeclarationCollectorAndUniqueRenamerVisitor()
        if pre_spike_function is not None:
            pre_spike_function.accept(declaration_visitor)
        if post_spike_function is not None:
            post_spike_function.accept(declaration_visitor)
        if update_block is not None:
            update_block.accept(declaration_visitor)

        declaration_vars = list()
        for decl in declaration_visitor.declarations:
            for var in decl.get_variables():
                declaration_vars.append(var.get_name())

        syn_info["InFunctionDeclarationsVars"] = declaration_visitor.declarations  # list(declaration_vars)
        return syn_info

    @classmethod
    def transform_convolutions_analytic_solutions(cls, neuron: ASTModel, cm_syns_info: dict):

        enriched_syns_info = copy.copy(cm_syns_info)
        for convolution_name in cm_syns_info["convolutions"].keys():
            analytic_solution = enriched_syns_info[
                "convolutions"][convolution_name]["analytic_solution"]
            analytic_solution_transformed = defaultdict(
                lambda: defaultdict())

            for variable_name, expression_str in analytic_solution["initial_values"].items():
                variable = neuron.get_equations_blocks()[0].get_scope().resolve_to_symbol(variable_name,
                                                                                          SymbolKind.VARIABLE)
                if variable is None:
                    ASTUtils.add_declarations_to_internals(
                        neuron, analytic_solution["initial_values"])
                    variable = neuron.get_equations_blocks()[0].get_scope().resolve_to_symbol(
                        variable_name,
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
                variable = neuron.get_equations_blocks()[0].get_scope().resolve_to_symbol(variable_name,
                                                                                          SymbolKind.VARIABLE)
                if variable is None:
                    ASTUtils.add_declarations_to_internals(
                        neuron, analytic_solution["propagators"])
                    variable = neuron.get_equations_blocks()[0].get_scope().resolve_to_symbol(
                        variable_name,
                        SymbolKind.VARIABLE)

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

            enriched_syns_info["convolutions"][convolution_name]["analytic_solution"] = \
                analytic_solution_transformed

        transformed_inlines = dict()
        for inline in enriched_syns_info["Inlines"]:
            transformed_inlines[inline.get_variable_name()] = dict()
            transformed_inlines[inline.get_variable_name()]["inline_expression"] = \
                SynsInfoEnricherVisitor.inline_name_to_transformed_inline[inline.get_variable_name()]
            transformed_inlines[inline.get_variable_name()]["inline_expression_d"] = \
                cls.compute_expression_derivative(
                    transformed_inlines[inline.get_variable_name()]["inline_expression"])
        enriched_syns_info["Inlines"] = transformed_inlines

        # now also identify analytic helper variables such as __h
        enriched_syns_info["analytic_helpers"] = cls.get_analytic_helper_variable_declarations(
            enriched_syns_info)

        neuron.accept(ASTParentVisitor())

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
    def get_new_variables_after_transformation(cls, single_synapse_info):
        total = set()
        if "total_used_declared" in single_synapse_info:
            total = single_synapse_info["total_used_declared"]
        return cls.get_all_synapse_variables(single_synapse_info).difference(
            total)

    @classmethod
    def get_all_synapse_variables(cls, single_synapse_info):
        """returns all variable names referenced by the synapse inline
        and by the analytical solution
        assumes that the model has already been transformed"""

        inline_variables = set()
        for inline_name, inline in single_synapse_info["Inlines"].items():
            inline_variables = cls.get_variable_names_used(inline["inline_expression"])

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
    def get_variable_names_used(cls, node) -> set:
        variable_names_extractor = ASTUsedVariableNamesExtractor(node)
        return variable_names_extractor.variable_names


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


class ASTDeclarationCollectorAndUniqueRenamerVisitor(ASTVisitor):
    def __init__(self):
        super(ASTDeclarationCollectorAndUniqueRenamerVisitor, self).__init__()
        self.declarations = list()
        self.variable_names = dict()
        self.inside_declaration = False
        self.inside_block = False
        self.current_block = None

    def visit_block(self, node):
        self.inside_block = True
        self.current_block = node

    def endvisit_block(self, node):
        self.inside_block = False
        self.current_block = None

    def visit_declaration(self, node):
        self.inside_declaration = True
        for variable in node.get_variables():
            if variable.get_name() in self.variable_names:
                self.variable_names[variable.get_name()] += 1
            else:
                self.variable_names[variable.get_name()] = 0
            new_name = variable.get_name() + '_' + str(self.variable_names[variable.get_name()])
            name_replacer = ASTVariableNameReplacerVisitor(variable.get_name(), new_name)
            self.current_block.accept(name_replacer)
        node.accept(ASTSymbolTableVisitor())
        self.declarations.append(node.clone())

    def endvisit_declaration(self, node):
        self.inside_declaration = False


class ASTVariableNameReplacerVisitor(ASTVisitor):
    def __init__(self, old_name, new_name):
        super(ASTVariableNameReplacerVisitor, self).__init__()
        self.inside_variable = False
        self.new_name = new_name
        self.old_name = old_name

    def visit_variable(self, node):
        self.inside_variable = True
        if node.get_name() == self.old_name:
            node.set_name(self.new_name)

    def endvisit_variable(self, node):
        self.inside_variable = False


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
