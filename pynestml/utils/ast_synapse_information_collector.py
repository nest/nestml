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
import copy
from collections import defaultdict

from pynestml.meta_model.ast_inline_expression import ASTInlineExpression
from pynestml.meta_model.ast_kernel import ASTKernel
from pynestml.symbols.predefined_units import PredefinedUnits
from pynestml.symbols.predefined_variables import PredefinedVariables
from pynestml.visitors.ast_visitor import ASTVisitor


class ASTSynapseInformationCollector(object):
    """This class contains all basic mechanism information collection. Further collectors may be implemented to collect
    further information for specific mechanism types (example: ASTReceptorInformationCollector)"""
    collector_visitor = None
    synapse = None

    @classmethod
    def __init__(cls, synapse):
        cls.synapse = synapse
        cls.collector_visitor = ASTMechanismInformationCollectorVisitor()
        synapse.accept(cls.collector_visitor)

    @classmethod
    def collect_definitions(cls, synapse, syn_info):
        # variables
        var_collector_visitor = ASTVariableCollectorVisitor()
        synapse.accept(var_collector_visitor)
        syn_info["States"] = var_collector_visitor.all_states
        syn_info["Parameters"] = var_collector_visitor.all_parameters
        syn_info["Internals"] = var_collector_visitor.all_internals

        # ODEs
        ode_collector_visitor = ASTODEEquationCollectorVisitor()
        synapse.accept(ode_collector_visitor)
        syn_info["ODEs"] = ode_collector_visitor.all_ode_equations

        # inlines
        inline_collector_visitor = ASTInlineEquationCollectorVisitor()
        synapse.accept(inline_collector_visitor)
        syn_info["Inlines"] = inline_collector_visitor.all_inlines

        # functions
        function_collector_visitor = ASTFunctionCollectorVisitor()
        synapse.accept(function_collector_visitor)
        syn_info["Functions"] = function_collector_visitor.all_functions

        return syn_info

    @classmethod
    def collect_on_receive_blocks(cls, synapse, syn_info, pre_port, post_port):
        pre_spike_collector_visitor = ASTOnReceiveBlockVisitor(pre_port)
        synapse.accept(pre_spike_collector_visitor)
        syn_info["PreSpikeFunction"] = pre_spike_collector_visitor.on_receive_block

        post_spike_collector_visitor = ASTOnReceiveBlockVisitor(post_port)
        synapse.accept(post_spike_collector_visitor)
        syn_info["PostSpikeFunction"] = post_spike_collector_visitor.on_receive_block

        return syn_info

    @classmethod
    def collect_update_block(cls, synapse, syn_info):
        update_block_collector_visitor = ASTUpdateBlockVisitor()
        synapse.accept(update_block_collector_visitor)
        syn_info["UpdateBlock"] = update_block_collector_visitor.update_block
        return syn_info

    @classmethod
    def collect_ports(cls, synapse, syn_info):
        port_collector_visitor = ASTPortVisitor()
        synapse.accept(port_collector_visitor)
        syn_info["SpikingPorts"] = port_collector_visitor.spiking_ports
        syn_info["ContinuousPorts"] = port_collector_visitor.continuous_ports
        return syn_info

    @classmethod
    def collect_potential_dependencies(cls, synapse, syn_info):
        non_dec_asmt_visitor = ASTNonDeclaringAssignmentVisitor()
        synapse.accept(non_dec_asmt_visitor)

        potential_dependencies = copy.deepcopy(syn_info["States"])
        for state in syn_info["States"]:
            for assignment in non_dec_asmt_visitor.non_declaring_assignments:
                if state == assignment.get_variable().get_name():
                    if state in potential_dependencies:
                        del potential_dependencies[state]

        syn_info["PotentialDependencies"] = potential_dependencies

        return syn_info

    @classmethod
    def extend_variables_with_initialisations(cls, synapse, syn_info):
        """collects initialization expressions for all variables and parameters contained in syn_info"""
        var_init_visitor = VariableInitializationVisitor(syn_info)
        synapse.accept(var_init_visitor)
        syn_info["States"] = var_init_visitor.states
        syn_info["Parameters"] = var_init_visitor.parameters
        syn_info["Internals"] = var_init_visitor.internals

        return syn_info

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
    def collect_mechanism_related_definitions(cls, neuron, syn_info):
        """Collects all parts of the nestml code the root expressions previously collected depend on. search
        is cut at other mechanisms root expressions"""
        from pynestml.meta_model.ast_inline_expression import ASTInlineExpression
        from pynestml.meta_model.ast_ode_equation import ASTOdeEquation

        for mechanism_name, mechanism_info in syn_info.items():
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

            mechanism_inlines.append(syn_info[mechanism_name]["root_expression"])

            search_variables = list()
            search_functions = list()

            found_variables = list()
            found_functions = list()

            local_variable_collector = ASTVariableCollectorVisitor()
            mechanism_inlines[0].accept(local_variable_collector)
            search_variables = local_variable_collector.all_variables

            local_function_call_collector = ASTFunctionCallCollectorVisitor()
            mechanism_inlines[0].accept(local_function_call_collector)
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
                    if not variable.name == "v_comp":
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
                                if isinstance(ode.get_decorators(), list):
                                    if "mechanism" in [e.namespace for e in ode.get_decorators()]:
                                        is_dependency = True
                                        if not (isinstance(mechanism_info["root_expression"],
                                                           ASTOdeEquation) and ode.lhs.name == mechanism_info["root_expression"].lhs.name):
                                            if "concentration" in [e.name for e in ode.get_decorators()]:
                                                if not ode.lhs.name in [o.lhs.name for o in
                                                                        mechanism_dependencies["concentrations"]]:
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

                        for state in global_states:
                            if variable.name == state.name and not is_dependency:
                                mechanism_states.append(state)

                        for parameter in global_parameters:
                            if variable.name == parameter.name:
                                mechanism_parameters.append(parameter)

                        for internal in global_internals:
                            if variable.name == internal.name:
                                mechanism_internals.append(internal)

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

            syn_info[mechanism_name]["States"] = mechanism_states
            syn_info[mechanism_name]["Parameters"] = mechanism_parameters
            syn_info[mechanism_name]["Internals"] = mechanism_internals
            syn_info[mechanism_name]["Functions"] = mechanism_functions
            syn_info[mechanism_name]["SecondaryInlineExpressions"] = mechanism_inlines
            syn_info[mechanism_name]["ODEs"] = mechanism_odes
            syn_info[mechanism_name]["Continuous"] = mechanism_continuous_inputs
            syn_info[mechanism_name]["Dependencies"] = mechanism_dependencies

        return syn_info


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

    def get_extracted_kernel_args_by_name(self, inline_name: str) -> set:
        inline_expression = [inline for inline in self.inline_expression_to_kernel_args.keys() if
                             inline.get_variable_name() == inline_name]

        return self.inline_expression_to_kernel_args[inline_expression[0]]

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
        self.current_declaration = None
        self.states = defaultdict()
        self.parameters = defaultdict()
        self.internals = defaultdict()
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
        if node.is_internals:
            self.inside_internal_block = True

    def endvisit_block_with_variables(self, node):
        self.inside_state_block = False
        self.inside_parameter_block = False
        self.inside_internal_block = False

    def visit_variable(self, node):
        self.inside_variable = True
        if self.inside_state_block and self.inside_declaration:
            if any(node.name == variable.name for variable in self.channel_info["States"]):
                self.states[node.name] = defaultdict()
                self.states[node.name]["ASTVariable"] = node.clone()
                self.states[node.name]["rhs_expression"] = self.current_declaration.get_expression()

        if self.inside_parameter_block and self.inside_declaration:
            if any(node.name == variable.name for variable in self.channel_info["Parameters"]):
                self.parameters[node.name] = defaultdict()
                self.parameters[node.name]["ASTVariable"] = node.clone()
                self.parameters[node.name]["rhs_expression"] = self.current_declaration.get_expression()

        if self.inside_internal_block and self.inside_declaration:
            if any(node.name == variable.name for variable in self.channel_info["Internals"]):
                self.internals[node.name] = defaultdict()
                self.internals[node.name]["ASTVariable"] = node.clone()
                self.internals[node.name]["rhs_expression"] = self.current_declaration.get_expression()

    def endvisit_variable(self, node):
        self.inside_variable = False


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
        self.all_internals = list()
        self.inside_states_block = False
        self.inside_parameters_block = False
        self.inside_internals_block = False
        self.all_variables = list()

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
        if not (node.name == "v_comp" or node.name in PredefinedUnits.get_units()):
            self.all_variables.append(node.clone())
            if self.inside_states_block:
                self.all_states.append(node.clone())
            if self.inside_parameters_block:
                self.all_parameters.append(node.clone())
            if self.inside_internals_block:
                self.all_internals.append(node.clone())

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


class ASTOnReceiveBlockVisitor(ASTVisitor):
    def __init__(self, port_name):
        super(ASTOnReceiveBlockVisitor, self).__init__()
        self.inside_on_receive = False
        self.port_name = port_name
        self.on_receive_block = None

    def visit_on_receive_block(self, node):
        self.inside_on_receive = True
        if node.port_name in self.port_name:
            self.on_receive_block = node.clone()

    def endvisit_on_receive_block(self, node):
        self.inside_on_receive = False


class ASTUpdateBlockVisitor(ASTVisitor):
    def __init__(self):
        super(ASTUpdateBlockVisitor, self).__init__()
        self.inside_update_block = False
        self.update_block = None

    def visit_update_block(self, node):
        self.inside_update_block = True
        self.update_block = node.clone()

    def endvisit_update_block(self, node):
        self.inside_update_block = False


class ASTPortVisitor(ASTVisitor):
    def __init__(self):
        super(ASTPortVisitor, self).__init__()
        self.inside_port = False
        self.spiking_ports = list()
        self.continuous_ports = list()

    def visit_input_port(self, node):
        self.inside_port = True
        if node.is_spike():
            self.spiking_ports.append(node.clone())
        if node.is_continuous():
            self.continuous_ports.append(node.clone())

    def endvisit_input_port(self, node):
        self.inside_port = False


class ASTNonDeclaringAssignmentVisitor(ASTVisitor):
    def __init__(self):
        super(ASTNonDeclaringAssignmentVisitor, self).__init__()
        self.inside_states_block = False
        self.inside_parameters_block = False
        self.inside_internals_block = False
        self.inside_assignment = False
        self.non_declaring_assignments = list()

    def visit_states_block(self, node):
        self.inside_states_block = True

    def endvisit_states_block(self, node):
        self.inside_states_block = False

    def visit_parameters_block(self, node):
        self.inside_parameters_block = True

    def endvisit_parameters_block(self, node):
        self.inside_parameters_block = False

    def visit_internals_block(self, node):
        self.inside_internals_block = True

    def endvisit_internals_block(self, node):
        self.inside_internals_block = False

    def visit_assignment(self, node):
        self.inside_assignment = True
        if not self.inside_parameters_block or not self.inside_internals_block or self.inside_states_block:
            self.non_declaring_assignments.append(node.clone())

    def endvisit_assignment(self, node):
        self.inside_assignment = False
