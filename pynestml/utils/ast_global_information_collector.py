# -*- coding: utf-8 -*-
#
# ast_global_information_collector.py
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

from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.symbols.predefined_units import PredefinedUnits
from pynestml.symbols.predefined_variables import PredefinedVariables
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_visitor import ASTVisitor


class ASTGlobalInformationCollector(object):
    """
    This file is part of the compartmental code generation process.

    Collects information about parts of the code that are relevant within the update or OnReceive(self_spike) blocks.
    """
    collector_visitor = None
    synapse = None

    @classmethod
    def __init__(cls, neuron):
        cls.neuron = neuron
        cls.collector_visitor = ASTMechanismInformationCollectorVisitor()
        neuron.accept(cls.collector_visitor)

    @classmethod
    def collect_update_block(cls, synapse, global_info):
        update_block_collector_visitor = ASTUpdateBlockVisitor()
        synapse.accept(update_block_collector_visitor)
        global_info["UpdateBlock"] = update_block_collector_visitor.update_block
        return global_info

    @classmethod
    def collect_self_spike_function(cls, neuron, global_info):
        from pynestml.codegeneration.nest_compartmental_code_generator import NESTCompartmentalCodeGenerator
        on_receive_collector_visitor = ASTOnReceiveBlockCollectorVisitor()
        neuron.accept(on_receive_collector_visitor)
        for function in on_receive_collector_visitor.all_on_receive_blocks:
            if "self_spikes_port" in FrontendConfiguration.get_codegen_opts().keys():
                self_spikes_port_name  = FrontendConfiguration.get_codegen_opts()["self_spikes_port"]
            else:
                self_spikes_port_name = NESTCompartmentalCodeGenerator._default_options ["self_spikes_port"]
            if function.get_port_name() == self_spikes_port_name:
                global_info["SelfSpikesFunction"] = function

        return global_info

    @classmethod
    def extend_variables_with_initialisations(cls, neuron, global_info):
        """collects initialization expressions for all variables and parameters contained in global_info"""
        var_init_visitor = VariableInitializationVisitor(global_info)
        neuron.accept(var_init_visitor)
        global_info["States"] = var_init_visitor.states
        global_info["Parameters"] = var_init_visitor.parameters
        global_info["Internals"] = var_init_visitor.internals

        return global_info

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
    def log_unresolved_function_dependency(cls, neuron, function_call, context: str):
        if PredefinedFunctions.get_function(function_call.callee_name):
            return

        code, message = Messages.get_cm_unresolved_function_dependency(function_call.callee_name, context)
        Logger.log_message(node=neuron, code=code, message=message, error_position=function_call.get_source_position(),
                           log_level=LoggingLevel.ERROR)

    @classmethod
    def log_unresolved_variable_dependency(cls, neuron, variable, context: str):
        if variable.name in PredefinedUnits.get_units() or variable.name in PredefinedVariables.get_variables():
            return

        code, message = Messages.get_cm_unresolved_variable_dependency(variable.name, context)
        Logger.log_message(node=neuron, code=code, message=message, error_position=variable.get_source_position(),
                           log_level=LoggingLevel.ERROR)

    @classmethod
    def get_function_external_variables(cls, function):
        local_variable_collector = ASTVariableCollectorVisitor()
        function.accept(local_variable_collector)

        local_declaration_collector = ASTLocalVariableDeclarationCollectorVisitor()
        function.accept(local_declaration_collector)
        local_names = {parameter.get_name() for parameter in function.get_parameters()}
        local_names.update(local_declaration_collector.local_variable_names)

        return [
            variable
            for variable in local_variable_collector.all_variables
            if variable.get_name() not in local_names
        ]

    @classmethod
    def collect_related_definitions(cls, neuron, global_info):
        """Collects all parts of the nestml code the root expressions previously collected depend on. search
        is cut at other mechanisms root expressions"""

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

        input_port_collector = ASTInputPortDeclarationVisitor()
        neuron.accept(input_port_collector)
        global_continuous_inputs = input_port_collector.continuous_ports
        global_input_ports = input_port_collector.all_ports

        mechanism_states = list()
        mechanism_parameters = list()
        mechanism_internals = list()
        mechanism_functions = list()
        mechanism_inlines = list()
        mechanism_odes = list()
        synapse_kernels = list()
        mechanism_continuous_inputs = list()

        search_variables = list()
        search_functions = list()

        found_variables = list()
        found_functions = list()

        if "SelfSpikesFunction" in global_info and global_info["SelfSpikesFunction"] is not None:
            local_variable_collector = ASTVariableCollectorVisitor()
            global_info["SelfSpikesFunction"].accept(local_variable_collector)
            search_variables_self_spike = local_variable_collector.all_variables
            search_variables = cls.extend_variable_list_name_based_restricted(search_variables,
                                                                              search_variables_self_spike,
                                                                              search_variables)

            local_function_call_collector = ASTFunctionCallCollectorVisitor()
            global_info["SelfSpikesFunction"].accept(local_function_call_collector)
            search_functions_self_spike = local_function_call_collector.all_function_calls
            search_functions = cls.extend_function_call_list_name_based_restricted(search_functions,
                                                                                   search_functions_self_spike,
                                                                                   search_functions)

        if "UpdateBlock" in global_info and global_info["UpdateBlock"] is not None:
            local_variable_collector = ASTVariableCollectorVisitor()
            global_info["UpdateBlock"].accept(local_variable_collector)
            search_variables_update = local_variable_collector.all_variables
            search_variables = cls.extend_variable_list_name_based_restricted(search_variables,
                                                                              search_variables_update,
                                                                              search_variables)

            local_function_call_collector = ASTFunctionCallCollectorVisitor()
            global_info["UpdateBlock"].accept(local_function_call_collector)
            search_functions_update = local_function_call_collector.all_function_calls
            search_functions = cls.extend_function_call_list_name_based_restricted(search_functions,
                                                                                   search_functions_update,
                                                                                   search_functions)

        while len(search_functions) > 0 or len(search_variables) > 0:
            if len(search_functions) > 0:
                function_call = search_functions[0]
                function_found = False
                for function in global_functions:
                    if function.name == function_call.callee_name:
                        function_found = True
                        mechanism_functions.append(function)
                        found_functions.append(function_call)

                        search_variables = cls.extend_variable_list_name_based_restricted(search_variables,
                                                                                          cls.get_function_external_variables(function),
                                                                                          search_variables + found_variables)

                        local_function_call_collector = ASTFunctionCallCollectorVisitor()
                        function.accept(local_function_call_collector)
                        search_functions = cls.extend_function_call_list_name_based_restricted(search_functions,
                                                                                               local_function_call_collector.all_function_calls,
                                                                                               search_functions + found_functions)
                if not function_found:
                    cls.log_unresolved_function_dependency(neuron, function_call, "compartmental global information")
                search_functions.remove(function_call)

            elif len(search_variables) > 0:
                variable = search_variables[0]
                variable_found = variable.name == "v_comp" or variable.name in PredefinedUnits.get_units() \
                    or variable.name in PredefinedVariables.get_variables()
                if not variable_found:
                    is_dependency = False
                    for inline in global_inlines:
                        if variable.name == inline.variable_name:
                            variable_found = True
                            if isinstance(inline.get_decorators(), list):
                                if "mechanism" in [e.namespace for e in inline.get_decorators()]:
                                    is_dependency = True

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
                            variable_found = True
                            if isinstance(ode.get_decorators(), list):
                                if "mechanism" in [e.namespace for e in ode.get_decorators()]:
                                    is_dependency = True

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
                            variable_found = True
                            mechanism_states.append(state)

                    for parameter in global_parameters:
                        if variable.name == parameter.name:
                            variable_found = True
                            mechanism_parameters.append(parameter)

                    for internal in global_internals:
                        if variable.name == internal.name:
                            variable_found = True
                            mechanism_internals.append(internal)

                    for kernel in global_kernels:
                        if variable.name == kernel.get_variables()[0].name:
                            variable_found = True
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
                            variable_found = True
                            mechanism_continuous_inputs.append(input)
                    for input in global_input_ports:
                        if variable.name == input.name:
                            variable_found = True
                if not variable_found:
                    cls.log_unresolved_variable_dependency(neuron, variable, "compartmental global information")
                search_variables.remove(variable)
                found_variables.append(variable)

        global_info["States"] = mechanism_states
        global_info["Parameters"] = mechanism_parameters
        global_info["Internals"] = mechanism_internals
        global_info["Functions"] = mechanism_functions
        global_info["SecondaryInlineExpressions"] = mechanism_inlines
        global_info["ODEs"] = mechanism_odes
        global_info["Continuous"] = mechanism_continuous_inputs

        return global_info


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


class ASTInputPortDeclarationVisitor(ASTVisitor):
    def __init__(self):
        super(ASTInputPortDeclarationVisitor, self).__init__()
        self.inside_port = False
        self.current_port = None
        self.continuous_ports = list()
        self.all_ports = list()

    def visit_input_port(self, node):
        self.inside_port = True
        self.current_port = node
        self.all_ports.append(node.clone())
        if self.current_port.is_continuous():
            self.continuous_ports.append(node.clone())

    def endvisit_input_port(self, node):
        self.inside_port = False


class ASTLocalVariableDeclarationCollectorVisitor(ASTVisitor):
    def __init__(self):
        super(ASTLocalVariableDeclarationCollectorVisitor, self).__init__()
        self.local_variable_names = set()

    def visit_declaration(self, node):
        for variable in node.get_variables():
            self.local_variable_names.add(variable.get_name())


class ASTOnReceiveBlockCollectorVisitor(ASTVisitor):
    def __init__(self):
        super(ASTOnReceiveBlockCollectorVisitor, self).__init__()
        self.inside_on_receive_block = False
        self.all_on_receive_blocks = list()

    def visit_on_receive_block(self, node):
        self.inside_on_receive_block = True
        self.all_on_receive_blocks.append(node.clone())

    def endvisit_on_receive_block(self, node):
        self.inside_on_receive_block = False
