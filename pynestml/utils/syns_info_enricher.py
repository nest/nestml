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

from collections import defaultdict

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
    def enrich_with_additional_info(cls, synapse: ASTModel, syns_info: dict, chan_info: dict, recs_info: dict, conc_info: dict, con_in_info: dict):
        syns_info = cls.transform_ode_solutions(synapse, syns_info)
        syns_info = cls.confirm_dependencies(syns_info, chan_info, recs_info, conc_info, con_in_info)

        return syns_info


    @classmethod
    def transform_ode_solutions(cls, synapse, syns_info):
        for ode_var_name, ode_info in syns_info["ODEs"].items():
            syns_info["ODEs"][ode_var_name]["transformed_solutions"] = list()

            for ode_solution_index in range(len(ode_info["ode_toolbox_output"])):
                solution_transformed = defaultdict()
                solution_transformed["states"] = defaultdict()
                solution_transformed["propagators"] = defaultdict()

                for variable_name, rhs_str in ode_info["ode_toolbox_output"][ode_solution_index][
                    "initial_values"].items():
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
                for variable_name, rhs_str in ode_info["ode_toolbox_output"][ode_solution_index][
                    "propagators"].items():
                    prop_variable = synapse.get_equations_blocks()[0].get_scope().resolve_to_symbol(variable_name,
                                                                                                   SymbolKind.VARIABLE)
                    if prop_variable is None:
                        ASTUtils.add_declarations_to_internals(
                            synapse, ode_info["ode_toolbox_output"][ode_solution_index]["propagators"])
                        prop_variable = synapse.get_equations_blocks()[0].get_scope().resolve_to_symbol(
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
    def confirm_dependencies(cls, syns_info: dict, chan_info: dict, recs_info: dict, conc_info: dict, con_in_info: dict):
        actual_dependencies = list()
        for pot_dep in syns_info["PotentialDependencies"]:
            mechanism_names = list(chan_info.keys()) + list(recs_info.keys()) + list(conc_info.keys()) + list(con_in_info.keys())
            if pot_dep in mechanism_names:
                actual_dependencies.append(pot_dep)

        syns_info["Dependencies"] = actual_dependencies
        return syns_info




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