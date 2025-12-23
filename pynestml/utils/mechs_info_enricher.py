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
import copy
from collections import defaultdict

from odetoolbox import analysis
from pynestml.cocos.co_cos_manager import CoCosManager

from pynestml.symbol_table.symbol_table import SymbolTable

from pynestml.codegeneration.printers.sympy_simple_expression_printer import SympySimpleExpressionPrinter
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression

from pynestml.meta_model.ast_small_stmt import ASTSmallStmt

from pynestml.codegeneration.printers.ode_toolbox_expression_printer import ODEToolboxExpressionPrinter

from pynestml.codegeneration.printers.ode_toolbox_function_call_printer import ODEToolboxFunctionCallPrinter

from pynestml.codegeneration.printers.ode_toolbox_variable_printer import ODEToolboxVariablePrinter

from pynestml.codegeneration.printers.constant_printer import ConstantPrinter

from pynestml.codegeneration.printers.nestml_printer import NESTMLPrinter

from pynestml.meta_model.ast_inline_expression import ASTInlineExpression
from pynestml.meta_model.ast_model import ASTModel
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.symbols.symbol import SymbolKind
from pynestml.utils.ast_vector_parameter_setter_and_printer_factory import ASTVectorParameterSetterAndPrinterFactory
from pynestml.visitors.ast_parent_visitor import ASTParentVisitor
from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor
from pynestml.utils.ast_utils import ASTUtils
from pynestml.utils.model_parser import ModelParser
from pynestml.visitors.ast_visitor import ASTVisitor


class MechsInfoEnricher:
    """
    This file is part of the compartmental code generation process.

    Adds information collection that can't be done in the processing class since that is used in the cocos.
    Here we use the ModelParser which would lead to a cyclic dependency.
    """

    # ODE-toolbox printers
    _constant_printer = ConstantPrinter()
    _ode_toolbox_variable_printer = ODEToolboxVariablePrinter(None)
    _ode_toolbox_function_call_printer = ODEToolboxFunctionCallPrinter(None)
    _ode_toolbox_printer = ODEToolboxExpressionPrinter(
        simple_expression_printer=SympySimpleExpressionPrinter(
            variable_printer=_ode_toolbox_variable_printer,
            constant_printer=_constant_printer,
            function_call_printer=_ode_toolbox_function_call_printer))

    _ode_toolbox_variable_printer._expression_printer = _ode_toolbox_printer
    _ode_toolbox_function_call_printer._expression_printer = _ode_toolbox_printer

    def __init__(self):
        pass

    @classmethod
    def enrich_with_additional_info(cls, neuron: ASTModel, mechs_info: dict):
        neuron.accept(SynsInfoEnricherVisitor())
        mechs_info = cls.get_transformed_ode_equations(mechs_info)
        mechs_info = cls.ode_toolbox_processing(neuron, mechs_info)

        cls.add_propagators_to_internals(neuron, mechs_info)
        neuron.accept(SynsInfoEnricherVisitor())

        mechs_info = cls.transform_ode_solutions(neuron, mechs_info)
        mechs_info = cls.transform_convolutions_analytic_solutions_generall(neuron, mechs_info)
        mechs_info = cls.enrich_mechanism_specific(neuron, mechs_info)
        return mechs_info

    @classmethod
    def get_transformed_ode_equations(cls, mechs_info: dict):
        enriched_mechs_info = copy.copy(mechs_info)
        for mechanism_name, mechanism_info in mechs_info.items():
            transformed_odes = list()
            for ode in mechs_info[mechanism_name]["ODEs"]:
                ode_name = ode.lhs.name
                transformed_odes.append(
                    SynsInfoEnricherVisitor.ode_name_to_transformed_ode[ode_name])
            enriched_mechs_info[mechanism_name]["ODEs"] = transformed_odes

        return enriched_mechs_info

    @classmethod
    def ode_toolbox_processing(cls, neuron, mechs_info):
        mechs_info = cls.prepare_equations_for_ode_toolbox(neuron, mechs_info)
        mechs_info = cls.collect_raw_odetoolbox_output(mechs_info)
        return mechs_info

    @classmethod
    def prepare_equations_for_ode_toolbox(cls, neuron, mechs_info):
        """Transforms the collected ode equations to the required input format of ode-toolbox and adds it to the
        mechs_info dictionary"""
        for mechanism_name, mechanism_info in mechs_info.items():
            mechanism_odes = defaultdict()
            for ode in mechanism_info["ODEs"]:
                nestml_printer = NESTMLPrinter()
                ode_nestml_expression = nestml_printer.print_ode_equation(ode)
                mechanism_odes[ode.lhs.name] = defaultdict()
                mechanism_odes[ode.lhs.name]["ASTOdeEquation"] = ode
                mechanism_odes[ode.lhs.name]["ODENestmlExpression"] = ode_nestml_expression
            mechs_info[mechanism_name]["ODEs"] = mechanism_odes

        for mechanism_name, mechanism_info in mechs_info.items():
            for ode_variable_name, ode_info in mechanism_info["ODEs"].items():
                # Expression:
                odetoolbox_indict = {"dynamics": []}
                lhs = ASTUtils.to_ode_toolbox_name(ode_info["ASTOdeEquation"].get_lhs().get_complete_name())
                rhs = cls._ode_toolbox_printer.print(ode_info["ASTOdeEquation"].get_rhs())
                entry = {"expression": lhs + " = " + rhs, "initial_values": {}}

                # Initial values:
                symbol_order = ode_info["ASTOdeEquation"].get_lhs().get_differential_order()
                for order in range(symbol_order):
                    iv_symbol_name = ode_info["ASTOdeEquation"].get_lhs().get_name() + "'" * order
                    initial_value_expr = neuron.get_initial_value(iv_symbol_name)
                    entry["initial_values"][
                        ASTUtils.to_ode_toolbox_name(iv_symbol_name)] = cls._ode_toolbox_printer.print(
                        initial_value_expr)

                odetoolbox_indict["dynamics"].append(entry)
                mechs_info[mechanism_name]["ODEs"][ode_variable_name]["ode_toolbox_input"] = odetoolbox_indict

        return mechs_info

    @classmethod
    def collect_raw_odetoolbox_output(cls, mechs_info):
        """calls ode-toolbox for each ode individually and collects the raw output"""
        for mechanism_name, mechanism_info in mechs_info.items():
            for ode_variable_name, ode_info in mechanism_info["ODEs"].items():
                solver_result = analysis(ode_info["ode_toolbox_input"], disable_stiffness_check=True)
                mechs_info[mechanism_name]["ODEs"][ode_variable_name]["ode_toolbox_output"] = solver_result

        return mechs_info

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

        neuron.accept(ASTParentVisitor())

        return mechs_info

    @classmethod
    def transform_convolutions_analytic_solutions_generall(cls, neuron: ASTModel, cm_mechs_info: dict):
        enriched_syns_info = copy.copy(cm_mechs_info)
        for mechanism_name, mechanism_info in cm_mechs_info.items():
            for convolution_name in mechanism_info["convolutions"].keys():
                analytic_solution = enriched_syns_info[mechanism_name][
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

                    mechanism_info = cls.get_time_res_var_conv_declaration(neuron, mechanism_info, expression)

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

                    mechanism_info = cls.get_time_res_var_conv_declaration(neuron, mechanism_info, expression)

                enriched_syns_info[mechanism_name]["convolutions"][convolution_name]["analytic_solution"] = \
                    analytic_solution_transformed

            if isinstance(enriched_syns_info[mechanism_name]["root_expression"], ASTInlineExpression):
                inline_expression_name = enriched_syns_info[mechanism_name]["root_expression"].variable_name
                enriched_syns_info[mechanism_name]["root_expression"] = \
                    SynsInfoEnricherVisitor.inline_name_to_transformed_inline[inline_expression_name]

            transformed_inlines = list()
            for inline in cm_mechs_info[mechanism_name]["SecondaryInlineExpressions"]:
                inline_expression_name = inline.variable_name
                transformed_inlines.append(
                    SynsInfoEnricherVisitor.inline_name_to_transformed_inline[inline_expression_name])
            enriched_syns_info[mechanism_name]["secondary_inline_expressions"] = transformed_inlines

        return enriched_syns_info

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
        return cls.get_all_synapse_variables(single_synapse_info).difference(
            single_synapse_info["total_used_declared"])

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
    def get_variable_names_used(cls, node) -> set:
        variable_names_extractor = ASTUsedVariableNamesExtractor(node)
        return variable_names_extractor.variable_names

    @classmethod
    def get_time_res_var_conv_declaration(cls, neuron, mechanism_info, expression):
        expression_variable_collector = ASTEnricherInfoCollectorVisitor()
        expression.accept(expression_variable_collector)

        # now also identify analytic helper variables such as __h
        neuron_internal_declaration_collector = ASTEnricherInfoCollectorVisitor()
        neuron.accept(neuron_internal_declaration_collector)

        for variable in expression_variable_collector.all_variables:
            for internal_declaration in neuron_internal_declaration_collector.internal_declarations:
                if variable.get_name() == internal_declaration.get_variables()[0].get_name() \
                        and (isinstance(internal_declaration.get_expression(), ASTSmallStmt)
                             or isinstance(internal_declaration.get_expression(), ASTSimpleExpression)) \
                        and internal_declaration.get_expression().is_function_call() \
                        and internal_declaration.get_expression().get_function_call().callee_name == \
                        PredefinedFunctions.TIME_RESOLUTION:
                    mechanism_info["time_resolution_var"] = variable

        return mechanism_info

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


class SynsInfoEnricherVisitor(ASTVisitor):
    variables_to_internal_declarations = {}
    internal_variable_name_to_variable = {}
    inline_name_to_transformed_inline = {}
    ode_name_to_transformed_ode = {}

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
        self.inside_ode_equation = False

    def visit_inline_expression(self, node):
        self.inside_inline_expression = True
        inline_name = node.variable_name
        SynsInfoEnricherVisitor.inline_name_to_transformed_inline[inline_name] = node

    def endvisit_inline_expression(self, node):
        self.inside_inline_expression = False

    def visit_ode_equation(self, node):
        self.inside_ode_equation = True
        ode_name = node.lhs.name
        SynsInfoEnricherVisitor.ode_name_to_transformed_ode[ode_name] = node

    def endvisit_ode_equation(self, node):
        self.inside_ode_equation = False

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
