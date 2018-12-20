#
# nest_codegeneration.py
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
import re

from jinja2 import Environment, FileSystemLoader
from odetoolbox import analysis

from pynestml.codegeneration.codegenerator import CodeGenerator
from pynestml.codegeneration.expressions_pretty_printer import ExpressionsPrettyPrinter
from pynestml.codegeneration.gsl_names_converter import GSLNamesConverter
from pynestml.codegeneration.gsl_reference_converter import GSLReferenceConverter
from pynestml.codegeneration.legacy_expression_printer import LegacyExpressionPrinter
from pynestml.codegeneration.nest_assignments_helper import NestAssignmentsHelper
from pynestml.codegeneration.nest_declarations_helper import NestDeclarationsHelper
from pynestml.codegeneration.nest_names_converter import NestNamesConverter
from pynestml.codegeneration.nest_printer import NestPrinter
from pynestml.codegeneration.nest_reference_converter import NESTReferenceConverter
from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.meta_model.ast_equations_block import ASTEquationsBlock
from pynestml.solver.solution_transformers import integrate_exact_solution, functional_shapes_to_odes, \
    integrate_delta_solution
from pynestml.solver.transformer_base import add_assignment_to_update_block
from pynestml.symbols.symbol import SymbolKind
from pynestml.utils.ast_utils import ASTUtils
from pynestml.utils.logger import Logger
from pynestml.utils.logger import LoggingLevel
from pynestml.utils.messages import Messages
from pynestml.utils.model_parser import ModelParser
from pynestml.utils.ode_transformer import OdeTransformer
from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor


class AutoDocCodeGenerator(CodeGenerator):

    def __init__(self):
        # setup the template environment
        env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'resources_autodoc')))
        self._template_nestml_models_index = env.get_template('nestml_models_index.jinja2')
        # setup the module class template
        self._template_nestml_model = env.get_template('nestml_model.jinja2')

        self._printer = ExpressionsPrettyPrinter()

    def generate_code(self, neurons):
        self.generate_index(neurons)

    def generate_index(self, neurons):
        # type: (ASTNeuron) -> None
        """
        """
        nestml_models_index = self._template_nestml_models_index.render(self.setup_generation_helpers(neurons))
        with open(str(os.path.join(FrontendConfiguration.get_target_path(), 'index.html')), 'w+') as f:
            f.write(str(nestml_models_index))


    def setup_generation_helpers(self, neurons):
        """
        Returns a standard namespace with often required functionality.
        :param neuron: a single neuron instance
        :type neuron: ASTNeuron
        :return: a map from name to functionality.
        :rtype: dict
        """
        gsl_converter = GSLReferenceConverter()
        gsl_printer = LegacyExpressionPrinter(gsl_converter)
        # helper classes and objects
        converter = NESTReferenceConverter(False)
        legacy_pretty_printer = LegacyExpressionPrinter(converter)

        namespace = dict()

        namespace['now'] = datetime.datetime.utcnow()
        namespace['neurons'] = neurons
        namespace['neuronNames'] = [str(neuron.get_name()) for neuron in neurons]
        namespace['printer'] = NestPrinter(legacy_pretty_printer)
        namespace['assignments'] = NestAssignmentsHelper()
        namespace['names'] = NestNamesConverter()
        namespace['declarations'] = NestDeclarationsHelper()
        namespace['utils'] = ASTUtils()
        namespace['idemPrinter'] = LegacyExpressionPrinter()
        namespace['odeTransformer'] = OdeTransformer()

        return namespace
