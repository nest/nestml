# -*- coding: utf-8 -*-
#
# synapse_remove_post_port.py
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

from typing import Optional, Mapping, Any, Union, Sequence

from pynestml.meta_model.ast_node import ASTNode

from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.transformers.transformer import Transformer
from pynestml.utils.ast_utils import ASTUtils
from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor
from pynestml.frontend.frontend_configuration import FrontendConfiguration

from pynestml.utils.string_utils import removesuffix


class SynapseRemovePostPortTransformer(Transformer):
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
            if not (neuron_name in [neuron_synapse_pair["neuron"],
                                    neuron_synapse_pair["neuron"] + FrontendConfiguration.suffix]
                    and synapse_name in [neuron_synapse_pair["synapse"],
                                         neuron_synapse_pair["synapse"] + FrontendConfiguration.suffix]):
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

    def is_post_port(self, port_name: str, neuron_name: str, synapse_name: str) -> bool:
        return self.is_special_port("post", port_name, neuron_name, synapse_name)

    def is_vt_port(self, port_name: str, neuron_name: str, synapse_name: str) -> bool:
        return self.is_special_port("vt", port_name, neuron_name, synapse_name)

    def get_post_port_names(self, synapse, neuron_name: str, synapse_name: str):
        post_port_names = []
        for input_block in synapse.get_input_blocks():
            for port in input_block.get_input_ports():
                if self.is_post_port(port.name, neuron_name, synapse_name):
                    post_port_names.append(port.get_name())
        return post_port_names

    def get_spiking_post_port_names(self, synapse, neuron_name: str, synapse_name: str):
        post_port_names = []
        for input_block in synapse.get_input_blocks():
            for port in input_block.get_input_ports():
                if self.is_post_port(port.name, neuron_name, synapse_name) and port.is_spike():
                    post_port_names.append(port.get_name())
        return post_port_names

    def get_vt_port_names(self, synapse, neuron_name: str, synapse_name: str):
        post_port_names = []
        for input_block in synapse.get_input_blocks():
            for port in input_block.get_input_ports():
                if self.is_vt_port(port.name, neuron_name, synapse_name):
                    post_port_names.append(port.get_name())
        return post_port_names

    def transform_neuron_synapse_pair_(self, neuron, synapse):

        new_neuron = neuron.clone()
        new_synapse = synapse.clone()

        assert len(new_neuron.get_equations_blocks()) <= 1, "Only one equations block per neuron supported for now."
        assert len(new_synapse.get_equations_blocks()) <= 1, "Only one equations block per synapse supported for now."
        assert len(new_neuron.get_state_blocks()) <= 1, "Only one state block supported per neuron for now."
        assert len(new_synapse.get_state_blocks()) <= 1, "Only one state block supported per synapse for now."
        assert len(new_neuron.get_update_blocks()) <= 1, "Only one update block supported per neuron for now."
        assert len(new_synapse.get_update_blocks()) <= 1, "Only one update block supported per synapse for now."

        #
        #     rename neuron
        #

        name_separator_str = "__with_"

        new_neuron_name = neuron.get_name() + name_separator_str + synapse.get_name()
        new_neuron.set_name(new_neuron_name)
        new_neuron.paired_synapse = new_synapse
        new_neuron.recursive_vars_used = []
        new_neuron._transferred_variables = []

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
        new_synapse.spiking_post_port_names = self.get_spiking_post_port_names(synapse, base_neuron_name,
                                                                               base_synapse_name)
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

            # Replace the original synapse model with the co-generated one
            model_idx = models.index(synapse)
            models[model_idx] = new_synapse
            models.append(new_neuron)

        return models
