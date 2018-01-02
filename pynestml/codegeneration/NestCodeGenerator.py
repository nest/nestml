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
from jinja2 import Environment, FileSystemLoader
from pynestml.codegeneration.NestDeclarationsHelper import NestDeclarationsHelper
from pynestml.codegeneration.NestAssignmentsHelper import NestAssignmentsHelper
from pynestml.codegeneration.NestNamesConverter import NestNamesConverter
from pynestml.codegeneration.NestPrinter import NestPrinter
from pynestml.codegeneration.LegacyExpressionPrinter import LegacyExpressionPrinter
from pynestml.codegeneration.NestReferenceConverter import NESTReferenceConverter
from pynestml.codegeneration.GSLNamesConverter import GSLNamesConverter
from pynestml.codegeneration.GSLReferenceConverter import GSLReferenceConverter
from pynestml.utils.OdeTransformer import OdeTransformer
from pynestml.utils.ASTUtils import ASTUtils
from pynestml.utils.Logger import LOGGING_LEVEL, Logger
from pynestml.utils.Messages import Messages
from pynestml.modelprocessor.ASTNeuron import ASTNeuron
from pynestml.modelprocessor.ASTSymbolTableVisitor import SymbolTableASTVisitor
from pynestml.frontend.FrontendConfiguration import FrontendConfiguration
from pynestml.solver.EquationsBlockProcessor import EquationsBlockProcessor
from copy import deepcopy
import os


class NestCodeGenerator(object):
    """
    This class represents a generator which can be used to print an internal ast to a model in
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
        namespace = {'neurons': _neurons, 'moduleName': FrontendConfiguration.getModuleName()}
        with open(str(os.path.join(FrontendConfiguration.getTargetPath(),
                                   FrontendConfiguration.getModuleName())) + '.h', 'w+') as f:
            f.write(str(self.__templateModuleHeader.render(namespace)))
        with open(str(os.path.join(FrontendConfiguration.getTargetPath(),
                                   FrontendConfiguration.getModuleName())) + '.cpp', 'w+') as f:
            f.write(str(self.__templateModuleClass.render(namespace)))
        with open(str(os.path.join(FrontendConfiguration.getTargetPath(),
                                   'CMakeLists')) + '.txt', 'w+') as f:
            f.write(str(self.__templateCMakeLists.render(namespace)))
        if not os.path.isdir(os.path.realpath(os.path.join(FrontendConfiguration.getTargetPath(), 'sli'))):
            os.makedirs(os.path.realpath(os.path.join(FrontendConfiguration.getTargetPath(), 'sli')))
        with open(str(os.path.join(FrontendConfiguration.getTargetPath(), 'sli',
                                   FrontendConfiguration.getModuleName() + "-init")) + '.sli', 'w+') as f:
            f.write(str(self.__templateSLIInit.render(namespace)))
        code, message = Messages.getModuleGenerated(FrontendConfiguration.getTargetPath())
        Logger.logMessage(_neuron=None, _code=code, _message=message, _logLevel=LOGGING_LEVEL.INFO)
        return

    def analyseAndGenerateNeuron(self, _neuron=None):
        """
        Analysis a single neuron, solves it and generates the corresponding code.
        :param _neuron: a single neuron.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CodeGenerator.NEST) No or wrong type of module neuron provided (%s)!' % type(_neuron)
        code, message = Messages.getStartProcessingNeuron(_neuron.getName())
        Logger.logMessage(_neuron=_neuron, _errorPosition=_neuron.getSourcePosition(), _code=code, _message=message,
                          _logLevel=LOGGING_LEVEL.INFO)
        workingVersion = deepcopy(_neuron)
        # solve all equations
        workingVersion = self.solveOdesAndShapes(workingVersion)
        # update the symbol table
        SymbolTableASTVisitor.updateSymbolTable(workingVersion)
        self.generateNestCode(workingVersion)
        code, message = Messages.getCodeGenerated(_neuron.getName(), FrontendConfiguration.getTargetPath())
        Logger.logMessage(_neuron=_neuron, _errorPosition=_neuron.getSourcePosition(), _code=code, _message=message,
                          _logLevel=LOGGING_LEVEL.INFO)
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
        inputNeuronHeader = self.setupStandardNamespace(_neuron)
        outputNeuronHeader = self.__templateNeuronHeader.render(inputNeuronHeader)
        with open(str(os.path.join(FrontendConfiguration.getTargetPath(), _neuron.getName())) + '.h', 'w+') as f:
            f.write(str(outputNeuronHeader))
        return

    def generateModelImplementation(self, _neuron=None):
        """
        For a handed over neuron, this method generates the corresponding implementation file.
        :param _neuron: a single neuron object.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CodeGenerator.NEST) No or wrong type of neuron provided (%s)!' % type(_neuron)
        inputNeuronImplementation = self.setupStandardNamespace(_neuron)
        outputNeuronImplementation = self.__templateNeuronImplementation.render(inputNeuronImplementation)
        with open(str(os.path.join(FrontendConfiguration.getTargetPath(), _neuron.getName())) + '.cpp', 'w+') as f:
            f.write(str(outputNeuronImplementation))
        return

    def generateNestCode(self, _neuron=None):
        """
        For a handed over neuron, this method generates the corresponding header and implementation file.
        :param _neuron: a single neuron object.
        :type _neuron: ASTNeuron
        """
        if not os.path.isdir(FrontendConfiguration.getTargetPath()):
            os.makedirs(FrontendConfiguration.getTargetPath())
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
        namespace['neuronName'] = _neuron.getName()
        namespace['neuron'] = _neuron
        namespace['moduleName'] = FrontendConfiguration.getModuleName()
        # helper classes and objects
        converter = NESTReferenceConverter(_usesGSL=False)
        legacyPrettyPrinter = LegacyExpressionPrinter(_referenceConverter=converter)
        namespace['printer'] = NestPrinter(_expressionPrettyPrinter=legacyPrettyPrinter)
        namespace['assignments'] = NestAssignmentsHelper()
        namespace['names'] = NestNamesConverter()
        namespace['declarations'] = NestDeclarationsHelper()
        namespace['utils'] = ASTUtils()
        namespace['idemPrinter'] = LegacyExpressionPrinter()
        # information regarding the neuron
        namespace['outputEvent'] = namespace['printer'].printOutputEvent(_neuron.getBody())
        namespace['isSpikeInput'] = ASTUtils.isSpikeInput(_neuron.getBody())
        namespace['isCurrentInput'] = ASTUtils.isCurrentInput(_neuron.getBody())
        namespace['odeTransformer'] = OdeTransformer()
        # some additional information
        self.defineSolverType(namespace, _neuron)
        # GSL stuff
        gslConverter = GSLReferenceConverter()
        gslPrinter = LegacyExpressionPrinter(_referenceConverter=gslConverter)
        namespace['printerGSL'] = gslPrinter
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
        if _neuron.getEquationsBlocks() is not None and len(_neuron.getEquationsBlocks().getDeclarations()) > 0:
            if (not self.functionShapeExists(_neuron.getEquationsBlocks().getOdeShapes())) or \
                            len(_neuron.getEquationsBlocks().getOdeEquations()) > 1:
                _namespace['names'] = GSLNamesConverter()
                _namespace['useGSL'] = True
                converter = NESTReferenceConverter(_usesGSL=True)
                legacyPrettyPrinter = LegacyExpressionPrinter(_referenceConverter=converter)
                _namespace['printer'] = NestPrinter(_expressionPrettyPrinter=legacyPrettyPrinter)
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
        from pynestml.modelprocessor.ASTOdeShape import ASTOdeShape
        for shape in _shapes:
            if isinstance(shape, ASTOdeShape) and shape.getVariable().getDifferentialOrder() == 0:
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
        equationsBlock = _neuron.getEquationsBlocks()
        if equationsBlock is None:
            return _neuron
        else:
            if len(equationsBlock.getOdeEquations()) > 1 and len(equationsBlock.getOdeShapes()) == 0:
                code, message = Messages.getNeuronSolvedBySolver(_neuron.getName())
                Logger.logMessage(_neuron=_neuron, _code=code, _message=message,
                                  _errorPosition=_neuron.getSourcePosition(), _logLevel=LOGGING_LEVEL.INFO)
                return _neuron
            else:
                code, message = Messages.getNeuronAnalyzed(_neuron.getName())
                Logger.logMessage(_neuron=_neuron, _code=code, _message=message,
                                  _errorPosition=_neuron.getSourcePosition(),
                                  _logLevel=LOGGING_LEVEL.INFO)
                workingCopy = EquationsBlockProcessor.solveOdeWithShapes(_neuron)
                return workingCopy
