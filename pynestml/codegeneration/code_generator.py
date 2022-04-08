# -*- coding: utf-8 -*-
#
# code_generator.py
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
from abc import abstractmethod

from typing import Any, Dict, Mapping, List, Optional, Sequence, Union

import os

from jinja2 import Template

from pynestml.exceptions.invalid_target_exception import InvalidTargetException
from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.meta_model.ast_synapse import ASTSynapse
from pynestml.utils.logger import Logger
from pynestml.utils.logger import LoggingLevel
from pynestml.utils.messages import Messages
from pynestml.utils.with_options import WithOptions


class CodeGenerator(WithOptions):

    _default_options: Mapping[str, Any] = {}

    def __init__(self, target, options: Optional[Mapping[str, Any]] = None):
        super(CodeGenerator, self).__init__(options)
        from pynestml.frontend.pynestml_frontend import get_known_targets

        if not target.upper() in get_known_targets():
            code, msg = Messages.get_unknown_target(target)
            Logger.log_message(message=msg, code=code, log_level=LoggingLevel.ERROR)
            self._target = ""
            raise InvalidTargetException()

        self._target = target

    @abstractmethod
    def generate_code(self, neurons: Sequence[ASTNeuron], synapses: Sequence[ASTSynapse]) -> None:
        """the base class CodeGenerator does not generate any code"""
        pass

    def generate_neurons(self, neurons: Sequence[ASTNeuron]) -> None:
        """
        Generate code for the given neurons.

        :param neurons: a list of neurons.
        """
        from pynestml.frontend.frontend_configuration import FrontendConfiguration

        for neuron in neurons:
            self.generate_neuron_code(neuron)
            if not Logger.has_errors(neuron):
                code, message = Messages.get_code_generated(neuron.get_name(), FrontendConfiguration.get_target_path())
                Logger.log_message(neuron, code, message, neuron.get_source_position(), LoggingLevel.INFO)

    def generate_synapses(self, synapses: Sequence[ASTSynapse]) -> None:
        """
        Generates code for a list of synapses.
        :param synapses: a list of synapses.
        """
        from pynestml.frontend.frontend_configuration import FrontendConfiguration

        for synapse in synapses:
            if Logger.logging_level == LoggingLevel.INFO:
                print("Generating code for the synapse {}.".format(synapse.get_name()))
            self.generate_synapse_code(synapse)
            code, message = Messages.get_code_generated(synapse.get_name(), FrontendConfiguration.get_target_path())
            Logger.log_message(synapse, code, message, synapse.get_source_position(), LoggingLevel.INFO)

    def generate_model_code(self,
                            model_name: str,
                            model_templates: List[Template],
                            template_namespace: Dict[str, Any],
                            model_name_escape_string: str="@MODEL_NAME@") -> None:
        """
        For a handed over model, this method generates the corresponding header and implementation file.
        :param model: a single neuron or synapse
        """
        if not os.path.isdir(FrontendConfiguration.get_target_path()):
            os.makedirs(FrontendConfiguration.get_target_path())

        for _model_templ in model_templates:
            if not len(_model_templ.filename.split(".")) == 3:
                raise Exception("Template file name should be of the form: \"PREFIX@NEURON_NAME@SUFFIX.FILE_EXTENSION.jinja2\"")
            templ_file_name = os.path.basename(_model_templ.filename)
            templ_file_name = templ_file_name.split(".")[0]   # for example, "cm_main_@NEURON_NAME@"
            templ_file_name = templ_file_name.replace(model_name_escape_string, model_name)
            file_extension = _model_templ.filename.split(".")[-2]   # for example, "cpp"
            rendered_templ_file_name = os.path.join(FrontendConfiguration.get_target_path(),
                                                    templ_file_name + "." + file_extension)
            _file = _model_templ.render(template_namespace)
            Logger.log_message(message="Rendering template " + rendered_templ_file_name,
                               log_level=LoggingLevel.INFO)
            with open(rendered_templ_file_name, "w+") as f:
                f.write(str(_file))

    def generate_neuron_code(self, neuron: ASTNeuron) -> None:
        self.generate_model_code(neuron.get_name(),
                                 model_templates=self._model_templates["neuron"],
                                 template_namespace=self._get_neuron_model_namespace(neuron),
                                 model_name_escape_string="@NEURON_NAME@")

    def generate_synapse_code(self, synapse: ASTNeuron) -> None:
        self.generate_model_code(synapse.get_name(),
                                 model_templates=self._model_templates["synapse"],
                                 template_namespace=self._get_synapse_model_namespace(synapse),
                                 model_name_escape_string="@SYNAPSE_NAME@")

    def generate_module_code(self, neurons: Sequence[ASTNeuron], synapses: Sequence[ASTSynapse]) -> None:
        self.generate_model_code(FrontendConfiguration.get_module_name(),
                                 model_templates=self._module_templates,
                                 template_namespace=self._get_module_namespace(neurons, synapses),
                                 model_name_escape_string="@MODULE_NAME@")
        code, message = Messages.get_module_generated(FrontendConfiguration.get_target_path())
        Logger.log_message(None, code, message, None, LoggingLevel.INFO)
