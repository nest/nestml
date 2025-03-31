# -*- coding: utf-8 -*-
#
# pretty_render_code_generator.py
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

from typing import Sequence

import datetime
import os

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, load_lexer_from_file

from pynestml.codegeneration.code_generator import CodeGenerator
from pynestml.codegeneration.code_generator_utils import CodeGeneratorUtils
from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.meta_model.ast_model import ASTModel


class PrettyRenderCodeGenerator(CodeGenerator):
    r"""
    Code generator for a "pretty render" of NESTML model code as a stylised HTML page.
    """

    _default_options = {
        "synapse_models": [],
        "templates": {
            "path": "resources_pretty_render",
            "model_templates": {
                "neuron": ["@MODEL_NAME@.html.jinja2"],
                "synapse": ["@MODEL_NAME@.html.jinja2"]
            },
            "module_templates": []
        },
    }

    def generate_code(self, models: Sequence[ASTModel]) -> None:
        neurons, synapses = CodeGeneratorUtils.get_model_types_from_names(models, synapse_models=self.get_option("synapse_models"))

        # Load the custom lexer
        lexer_fname = os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'extras', 'syntax-highlighting', 'pygments', 'pygments_nestml.py'))
        self.lexer = load_lexer_from_file(lexer_fname, 'NESTMLLexer')

        self.setup_template_env()

        for neuron in neurons:
            self.generate_model_code(neuron.get_name(),
                                     model_templates=self._model_templates["neuron"],
                                     template_namespace=self._get_neuron_model_namespace(neuron))

        for synapse in synapses:
            self.generate_model_code(synapse.get_name(),
                                     model_templates=self._model_templates["synapse"],
                                     template_namespace=self._get_synapse_model_namespace(synapse))

    def _get_model_namespace(self, model: ASTModel):
        # Read the source code file
        with open(model.file_path, 'r') as f:
            code = f.read()

        # Create the HTML formatter
        formatter = HtmlFormatter(full=True, style='colorful')

        # Highlight the code
        highlighted_code_html = highlight(code, self.lexer, formatter)

        namespace = {"highlighted_code_html": highlighted_code_html,
                     "now": datetime.datetime.utcnow()}

        return namespace

    def _get_neuron_model_namespace(self, neuron: ASTModel):
        namespace = self._get_model_namespace(neuron)
        namespace["model_type"] = "neuron"
        namespace["model_title"] = "Integrate-and-fire NESTML neuron model"

        return namespace

    def _get_synapse_model_namespace(self, neuron: ASTModel):
        namespace = self._get_model_namespace(neuron)
        namespace["model_type"] = "neuron"
        namespace["model_title"] = "STDP synapse NESTML model"

        return namespace
