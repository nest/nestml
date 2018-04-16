#
# NestGenerator.py
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
from copy import deepcopy

from jinja2 import Environment, FileSystemLoader

from pynestml.meta_model.ASTNeuron import ASTNeuron
from pynestml.codegeneration.GSLNamesConverter import GSLNamesConverter
from pynestml.codegeneration.GSLReferenceConverter import GSLReferenceConverter
from pynestml.codegeneration.LegacyExpressionPrinter import LegacyExpressionPrinter
from pynestml.codegeneration.NestAssignmentsHelper import NestAssignmentsHelper
from pynestml.codegeneration.NestDeclarationsHelper import NestDeclarationsHelper
from pynestml.codegeneration.NestNamesConverter import NestNamesConverter
from pynestml.codegeneration.NestPrinter import NestPrinter
from pynestml.codegeneration.NestReferenceConverter import NESTReferenceConverter
from pynestml.frontend.FrontendConfiguration import FrontendConfiguration
from pynestml.solver.EquationsBlockProcessor import EquationsBlockProcessor
from pynestml.utils.ASTUtils import ASTUtils
from pynestml.utils.Logger import LoggingLevel, Logger
from pynestml.utils.Messages import Messages
from pynestml.utils.OdeTransformer import OdeTransformer
from pynestml.visitors.ASTSymbolTableVisitor import ASTSymbolTableVisitor


class NestCodeGenerator(object):
    """
    This class represents a generator which can be used to print an internal meta_model to a model in
    nest format.
    """
    __templateCMakeLists = None
    __templateModuleClass = None
    __templateModuleHeader = None
    __templateSLIInit = None
    __templateNeuronHeader = None
    __templateNeuronImplementation = None

    def __init__(self):
        """
        Standard constructor to init the generator.
        """
        # setup the environment
        env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templatesNEST')))
        # setup the cmake template
        self.__templateCMakeLists = env.get_template('CMakeLists.jinja2')
        # setup the module class template
        self.__templateModuleClass = env.get_template('ModuleClass.jinja2')
        # setup the module header
        self.__templateModuleHeader = env.get_template('ModuleHeader.jinja2')
        # setup the SLI_Init file
        self.__templateSLIInit = env.get_template('SLI_Init.jinja2')
        # setup the neuron header template
        self.__templateNeuronHeader = env.get_template('NeuronHeader.jinja2')
        # setup the neuron implementation template
        self.__templateNeuronImplementation = env.get_template('NeuronClass.jinja2')
        return

    def generateNESTModuleCode(self, _neurons=None):
        """
        Generates code that is necessary to integrate neuron models into the NEST infrastructure.
        :param _neurons: a list of neurons
        :type _neurons: list(ASTNeuron)
        """
        namespace = {'neurons': _neurons, 'moduleName': FrontendConfiguration.get_module_name()}
        with open(str(os.path.join(FrontendConfiguration.get_target_path(),
                                   FrontendConfiguration.get_module_name())) + '.h', 'w+') as f:
            f.write(str(self.__templateModuleHeader.render(namespace)))
        with open(str(os.path.join(FrontendConfiguration.get_target_path(),
                                   FrontendConfiguration.get_module_name())) + '.cpp', 'w+') as f:
            f.write(str(self.__templateModuleClass.render(namespace)))
        with open(str(os.path.join(FrontendConfiguration.get_target_path(),
                                   'CMakeLists')) + '.txt', 'w+') as f:
            f.write(str(self.__templateCMakeLists.render(namespace)))
        if not os.path.isdir(os.path.realpath(os.path.join(FrontendConfiguration.get_target_path(), 'sli'))):
            os.makedirs(os.path.realpath(os.path.join(FrontendConfiguration.get_target_path(), 'sli')))
        with open(str(os.path.join(FrontendConfiguration.get_target_path(), 'sli',
                                   FrontendConfiguration.get_module_name() + "-init")) + '.sli', 'w+') as f:
            f.write(str(self.__templateSLIInit.render(namespace)))
        code, message = Messages.get_module_generated(FrontendConfiguration.get_target_path())
        Logger.log_message(neuron=None, code=code, message=message, log_level=LoggingLevel.INFO)
        return

    def analyseAndGenerateNeuron(self, _neuron=None):
        """
        Analysis a single neuron, solves it and generates the corresponding code.
        :param _neuron: a single neuron.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CodeGenerator.NEST) No or wrong type of module neuron provided (%s)!' % type(_neuron)
        code, message = Messages.get_start_processing_neuron(_neuron.get_name())
        Logger.log_message(neuron=_neuron, error_position=_neuron.get_source_position(), code=code, message=message,
                           log_level=LoggingLevel.INFO)
        working_version = deepcopy(_neuron)
        # solve all equations
        working_version = self.solveOdesAndShapes(working_version)
        # update the symbol table
        working_version.accept(ASTSymbolTableVisitor())
        self.generateNestCode(working_version)
        code, message = Messages.get_code_generated(_neuron.get_name(), FrontendConfiguration.get_target_path())
        Logger.log_message(neuron=_neuron, error_position=_neuron.get_source_position(), code=code, message=message,
                           log_level=LoggingLevel.INFO)
        return

    def analyseAndGenerateNeurons(self, _neurons=None):
        """
        Analysis a list of neurons, solves them and generates the corresponding code.
        :param _neurons: a list of neurons.
        :type _neurons: list(ASTNeuron)
        """
        for neuron in _neurons:
            self.analyseAndGenerateNeuron(neuron)
        return

    def generateModelHeader(self, _neuron=None):
        """
        For a handed over neuron, this method generates the corresponding header file.
        :param _neuron: a single neuron object.
        :type _neuron:  ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CodeGenerator.NEST) No or wrong type of neuron provided (%s)!' % type(_neuron)
        input_neuron_header = self.setupStandardNamespace(_neuron)
        output_neuron_header = self.__templateNeuronHeader.render(input_neuron_header)
        with open(str(os.path.join(FrontendConfiguration.get_target_path(), _neuron.get_name())) + '.h', 'w+') as f:
            f.write(str(output_neuron_header))
        return

    def generateModelImplementation(self, _neuron=None):
        """
        For a handed over neuron, this method generates the corresponding implementation file.
        :param _neuron: a single neuron object.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CodeGenerator.NEST) No or wrong type of neuron provided (%s)!' % type(_neuron)
        input_neuron_implementation = self.setupStandardNamespace(_neuron)
        output_neuron_implementation = self.__templateNeuronImplementation.render(input_neuron_implementation)
        with open(str(os.path.join(FrontendConfiguration.get_target_path(), _neuron.get_name())) + '.cpp', 'w+') as f:
            f.write(str(output_neuron_implementation))
        return

    def generateNestCode(self, _neuron=None):
        """
        For a handed over neuron, this method generates the corresponding header and implementation file.
        :param _neuron: a single neuron object.
        :type _neuron: ASTNeuron
        """
        if not os.path.isdir(FrontendConfiguration.get_target_path()):
            os.makedirs(FrontendConfiguration.get_target_path())
        self.generateModelHeader(_neuron)
        self.generateModelImplementation(_neuron)
        return

    def setupStandardNamespace(self, _neuron=None):
        """
        Returns a standard namespace with often required functionality.
        :param _neuron: a single neuron instance
        :type _neuron: ASTNeuron
        :return: a map from name to functionality.
        :rtype: dict
        """
        namespace = {}
        namespace['neuronName'] = _neuron.get_name()
        namespace['neuron'] = _neuron
        namespace['moduleName'] = FrontendConfiguration.get_module_name()
        # helper classes and objects
        converter = NESTReferenceConverter(_usesGSL=False)
        legacy_pretty_printer = LegacyExpressionPrinter(_referenceConverter=converter)
        namespace['printer'] = NestPrinter(_expressionPrettyPrinter=legacy_pretty_printer)
        namespace['assignments'] = NestAssignmentsHelper()
        namespace['names'] = NestNamesConverter()
        namespace['declarations'] = NestDeclarationsHelper()
        namespace['utils'] = ASTUtils()
        namespace['idemPrinter'] = LegacyExpressionPrinter()
        # information regarding the neuron
        namespace['outputEvent'] = namespace['printer'].printOutputEvent(_neuron.get_body())
        namespace['is_spike_input'] = ASTUtils.is_spike_input(_neuron.get_body())
        namespace['is_current_input'] = ASTUtils.is_current_input(_neuron.get_body())
        namespace['odeTransformer'] = OdeTransformer()
        # some additional information
        self.defineSolverType(namespace, _neuron)
        # GSL stuff
        gsl_converter = GSLReferenceConverter()
        gsl_printer = LegacyExpressionPrinter(_referenceConverter=gsl_converter)
        namespace['printerGSL'] = gsl_printer
        return namespace

    def defineSolverType(self, _namespace=dict, _neuron=None):
        """
        For a handed over neuron this method enriches the namespace by methods which are used to solve
        odes.
        :param _namespace: a single namespace dict.
        :type _namespace:  dict
        :param _neuron: a single neuron
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CodeGeneration.CodeGenerator) No or wrong type of neuron provided (%s)!' % type(_neuron)
        _namespace['useGSL'] = False
        if _neuron.get_equations_blocks() is not None and len(_neuron.get_equations_blocks().get_declarations()) > 0:
            if (not self.functionShapeExists(_neuron.get_equations_blocks().get_ode_shapes())) or \
                    len(_neuron.get_equations_blocks().get_ode_equations()) > 1:
                _namespace['names'] = GSLNamesConverter()
                _namespace['useGSL'] = True
                converter = NESTReferenceConverter(_usesGSL=True)
                legacy_pretty_printer = LegacyExpressionPrinter(_referenceConverter=converter)
                _namespace['printer'] = NestPrinter(_expressionPrettyPrinter=legacy_pretty_printer)
        return

    @classmethod
    def functionShapeExists(cls, _shapes=list()):
        """
        For a handed over list of shapes this method checks if a single shape exits with differential order of 0.
        :param _shapes: a list of shapes
        :type _shapes: list(ASTOdeShape)
        :return: True if at leas one shape with diff. order of 0 exits, otherwise False.
        :rtype: bool
        """
        from pynestml.meta_model.ASTOdeShape import ASTOdeShape
        for shape in _shapes:
            if isinstance(shape, ASTOdeShape) and shape.get_variable().get_differential_order() == 0:
                return True
        return False

    @classmethod
    def solveOdesAndShapes(cls, _neuron=None):
        """
        Solves all odes and equations in the handed over neuron.
        :param _neuron: a single neuron instance.
        :type _neuron: ASTNeuron
        :return: a solved instance.
        :rtype: ASTNeuron
        """
        # it should be ensured that most one equations block is present
        equations_block = _neuron.get_equations_blocks()
        if equations_block is None:
            return _neuron
        else:
            if len(equations_block.get_ode_equations()) > 1 and len(equations_block.get_ode_shapes()) == 0:
                code, message = Messages.get_neuron_solved_by_solver(_neuron.get_name())
                Logger.log_message(neuron=_neuron, code=code, message=message,
                                   error_position=_neuron.get_source_position(), log_level=LoggingLevel.INFO)
                return _neuron
            else:
                code, message = Messages.get_neuron_analyzed(_neuron.get_name())
                Logger.log_message(neuron=_neuron, code=code, message=message,
                                   error_position=_neuron.get_source_position(),
                                   log_level=LoggingLevel.INFO)
                working_copy = EquationsBlockProcessor.solveOdeWithShapes(_neuron)
                return working_copy
