# -*- coding: utf-8 -*-
#
# code_generator_utils.py
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

from typing import List, Optional

from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.meta_model.ast_model import ASTModel
from pynestml.utils.string_utils import removesuffix


class CodeGeneratorUtils:

    @classmethod
    def get_model_types_from_names(cls, models: List[ASTModel], synapse_models: Optional[List[str]] = None):
        r"""
        Determine which models are neuron models, and which are synapse models. All model names given in ``synapse_models``, as well as models of which the name ends in ``synapse``, are taken to be synapse models. All others are taken to be neuron models.

        :param models: a list of models
        :param synapse_models: a list of model names that should be interpreted as synapse models.
        :return: a tuple ``(neurons, synapses)``, each element a list of strings containing model names.
        """

        if synapse_models is None:
            synapse_models = []

        neurons = []
        synapses = []
        for model in models:
            stripped_model_name = removesuffix(removesuffix(model.name.split("_with_")[0], "_"), FrontendConfiguration.suffix)

            if stripped_model_name in synapse_models \
               or stripped_model_name.endswith("synapse"):
                synapses.append(model)
            else:
                neurons.append(model)

        return neurons, synapses

    @classmethod
    def is_special_port(cls, special_type: str, port_name: str, neuron_name: str, synapse_name: str, neuron_synapse_pairs) -> bool:
        """
        Check if a port by the given name is specified as connecting to the postsynaptic neuron. Only makes sense
        for synapses.
        """
        assert special_type in ["post", "vt"]

        for neuron_synapse_pair in neuron_synapse_pairs:
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

    @classmethod
    def is_continuous_port(cls, port_name: str, parent_node: ASTModel):
        for input_block in parent_node.get_input_blocks():
            for port in input_block.get_input_ports():
                if port.is_continuous() and port_name == port.get_name():
                    return True

        return False

    @classmethod
    def is_post_port(cls, port_name: str, neuron_name: str, synapse_name: str, neuron_synapse_pairs) -> bool:
        return CodeGeneratorUtils.is_special_port("post", port_name, neuron_name, synapse_name, neuron_synapse_pairs=neuron_synapse_pairs)

    @classmethod
    def is_vt_port(cls, port_name: str, neuron_name: str, synapse_name: str, neuron_synapse_pairs) -> bool:
        return CodeGeneratorUtils.is_special_port("vt", port_name, neuron_name, synapse_name, neuron_synapse_pairs=neuron_synapse_pairs)

    @classmethod
    def get_spiking_post_port_names(cls, synapse: ASTModel, neuron_name: str, synapse_name: str, neuron_synapse_pairs):
        post_port_names = []
        for input_block in synapse.get_input_blocks():
            for port in input_block.get_input_ports():
                if CodeGeneratorUtils.is_post_port(port.name, neuron_name, synapse_name, neuron_synapse_pairs) and port.is_spike():
                    post_port_names.append(port.get_name())

        return post_port_names

    @classmethod
    def get_post_port_names(cls, synapse: ASTModel, neuron_name: str, synapse_name: str, neuron_synapse_pairs):
        post_port_names = []
        for input_block in synapse.get_input_blocks():
            for port in input_block.get_input_ports():
                if CodeGeneratorUtils.is_post_port(port.name, neuron_name, synapse_name, neuron_synapse_pairs=neuron_synapse_pairs):
                    post_port_names.append(port.get_name())

        return post_port_names

    @classmethod
    def get_vt_port_names(cls, synapse: ASTModel, neuron_name: str, synapse_name: str, neuron_synapse_pairs):
        post_port_names = []
        for input_block in synapse.get_input_blocks():
            for port in input_block.get_input_ports():
                if CodeGeneratorUtils.is_vt_port(port.name, neuron_name, synapse_name, neuron_synapse_pairs=neuron_synapse_pairs):
                    post_port_names.append(port.get_name())

        return post_port_names
