# -*- coding: utf-8 -*-
#
# nest_code_generator.py
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
import os
from typing import Sequence, Union, Optional, Mapping, Any, Dict

from pynestml.codegeneration.code_generator import CodeGenerator
from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.meta_model.ast_synapse import ASTSynapse


class NESTDesktopCodeGenerator(CodeGenerator):
    """
    Code generator for NEST Desktop
    """
    _default_options = {
        "templates": {
            "path": "",
            "model_templates": {
                "neuron": ["@NEURON_NAME@.json.jinja2"],
                # "synapse": ["@SYNAPSE_NAME@.json.jinja2"]
            }
        }
    }

    def __init__(self, options: Optional[Mapping[str, Any]] = None):
        self._target = "NEST_DESKTOP"
        super().__init__(self._target, options)
        self.setup_template_env()

    def generate_code(self, models: Sequence[Union[ASTNeuron, ASTSynapse]]) -> None:
        """
        Generate the .json files for the given neuron and synapse models
        :param models:
        :return:
        """
        if not os.path.isdir(FrontendConfiguration.get_target_path()):
            os.makedirs(FrontendConfiguration.get_target_path())
        neurons = [model for model in models if isinstance(model, ASTNeuron)]
        synapses = [model for model in models if isinstance(model, ASTSynapse)]
        self.generate_neurons(neurons)
        self.generate_synapses(synapses)

    def _get_neuron_model_namespace(self, neuron: ASTNeuron) -> Dict:
        """

        :param neuron:
        :return:
        """
        namespace = dict()
        namespace["neuronName"] = neuron.get_name()
        namespace["neuron"] = neuron

        return namespace
