# -*- coding: utf-8 -*-
#
# global_info_enricher.py
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

from collections import defaultdict

from executing.executing import node_linenos

from pynestml.meta_model.ast_model import ASTModel
from pynestml.visitors.ast_parent_visitor import ASTParentVisitor
from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor
from pynestml.utils.ast_utils import ASTUtils
from pynestml.visitors.ast_visitor import ASTVisitor
from pynestml.utils.model_parser import ModelParser
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.symbols.symbol import SymbolKind

from collections import defaultdict


class GlobalInfoEnricher:
    """
    Adds information collection that can't be done in the processing class since that is used in the cocos.
    Here we use the ModelParser which would lead to a cyclic dependency.

    Additionally, we require information about the paired neurons mechanism to confirm what dependencies are actually existent in the neuron.
    """

    def __init__(self):
        pass

    @classmethod
    def enrich_with_additional_info(cls, neuron: ASTModel, global_info: dict):
        global_info = cls.transform_ode_solutions(neuron, global_info)
        global_info = cls.extract_infunction_declarations(global_info)
        #global_info = cls.substituteNoneWithEmptyBlocks(global_info)

        return global_info

    @classmethod
    def transform_ode_solutions(cls, neuron, global_info):
        for ode_var_name, ode_info in global_info["ODEs"].items():
            global_info["ODEs"][ode_var_name]["transformed_solutions"] = list()

            for ode_solution_index in range(len(ode_info["ode_toolbox_output"])):
                solution_transformed = defaultdict()
                solution_transformed["states"] = defaultdict()
                solution_transformed["propagators"] = defaultdict()

                for variable_name, rhs_str in ode_info["ode_toolbox_output"][ode_solution_index][
                    "initial_values"].items():
                    variable = neuron.get_equations_blocks()[0].get_scope().resolve_to_symbol(variable_name,
                                                                                              SymbolKind.VARIABLE)

                    expression = ModelParser.parse_expression(rhs_str)
                    # pretend that update expressions are in "equations" block,
                    # which should always be present, as neurons have been
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
                for variable_name, rhs_str in ode_info["ode_toolbox_output"][ode_solution_index][
                    "propagators"].items():
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
                    # which should always be present, as neurons have been
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
                                global_info["time_resolution_var"] = variable

                global_info["ODEs"][ode_var_name]["transformed_solutions"].append(solution_transformed)

        neuron.accept(ASTParentVisitor())

        return global_info

    @classmethod
    def extract_infunction_declarations(cls, global_info):
        declaration_visitor = ASTDeclarationCollectorAndUniqueRenamerVisitor()
        if "SelfSpikesFunction" in global_info and global_info["SelfSpikesFunction"] is not None:
            self_spike_function = global_info["SelfSpikesFunction"]
            self_spike_function.accept(declaration_visitor)
        if "UpdateBlock" in global_info and global_info["UpdateBlock"] is not None:
            update_block = global_info["UpdateBlock"]
            update_block.accept(declaration_visitor)

        declaration_vars = list()
        for decl in declaration_visitor.declarations:
            for var in decl.get_variables():
                declaration_vars.append(var.get_name())

        global_info["InFunctionDeclarationsVars"] = declaration_visitor.declarations
        return global_info

    @classmethod
    def substituteNoneWithEmptyBlocks(cls, global_info):
        if (not "UpdateBlock" in global_info) or (global_info["UpdateBlock"] is None):
            empty = ModelParser.parse_block("")
            global_info["UpdateBlock"] = empty.clone()
        if (not "SelfSpikesFunction" in global_info) or (global_info["SelfSpikesFunction"] is None):
            empty = ModelParser.parse_block("")
            global_info["SelfSpikesFunction"] = empty.clone()

        return global_info

    @classmethod
    def compute_update_block_variations(cls, info_collector, mechs_info, global_info):
        if global_info["UpdateBlock"] is not None:
            info_collector.collect_update_block_dependencies_and_owned(mechs_info, global_info)
            global_info["UpdateBlock"] = info_collector.recursive_update_block_reduction(mechs_info, [],
                                                                                         global_info["UpdateBlock"])



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