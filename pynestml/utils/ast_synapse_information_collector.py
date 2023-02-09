# -*- coding: utf-8 -*-
#
# ast_synapse_information_collector.py
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

from pynestml.meta_model.ast_inline_expression import ASTInlineExpression
from pynestml.meta_model.ast_kernel import ASTKernel
from pynestml.symbols.predefined_variables import PredefinedVariables
from pynestml.visitors.ast_visitor import ASTVisitor


class ASTSynapseInformationCollector(ASTVisitor):
    """
    for each inline expression inside the equations block,
    collect all synapse relevant information

    """

    def __init__(self):
        super(ASTSynapseInformationCollector, self).__init__()

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
        # self.inside_variable = False
        self.inside_simple_expression = False
        self.inside_expression = False
        # self.inside_function_call = False

        self.current_inline_expression = None
        self.current_kernel = None
        self.current_expression = None
        self.current_simple_expression = None
        self.current_declaration = None
        # self.current_variable = None

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

    # extracts all variables specific to a single synapse
    # (which is defined by the inline expression containing kernels)
    # independently from what block they are declared in
    # it also cascades over all right hand side variables until all
    # variables are included

    @classmethod
    def extend_variable_list_name_based_restricted(cls, extended_list, appending_list, restrictor_list):
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
    def collect_synapse_related_definitions(cls, neuron, syns_info):
        for synapse_name, synapse_info in syns_info.items():
            variable_collector = ASTVariableCollectorVisitor()
            neuron.accept(variable_collector)
            global_states = variable_collector.all_states
            global_parameters = variable_collector.all_parameters

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

            #print("states: "+str(len(global_states))+" param: "+str(len(global_parameters))+" funcs: "+str(len(global_functions))+" inlines: "+str(len(global_inlines))+" odes: "+str(len(global_odes)))

            synapse_states = list()
            synapse_parameters = list()
            synapse_functions = list()
            synapse_inlines = list()
            synapse_odes = list()
            synapse_kernels = list()

            synapse_inlines.append(syns_info[synapse_name]["inline_expression"])

            search_variables = list()
            search_functions = list()

            found_variables = list()
            found_functions = list()

            local_variable_collector = ASTVariableCollectorVisitor()
            synapse_inlines[0].accept(local_variable_collector)
            search_variables = local_variable_collector.all_variables

            local_function_call_collector = ASTFunctionCallCollectorVisitor()
            synapse_inlines[0].accept(local_function_call_collector)
            search_functions = local_function_call_collector.all_function_calls


            while (len(search_functions) > 0 or len(search_variables) > 0):
                #print(str(len(search_functions))+", "+str(len(search_variables)))
                if(len(search_functions) > 0):
                    function_call = search_functions[0]
                    for function in global_functions:
                        if function.name == function_call.callee_name:
                            print("function found")
                            synapse_functions.append(function)
                            found_functions.append(function_call)

                            local_variable_collector = ASTVariableCollectorVisitor()
                            function.accept(local_variable_collector)
                            #search_variables = search_variables + [item for item in list(dict.fromkeys(local_variable_collector.all_variables)) if item not in found_variables+search_variables]
                            search_variables = cls.extend_variable_list_name_based_restricted(search_variables, local_variable_collector.all_variables, search_variables+found_variables)

                            local_function_call_collector = ASTFunctionCallCollectorVisitor()
                            function.accept(local_function_call_collector)
                            #search_functions = search_functions + [item for item in list(dict.fromkeys(local_function_call_collector.all_function_calls)) if item not in found_functions+search_functions]
                            search_functions = cls.extend_function_call_list_name_based_restricted(search_functions,
                                                                                              local_function_call_collector.all_function_calls,
                                                                                              search_functions + found_functions)
                            #IMPLEMENT CATCH NONDEFINED!!!
                    search_functions.remove(function_call)

                elif (len(search_variables) > 0):
                    variable = search_variables[0]
                    for kernel in global_kernels:
                        if variable.name == kernel.get_variables()[0].name:
                            print("kernel found")
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

                    for inline in global_inlines:
                        if variable.name == inline.variable_name:
                            print("inline found")
                            synapse_inlines.append(inline)

                            local_variable_collector = ASTVariableCollectorVisitor()
                            inline.accept(local_variable_collector)
                            search_variables = cls.extend_variable_list_name_based_restricted(search_variables, local_variable_collector.all_variables, search_variables+found_variables)

                            local_function_call_collector = ASTFunctionCallCollectorVisitor()
                            inline.accept(local_function_call_collector)
                            search_functions = cls.extend_function_call_list_name_based_restricted(search_functions,
                                                                                                   local_function_call_collector.all_function_calls,
                                                                                                   search_functions + found_functions)

                    for ode in global_odes:
                        if variable.name == ode.lhs.name:
                            print("ode found")
                            synapse_odes.append(ode)

                            local_variable_collector = ASTVariableCollectorVisitor()
                            ode.accept(local_variable_collector)
                            search_variables = cls.extend_variable_list_name_based_restricted(search_variables, local_variable_collector.all_variables, search_variables+found_variables)

                            local_function_call_collector = ASTFunctionCallCollectorVisitor()
                            ode.accept(local_function_call_collector)
                            search_functions = cls.extend_function_call_list_name_based_restricted(search_functions,
                                                                                                   local_function_call_collector.all_function_calls,
                                                                                                   search_functions + found_functions)

                    for state in global_states:
                        if variable.name == state.name:
                            print("state found")
                            synapse_states.append(state)

                    for parameter in global_parameters:
                        if variable.name == parameter.name:
                            print("parameter found")
                            synapse_parameters.append(parameter)

                    search_variables.remove(variable)
                    found_variables.append(variable)
                    # IMPLEMENT CATCH NONDEFINED!!!

            #syns_info[synapse_name]["states_used"] = synapse_states
            #syns_info[synapse_name]["parameters_used"] = synapse_parameters
            syns_info[synapse_name]["functions_used"] = synapse_functions
            syns_info[synapse_name]["secondaryInlineExpressions"] = synapse_inlines
            syns_info[synapse_name]["ODEs"] = synapse_odes
            syns_info[synapse_name]["kernels_used"] = synapse_kernels

        return syns_info

    @classmethod
    def extend_variables_with_initialisations(cls, neuron, chan_info):
        for ion_channel_name, channel_info in chan_info.items():
            var_init_visitor = VariableInitializationVisitor(channel_info)
            neuron.accept(var_init_visitor)
            chan_info[ion_channel_name]["states_used"] = var_init_visitor.states
            chan_info[ion_channel_name]["parameters_used"] = var_init_visitor.parameters

        return chan_info

    def get_variable_names_of_synapse(self, synapse_inline: ASTInlineExpression, exclude_names: set = set(), exclude_ignorable=True) -> set:
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
                dereferenced[potential_internals_name] = self.internal_var_name_to_declaration[potential_internals_name]
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

    """
    for every occurence of convolve(port, spikes) generate "port__X__spikes" variable
    gather those variables for this synapse inline and return their list

    note that those variables will occur as substring in other kernel variables
    i.e  "port__X__spikes__d" or "__P__port__X__spikes__port__X__spikes"

    so we can use the result to identify all the other kernel variables related to the
    specific synapse inline declaration
    """

    def get_basic_kernel_variable_names(self, synapse_inline):
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
    def construct_kernel_X_spike_buf_name(kernel_var_name: str, spike_input_port, order: int, diff_order_symbol="__d"):
        assert type(kernel_var_name) is str
        assert type(order) is int
        assert type(diff_order_symbol) is str
        return kernel_var_name.replace("$", "__DOLLAR") + "__X__" + str(spike_input_port) + diff_order_symbol * order

#Helper classes:
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
        self.all_states = list()
        self.all_parameters = list()
        self.inside_states_block = False
        self.inside_parameters_block = False
        self.all_variables = list()

    def visit_block_with_variables(self, node):
        self.inside_block_with_variables = True
        if node.is_state:
            self.inside_states_block = True
        if node.is_parameters:
            self.inside_parameters_block = True

    def endvisit_block_with_variables(self, node):
        self.inside_states_block = False
        self.inside_parameters_block = False
        self.inside_block_with_variables = False

    def visit_variable(self, node):
        self.inside_variable = True
        self.all_variables.append(node.clone())
        if self.inside_states_block:
            self.all_states.append(node.clone())
        if self.inside_parameters_block:
            self.all_parameters.append(node.clone())

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

class VariableInitializationVisitor(ASTVisitor):
    def __init__(self, channel_info):
        super(VariableInitializationVisitor, self).__init__()
        self.inside_variable = False
        self.inside_declaration = False
        self.inside_parameter_block = False
        self.inside_state_block = False
        self.current_declaration = None
        self.states = defaultdict()
        self.parameters = defaultdict()
        self.channel_info = channel_info

    def visit_declaration(self, node):
        self.inside_declaration = True
        self.current_declaration = node

    def endvisit_declaration(self, node):
        self.inside_declaration = False
        self.current_declaration = None

    def visit_block_with_variables(self, node):
        if node.is_state:
            self.inside_state_block = True
        if node.is_parameters:
            self.inside_parameter_block = True

    def visit_variable(self, node):
        self.inside_variable = True
        if self.inside_state_block and self.inside_declaration:
            if any(node.name == variable.name for variable in self.channel_info["states_used"]):
                self.states[node.name] = defaultdict()
                self.states[node.name]["ASTVariable"] = node.clone()
                self.states[node.name]["rhs_expression"] = self.current_declaration.get_expression()

        if self.inside_parameter_block and self.inside_declaration:
            if any(node.name == variable.name for variable in self.channel_info["parameters_used"]):
                self.parameters[node.name] = defaultdict()
                self.parameters[node.name]["ASTVariable"] = node.clone()
                self.parameters[node.name]["rhs_expression"] = self.current_declaration.get_expression()

    def endvisit_variable(self, node):
        self.inside_variable = False