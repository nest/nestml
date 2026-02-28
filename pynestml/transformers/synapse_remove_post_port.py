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

from typing import Iterable, Optional, Mapping, Any, Union

from pynestml.meta_model.ast_model import ASTModel

try:
    # Available in the standard library starting with Python 3.12
    from typing import override
except ImportError:
    # Fallback for Python 3.8 - 3.11
    from typing_extensions import override

from pynestml.codegeneration.code_generator_utils import CodeGeneratorUtils
from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.meta_model.ast_node import ASTNode
from pynestml.transformers.transformer import Transformer
from pynestml.visitors.ast_parent_visitor import ASTParentVisitor
from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor
from pynestml.utils.ast_utils import ASTUtils
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.string_utils import removesuffix


class SynapseRemovePostPortTransformer(Transformer):
    _default_options = {
        "neuron_synapse_pairs": []
    }

    def __init__(self, options: Optional[Mapping[str, Any]] = None):
        super(Transformer, self).__init__(options)

    def transform_neuron_synapse_pair_(self, neuron, synapse, metadata):

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
        new_neuron._syn_to_neuron_state_vars = []

        #
        #    rename synapse
        #

        new_synapse_name = synapse.get_name() + name_separator_str + neuron.get_name()
        new_synapse.set_name(new_synapse_name)
        metadata[new_synapse.name]["paired_neuron"] = new_neuron
        metadata[new_neuron.name]["paired_synapse"] = new_synapse

        base_neuron_name = removesuffix(neuron.get_name(), FrontendConfiguration.suffix)
        base_synapse_name = removesuffix(synapse.get_name(), FrontendConfiguration.suffix)

        new_synapse.post_port_names = CodeGeneratorUtils.get_post_port_names(synapse, base_neuron_name, base_synapse_name, neuron_synapse_pairs=self._options["neuron_synapse_pairs"])
        new_synapse.spiking_post_port_names = CodeGeneratorUtils.get_spiking_post_port_names(synapse, base_neuron_name, base_synapse_name, neuron_synapse_pairs=self._options["neuron_synapse_pairs"])
        new_synapse.vt_port_names = CodeGeneratorUtils.get_vt_port_names(synapse, base_neuron_name, base_synapse_name, neuron_synapse_pairs=self._options["neuron_synapse_pairs"])

        #
        #    add modified versions of neuron and synapse to list
        #

        new_neuron.parent_ = None    # set root element
        new_neuron.accept(ASTParentVisitor())
        new_synapse.parent_ = None    # set root element
        new_synapse.accept(ASTParentVisitor())

        new_neuron.accept(ASTSymbolTableVisitor())
        new_synapse.accept(ASTSymbolTableVisitor())

        ASTUtils.update_blocktype_for_common_parameters(new_synapse)

        Logger.log_message(None, -1, "Successfully constructed neuron-synapse pair "
                           + new_neuron.name + ", " + new_synapse.name, None, LoggingLevel.INFO)

        return new_neuron, new_synapse

    @override
    def transform(self,
                  models: Iterable[ASTModel],
                  metadata: Optional[Mapping[str, Mapping[str, Any]]] = None) -> Union[ASTModel, Iterable[ASTModel]]:
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
