# -*- coding: utf-8 -*-
#
# ast_mechanism_information_collector.py
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

from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.meta_model.ast_inline_expression import ASTInlineExpression
from pynestml.meta_model.ast_kernel import ASTKernel
from pynestml.symbols.predefined_units import PredefinedUnits
from pynestml.visitors.ast_parent_visitor import ASTParentVisitor
from pynestml.visitors.ast_visitor import ASTVisitor


class ASTMechanismInformationCollector(object):
    """
    This file is part of the compartmental code generation process.

    This class contains all basic mechanism information collection. Further collectors may be implemented to collect
    further information for specific mechanism types (example: ASTReceptorInformationCollector)
    """
    collector_visitor = None
    neuron = None

    @classmethod
    def __init__(cls, neuron):
        cls.neuron = neuron
        cls.collector_visitor = ASTMechanismInformationCollectorVisitor()
        neuron.accept(cls.collector_visitor)

    @classmethod
    def detect_mechs(cls, mech_type: str):
        """Detects the root expressions (either ode or inline) of the given type and returns the initial
        info dictionary"""
        mechs_info = defaultdict()
        if not FrontendConfiguration.get_target_platform().upper() == 'NEST_COMPARTMENTAL':
            return mechs_info

        mechanism_expressions = cls.collector_visitor.inlinesInEquationsBlock
        for mechanism_expression in mechanism_expressions:
            if "mechanism::" + mech_type in [(e.namespace + "::" + e.name) for e in
                                             mechanism_expression.get_decorators()]:
                mechanism_name = mechanism_expression.variable_name
                mechs_info[mechanism_name] = defaultdict()
                mechs_info[mechanism_name]["root_expression"] = mechanism_expression

        mechanism_expressions = cls.collector_visitor.odes
        for mechanism_expression in mechanism_expressions:
            if "mechanism::" + mech_type in [(e.namespace + "::" + e.name) for e in
                                             mechanism_expression.get_decorators()]:
                mechanism_name = mechanism_expression.lhs.name
                mechs_info[mechanism_name] = defaultdict()
                mechs_info[mechanism_name]["root_expression"] = mechanism_expression

        return mechs_info

    @classmethod
    def extend_variable_list_name_based_restricted(cls, extended_list, appending_list, restrictor_list):
        """go through appending_list and append every variable that is not in restrictor_list to extended_list for the
         purpose of not re-searching the same variable"""
        for app_item in appending_list:
            appendable = True
            for rest_item in restrictor_list:
                if rest_item.name == app_item.name:
                    appendable = False
                    break
            if appendable:
                extended_list.append(app_item)

        return extended_list

    @classmethod
    def extend_function_call_list_name_based_restricted(cls, extended_list, appending_list, restrictor_list):
        """go through appending_list and append every variable that is not in restrictor_list to extended_list for the
        purpose of not re-searching the same function"""
        for app_item in appending_list:
            appendable = True
            for rest_item in restrictor_list:
                if rest_item.callee_name == app_item.callee_name:
                    appendable = False
                    break
            if appendable:
                extended_list.append(app_item)

        return extended_list

    @classmethod
    def extend_variables_with_initialisations(cls, neuron, mechs_info):
        """collects initialization expressions for all variables and parameters contained in mechs_info"""
        for mechanism_name, mechanism_info in mechs_info.items():
            var_init_visitor = VariableInitializationVisitor(mechanism_info)
            neuron.accept(var_init_visitor)
            mechs_info[mechanism_name]["States"] = var_init_visitor.states
            mechs_info[mechanism_name]["Parameters"] = var_init_visitor.parameters
            mechs_info[mechanism_name]["Internals"] = var_init_visitor.internals

        return mechs_info

    @classmethod
    def collect_mechanism_related_definitions(cls, neuron, mechs_info, global_info, mech_type: str):
        """Collects all parts of the nestml code the root expressions previously collected depend on. search
        is cut at other mechanisms root expressions"""
        from pynestml.meta_model.ast_inline_expression import ASTInlineExpression
        from pynestml.meta_model.ast_ode_equation import ASTOdeEquation

        if "Dependencies" not in global_info:
            global_info["Dependencies"] = dict()

        for mechanism_name, mechanism_info in mechs_info.items():
            if mech_type not in global_info["Dependencies"]:
                global_info["Dependencies"][mech_type] = dict()
            global_info["Dependencies"][mech_type][mechanism_name] = list()

            variable_collector = ASTVariableCollectorVisitor()
            neuron.accept(variable_collector)
            global_states = variable_collector.all_states
            global_parameters = variable_collector.all_parameters
            global_internals = variable_collector.all_internals

            function_collector = ASTFunctionCollectorVisitor()
            neuron.accept(function_collector)
            global_functions = function_collector.all_functions

            inline_collector = ASTInlineEquationCollectorVisitor()
            neuron.accept(inline_collector)
            global_inlines = inline_collector.all_inlines

            ode_collector = ASTODEEquationCollectorVisitor()
            neuron.accept(ode_collector)
            global_odes = ode_collector.all_ode_equations

            kernel_collector = ASTKernelCollectorVisitor()
            neuron.accept(kernel_collector)
            global_kernels = kernel_collector.all_kernels

            continuous_input_collector = ASTContinuousInputDeclarationVisitor()
            neuron.accept(continuous_input_collector)
            global_continuous_inputs = continuous_input_collector.ports

            mechanism_states = list()
            mechanism_parameters = list()
            mechanism_internals = list()
            mechanism_functions = list()
            mechanism_inlines = list()
            mechanism_odes = list()
            synapse_kernels = list()
            mechanism_continuous_inputs = list()
            mechanism_dependencies = defaultdict()
            mechanism_dependencies["concentrations"] = list()
            mechanism_dependencies["channels"] = list()
            mechanism_dependencies["receptors"] = list()
            mechanism_dependencies["continuous"] = list()
            mechanism_dependencies["global"] = list()

            found_variables = list()
            found_functions = list()

            local_variable_collector = ASTVariableCollectorVisitor()
            mechs_info[mechanism_name]["root_expression"].accept(local_variable_collector)
            search_variables = local_variable_collector.all_variables

            local_function_call_collector = ASTFunctionCallCollectorVisitor()
            mechs_info[mechanism_name]["root_expression"].accept(local_function_call_collector)
            search_functions = local_function_call_collector.all_function_calls

            while len(search_functions) > 0 or len(search_variables) > 0:
                if len(search_functions) > 0:
                    function_call = search_functions[0]
                    for function in global_functions:
                        if function.name == function_call.callee_name:
                            mechanism_functions.append(function)
                            found_functions.append(function_call)

                            local_variable_collector = ASTVariableCollectorVisitor()
                            function.accept(local_variable_collector)
                            search_variables = cls.extend_variable_list_name_based_restricted(search_variables,
                                                                                              local_variable_collector.all_variables,
                                                                                              search_variables + found_variables)

                            local_function_call_collector = ASTFunctionCallCollectorVisitor()
                            function.accept(local_function_call_collector)
                            search_functions = cls.extend_function_call_list_name_based_restricted(search_functions,
                                                                                                   local_function_call_collector.all_function_calls,
                                                                                                   search_functions + found_functions)
                            # IMPLEMENT CATCH NONDEFINED!!!
                    search_functions.remove(function_call)

                elif len(search_variables) > 0:
                    variable = search_variables[0]
                    from pynestml.symbols.symbol import SymbolKind
                    if (not (variable.name == "v_comp" or variable.get_scope().resolve_to_symbol(variable.name, SymbolKind.VARIABLE) is None)):
                        is_dependency = False
                        for inline in global_inlines:
                            if variable.name == inline.variable_name:
                                if isinstance(inline.get_decorators(), list):
                                    if "mechanism" in [e.namespace for e in inline.get_decorators()]:
                                        is_dependency = True
                                        if not (isinstance(mechanism_info["root_expression"],
                                                           ASTInlineExpression) and inline.variable_name == mechanism_info["root_expression"].variable_name):
                                            if "channel" in [e.name for e in inline.get_decorators()]:
                                                if not inline.variable_name in [i.variable_name for i in
                                                                                mechanism_dependencies["channels"]]:
                                                    mechanism_dependencies["channels"].append(inline)
                                            if "receptor" in [e.name for e in inline.get_decorators()]:
                                                if not inline.variable_name in [i.variable_name for i in
                                                                                mechanism_dependencies["receptors"]]:
                                                    mechanism_dependencies["receptors"].append(inline)
                                            if "continuous" in [e.name for e in inline.get_decorators()]:
                                                if not inline.variable_name in [i.variable_name for i in
                                                                                mechanism_dependencies["continuous"]]:
                                                    mechanism_dependencies["continuous"].append(inline)

                                if not is_dependency:
                                    mechanism_inlines.append(inline)

                                    local_variable_collector = ASTVariableCollectorVisitor()
                                    inline.accept(local_variable_collector)
                                    search_variables = cls.extend_variable_list_name_based_restricted(search_variables,
                                                                                                      local_variable_collector.all_variables,
                                                                                                      search_variables + found_variables)

                                    local_function_call_collector = ASTFunctionCallCollectorVisitor()
                                    inline.accept(local_function_call_collector)
                                    search_functions = cls.extend_function_call_list_name_based_restricted(
                                        search_functions,
                                        local_function_call_collector.all_function_calls,
                                        search_functions + found_functions)

                        for ode in global_odes:
                            if variable.name == ode.lhs.name:
                                if ode.lhs.name in global_info["States"]:
                                    global_info["Dependencies"][mech_type][mechanism_name].append(ode.lhs)
                                    del global_info["States"][ode.lhs.name]
                                    # is_dependency = True
                                if isinstance(ode.get_decorators(), list):
                                    if "mechanism" in [e.namespace for e in ode.get_decorators()]:
                                        is_dependency = True
                                        if not (isinstance(mechanism_info["root_expression"],
                                                           ASTOdeEquation) and ode.lhs.name == mechanism_info["root_expression"].lhs.name):
                                            if "concentration" in [e.name for e in ode.get_decorators()]:
                                                if not ode.lhs.name in [o.lhs.name for o in mechanism_dependencies["concentrations"]]:
                                                    mechanism_dependencies["concentrations"].append(ode)

                                if not is_dependency:
                                    mechanism_odes.append(ode)

                                    local_variable_collector = ASTVariableCollectorVisitor()
                                    ode.accept(local_variable_collector)
                                    search_variables = cls.extend_variable_list_name_based_restricted(search_variables,
                                                                                                      local_variable_collector.all_variables,
                                                                                                      search_variables + found_variables)

                                    local_function_call_collector = ASTFunctionCallCollectorVisitor()
                                    ode.accept(local_function_call_collector)
                                    search_functions = cls.extend_function_call_list_name_based_restricted(
                                        search_functions,
                                        local_function_call_collector.all_function_calls,
                                        search_functions + found_functions)

                        for state_name, state in global_states.items():
                            if variable.name == state_name:
                                if state["ASTVariable"] in global_info["States"]:
                                    mechanism_dependencies["global"].append(state["ASTVariable"])
                                    global_info["Dependencies"][mech_type][mechanism_name].append(state["ASTVariable"])
                                    del global_info["States"][state_name]

                                if not is_dependency:
                                    mechanism_states.append(state["ASTVariable"])

                        for parameter_name, parameter in global_parameters.items():
                            if variable.name == parameter_name:
                                mechanism_parameters.append(parameter["ASTVariable"])

                        for internal_name, internal in global_internals.items():
                            if variable.name == internal_name:
                                mechanism_internals.append(internal["ASTVariable"])

                                local_variable_collector = ASTVariableCollectorVisitor()
                                internal["ASTExpression"].accept(local_variable_collector)
                                search_variables = cls.extend_variable_list_name_based_restricted(search_variables,
                                                                                                  local_variable_collector.all_variables,
                                                                                                  search_variables + found_variables)

                                local_function_call_collector = ASTFunctionCallCollectorVisitor()
                                internal["ASTExpression"].accept(local_function_call_collector)
                                search_functions = cls.extend_function_call_list_name_based_restricted(search_functions,
                                                                                                       local_function_call_collector.all_function_calls,
                                                                                                       search_functions + found_functions)

                        for kernel in global_kernels:
                            if variable.name == kernel.get_variables()[0].name:
                                synapse_kernels.append(kernel)

                                local_variable_collector = ASTVariableCollectorVisitor()
                                kernel.accept(local_variable_collector)
                                search_variables = cls.extend_variable_list_name_based_restricted(search_variables,
                                                                                                  local_variable_collector.all_variables,
                                                                                                  search_variables + found_variables)

                                local_function_call_collector = ASTFunctionCallCollectorVisitor()
                                kernel.accept(local_function_call_collector)
                                search_functions = cls.extend_function_call_list_name_based_restricted(search_functions,
                                                                                                       local_function_call_collector.all_function_calls,
                                                                                                       search_functions + found_functions)

                        for input in global_continuous_inputs:
                            if variable.name == input.name:
                                mechanism_continuous_inputs.append(input)

                    search_variables.remove(variable)
                    found_variables.append(variable)

            mechs_info[mechanism_name]["States"] = mechanism_states
            mechs_info[mechanism_name]["Parameters"] = mechanism_parameters
            mechs_info[mechanism_name]["Internals"] = mechanism_internals
            mechs_info[mechanism_name]["Functions"] = mechanism_functions
            mechs_info[mechanism_name]["SecondaryInlineExpressions"] = mechanism_inlines
            mechs_info[mechanism_name]["ODEs"] = mechanism_odes
            mechs_info[mechanism_name]["Continuous"] = mechanism_continuous_inputs
            mechs_info[mechanism_name]["Dependencies"] = mechanism_dependencies

        return mechs_info

    @classmethod
    def collect_kernels(cls, neuron, mechs_info):
        """
        Collect internals, kernels, inputs and convolutions associated with the synapse.
        """
        for mechanism_name, mechanism_info in mechs_info.items():
            mechanism_info["convolutions"] = defaultdict()
            info_collector = ASTKernelInformationCollectorVisitor()
            neuron.accept(info_collector)

            inlines = copy.copy(mechanism_info["SecondaryInlineExpressions"])
            if isinstance(mechanism_info["root_expression"], ASTInlineExpression):
                inlines.append(mechanism_info["root_expression"])
            for inline in inlines:
                kernel_arg_pairs = info_collector.get_extracted_kernel_args_by_name(
                    inline.get_variable_name())
                for kernel_var, spikes_var in kernel_arg_pairs:
                    kernel_name = kernel_var.get_name()
                    spikes_name = spikes_var.get_name()
                    convolution_name = info_collector.construct_kernel_X_spike_buf_name(
                        kernel_name, spikes_name, 0)
                    mechanism_info["convolutions"][convolution_name] = {
                        "kernel": {
                            "name": kernel_name,
                            "ASTKernel": info_collector.get_kernel_by_name(kernel_name),
                        },
                        "spikes": {
                            "name": spikes_name,
                            "ASTInputPort": info_collector.get_input_port_by_name(spikes_name),
                        },
                    }
        return mechs_info

    @classmethod
    def collect_block_dependencies_and_owned(cls, mech_info, blocks, block_type):
        block = blocks[0].clone()
        blocks.pop(0)
        for next_block in blocks:
            block.stmts += next_block.stmts

        block.accept(ASTParentVisitor())

        for mechanism_name, mechanism_info in mech_info.items():
            dependencies = list()
            updated_dependencies = list()
            owned = list()
            updated_owned = mechanism_info["States"] + mechanism_info["Parameters"] + mechanism_info["Internals"]

            loop_counter = 0
            while set([v.get_name() for v in owned]) != set([v.get_name() for v in updated_owned]) or set(
                    [v.get_name() for v in dependencies]) != set([v.get_name() for v in updated_dependencies]):
                owned = updated_owned
                dependencies = updated_dependencies
                collector = ASTUpdateBlockDependencyAndOwnedExtractor(owned, dependencies)
                block.accept(collector)
                updated_owned = collector.owned
                updated_dependencies = collector.dependencies
                loop_counter += 1

            mechanism_info["Blocks"] = dict()
            mechanism_info["Blocks"]["dependencies"] = dependencies
            mechanism_info["Blocks"]["owned"] = owned

    @classmethod
    def block_reduction(cls, mech_info, block, block_type):
        for mechanism_name, mechanism_info in mech_info.items():
            owned = mechanism_info["Blocks"]["owned"]
            dependencies = mechanism_info["Blocks"]["dependencies"]
            new_update_block = block.clone()
            new_update_block.accept(ASTParentVisitor())
            update_block_reductor = ASTUpdateBlockReductor(owned, dependencies)
            new_update_block.accept(update_block_reductor)
            mechanism_info["Blocks"][block_type] = new_update_block

    @classmethod
    def recursive_update_block_reduction(cls, mech_info, eliminated, update_block):
        reduced_update_blocks = dict()
        reduced_update_blocks["Block"] = update_block
        reduced_update_blocks["Reductions"] = dict()
        for mechanism_name, mechanism_info in mech_info.items():
            if mechanism_name not in eliminated:
                if "UpdateBlockComputation" in mechanism_info:
                    owned = mechanism_info["UpdateBlockComputation"]["owned"]
                    exclusive_dependencies = mechanism_info["UpdateBlockComputation"]["dependencies"]
                    leftovers_depend = False
                    for comp_mechanism_name, comp_mechanism_info in mech_info.items():
                        if mechanism_name != comp_mechanism_name:
                            if "UpdateBlockComputation" in comp_mechanism_info:
                                exclusive_dependencies = list(set(exclusive_dependencies) - set(
                                    comp_mechanism_info["UpdateBlockComputation"]["dependencies"]))
                                leftovers_depend = leftovers_depend and len(set(comp_mechanism_info["UpdateBlockComputation"]["dependencies"] + comp_mechanism_info["UpdateBlockComputation"]["owned"]) & set(owned)) > 0
                    if not leftovers_depend:
                        new_update_block = update_block.clone()
                        update_block_reductor = ASTUpdateBlockReductor(owned, exclusive_dependencies)
                        new_update_block.accept(update_block_reductor)
                        reduced_update_blocks["Reductions"][mechanism_name] = cls.recursive_update_block_reduction(
                            mech_info, eliminated.append(mechanism_name), new_update_block)

        return reduced_update_blocks


class ASTMechanismInformationCollectorVisitor(ASTVisitor):

    def __init__(self):
        super(ASTMechanismInformationCollectorVisitor, self).__init__()
        self.inEquationsBlock = False
        self.inlinesInEquationsBlock = list()
        self.odes = list()

    def visit_equations_block(self, node):
        self.inEquationsBlock = True

    def endvisit_equations_block(self, node):
        self.inEquationsBlock = False

    def visit_inline_expression(self, node):
        if self.inEquationsBlock:
            self.inlinesInEquationsBlock.append(node)

    def visit_ode_equation(self, node):
        self.odes.append(node)


# Helper collectors:
class VariableInitializationVisitor(ASTVisitor):
    def __init__(self, channel_info):
        super(VariableInitializationVisitor, self).__init__()
        self.inside_variable = False
        self.inside_declaration = False
        self.inside_parameter_block = False
        self.inside_state_block = False
        self.inside_internal_block = False
        self.inside_expression = False

        self.current_declaration = None
        self.states = defaultdict()
        self.parameters = defaultdict()
        self.internals = defaultdict()
        self.channel_info = channel_info
        self.search_vars = channel_info["States"] + channel_info["Parameters"] + channel_info["Internals"]
        if "Blocks" in channel_info:
            self.search_vars += channel_info["Blocks"]["dependencies"]
            self.search_vars += channel_info["Blocks"]["owned"]

    def visit_declaration(self, node):
        self.inside_declaration = True
        self.current_declaration = node
        for var in node.variables:
            if any(var.name == variable.name for variable in self.search_vars):
                if self.inside_state_block:
                    self.states[var.name] = defaultdict()
                    self.states[var.name]["ASTVariable"] = var.clone()
                    self.states[var.name]["rhs_expression"] = node.get_expression().clone()

                if self.inside_parameter_block:
                    self.parameters[var.name] = defaultdict()
                    self.parameters[var.name]["ASTVariable"] = var.clone()
                    self.parameters[var.name]["rhs_expression"] = node.get_expression().clone()

                if self.inside_internal_block:
                    self.internals[var.name] = defaultdict()
                    self.internals[var.name]["ASTVariable"] = var.clone()
                    self.internals[var.name]["rhs_expression"] = node.get_expression().clone()

    def endvisit_declaration(self, node):
        self.inside_declaration = False
        self.current_declaration = None

    def visit_block_with_variables(self, node):
        if node.is_state:
            self.inside_state_block = True
        if node.is_parameters:
            self.inside_parameter_block = True
        if node.is_internals:
            self.inside_internal_block = True

    def endvisit_block_with_variables(self, node):
        self.inside_state_block = False
        self.inside_parameter_block = False
        self.inside_internal_block = False

    def visit_variable(self, node):
        self.inside_variable = True

    def endvisit_variable(self, node):
        self.inside_variable = False

    def visit_expression(self, node):
        self.inside_expression = True

    def endvisit_expression(self, node):
        self.inside_expression = False


class ASTODEEquationCollectorVisitor(ASTVisitor):
    def __init__(self):
        super(ASTODEEquationCollectorVisitor, self).__init__()
        self.inside_ode_expression = False
        self.all_ode_equations = list()

    def visit_ode_equation(self, node):
        self.inside_ode_expression = True
        self.all_ode_equations.append(node.clone())

    def endvisit_ode_equation(self, node):
        self.inside_ode_expression = False


class ASTVariableCollectorVisitor(ASTVisitor):
    def __init__(self):
        super(ASTVariableCollectorVisitor, self).__init__()
        self.inside_variable = False
        self.inside_block_with_variables = False
        self.all_states = dict()
        self.all_parameters = dict()
        self.all_internals = dict()
        self.inside_states_block = False
        self.inside_parameters_block = False
        self.inside_internals_block = False
        self.inside_declaration = False
        self.inside_expression_inside_declaration = False
        self.expression_recursion = 0
        self.all_variables = list()
        self.current_declaration_expression = None

    def visit_declaration(self, node):
        self.inside_declaration = True
        if node.has_expression():
            self.current_declaration_expression = node.get_expression().clone()

    def endvisit_declaration(self, node):
        self.inside_declaration = False
        self.current_declaration_expression = None

    def visit_expression(self, node):
        if self.inside_declaration:
            self.inside_expression_inside_declaration = True
            self.expression_recursion += 1

    def endvisit_expression(self, node):
        if self.inside_declaration:
            self.expression_recursion -= 1
            if self.expression_recursion == 0:
                self.inside_expression_inside_declaration = False

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
        self.inside_internals_block = False
        self.inside_block_with_variables = False

    def visit_variable(self, node):
        self.inside_variable = True
        if not self.inside_expression_inside_declaration:
            self.all_variables.append(node.clone())
            if self.inside_states_block:
                self.all_states[node.get_name()] = {"ASTVariable": node.clone(),
                                                    "ASTExpression": self.current_declaration_expression}
            if self.inside_parameters_block:
                self.all_parameters[node.get_name()] = {"ASTVariable": node.clone(),
                                                        "ASTExpression": self.current_declaration_expression}
            if self.inside_internals_block:
                self.all_internals[node.get_name()] = {"ASTVariable": node.clone(),
                                                       "ASTExpression": self.current_declaration_expression}

    def endvisit_variable(self, node):
        self.inside_variable = False


class ASTFunctionCollectorVisitor(ASTVisitor):
    def __init__(self):
        super(ASTFunctionCollectorVisitor, self).__init__()
        self.inside_function = False
        self.all_functions = list()

    def visit_function(self, node):
        self.inside_function = True
        self.all_functions.append(node.clone())

    def endvisit_function(self, node):
        self.inside_function = False


class ASTInlineEquationCollectorVisitor(ASTVisitor):
    def __init__(self):
        super(ASTInlineEquationCollectorVisitor, self).__init__()
        self.inside_inline_expression = False
        self.all_inlines = list()

    def visit_inline_expression(self, node):
        self.inside_inline_expression = True
        self.all_inlines.append(node.clone())

    def endvisit_inline_expression(self, node):
        self.inside_inline_expression = False


class ASTFunctionCallCollectorVisitor(ASTVisitor):
    def __init__(self):
        super(ASTFunctionCallCollectorVisitor, self).__init__()
        self.inside_function_call = False
        self.all_function_calls = list()

    def visit_function_call(self, node):
        self.inside_function_call = True
        self.all_function_calls.append(node.clone())

    def endvisit_function_call(self, node):
        self.inside_function_call = False


class ASTKernelCollectorVisitor(ASTVisitor):
    def __init__(self):
        super(ASTKernelCollectorVisitor, self).__init__()
        self.inside_kernel = False
        self.all_kernels = list()

    def visit_kernel(self, node):
        self.inside_kernel = True
        self.all_kernels.append(node.clone())

    def endvisit_kernel(self, node):
        self.inside_kernel = False


class ASTContinuousInputDeclarationVisitor(ASTVisitor):
    def __init__(self):
        super(ASTContinuousInputDeclarationVisitor, self).__init__()
        self.inside_port = False
        self.current_port = None
        self.ports = list()

    def visit_input_port(self, node):
        self.inside_port = True
        self.current_port = node
        if self.current_port.is_continuous():
            self.ports.append(node.clone())

    def endvisit_input_port(self, node):
        self.inside_port = False


class ASTKernelInformationCollectorVisitor(ASTVisitor):
    def __init__(self):
        super(ASTKernelInformationCollectorVisitor, self).__init__()

        # various dicts to store collected information
        self.kernel_name_to_kernel = defaultdict()
        self.inline_expression_to_kernel_args = defaultdict(lambda: set())
        self.inline_expression_to_function_calls = defaultdict(lambda: set())
        self.kernel_to_function_calls = defaultdict(lambda: set())
        self.parameter_name_to_declaration = defaultdict(lambda: None)
        self.state_name_to_declaration = defaultdict(lambda: None)
        self.variable_name_to_declaration = defaultdict(lambda: None)
        self.internal_var_name_to_declaration = defaultdict(lambda: None)
        self.inline_expression_to_variables = defaultdict(lambda: set())
        self.kernel_to_rhs_variables = defaultdict(lambda: set())
        self.declaration_to_rhs_variables = defaultdict(lambda: set())
        self.input_port_name_to_input_port = defaultdict()

        # traversal states and nodes
        self.inside_parameter_block = False
        self.inside_state_block = False
        self.inside_internals_block = False
        self.inside_equations_block = False
        self.inside_input_block = False
        self.inside_inline_expression = False
        self.inside_kernel = False
        self.inside_kernel_call = False
        self.inside_declaration = False
        self.inside_simple_expression = False
        self.inside_expression = False

        self.current_inline_expression = None
        self.current_kernel = None
        self.current_expression = None
        self.current_simple_expression = None
        self.current_declaration = None

        self.current_synapse_name = None

    def get_state_declaration(self, variable_name):
        return self.state_name_to_declaration[variable_name]

    def get_variable_declaration(self, variable_name):
        return self.variable_name_to_declaration[variable_name]

    def get_kernel_by_name(self, name: str):
        return self.kernel_name_to_kernel[name]

    def get_inline_expressions_with_kernels(self):
        return self.inline_expression_to_kernel_args.keys()

    def get_kernel_function_calls(self, kernel: ASTKernel):
        return self.kernel_to_function_calls[kernel]

    def get_inline_function_calls(self, inline: ASTInlineExpression):
        return self.inline_expression_to_function_calls[inline]

    def get_variable_names_of_synapse(self, synapse_inline: ASTInlineExpression, exclude_names: set = set(),
                                      exclude_ignorable=True) -> set:
        """extracts all variables specific to a single synapse
        (which is defined by the inline expression containing kernels)
        independently of what block they are declared in
        it also cascades over all right hand side variables until all
        variables are included"""
        if exclude_ignorable:
            exclude_names.update(self.get_variable_names_to_ignore())

        # find all variables used in the inline
        potential_variables = self.inline_expression_to_variables[synapse_inline]

        # find all kernels referenced by the inline
        # and collect variables used by those kernels
        kernel_arg_pairs = self.get_extracted_kernel_args(synapse_inline)
        for kernel_var, spikes_var in kernel_arg_pairs:
            kernel = self.get_kernel_by_name(kernel_var.get_name())
            potential_variables.update(self.kernel_to_rhs_variables[kernel])

        # find declarations for all variables and check
        # what variables their rhs expressions use
        # for example if we have
        # a = b * c
        # then check if b and c are already in potential_variables
        # if not, add those as well
        potential_variables_copy = copy.copy(potential_variables)

        potential_variables_prev_count = len(potential_variables)
        while True:
            for potential_variable in potential_variables_copy:
                var_name = potential_variable.get_name()
                if var_name in exclude_names:
                    continue
                declaration = self.get_variable_declaration(var_name)
                if declaration is None:
                    continue
                variables_referenced = self.declaration_to_rhs_variables[var_name]
                potential_variables.update(variables_referenced)
            if potential_variables_prev_count == len(potential_variables):
                break
            potential_variables_prev_count = len(potential_variables)

        # transform variables into their names and filter
        # out anything form exclude_names
        result = set()
        for potential_variable in potential_variables:
            var_name = potential_variable.get_name()
            if var_name not in exclude_names:
                result.add(var_name)

        return result

    @classmethod
    def get_variable_names_to_ignore(cls):
        return set(PredefinedVariables.get_variables().keys()).union({"v_comp"})

    def get_synapse_specific_internal_declarations(self, synapse_inline: ASTInlineExpression) -> defaultdict:
        synapse_variable_names = self.get_variable_names_of_synapse(
            synapse_inline)

        # now match those variable names with
        # variable declarations from the internals block
        dereferenced = defaultdict()
        for potential_internals_name in synapse_variable_names:
            if potential_internals_name in self.internal_var_name_to_declaration:
                dereferenced[potential_internals_name] = self.internal_var_name_to_declaration[
                    potential_internals_name]
        return dereferenced

    def get_synapse_specific_state_declarations(self, synapse_inline: ASTInlineExpression) -> defaultdict:
        synapse_variable_names = self.get_variable_names_of_synapse(
            synapse_inline)

        # now match those variable names with
        # variable declarations from the state block
        dereferenced = defaultdict()
        for potential_state_name in synapse_variable_names:
            if potential_state_name in self.state_name_to_declaration:
                dereferenced[potential_state_name] = self.state_name_to_declaration[potential_state_name]
        return dereferenced

    def get_synapse_specific_parameter_declarations(self, synapse_inline: ASTInlineExpression) -> defaultdict:
        synapse_variable_names = self.get_variable_names_of_synapse(
            synapse_inline)

        # now match those variable names with
        # variable declarations from the parameter block
        dereferenced = defaultdict()
        for potential_param_name in synapse_variable_names:
            if potential_param_name in self.parameter_name_to_declaration:
                dereferenced[potential_param_name] = self.parameter_name_to_declaration[potential_param_name]
        return dereferenced

    def get_extracted_kernel_args(self, inline_expression: ASTInlineExpression) -> set:
        return self.inline_expression_to_kernel_args[inline_expression]

    def get_extracted_kernel_args_by_name(self, inline_name: str) -> set:
        inline_expression = [inline for inline in self.inline_expression_to_kernel_args.keys() if
                             inline.get_variable_name() == inline_name]
        if len(inline_expression):
            return self.inline_expression_to_kernel_args[inline_expression[0]]
        else:
            return set()

    def get_basic_kernel_variable_names(self, synapse_inline):
        """
        for every occurence of convolve(port, spikes) generate "port__X__spikes" variable
        gather those variables for this synapse inline and return their list

        note that those variables will occur as substring in other kernel variables            i.e  "port__X__spikes__d" or "__P__port__X__spikes__port__X__spikes"

        so we can use the result to identify all the other kernel variables related to the
        specific synapse inline declaration
        """
        order = 0
        results = []
        for syn_inline, args in self.inline_expression_to_kernel_args.items():
            if synapse_inline.variable_name == syn_inline.variable_name:
                for kernel_var, spike_var in args:
                    kernel_name = kernel_var.get_name()
                    spike_input_port = self.input_port_name_to_input_port[spike_var.get_name(
                    )]
                    kernel_variable_name = self.construct_kernel_X_spike_buf_name(
                        kernel_name, spike_input_port, order)
                    results.append(kernel_variable_name)

        return results

    def get_used_kernel_names(self, inline_expression: ASTInlineExpression):
        return [kernel_var.get_name() for kernel_var, _ in self.get_extracted_kernel_args(inline_expression)]

    def get_input_port_by_name(self, name):
        return self.input_port_name_to_input_port[name]

    def get_used_spike_names(self, inline_expression: ASTInlineExpression):
        return [spikes_var.get_name() for _, spikes_var in self.get_extracted_kernel_args(inline_expression)]

    def visit_kernel(self, node):
        self.current_kernel = node
        self.inside_kernel = True
        if self.inside_equations_block:
            kernel_name = node.get_variables()[0].get_name_of_lhs()
            self.kernel_name_to_kernel[kernel_name] = node

    def visit_function_call(self, node):
        if self.inside_equations_block:
            if self.inside_inline_expression and self.inside_simple_expression:
                if node.get_name() == "convolve":
                    self.inside_kernel_call = True
                    kernel, spikes = node.get_args()
                    kernel_var = kernel.get_variables()[0]
                    spikes_var = spikes.get_variables()[0]
                    self.inline_expression_to_kernel_args[self.current_inline_expression].add(
                        (kernel_var, spikes_var))
                else:
                    self.inline_expression_to_function_calls[self.current_inline_expression].add(
                        node)
            if self.inside_kernel and self.inside_simple_expression:
                self.kernel_to_function_calls[self.current_kernel].add(node)

    def endvisit_function_call(self, node):
        self.inside_kernel_call = False

    def endvisit_kernel(self, node):
        self.current_kernel = None
        self.inside_kernel = False

    def visit_variable(self, node):
        if self.inside_inline_expression and not self.inside_kernel_call:
            self.inline_expression_to_variables[self.current_inline_expression].add(
                node)
        elif self.inside_kernel and (self.inside_expression or self.inside_simple_expression):
            self.kernel_to_rhs_variables[self.current_kernel].add(node)
        elif self.inside_declaration and self.inside_expression:
            declared_variable = self.current_declaration.get_variables()[
                0].get_name()
            self.declaration_to_rhs_variables[declared_variable].add(node)

    def visit_inline_expression(self, node):
        self.inside_inline_expression = True
        self.current_inline_expression = node

    def endvisit_inline_expression(self, node):
        self.inside_inline_expression = False
        self.current_inline_expression = None

    def visit_equations_block(self, node):
        self.inside_equations_block = True

    def endvisit_equations_block(self, node):
        self.inside_equations_block = False

    def visit_input_block(self, node):
        self.inside_input_block = True

    def visit_input_port(self, node):
        self.input_port_name_to_input_port[node.get_name()] = node

    def endvisit_input_block(self, node):
        self.inside_input_block = False

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
        self.current_simple_expression = node

    def endvisit_simple_expression(self, node):
        self.inside_simple_expression = False
        self.current_simple_expression = None

    def visit_declaration(self, node):
        self.inside_declaration = True
        self.current_declaration = node

        # collect decalarations generally
        variable_name = node.get_variables()[0].get_name()
        self.variable_name_to_declaration[variable_name] = node

        # collect declarations per block
        if self.inside_parameter_block:
            self.parameter_name_to_declaration[variable_name] = node
        elif self.inside_state_block:
            self.state_name_to_declaration[variable_name] = node
        elif self.inside_internals_block:
            self.internal_var_name_to_declaration[variable_name] = node

    def endvisit_declaration(self, node):
        self.inside_declaration = False
        self.current_declaration = None

    def visit_expression(self, node):
        self.inside_expression = True
        self.current_expression = node

    def endvisit_expression(self, node):
        self.inside_expression = False
        self.current_expression = None

    # this method was copied over from ast_transformer
    # in order to avoid a circular dependency
    @staticmethod
    def construct_kernel_X_spike_buf_name(kernel_var_name: str, spike_input_port, order: int,
                                          diff_order_symbol="__d"):
        assert type(kernel_var_name) is str
        assert type(order) is int
        assert type(diff_order_symbol) is str
        return kernel_var_name.replace("$", "__DOLLAR") + "__X__" + str(
            spike_input_port) + diff_order_symbol * order


class ASTUpdateBlockDependencyAndOwnedExtractor(ASTVisitor):
    def __init__(self, init_owned, init_dep):
        super(ASTUpdateBlockDependencyAndOwnedExtractor, self).__init__()

        self.inside_block = None
        self.dependencies = init_dep
        self.owned = init_owned

        self.block_with_dep = False
        self.block_with_owned = False

        self.control_depth = 0
        self.current_control_vars = list()
        self.inside_ctl_condition = False

        self.expression_depth = 0

        self.inside_small_stmt = False
        self.inside_stmt = False
        self.inside_variable = False
        self.inside_if_stmt = False
        self.inside_while_stmt = False
        self.inside_for_stmt = False

        self.inside_if_clause = False
        self.inside_elif_clause = False
        self.inside_else_clause = False
        self.inside_for_clause = False
        self.inside_while_clause = False

    def visit_variable(self, node):
        self.inside_variable = True

    def endvisit_variable(self, node):
        self.inside_variable = False

    def visit_if_stmt(self, node):
        self.inside_if_stmt = True
        self.control_depth += 1
        self.inside_ctl_condition = True

    def endvisit_if_stmt(self, node):
        self.control_depth -= 1
        self.inside_ctl_condition = False
        self.current_control_vars.pop()
        self.inside_if_stmt = False

    def visit_while_stmt(self, node):
        self.inside_while_stmt = True
        self.control_depth += 1
        var_collector = ASTVariableCollectorVisitor()
        node.condition.accept(var_collector)
        self.current_control_vars.append(var_collector.all_variables)
        self.inside_ctl_condition = True

    def endvisit_while_stmt(self, node):
        self.control_depth -= 1
        self.inside_ctl_condition = False
        self.current_control_vars.pop()
        self.inside_while_stmt = False

    def visit_for_stmt(self, node):
        self.inside_for_stmt = True
        self.control_depth += 1
        var_collector = ASTVariableCollectorVisitor()
        node.condition.accept(var_collector)
        self.current_control_vars.append(var_collector.all_variables)
        self.inside_ctl_condition = True

    def endvisit_for_stmt(self, node):
        self.control_depth -= 1
        self.inside_ctl_condition = False
        self.current_control_vars.pop()
        self.inside_for_stmt = False

    def visit_if_clause(self, node):
        self.inside_if_clause = True
        var_collector = ASTVariableCollectorVisitor()
        node.condition.accept(var_collector)
        self.current_control_vars.append(var_collector.all_variables)

    def endvisit_if_clause(self, node):
        self.inside_if_clause = False

    def visit_elif_clause(self, node):
        self.inside_elif_clause = True
        var_collector = ASTVariableCollectorVisitor()
        node.condition.accept(var_collector)
        self.current_control_vars[-1].extend(var_collector.all_variables)

    def endvisit_elif_clause(self, node):
        self.inside_elif_clause = False

    def visit_block(self, node):
        self.inside_block = True
        self.inside_ctl_condition = False

    def endvisit_block(self, node):
        self.inside_block = False
        self.inside_ctl_condition = True

    def visit_assignment(self, node):
        self.inside_assignment = True
        var_collector = ASTVariableCollectorVisitor()
        node.rhs.accept(var_collector)
        if node.lhs.get_name() in [n.get_name() for n in (self.dependencies + self.owned)]:
            self.dependencies.extend(var_collector.all_variables)
            for dep in self.current_control_vars:
                self.dependencies.extend(dep)

        if len(set([n.get_name() for n in self.owned]) & set([n.get_name() for n in var_collector.all_variables])):
            self.owned.append(node.lhs)

    def endvisit_assignment(self, node):
        self.inside_assignment = False


class ASTUpdateBlockReductor(ASTVisitor):
    def __init__(self, init_owned, init_exclusive_dep):
        super(ASTUpdateBlockReductor, self).__init__()

        self.dependencies = init_exclusive_dep
        self.owned = init_owned

        self.delete_stmts = list()
        self.current_stmt_index = list()
        self.block_depth = -1

        self.inside_stmt = False
        self.inside_if_stmt = False
        self.inside_while_stmt = False
        self.inside_for_stmt = False

    def visit_if_stmt(self, node):
        self.inside_if_stmt = True

    def endvisit_if_stmt(self, node):
        all_empty = len(node.get_if_clause().get_stmts_body().get_stmts()) == 0
        for block in [n.get_stmts_body() for n in node.get_elif_clauses()]:
            all_empty = all_empty and len(block.get_stmts()) == 0
        if node.get_else_clause() is not None:
            all_empty = all_empty and len(node.get_else_clause().get_stmts_body().get_stmts()) == 0
        if all_empty:
            self.delete_stmts[self.block_depth].append(node.get_parent().get_parent())
        self.inside_if_stmt = False

    def visit_while_stmt(self, node):
        self.inside_while_stmt = True

    def endvisit_while_stmt(self, node):
        if len(node.get_stmts_body().get_stmts()) == 0:
            self.delete_stmts[self.block_depth].append(node.get_parent().get_parent())
        self.inside_while_stmt = False

    def visit_for_stmt(self, node):
        self.inside_for_stmt = True

    def endvisit_for_stmt(self, node):
        if len(node.get_stmts_body().get_stmts()) == 0:
            self.delete_stmts[self.block_depth].append(node.get_parent().get_parent())
        self.inside_for_stmt = False

    def visit_block(self, node):
        self.inside_block = True
        self.block_depth += 1
        self.delete_stmts.append(list())

    def endvisit_block(self, node):
        for stmt in self.delete_stmts[self.block_depth]:
            node.delete_stmt(stmt)
        self.delete_stmts.pop()
        self.block_depth -= 1
        self.inside_block = False

    def visit_assignment(self, node):
        self.inside_assignment = True
        var_collector = ASTVariableCollectorVisitor()
        node.rhs.accept(var_collector)
        if node.lhs.get_name() not in [n.get_name() for n in (self.dependencies + self.owned)]:
            self.delete_stmts[self.block_depth].append(node.get_parent().get_parent())

    def endvisit_assignment(self, node):
        self.inside_assignment = False
