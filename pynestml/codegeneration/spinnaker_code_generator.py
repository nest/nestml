# -*- coding: utf-8 -*-
#
# spinnaker_code_generator.py
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

from typing import Sequence, Union, Optional, Mapping, Any, Dict

import os

from pynestml.codegeneration.code_generator import CodeGenerator
from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.meta_model.ast_synapse import ASTSynapse


class SpiNNakerCodeGenerator(CodeGenerator):
    """
    Code generator for SpiNNaker
    """
    _default_options = {
        "templates": {
            "path": "",
            "model_templates": {
                "neuron": ["@NEURON_NAME@.cpp.jinja2"],
            }
        }
    }

    def __init__(self, options: Optional[Mapping[str, Any]] = None):
        self._target = "SPINNAKER"
        super().__init__(self._target, options)
        self.setup_template_env()

    def generate_code(self, models: Sequence[Union[ASTNeuron, ASTSynapse]]) -> None:
        """
        Generate the code for the given neuron and synapse models
        :param models: list of models
        """
        if not os.path.isdir(FrontendConfiguration.get_target_path()):
            os.makedirs(FrontendConfiguration.get_target_path())
        neurons = [model for model in models if isinstance(model, ASTNeuron)]
        synapses = [model for model in models if isinstance(model, ASTSynapse)]
        self.generate_neurons(neurons)
        self.generate_synapses(synapses)

    def _get_neuron_model_namespace(self, neuron: ASTNeuron) -> Dict:
        """
        Returns a standard namespace with often required functionality.
        :param neuron: a single neuron instance
        :return: a map from name to functionality.
        """
        from pynestml.codegeneration.nest_tools import NESTTools
        namespace = dict()
        namespace["neuronName"] = neuron.get_name()
        namespace["neuron"] = neuron
        namespace["parameters"] = NESTTools.get_neuron_parameters(neuron.get_name())
        return namespace

