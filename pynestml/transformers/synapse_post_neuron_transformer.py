# -*- coding: utf-8 -*-
#
# synapse_post_neuron_transformer.py
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

from __future__ import annotations

from typing import Any, Sequence, Mapping, Optional, Union

from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.meta_model.ast_assignment import ASTAssignment
from pynestml.meta_model.ast_equations_block import ASTEquationsBlock
from pynestml.meta_model.ast_inline_expression import ASTInlineExpression
from pynestml.meta_model.ast_neuron_or_synapse import ASTNeuronOrSynapse
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.symbols.symbol import SymbolKind
from pynestml.symbols.variable_symbol import BlockType
from pynestml.transformers.transformer import Transformer
from pynestml.utils.ast_utils import ASTUtils
from pynestml.utils.logger import Logger
from pynestml.utils.logger import LoggingLevel
from pynestml.utils.string_utils import removesuffix
from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor
from pynestml.visitors.ast_higher_order_visitor import ASTHigherOrderVisitor
from pynestml.visitors.ast_visitor import ASTVisitor


class SynapsePostNeuronTransformer(Transformer):
    r"""In a (pre neuron, synapse, post neuron) tuple, process (synapse, post_neuron) to move all variables that are only triggered by postsynaptic events to the postsynaptic neuron."""

    _default_options = {
        "neuron_synapse_pairs": []
    }

    def __init__(self, options: Optional[Mapping[str, Any]] = None):
        super(Transformer, self).__init__(options)

    def is_special_port(self, special_type: str, port_name: str, neuron_name: str, synapse_name: str) -> bool:
        """
        Check if a port by the given name is specified as connecting to the postsynaptic neuron. Only makes sense
        for synapses.
        """
        assert special_type in ["post", "vt"]
        if not "neuron_synapse_pairs" in self._options.keys():
            return False

        for neuron_synapse_pair in self._options["neuron_synapse_pairs"]:
            if not (neuron_name in [neuron_synapse_pair["neuron"], neuron_synapse_pair["neuron"] + FrontendConfiguration.suffix]
                    and synapse_name in [neuron_synapse_pair["synapse"], neuron_synapse_pair["synapse"] + FrontendConfiguration.suffix]):
                continue

            if not special_type + "_ports" in neuron_synapse_pair.keys():
                return False

            post_ports = neuron_synapse_pair[special_type + "_ports"]
            if not isinstance(post_ports, list):
                # only one port name given, not a list
                return port_name == post_ports

            for post_port in post_ports:
                if type(post_port) is not str and len(post_port) == 2:  # (syn_port_name, neuron_port_name) tuple
                    post_port = post_port[0]
                if type(post_port) is not str and len(post_port) == 1:  # (syn_port_name)
                    return post_port[0] == port_name
                if port_name == post_port:
                    return True

        return False

    def is_continuous_port(self, port_name: str, parent_node: ASTNeuronOrSynapse):
        for input_block in parent_node.get_input_blocks():
            for port in input_block.get_input_ports():
                if port.is_continuous() and port_name == port.get_name():
                    return True
        return False

    def is_post_port(self, port_name: str, neuron_name: str, synapse_name: str) -> bool:
        return self.is_special_port("post", port_name, neuron_name, synapse_name)

    def is_vt_port(self, port_name: str, neuron_name: str, synapse_name: str) -> bool:
        return self.is_special_port("vt", port_name, neuron_name, synapse_name)

    def get_spiking_post_port_names(self, synapse, neuron_name: str, synapse_name: str):
        post_port_names = []
        for input_block in synapse.get_input_blocks():
            for port in input_block.get_input_ports():
                if self.is_post_port(port.name, neuron_name, synapse_name) and port.is_spike():
                    post_port_names.append(port.get_name())
        return post_port_names

    def get_post_port_names(self, synapse, neuron_name: str, synapse_name: str):
        post_port_names = []
        for input_block in synapse.get_input_blocks():
            for port in input_block.get_input_ports():
                if self.is_post_port(port.name, neuron_name, synapse_name):
                    post_port_names.append(port.get_name())
        return post_port_names

    def get_vt_port_names(self, synapse, neuron_name: str, synapse_name: str):
        post_port_names = []
        for input_block in synapse.get_input_blocks():
            for port in input_block.get_input_ports():
                if self.is_vt_port(port.name, neuron_name, synapse_name):
                    post_port_names.append(port.get_name())
        return post_port_names

    def get_neuron_var_name_from_syn_port_name(self, port_name: str, neuron_name: str, synapse_name: str) -> Optional[str]:
        """
        Check if a port by the given name is specified as connecting to the postsynaptic neuron. Only makes sense for synapses.
        """
        if not "neuron_synapse_pairs" in self._options.keys():
            return False

        for neuron_synapse_pair in self._options["neuron_synapse_pairs"]:
            if not (neuron_name in [neuron_synapse_pair["neuron"], neuron_synapse_pair["neuron"] + FrontendConfiguration.suffix]
                    and synapse_name in [neuron_synapse_pair["synapse"], neuron_synapse_pair["synapse"] + FrontendConfiguration.suffix]):
                continue

            if not "post_ports" in neuron_synapse_pair.keys():
                return None

            post_ports = neuron_synapse_pair["post_ports"]

            for post_port in post_ports:
                if type(post_port) is not str and len(post_port) == 2:  # (syn_port_name, neuron_var_name) tuple
                    if port_name == post_port[0]:
                        return post_port[1]

            return None

        return None

    def get_convolve_with_not_post_vars(self, nodes: Union[ASTEquationsBlock, Sequence[ASTEquationsBlock]], neuron_name: str, synapse_name: str, parent_node: ASTNode):
        class ASTVariablesUsedInConvolutionVisitor(ASTVisitor):
            _variables = []

            def __init__(self, node: ASTNode, parent_node: ASTNode, codegen_class):
                super(ASTVariablesUsedInConvolutionVisitor, self).__init__()
                self.node = node
                self.parent_node = parent_node
                self.codegen_class = codegen_class

            def visit_function_call(self, node):
                func_name = node.get_name()
                if func_name == "convolve":
                    symbol_buffer = node.get_scope().resolve_to_symbol(str(node.get_args()[1]),
                                                                       SymbolKind.VARIABLE)
                    input_port = ASTUtils.get_input_port_by_name(
                        self.parent_node.get_input_blocks(), symbol_buffer.name)
                    if input_port and not self.codegen_class.is_post_port(input_port.name, neuron_name, synapse_name):
                        kernel_name = node.get_args()[0].get_variable().name
                        self._variables.append(kernel_name)

                        found_parent_assignment = False
                        node_ = node
                        while not found_parent_assignment:
                            node_ = self.parent_node.get_parent(node_)
                            # XXX TODO also needs to accept normal ASTExpression, ASTAssignment?
                            if isinstance(node_, ASTInlineExpression):
                                found_parent_assignment = True
                        var_name = node_.get_variable_name()
                        self._variables.append(var_name)

        if not nodes:
            return []

        if isinstance(nodes, ASTNode):
            nodes = [nodes]

        variables = []
        for node in nodes:
            visitor = ASTVariablesUsedInConvolutionVisitor(node, parent_node, self)
            node.accept(visitor)
            variables.extend(visitor._variables)

        return variables

    def get_all_variables_assigned_to(self, node):
        class ASTAssignedToVariablesFinderVisitor(ASTVisitor):
            _variables = []

            def __init__(self, synapse):
                super(ASTAssignedToVariablesFinderVisitor, self).__init__()
                self.synapse = synapse

            def visit_assignment(self, node):
                symbol = node.get_scope().resolve_to_symbol(node.get_variable().get_complete_name(), SymbolKind.VARIABLE)
                assert symbol is not None  # should have been checked in a CoCo before
                self._variables.append(symbol)

        if node is None:
            return []

        visitor = ASTAssignedToVariablesFinderVisitor(node)
        node.accept(visitor)

        return [v.name for v in visitor._variables]

    def transform_neuron_synapse_pair_(self, neuron, synapse):
        r"""
        "Co-generation" or in-tandem generation of neuron and synapse code.

        Does not modify existing neurons or synapses, but returns lists with additional elements representing new pair neuron and synapse
        """

        new_neuron = neuron.clone()
        new_synapse = synapse.clone()

        new_neuron.accept(ASTSymbolTableVisitor())
        new_synapse.accept(ASTSymbolTableVisitor())

        assert len(new_neuron.get_equations_blocks()) <= 1, "Only one equations block per neuron supported for now."
        assert len(new_synapse.get_equations_blocks()) <= 1, "Only one equations block per synapse supported for now."
        assert len(new_neuron.get_state_blocks()) <= 1, "Only one state block supported per neuron for now."
        assert len(new_synapse.get_state_blocks()) <= 1, "Only one state block supported per synapse for now."
        assert len(new_neuron.get_update_blocks()) <= 1, "Only one update block supported per neuron for now."
        assert len(new_synapse.get_update_blocks()) <= 1, "Only one update block supported per synapse for now."

        #
        #   suffix for variables that will be transferred to neuron
        #

        var_name_suffix = "__for_" + synapse.get_name()

        #
        #   determine which variables and dynamics in synapse can be transferred to neuron
        #

        if synapse.get_state_blocks():
            all_state_vars = ASTUtils.all_variables_defined_in_block(synapse.get_state_blocks()[0])
        else:
            all_state_vars = []

        all_state_vars = [var.get_complete_name() for var in all_state_vars]

        # add names of convolutions
        all_state_vars += ASTUtils.get_all_variables_used_in_convolutions(synapse.get_equations_blocks(), synapse)

        # add names of kernels
        kernel_buffers = ASTUtils.generate_kernel_buffers_(synapse, synapse.get_equations_blocks())
        all_state_vars += [var.name for k in kernel_buffers for var in k[0].variables]

        # if any variable is assigned to in any block that is not connected to a postsynaptic port
        strictly_synaptic_vars = []
        for input_block in new_synapse.get_input_blocks():
            for port in input_block.get_input_ports():
                if (not self.is_post_port(port.name, neuron.name, synapse.name)) or self.is_vt_port(port.name, neuron.name, synapse.name):
                    strictly_synaptic_vars += self.get_all_variables_assigned_to(synapse.get_on_receive_block(port.name))

        for update_block in synapse.get_update_blocks():
            strictly_synaptic_vars += self.get_all_variables_assigned_to(update_block)

        convolve_with_not_post_vars = self.get_convolve_with_not_post_vars(synapse.get_equations_blocks(), neuron.name, synapse.name, synapse)

        strictly_synaptic_vars_dependent = ASTUtils.recursive_dependent_variables_search(strictly_synaptic_vars, synapse)

        syn_to_neuron_state_vars = list(set(all_state_vars) - (set(strictly_synaptic_vars) | set(convolve_with_not_post_vars) | set(strictly_synaptic_vars_dependent)))

        #
        #   collect all the variable/parameter/kernel/function/etc. names used in defining expressions of `syn_to_neuron_state_vars`
        #

        recursive_vars_used = ASTUtils.recursive_dependent_variables_search(syn_to_neuron_state_vars, synapse)
        new_neuron.recursive_vars_used = recursive_vars_used
        new_neuron._transferred_variables = [neuron_state_var + var_name_suffix
                                             for neuron_state_var in syn_to_neuron_state_vars
                                             if new_synapse.get_kernel_by_name(neuron_state_var) is None]

        # all state variables that will be moved from synapse to neuron
        syn_to_neuron_state_vars = []
        for var_name in recursive_vars_used:
            if ASTUtils.get_state_variable_by_name(synapse, var_name) or ASTUtils.get_inline_expression_by_name(synapse, var_name) or ASTUtils.get_kernel_by_name(synapse, var_name):
                syn_to_neuron_state_vars.append(var_name)

        Logger.log_message(None, -1, "State variables that will be moved from synapse to neuron: " + str(syn_to_neuron_state_vars),
                           None, LoggingLevel.INFO)

        #
        #   collect all the parameters
        #

        all_declared_params = [s.get_variables() for s in new_synapse.get_parameters_blocks()[0].get_declarations()]
        all_declared_params = sum(all_declared_params, [])
        all_declared_params = [var.name for var in all_declared_params]

        syn_to_neuron_params = [v for v in recursive_vars_used if v in all_declared_params]

        # parameters used in the declarations of the state variables
        vars_used = []
        for var in syn_to_neuron_state_vars:
            decls = ASTUtils.get_declarations_from_block(var, neuron.get_state_blocks()[0])
            for decl in decls:
                if decl.has_expression():
                    vars_used.extend(ASTUtils.collect_variable_names_in_expression(decl.get_expression()))

            # parameters used in equations
            for equations_block in neuron.get_equations_blocks():
                vars_used.extend(ASTUtils.collects_vars_used_in_equation(var, equations_block))

        syn_to_neuron_params.extend([var for var in vars_used if var in all_declared_params])

        Logger.log_message(None, -1, "Parameters that will be copied from synapse to neuron: " + str(syn_to_neuron_params),
                           None, LoggingLevel.INFO)

        #
        #   collect all the internal parameters
        #

        # XXX: TODO

        #
        #   move state variable declarations from synapse to neuron
        #

        for state_var in syn_to_neuron_state_vars:
            decls = ASTUtils.move_decls(state_var,
                                        neuron.get_state_blocks()[0],
                                        synapse.get_state_blocks()[0],
                                        var_name_suffix,
                                        block_type=BlockType.STATE)
            ASTUtils.add_suffix_to_variable_names(decls, var_name_suffix)

        #
        #   move defining equations for variables from synapse to neuron
        #

        if not new_synapse.get_equations_blocks():
            ASTUtils.create_equations_block(new_synapse)

        if not new_neuron.get_equations_blocks():
            ASTUtils.create_equations_block(new_neuron)

        for state_var in syn_to_neuron_state_vars:
            Logger.log_message(None, -1, "Moving state var defining equation(s) " + str(state_var),
                               None, LoggingLevel.INFO)
            decls = ASTUtils.equations_from_block_to_block(state_var,
                                                           new_synapse.get_equations_blocks()[0],
                                                           new_neuron.get_equations_blocks()[0],
                                                           var_name_suffix,
                                                           mode="move")
            ASTUtils.add_suffix_to_variable_names(decls, var_name_suffix)

        #
        #    move initial values for equations
        #

        for state_var in syn_to_neuron_state_vars:
            Logger.log_message(None, -1, "Moving state variables for equation(s) " + str(state_var),
                               None, LoggingLevel.INFO)
            ASTUtils.move_decls(var_name=state_var,
                                from_block=new_synapse.get_state_blocks()[0],
                                to_block=new_neuron.get_state_blocks()[0],
                                var_name_suffix=var_name_suffix,
                                block_type=BlockType.STATE,
                                mode="move")

        #
        #     mark variables in the neuron pertaining to synapse postsynaptic ports
        #
        #     convolutions with them ultimately yield variable updates when post neuron calls emit_spike()
        #

        def mark_post_ports(neuron, synapse, mark_node):
            post_ports = []

            def mark_post_port(_expr=None):
                var = None
                if isinstance(_expr, ASTSimpleExpression) and _expr.is_variable():
                    var = _expr.get_variable()
                elif isinstance(_expr, ASTVariable):
                    var = _expr

                if var:
                    var_base_name = var.name[:-len(var_name_suffix)]   # prune the suffix
                    if self.is_post_port(var_base_name, neuron.name, synapse.name):
                        post_ports.append(var)
                        var._is_post_port = True

            mark_node.accept(ASTHigherOrderVisitor(lambda x: mark_post_port(x)))
            return post_ports

        mark_post_ports(new_neuron, new_synapse, new_neuron)

        #
        #    move statements in post receive block from synapse to ``new_neuron.moved_spike_updates``
        #

        vars_used = []

        new_neuron.moved_spike_updates = []

        spiking_post_port_names = self.get_spiking_post_port_names(synapse, neuron.name, synapse.name)
        assert len(spiking_post_port_names) <= 1, "Can only handle one spiking \"post\" port"
        if len(spiking_post_port_names) > 0:
            post_port_name = spiking_post_port_names[0]
            post_receive_block = new_synapse.get_on_receive_block(post_port_name)
            assert post_receive_block is not None
            for state_var in syn_to_neuron_state_vars:
                Logger.log_message(None, -1, "Moving onPost updates for " + str(state_var), None, LoggingLevel.INFO)

                stmts = ASTUtils.get_statements_from_block(state_var, post_receive_block)
                if stmts:
                    Logger.log_message(None, -1, "Moving state var updates for " + state_var
                                       + " from synapse to neuron", None, LoggingLevel.INFO)
                    for stmt in stmts:
                        vars_used.extend(ASTUtils.collect_variable_names_in_expression(stmt))
                        post_receive_block.block.stmts.remove(stmt)
                        ASTUtils.add_suffix_to_decl_lhs(stmt, suffix=var_name_suffix)
                        ASTUtils.add_suffix_to_variable_names(stmt, var_name_suffix)
                        stmt.update_scope(new_neuron.get_update_blocks()[0].get_scope())
                        stmt.accept(ASTSymbolTableVisitor())
                        new_neuron.moved_spike_updates.append(stmt)

        vars_used = list(set([v.name for v in vars_used]))
        syn_to_neuron_params.extend([v for v in vars_used if v in [p + var_name_suffix for p in all_declared_params]])

        #
        #   replace ``continuous`` type input ports that are connected to postsynaptic neuron with suffixed external variable references
        #

        Logger.log_message(
            None, -1, "In synapse: replacing ``continuous`` type input ports that are connected to postsynaptic neuron with suffixed external variable references", None, LoggingLevel.INFO)
        post_connected_continuous_input_ports = []
        post_variable_names = []
        for input_block in synapse.get_input_blocks():
            for port in input_block.get_input_ports():
                if self.is_post_port(port.get_name(), neuron.name, synapse.name) and self.is_continuous_port(port.get_name(), synapse):
                    post_connected_continuous_input_ports.append(port.get_name())
                    post_variable_names.append(self.get_neuron_var_name_from_syn_port_name(
                        port.get_name(), neuron.name, synapse.name))

        for state_var, alternate_name in zip(post_connected_continuous_input_ports, post_variable_names):
            Logger.log_message(None, -1, "\t• Replacing variable " + str(state_var), None, LoggingLevel.INFO)
            ASTUtils.replace_with_external_variable(state_var, new_synapse, "",
                                                    new_synapse.get_equations_blocks()[0], alternate_name)

        #
        #    copy parameters
        #

        Logger.log_message(None, -1, "Copying parameters from synapse to neuron...", None, LoggingLevel.INFO)
        for param_var in syn_to_neuron_params:
            decls = ASTUtils.move_decls(param_var,
                                        new_synapse.get_parameters_blocks()[0],
                                        new_neuron.get_parameters_blocks()[0],
                                        var_name_suffix=var_name_suffix,
                                        block_type=BlockType.PARAMETERS,
                                        mode="copy")

        #
        #   add suffix to variables in spike updates
        #

        Logger.log_message(
            None, -1, "Adding suffix to variables in spike updates", None, LoggingLevel.INFO)

        for stmt in new_neuron.moved_spike_updates:
            for param_var in syn_to_neuron_params:
                param_var = str(param_var)
                ASTUtils.add_suffix_to_variable_name(param_var, stmt, var_name_suffix, scope=new_neuron.get_update_blocks()[0].get_scope())

        #
        #    replace occurrences of the variables in expressions in the original synapse with calls to the corresponding neuron getters
        #

        Logger.log_message(
            None, -1, "In synapse: replacing variables with suffixed external variable references", None, LoggingLevel.INFO)
        for state_var in syn_to_neuron_state_vars:
            Logger.log_message(None, -1, "\t• Replacing variable " + str(state_var), None, LoggingLevel.INFO)
            ASTUtils.replace_with_external_variable(
                state_var, new_synapse, var_name_suffix, new_neuron.get_equations_blocks()[0])

        #
        #     rename neuron
        #

        name_separator_str = "__with_"

        new_neuron_name = neuron.get_name() + name_separator_str + synapse.get_name()
        new_neuron.set_name(new_neuron_name)
        new_neuron.paired_synapse = new_synapse

        #
        #    rename synapse
        #

        new_synapse_name = synapse.get_name() + name_separator_str + neuron.get_name()
        new_synapse.set_name(new_synapse_name)
        new_synapse.paired_neuron = new_neuron
        new_neuron.paired_synapse = new_synapse

        base_neuron_name = removesuffix(neuron.get_name(), FrontendConfiguration.suffix)
        base_synapse_name = removesuffix(synapse.get_name(), FrontendConfiguration.suffix)

        new_synapse.post_port_names = self.get_post_port_names(synapse, base_neuron_name, base_synapse_name)
        new_synapse.spiking_post_port_names = self.get_spiking_post_port_names(synapse, base_neuron_name, base_synapse_name)
        new_synapse.vt_port_names = self.get_vt_port_names(synapse, base_neuron_name, base_synapse_name)

        #
        #    add modified versions of neuron and synapse to list
        #

        new_neuron.accept(ASTSymbolTableVisitor())
        new_synapse.accept(ASTSymbolTableVisitor())

        ASTUtils.update_blocktype_for_common_parameters(new_synapse)

        Logger.log_message(None, -1, "Successfully constructed neuron-synapse pair "
                           + new_neuron.name + ", " + new_synapse.name, None, LoggingLevel.INFO)

        return new_neuron, new_synapse

    def transform(self, models: Union[ASTNode, Sequence[ASTNode]]) -> Union[ASTNode, Sequence[ASTNode]]:
        for neuron_synapse_pair in self.get_option("neuron_synapse_pairs"):
            neuron_name = neuron_synapse_pair["neuron"]
            synapse_name = neuron_synapse_pair["synapse"]
            neuron = ASTUtils.find_model_by_name(neuron_name + FrontendConfiguration.suffix, models)
            if neuron is None:
                raise Exception("Neuron used in pair (\"" + neuron_name + "\") not found")  # XXX: log error

            synapse = ASTUtils.find_model_by_name(synapse_name + FrontendConfiguration.suffix, models)
            if synapse is None:
                raise Exception("Synapse used in pair (\"" + synapse_name + "\") not found")  # XXX: log error

            new_neuron, new_synapse = self.transform_neuron_synapse_pair_(neuron, synapse)
            models.append(new_neuron)
            models.append(new_synapse)

        # remove the synapses used in neuron-synapse pairs, as they can potentially not be generated independently of a neuron and would otherwise result in an error
        for neuron_synapse_pair in self.get_option("neuron_synapse_pairs"):
            synapse_name = neuron_synapse_pair["synapse"]
            synapse = ASTUtils.find_model_by_name(synapse_name + FrontendConfiguration.suffix, models)
            if synapse:
                model_idx = models.index(synapse)
                models.pop(model_idx)

        return models
