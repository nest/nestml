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

from typing import Any, Dict, Mapping, List, Optional, Sequence, Union

import glob
import os

from abc import abstractmethod

from jinja2 import Environment, FileSystemLoader, Template, TemplateRuntimeError

from pynestml.exceptions.invalid_path_exception import InvalidPathException
from pynestml.exceptions.invalid_target_exception import InvalidTargetException
from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.meta_model.ast_synapse import ASTSynapse
from pynestml.utils.ast_utils import ASTUtils
from pynestml.utils.logger import Logger
from pynestml.utils.logger import LoggingLevel
from pynestml.utils.messages import Messages
from pynestml.utils.with_options import WithOptions


class CodeGenerator(WithOptions):
    _default_options: Mapping[str, Any] = {}

    def __init__(self, target, options: Optional[Mapping[str, Any]] = None):
        from pynestml.frontend.pynestml_frontend import get_known_targets

        if not target.upper() in get_known_targets():
            code, msg = Messages.get_unknown_target(target)
            Logger.log_message(message=msg, code=code, log_level=LoggingLevel.ERROR)
            self._target = ""
            raise InvalidTargetException()

        self._target = target
        super(CodeGenerator, self).__init__(options)

        self._init_templates_list()

    def raise_helper(self, msg):
        raise TemplateRuntimeError(msg)

    def setup_template_env(self):
        """
        Setup the Jinja2 template environment
        """
        self._init_templates_list()

        # Get templates path
        templates_root_dir = self.get_option("templates")["path"]
        if not os.path.isabs(templates_root_dir):
            # Prefix the default templates location
            templates_root_dir = os.path.join(os.path.dirname(__file__), templates_root_dir)
            code, message = Messages.get_template_root_path_created(templates_root_dir)
            Logger.log_message(None, code, message, None, LoggingLevel.INFO)
        if not os.path.isdir(templates_root_dir):
            raise InvalidPathException("Templates path (" + templates_root_dir + ")  is not a directory")

        # Setup neuron template environment
        if "neuron" in self.get_option("templates")["model_templates"]:
            neuron_model_templates = self.get_option("templates")["model_templates"]["neuron"]
            if not neuron_model_templates:
                raise Exception("A list of neuron model template files/directories is missing.")
            self._model_templates["neuron"].extend(
                self._setup_template_env(neuron_model_templates, templates_root_dir))

        # Setup synapse template environment
        if "synapse" in self.get_option("templates")["model_templates"]:
            synapse_model_templates = self.get_option("templates")["model_templates"]["synapse"]
            if synapse_model_templates:
                self._model_templates["synapse"].extend(
                    self._setup_template_env(synapse_model_templates, templates_root_dir))

        # Setup modules template environment
        if "module_templates" in self.get_option("templates"):
            module_templates = self.get_option("templates")["module_templates"]
            self._module_templates.extend(self._setup_template_env(module_templates, templates_root_dir))

    def _init_templates_list(self):
        self._model_templates: Mapping[str, List[Template]] = {}
        self._model_templates["neuron"]: List[Template] = []
        self._model_templates["synapse"]: List[Template] = []
        self._module_templates: List[Template] = []

    def _setup_template_env(self, template_files: List[str], templates_root_dir: str) -> List[Template]:
        """
        A helper function to set up the jinja2 template environment
        :param template_files: A list of template file names or a directory (relative to ``templates_root_dir``)
        containing the templates
        :param templates_root_dir: path of the root directory containing all the jinja2 templates
        :return: A list of jinja2 template objects
        """
        _template_files = self._get_abs_template_paths(template_files, templates_root_dir)
        _template_dirs = set([os.path.dirname(_file) for _file in _template_files])

        # Environment for neuron templates
        env = Environment(loader=FileSystemLoader(_template_dirs))
        env.globals["raise"] = self.raise_helper
        env.globals["is_delta_kernel"] = ASTUtils.is_delta_kernel

        # Load all the templates
        _templates = list()
        for _templ_file in _template_files:
            _templates.append(env.get_template(os.path.basename(_templ_file)))

        return _templates

    def _get_abs_template_paths(self, template_files: List[str], templates_root_dir: str) -> List[str]:
        """
        Resolve the directory paths and get the absolute paths of the jinja templates.
        :param template_files: A list of template file names or a directory (relative to ``templates_root_dir``)
        containing the templates
        :param templates_root_dir: path of the root directory containing all the jinja2 templates
        :return: A list of absolute paths of the ``template_files``
        """
        _abs_template_paths = list()
        for _path in template_files:
            # Convert from relative to absolute path
            _path = os.path.join(templates_root_dir, _path)
            if os.path.isdir(_path):
                for file in glob.glob(os.path.join(_path, "*.jinja2")):
                    _abs_template_paths.append(os.path.join(_path, file))
            else:
                _abs_template_paths.append(_path)

        return _abs_template_paths

    @abstractmethod
    def generate_code(self, models: Sequence[Union[ASTNeuron, ASTSynapse]]) -> None:
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
                            model_name_escape_string: str = "@MODEL_NAME@") -> None:
        """
        For a handed over model, this method generates the corresponding header and implementation file.
        :param model_name: name of the neuron or synapse model
        :param model_templates: list of neuron or synapse model templates
        :param template_namespace: namespace for the template
        :param model_name_escape_string: escape string where the model name is replaced
        """
        if not os.path.isdir(FrontendConfiguration.get_target_path()):
            os.makedirs(FrontendConfiguration.get_target_path())

        for _model_templ in model_templates:
            templ_file_name = os.path.basename(_model_templ.filename)
            if len(templ_file_name.split(".")) < 2:
                msg = f"Template file name '{templ_file_name}' should be of the form 'PREFIX@NEURON_NAME@SUFFIX.[FILE_EXTENSION.]jinja2' "
                raise Exception(msg)

            if len(templ_file_name.split(".")) < 3:
                file_extension = ""  # no extension, for instance if the template file name is "Makefile.jinja2"
            else:
                file_extension = templ_file_name.split(".")[-2]  # for example, "cpp"

            templ_file_base_name = templ_file_name.split(".")[0]  # for example, "cm_main_@NEURON_NAME@" or "Makefile"
            templ_file_base_name = templ_file_base_name.replace(model_name_escape_string, model_name)

            if file_extension:
                templ_file_base_name = templ_file_base_name + "." + file_extension
            rendered_templ_file_name = os.path.join(FrontendConfiguration.get_target_path(),
                                                    templ_file_base_name)
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
