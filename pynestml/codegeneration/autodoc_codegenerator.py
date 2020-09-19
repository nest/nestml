# -*- coding: utf-8 -*-
#
# autodoc_codegenerator.py
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

import datetime
import os
from typing import List

from jinja2 import Environment, FileSystemLoader

from pynestml.codegeneration.codegenerator import CodeGenerator
from pynestml.codegeneration.latex_expression_printer import LatexExpressionPrinter
from pynestml.codegeneration.nest_assignments_helper import NestAssignmentsHelper
from pynestml.codegeneration.nest_declarations_helper import NestDeclarationsHelper
from pynestml.codegeneration.nest_names_converter import NestNamesConverter
from pynestml.codegeneration.nest_printer import NestPrinter
from pynestml.codegeneration.latex_reference_converter import LatexReferenceConverter
from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.utils.ast_utils import ASTUtils
from pynestml.utils.ode_transformer import OdeTransformer


class AutoDocCodeGenerator(CodeGenerator):

    def __init__(self):
        # setup the template environment
        env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'resources_autodoc')))
        self._template_nestml_models_index = env.get_template('nestml_models_index.jinja2')
        # setup the module class template
        self._template_nestml_model = env.get_template('nestml_model.jinja2')

        self._printer = LatexExpressionPrinter()

    def generate_code(self, neurons: List[ASTNeuron]):
        """
        Generate model documentation and index page for each neuron that is provided.
        """
        self.generate_index(neurons)
        self.generate_neurons(neurons)

    def generate_index(self, neurons: List[ASTNeuron]):
        """
        Generate index (list) of all neuron models with links to their generated documentation.
        """
        nestml_models_index = self._template_nestml_models_index.render(self.setup_index_generation_helpers(neurons))
        with open(str(os.path.join(FrontendConfiguration.get_target_path(), 'index.rst')), 'w+') as f:
            f.write(str(nestml_models_index))

    def generate_neuron_code(self, neuron: ASTNeuron):
        """
        Generate model documentation for neuron model.
        :param neuron: a single neuron object.
        :type neuron: ASTNeuron
        """
        if not os.path.isdir(FrontendConfiguration.get_target_path()):
            os.makedirs(FrontendConfiguration.get_target_path())
        nestml_model_doc = self._template_nestml_model.render(self.setup_model_generation_helpers(neuron))
        with open(str(os.path.join(FrontendConfiguration.get_target_path(), neuron.get_name())) + '.rst', 'w+') as f:
            f.write(str(nestml_model_doc))

    def setup_model_generation_helpers(self, neuron: ASTNeuron):
        """
        Returns a namespace for Jinja2 neuron model documentation template.

        :param neuron: a single neuron instance
        :type neuron: ASTNeuron
        :return: a map from name to functionality.
        :rtype: dict
        """
        converter = LatexReferenceConverter()
        latex_expression_printer = LatexExpressionPrinter(converter)

        namespace = dict()

        namespace['now'] = datetime.datetime.utcnow()
        namespace['neuron'] = neuron
        namespace['neuronName'] = str(neuron.get_name())
        namespace['printer'] = NestPrinter(latex_expression_printer)
        namespace['assignments'] = NestAssignmentsHelper()
        namespace['names'] = NestNamesConverter()
        namespace['declarations'] = NestDeclarationsHelper()
        namespace['utils'] = ASTUtils()
        namespace['odeTransformer'] = OdeTransformer()

        import textwrap
        pre_comments_bak = neuron.pre_comments
        neuron.pre_comments = []
        namespace['neuron_source_code'] = textwrap.indent(neuron.__str__(), "   ")
        neuron.pre_comments = pre_comments_bak

        return namespace

    def setup_index_generation_helpers(self, neurons: List[ASTNeuron]):
        """
        Returns a namespace for Jinja2 neuron model index page template.

        :param neurons: a list of neuron instances
        :type neurons: List[ASTNeuron]
        :return: a map from name to functionality.
        :rtype: dict
        """
        converter = LatexReferenceConverter()
        latex_expression_printer = LatexExpressionPrinter(converter)

        namespace = dict()

        namespace['now'] = datetime.datetime.utcnow()
        namespace['neurons'] = neurons
        namespace['neuronNames'] = [str(neuron.get_name()) for neuron in neurons]
        namespace['printer'] = NestPrinter(latex_expression_printer)
        namespace['assignments'] = NestAssignmentsHelper()
        namespace['names'] = NestNamesConverter()
        namespace['declarations'] = NestDeclarationsHelper()
        namespace['utils'] = ASTUtils()
        namespace['odeTransformer'] = OdeTransformer()

        return namespace
