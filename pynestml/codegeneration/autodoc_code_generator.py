# -*- coding: utf-8 -*-
#
# autodoc_code_generator.py
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

from typing import List, Sequence

import datetime
import os
import textwrap

from jinja2 import Environment, FileSystemLoader

from pynestml.codegeneration.code_generator import CodeGenerator
from pynestml.codegeneration.nest_assignments_helper import NestAssignmentsHelper
from pynestml.codegeneration.printers.latex_expression_printer import LatexExpressionPrinter
from pynestml.codegeneration.printers.latex_reference_converter import LatexReferenceConverter
from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.meta_model.ast_synapse import ASTSynapse
from pynestml.utils.ast_utils import ASTUtils
from pynestml.utils.ode_transformer import OdeTransformer


class AutoDocCodeGenerator(CodeGenerator):

    def __init__(self):
        # setup the template environment
        env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'resources_autodoc')))
        self._template_nestml_models_index = env.get_template('nestml_models_index.jinja2')
        # setup the module class template
        self._template_neuron_nestml_model = env.get_template('nestml_neuron_model.jinja2')
        self._template_synapse_nestml_model = env.get_template('nestml_synapse_model.jinja2')

        converter = LatexReferenceConverter()
        self._printer = LatexExpressionPrinter(converter)

    def generate_code(self, neurons: List[ASTNeuron], synapses: List[ASTSynapse] = None) -> None:
        """
        Generate model documentation and index page for each neuron and synapse that is provided.
        """
        if not os.path.isdir(FrontendConfiguration.get_target_path()):
            os.makedirs(FrontendConfiguration.get_target_path())
        self.generate_index(neurons, synapses)
        self.generate_neurons(neurons)
        self.generate_synapses(synapses)

    def generate_index(self, neurons: Sequence[ASTNeuron], synapses: Sequence[ASTSynapse]):
        """
        Generate model documentation and index page for each neuron and synapse that is provided.
        """
        nestml_models_index = self._template_nestml_models_index.render(self.setup_index_generation_helpers(neurons, synapses))
        with open(str(os.path.join(FrontendConfiguration.get_target_path(), 'index.rst')), 'w+') as f:
            f.write(str(nestml_models_index))

    def generate_neuron_code(self, neuron: ASTNeuron):
        """
        Generate model documentation for neuron model.
        :param neuron: a single neuron object.
        """
        nestml_model_doc = self._template_neuron_nestml_model.render(self.setup_neuron_model_generation_helpers(neuron))
        with open(str(os.path.join(FrontendConfiguration.get_target_path(), neuron.get_name())) + '.rst',
                  'w+') as f:
            f.write(str(nestml_model_doc))

    def generate_synapse_code(self, synapse: ASTSynapse):
        """
        Generate model documentation for synapse model.
        :param synapse: a single synapse object.
        """
        nestml_model_doc = self._template_synapse_nestml_model.render(self.setup_synapse_model_generation_helpers(synapse))
        with open(str(os.path.join(FrontendConfiguration.get_target_path(), synapse.get_name())) + '.rst',
                  'w+') as f:
            f.write(str(nestml_model_doc))

    def setup_neuron_model_generation_helpers(self, neuron: ASTNeuron):
        """
        Returns a namespace for Jinja2 neuron model documentation template.

        :param neuron: a single neuron instance
        :return: a map from name to functionality.
        :rtype: dict
        """
        namespace = dict()

        namespace['now'] = datetime.datetime.utcnow()
        namespace['neuron'] = neuron
        namespace['neuronName'] = str(neuron.get_name())
        namespace['printer'] = self._printer
        namespace['assignments'] = NestAssignmentsHelper()
        namespace['utils'] = ASTUtils()
        namespace['odeTransformer'] = OdeTransformer()

        import textwrap
        pre_comments_bak = neuron.pre_comments
        neuron.pre_comments = []
        namespace['model_source_code'] = textwrap.indent(neuron.__str__(), "   ")
        neuron.pre_comments = pre_comments_bak

        return namespace

    def setup_synapse_model_generation_helpers(self, synapse: ASTSynapse):
        """
        Returns a namespace for Jinja2 synapse model documentation template.

        :param neuron: a single neuron instance
        :return: a map from name to functionality.
        :rtype: dict
        """
        namespace = dict()

        namespace['now'] = datetime.datetime.utcnow()
        namespace['synapse'] = synapse
        namespace['synapseName'] = str(synapse.get_name())
        namespace['printer'] = self._printer
        namespace['assignments'] = NestAssignmentsHelper()
        namespace['utils'] = ASTUtils()
        namespace['odeTransformer'] = OdeTransformer()

        pre_comments_bak = synapse.pre_comments
        synapse.pre_comments = []
        namespace['model_source_code'] = textwrap.indent(synapse.__str__(), "   ")
        synapse.pre_comments = pre_comments_bak

        return namespace

    def setup_index_generation_helpers(self, neurons: Sequence[ASTNeuron], synapses: Sequence[ASTSynapse]):
        """
        Returns a namespace for Jinja2 neuron model index page template.

        :param neurons: a list of neuron instances
        :return: a map from name to functionality.
        :rtype: dict
        """

        namespace = dict()

        namespace['now'] = datetime.datetime.utcnow()
        namespace['neurons'] = neurons
        namespace['synapses'] = synapses
        namespace['neuronNames'] = [str(neuron.get_name()) for neuron in neurons]
        namespace['synapseNames'] = [str(neuron.get_name()) for neuron in neurons]
        namespace['printer'] = self._printer
        namespace['assignments'] = NestAssignmentsHelper()
        namespace['utils'] = ASTUtils()
        namespace['odeTransformer'] = OdeTransformer()

        return namespace
