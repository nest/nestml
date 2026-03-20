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

from typing import Any, Dict, Iterable, Mapping, Optional

try:
    # Available in the standard library starting with Python 3.12
    from typing import override
except ImportError:
    # Fallback for Python 3.8 - 3.11
    from typing_extensions import override

import pynestml
from pynestml.codegeneration.code_generator import CodeGenerator
from pynestml.codegeneration.code_generator_utils import CodeGeneratorUtils
from pynestml.codegeneration.python_standalone_target_tools import PythonStandaloneTargetTools
from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.meta_model.ast_model import ASTModel


class NESTDesktopCodeGenerator(CodeGenerator):
    """
    Code generator for NEST Desktop
    """
    _default_options = {
        "synapse_models": [],
        "templates": {
            "path": "resources_nest_desktop",
            "model_templates": {
                "neuron": ["@NEURON_NAME@.json.jinja2"],
            }
        }
    }

    def __init__(self, options: Optional[Mapping[str, Any]] = None):
        super().__init__(options)
        self.setup_template_env()

    @override
    def generate_code(self,
                      models: Iterable[ASTModel],
                      metadata: Mapping[str, Mapping[str, Any]]) -> None:
        """
        Generate the .json files for the given neuron and synapse models
        :param models: list of neuron models
        """
        neurons, synapses = CodeGeneratorUtils.get_model_types_from_names(models,
                                                                          synapse_models=self.get_option("synapse_models"))
        self.generate_neurons(neurons, metadata)
        self.generate_synapses(synapses, metadata)

    def _get_neuron_model_namespace(self,
                                    neuron: ASTModel,
                                    metadata: Mapping[str, Mapping[str, Any]]) -> Dict:
        """
        Returns a standard namespace with often required functionality.
        :param neuron: a single neuron instance
        :return: a map from name to functionality.
        """
        namespace = dict()
        namespace["nestml_version"] = pynestml.__version__
        namespace["neuronName"] = neuron.get_name()
        namespace["neuron"] = neuron
        namespace["parameters"], namespace["internals"], namespace["state"] = PythonStandaloneTargetTools.get_neuron_numerical_initial_values(neuron.file_path)

        return namespace
