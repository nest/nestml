from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.utils.model_parser import ModelParser
from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor
from pynestml.symbols.symbol import SymbolKind
from pynestml.visitors.ast_visitor import ASTVisitor
from pynestml.symbols.predefined_functions import PredefinedFunctions
from collections import defaultdict
import copy

class MechsInfoEnricher():

    def __init__(self, params):
        pass

    @classmethod
    def enrich_with_additional_info(cls, neuron: ASTNeuron, mechs_info: dict):
        mechs_info = cls.transform_ode_solutions(neuron, mechs_info)
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

                    for variable_name, rhs_str in ode_info["ode_toolbox_output"][ode_solution_index][
                        "initial_values"].items():
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
                    for variable_name, rhs_str in ode_info["ode_toolbox_output"][ode_solution_index][
                        "propagators"].items(
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

                        neuron_internal_declaration_collector = ASTEnricherInfoCollectorVisitor()
                        neuron.accept(neuron_internal_declaration_collector)

                        # print("TRV: " + PredefinedFunctions.TIME_RESOLUTION)
                        for variable in expression_variable_collector.all_variables:
                            for internal_declaration in neuron_internal_declaration_collector.internal_declarations:
                                # print(internal_declaration.get_variables()[0].get_name())
                                # print(internal_declaration.get_expression().callee_name)
                                if variable.get_name() == internal_declaration.get_variables()[0].get_name() \
                                        and internal_declaration.get_expression().is_function_call() \
                                        and internal_declaration.get_expression().get_function_call().callee_name == PredefinedFunctions.TIME_RESOLUTION:
                                    mechanism_info["time_resolution_var"] = variable  # not so sensible (predefined) :D

                    mechanism_info["ODEs"][ode_var_name]["transformed_solutions"].append(solution_transformed)

        return mechs_info

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