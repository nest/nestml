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

from typing import Any, Dict, Iterable, List, Sequence, Mapping, Optional, Set, Tuple, Union

try:
    # Available in the standard library starting with Python 3.12
    from typing import override
except ImportError:
    # Fallback for Python 3.8 - 3.11
    from typing_extensions import override

from pynestml.cocos.co_cos_manager import CoCosManager
from pynestml.codegeneration.code_generator_utils import CodeGeneratorUtils
from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.meta_model.ast_assignment import ASTAssignment
from pynestml.meta_model.ast_equations_block import ASTEquationsBlock
from pynestml.meta_model.ast_inline_expression import ASTInlineExpression
from pynestml.meta_model.ast_model import ASTModel
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.symbols.predefined_variables import PredefinedVariables
from pynestml.symbols.symbol import SymbolKind
from pynestml.symbols.variable_symbol import BlockType
from pynestml.transformers.transformer import Transformer
from pynestml.utils.ast_utils import ASTUtils
from pynestml.utils.logger import Logger
from pynestml.utils.logger import LoggingLevel
from pynestml.utils.string_utils import removesuffix
from pynestml.visitors.ast_parent_visitor import ASTParentVisitor
from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor
from pynestml.visitors.ast_higher_order_visitor import ASTHigherOrderVisitor
from pynestml.visitors.ast_visitor import ASTVisitor


class SynapsePostNeuronTransformer(Transformer):
    r"""In a (pre neuron, synapse, post neuron) tuple, process (synapse, post_neuron) to move all variables that are only triggered by postsynaptic events to the postsynaptic neuron.

    Options:

    - **strictly_synaptic_vars**: a mapping from synapse name (as a string) to a list of state variables. These variables will not be moved from synapse to neuron during code generation.
    """

    _default_options = {
        "neuron_synapse_pairs": [],
        "strictly_synaptic_vars": {}
    }

    def __init__(self, options: Optional[Mapping[str, Any]] = None):
        super(Transformer, self).__init__(options)
        self._copy_custom_options(options)

    def _copy_custom_options(self, options):
        if options:
            if "delay_variable" in options:
                self._options["delay_variable"] = options["delay_variable"].copy()

            if "weight_variable" in options:
                self._options["weight_variable"] = options["weight_variable"].copy()

            if "strictly_synaptic_vars" in options:
                self._options["strictly_synaptic_vars"] = options["strictly_synaptic_vars"].copy()

    def set_options(self, options: Mapping[str, Any]) -> Mapping[str, Any]:
        r"""Set options. "Eats off" any options that it knows how to set, and returns the rest as "unhandled" options."""
        unused_options = super().set_options(options)
        self._copy_custom_options(options)

        return unused_options

    def get_neuron_var_name_from_syn_port_name(self, port_name: str, neuron_name: str, synapse_name: str) -> Optional[str]:
        """
        Check if a port by the given name is specified as connecting to the postsynaptic neuron. Only makes sense for synapses.
        """
        if not "neuron_synapse_pairs" in self._options.keys():
            return None

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

    def transform_neuron_synapse_pair_(self, neuron: ASTModel, synapse: ASTModel, metadata) -> Tuple[ASTModel, ASTModel, Dict[str, Dict[str, Any]]]:
        r"""
        "Co-generation" or in-tandem generation of neuron and synapse code.

        Does not modify existing neurons or synapses, but returns lists with additional elements representing new pair neuron and synapse
        """
        new_neuron = neuron.clone()
        new_synapse = synapse.clone()

        new_neuron.parent_ = None    # set root element
        new_neuron.accept(ASTParentVisitor())
        new_synapse.parent_ = None    # set root element
        new_synapse.accept(ASTParentVisitor())
        new_neuron.accept(ASTSymbolTableVisitor())
        new_synapse.accept(ASTSymbolTableVisitor())

        assert len(new_neuron.get_equations_blocks()) <= 1, "Only one equations block per neuron supported for now."
        assert len(new_synapse.get_equations_blocks()) <= 1, "Only one equations block per synapse supported for now."
        assert len(new_neuron.get_state_blocks()) <= 1, "Only one state block supported per neuron for now."
        assert len(new_synapse.get_state_blocks()) <= 1, "Only one state block supported per synapse for now."
        assert len(new_neuron.get_update_blocks()) <= 1, "Only one update block supported per neuron for now."
        assert len(new_synapse.get_update_blocks()) <= 1, "Only one update block supported per synapse for now."

        #
        #   rename new neuron and synapse
        #

        var_name_suffix = "__for_" + synapse.get_name()
        name_separator_str = "__with_"

        new_neuron_name = neuron.get_name() + name_separator_str + synapse.get_name()
        unpaired_name = neuron.get_name()
        new_neuron.set_name(new_neuron_name)
        metadata[new_neuron.name] = {}
        metadata[new_neuron.name]["unpaired_name"] = unpaired_name
        new_synapse_name = synapse.get_name() + name_separator_str + neuron.get_name()
        new_synapse.set_name(new_synapse_name)
        metadata[new_synapse.name] = {}
        metadata[new_synapse.name]["paired_neuron"] = new_neuron
        metadata[new_neuron.name]["paired_synapse"] = new_synapse
        metadata[new_neuron.name]["paired_synapse_original_model"] = synapse

        base_neuron_name = removesuffix(neuron.get_name(), FrontendConfiguration.suffix)
        base_synapse_name = removesuffix(synapse.get_name(), FrontendConfiguration.suffix)

        metadata[new_synapse.name]["post_port_names"] = CodeGeneratorUtils.get_post_port_names(synapse, base_neuron_name, base_synapse_name, neuron_synapse_pairs=self._options["neuron_synapse_pairs"])
        metadata[new_synapse.name]["spiking_post_port_names"] = CodeGeneratorUtils.get_spiking_post_port_names(synapse, base_neuron_name, base_synapse_name, neuron_synapse_pairs=self._options["neuron_synapse_pairs"])
        metadata[new_synapse.name]["vt_port_names"] = CodeGeneratorUtils.get_vt_port_names(synapse, base_neuron_name, base_synapse_name, neuron_synapse_pairs=self._options["neuron_synapse_pairs"])

        #
        #   collect all variables that will be moved from synapse to neuron
        #

        post_port_names = []
        for input_block in new_synapse.get_input_blocks():
            for port in input_block.get_input_ports():
                if CodeGeneratorUtils.is_post_port(port.name, neuron.name, synapse.name, neuron_synapse_pairs=self._options["neuron_synapse_pairs"]):
                    post_port_names.append(port.name)

        # exclude certain variables from being moved:
        strictly_synaptic_vars: Set[str] = set(PredefinedVariables.TIME_CONSTANT)      # "seed" this with the predefined variable t

        if self.option_exists("strictly_synaptic_vars") and removesuffix(synapse.get_name(), FrontendConfiguration.suffix) in self.get_option("strictly_synaptic_vars").keys() and self.get_option("strictly_synaptic_vars")[removesuffix(synapse.get_name(), FrontendConfiguration.suffix)]:
            strictly_synaptic_vars |= set(self.get_option("strictly_synaptic_vars")[removesuffix(synapse.get_name(), FrontendConfiguration.suffix)])

        if self.option_exists("delay_variable") and removesuffix(synapse.get_name(), FrontendConfiguration.suffix) in self.get_option("delay_variable").keys() and self.get_option("delay_variable")[removesuffix(synapse.get_name(), FrontendConfiguration.suffix)]:
            strictly_synaptic_vars.add(self.get_option("delay_variable")[removesuffix(synapse.get_name(), FrontendConfiguration.suffix)])

        if self.option_exists("weight_variable") and removesuffix(synapse.get_name(), FrontendConfiguration.suffix) in self.get_option("weight_variable").keys() and self.get_option("weight_variable")[removesuffix(synapse.get_name(), FrontendConfiguration.suffix)]:
            strictly_synaptic_vars.add(self.get_option("weight_variable")[removesuffix(synapse.get_name(), FrontendConfiguration.suffix)])

        affected_vars = ASTUtils.collect_variables_affected_by_ports(synapse, post_port_names, strictly_synaptic_vars=strictly_synaptic_vars)
        metadata[new_neuron.name]["syn_to_neuron_state_vars"] = [var for var in affected_vars if not (synapse.get_kernel_by_name(var) or neuron.get_kernel_by_name(var))]

        Logger.log_message(None, -1, "State variables that will be moved from synapse to neuron: " + str(affected_vars),
                           None, LoggingLevel.INFO)

        #
        #   collect all the parameters
        #

        syn_to_neuron_params, all_declared_params = ASTUtils.collect_parameters_needed_for_state_vars(synapse, affected_vars)

        Logger.log_message(None, -1, "Parameters that will be copied from synapse to neuron: " + str(syn_to_neuron_params),
                           None, LoggingLevel.INFO)

        #
        #   collect all the internal parameters
        #

        # XXX: TODO

        #
        #   collect all ``continuous`` type input ports that are connected to postsynaptic neuron
        #

        post_connected_continuous_input_ports = []
        post_variable_names = []
        for input_block in synapse.get_input_blocks():
            for port in input_block.get_input_ports():
                if CodeGeneratorUtils.is_post_port(port.get_name(), neuron.name, synapse.name, neuron_synapse_pairs=self._options["neuron_synapse_pairs"]) and CodeGeneratorUtils.is_continuous_port(port.get_name(), synapse):
                    post_connected_continuous_input_ports.append(port.get_name())
                    post_variable_names.append(self.get_neuron_var_name_from_syn_port_name(port.get_name(), neuron.name, synapse.name))

        #
        #   collect all ``continuous`` type input ports, the value of which is used in event handlers -- these have to be buffered in the hist_entry for each post spike in the postsynaptic history
        #

        state_vars_that_need_continuous_buffering = []
        for input_block in new_synapse.get_input_blocks():
            for port in input_block.get_input_ports():
                if CodeGeneratorUtils.is_continuous_port(port.name, new_synapse):
                    state_vars_that_need_continuous_buffering.append(port.name)

        # check that they are not used in the update block
        update_block_var_names = []
        for update_block in synapse.get_update_blocks():
            update_block_var_names.extend([var.get_complete_name() for var in ASTUtils.collect_variable_names_in_expression(update_block)])

        assert all([var not in update_block_var_names for var in state_vars_that_need_continuous_buffering])

        Logger.log_message(None, -1, "Synaptic state variables moved to neuron that will need buffering: " + str(state_vars_that_need_continuous_buffering), None, LoggingLevel.INFO)

        metadata[new_neuron.name]["state_vars_that_need_continuous_buffering"] = state_vars_that_need_continuous_buffering

        #
        #   move defining equations for variables from synapse to neuron
        #

        if not new_synapse.get_equations_blocks():
            ASTUtils.create_equations_block(new_synapse)

        if not new_neuron.get_equations_blocks():
            ASTUtils.create_equations_block(new_neuron)

        for var in affected_vars:
            Logger.log_message(None, -1, "Moving state var defining equation(s) " + str(var),
                               None, LoggingLevel.INFO)
            # move the ODE so a solver will be generated for it by ODE-toolbox
            decls = ASTUtils.equations_from_block_to_block(var,
                                                           new_synapse.get_equations_blocks()[0],
                                                           new_neuron.get_equations_blocks()[0],
                                                           var_name_suffix,
                                                           mode="move")
            ASTUtils.add_suffix_to_variable_names2(post_port_names + affected_vars + syn_to_neuron_params, decls, var_name_suffix)
            ASTUtils.replace_post_moved_variable_names(decls, [name + var_name_suffix for name in post_connected_continuous_input_ports], post_variable_names)
            ASTUtils.remove_state_var_from_integrate_odes_calls(new_synapse, var)
            # ASTUtils.add_integrate_odes_call_to_update_block(new_neuron, var)   # the moved state variables are never needed inside the neuron, their values are only read out from the side of the synapse. Therefore they do not have to be added to integrate_odes() calls; we just have to make sure the value has been updated before the end of the timestep
            # for now, moved variables are integrated separately in time in set_spiketime()

        #
        #    move initial values for equations
        #

        if affected_vars and not new_neuron.get_state_blocks():
            ASTUtils.create_state_block(new_neuron)

        for var in affected_vars:
            Logger.log_message(None, -1, "Moving state variables for equation(s) " + str(var),
                               None, LoggingLevel.INFO)
            ASTUtils.move_decls(var_name=var,
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
                    if CodeGeneratorUtils.is_post_port(var_base_name, neuron.name, synapse.name, neuron_synapse_pairs=self._options["neuron_synapse_pairs"]):
                        post_ports.append(var)
                        var._is_post_port = True

            mark_node.accept(ASTHigherOrderVisitor(lambda x: mark_post_port(x)))
            return post_ports

        mark_post_ports(new_neuron, new_synapse, new_neuron)

        #
        #    move statements in post receive block from synapse to new_neuron
        #

        # XXX: TODO: do not use a new member variable (`extra_on_emit_spike_stmts_from_synapse`) for this, but add a new event handler block in the neuron

        # find all statements in post receive block
        collected_on_post_stmts = []

        recursive_vars_used = ASTUtils.recursive_necessary_variables_search(affected_vars, synapse)

        metadata[new_neuron.name]["recursive_vars_used"] = recursive_vars_used

        for input_block in new_synapse.get_input_blocks():
            for port in input_block.get_input_ports():
                if CodeGeneratorUtils.is_post_port(port.name, neuron.name, synapse.name, neuron_synapse_pairs=self._options["neuron_synapse_pairs"]):
                    post_receive_blocks = ASTUtils.get_on_receive_blocks_by_input_port_name(new_synapse, port.name)
                    for post_receive_block in post_receive_blocks:
                        stmts = post_receive_block.get_stmts_body().get_stmts()
                        for stmt in stmts:
                            if stmt.is_small_stmt() \
                               and stmt.small_stmt.is_assignment() \
                               and ASTUtils.depends_only_on_vars(stmt.small_stmt.get_assignment().rhs, recursive_vars_used + all_declared_params) \
                               and stmt.small_stmt.get_assignment().get_variable().get_complete_name() in syn_to_neuron_params + affected_vars:
                                Logger.log_message(None, -1, "\tMoving statement " + str(stmt).strip(), None, LoggingLevel.INFO)

                                collected_on_post_stmts.append(stmt)

                                stmt.scope = new_neuron.scope
                                stmt.small_stmt.scope = new_neuron.scope
                                stmt.small_stmt.get_assignment().scope = new_neuron.scope
                                stmt.small_stmt.get_assignment().get_variable().scope = new_neuron.scope

                        for stmt in collected_on_post_stmts:
                            stmts.pop(stmts.index(stmt))

        metadata[new_neuron.name]["extra_on_emit_spike_stmts_from_synapse"] = collected_on_post_stmts

        #
        #   replace ``continuous`` type input ports that are connected to postsynaptic neuron with suffixed external variable references
        #

        Logger.log_message(
            None, -1, "In synapse: replacing ``continuous`` type input ports that are connected to postsynaptic neuron with external variable references", None, LoggingLevel.INFO)

        post_connected_continuous_input_ports = []
        post_variable_names = []
        for input_block in synapse.get_input_blocks():
            for port in input_block.get_input_ports():
                if CodeGeneratorUtils.is_post_port(port.get_name(), neuron.name, synapse.name, neuron_synapse_pairs=self._options["neuron_synapse_pairs"]) and CodeGeneratorUtils.is_continuous_port(port.get_name(), synapse):
                    post_connected_continuous_input_ports.append(port.get_name())
                    post_variable_names.append(self.get_neuron_var_name_from_syn_port_name(
                        port.get_name(), neuron.name, synapse.name))

        for var in post_connected_continuous_input_ports:
            Logger.log_message(None, -1, "\t• Replacing variable " + str(var), None, LoggingLevel.INFO)
            ASTUtils.replace_with_external_variable(var, new_synapse, "", None, "__" + var)

        #
        #    copy parameters
        #

        if not new_neuron.get_parameters_blocks():
            ASTUtils.create_parameters_block(new_neuron)

        Logger.log_message(None, -1, "Copying parameters from synapse to neuron...", None, LoggingLevel.INFO)
        for param_var in syn_to_neuron_params:
            decls = ASTUtils.move_decls(param_var,
                                        new_synapse.get_parameters_blocks()[0],
                                        new_neuron.get_parameters_blocks()[0],
                                        var_name_suffix=var_name_suffix,
                                        block_type=BlockType.PARAMETERS,
                                        mode="copy")

        #
        #   add suffix to variables in moved update statements
        #

        Logger.log_message(
            None, -1, "Adding suffix to variables in spike updates", None, LoggingLevel.INFO)

        for stmt in metadata[new_neuron.name]["extra_on_emit_spike_stmts_from_synapse"]:
            ASTUtils.add_suffix_to_variable_names(stmt, var_name_suffix, altscope=synapse.get_scope())
            ASTUtils.set_new_scope(stmt, new_neuron.get_scope())

        #
        #    replace occurrences of the variables in expressions in the original synapse with calls to the corresponding neuron getters
        #

        Logger.log_message(
            None, -1, "In synapse: replacing variables with suffixed external variable references", None, LoggingLevel.INFO)
        for var in affected_vars:
            Logger.log_message(None, -1, "\t• Replacing variable " + str(var), None, LoggingLevel.INFO)
            ASTUtils.replace_with_external_variable(var, new_synapse, var_name_suffix, new_neuron.get_scope())

        #
        #     remove newly added equation blocks again if they are empty
        #

        ASTUtils.remove_empty_equations_blocks(new_synapse)
        ASTUtils.remove_empty_equations_blocks(new_neuron)

        #
        #    add modified versions of neuron and synapse to list
        #

        new_neuron.accept(ASTParentVisitor())
        new_synapse.accept(ASTParentVisitor())
        ast_symbol_table_visitor = ASTSymbolTableVisitor()
        new_neuron.accept(ast_symbol_table_visitor)
        new_synapse.accept(ast_symbol_table_visitor)

        ASTUtils.update_blocktype_for_common_parameters(new_synapse)

        Logger.log_message(None, -1, "Successfully constructed neuron-synapse pair "
                           + new_neuron.name + ", " + new_synapse.name, None, LoggingLevel.INFO)

        return new_neuron, new_synapse

    @override
    def transform(self,
                  models: Iterable[ASTModel],
                  metadata: Optional[Mapping[str, Mapping[str, Any]]] = None) -> Union[ASTModel, Iterable[ASTModel]]:
        models = list(models)

        for neuron_synapse_pair in self.get_option("neuron_synapse_pairs"):
            neuron_name = neuron_synapse_pair["neuron"]
            synapse_name = neuron_synapse_pair["synapse"]
            neuron = ASTUtils.find_model_by_name(neuron_name + FrontendConfiguration.suffix, models)
            if neuron is None:
                raise Exception("Neuron used in pair (\"" + neuron_name + "\") not found")  # XXX: log error

            synapse = ASTUtils.find_model_by_name(synapse_name + FrontendConfiguration.suffix, models)
            if synapse is None:
                raise Exception("Synapse used in pair (\"" + synapse_name + "\") not found")  # XXX: log error

            new_neuron, new_synapse = self.transform_neuron_synapse_pair_(neuron, synapse, metadata)
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
