# -*- coding: utf-8 -*-
#
# nest_desktop_code_generator.py
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
from typing import Sequence, Optional, Mapping, Any, Dict

from pynestml.codegeneration.code_generator import CodeGenerator
from pynestml.codegeneration.code_generator_utils import CodeGeneratorUtils
from pynestml.meta_model.ast_model import ASTModel


class NESTDesktopCodeGenerator(CodeGenerator):
    """
    Code generator for NEST Desktop
    """
    _default_options = {
        "neuron_models": [],
        "synapse_models": [],
        "templates": {
            "path": "resources_nest_desktop",
            "model_templates": {
                "neuron": ["@NEURON_NAME@.json.jinja2"],
            }
        }
    }

    def __init__(self, options: Optional[Mapping[str, Any]] = None):
        self._target = "NEST_DESKTOP"
        super().__init__(self._target, options)
        self.setup_template_env()

    def generate_code(self, models: Sequence[ASTModel]) -> None:
        """
        Generate the .json files for the given neuron and synapse models
        :param models: list of neuron models
        """
        neurons, synapses = CodeGeneratorUtils.get_model_types_from_names(models, neuron_models=self.get_option("neuron_models"),
                                                                          synapse_models=self.get_option("synapse_models"))
        self.generate_neurons(neurons)
        self.generate_synapses(synapses)

    def _get_neuron_model_namespace(self, neuron: ASTModel) -> Dict:
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
