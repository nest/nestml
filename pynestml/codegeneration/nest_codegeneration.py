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
import re

from jinja2 import Environment, FileSystemLoader
from odetoolbox import analysis

from pynestml.codegeneration.ExpressionsPrettyPrinter import ExpressionsPrettyPrinter
from pynestml.codegeneration.GSLNamesConverter import GSLNamesConverter
from pynestml.codegeneration.GSLReferenceConverter import GSLReferenceConverter
from pynestml.codegeneration.LegacyExpressionPrinter import LegacyExpressionPrinter
from pynestml.codegeneration.NestAssignmentsHelper import NestAssignmentsHelper
from pynestml.codegeneration.NestDeclarationsHelper import NestDeclarationsHelper
from pynestml.codegeneration.NestNamesConverter import NestNamesConverter
from pynestml.codegeneration.NestPrinter import NestPrinter
from pynestml.codegeneration.NestReferenceConverter import NESTReferenceConverter
from pynestml.frontend.FrontendConfiguration import FrontendConfiguration
from pynestml.modelprocessor.ASTEquationsBlock import ASTEquationsBlock
from pynestml.modelprocessor.ASTNeuron import ASTNeuron
from pynestml.modelprocessor.ASTOdeEquation import ASTOdeEquation
from pynestml.modelprocessor.ASTOdeFunction import ASTOdeFunction
from pynestml.modelprocessor.ASTOdeShape import ASTOdeShape
from pynestml.modelprocessor.ASTSymbolTableVisitor import ASTSymbolTableVisitor
from pynestml.modelprocessor.ModelParser import ModelParser
from pynestml.modelprocessor.Symbol import SymbolKind
from pynestml.solver.TransformerBase import add_assignment_to_update_block
from pynestml.solver.solution_transformers import integrate_exact_solution, functional_shapes_to_odes, \
    integrate_delta_solution
from pynestml.utils.ASTUtils import ASTUtils
from pynestml.utils.Logger import Logger, LOGGING_LEVEL
from pynestml.utils.Messages import Messages
from pynestml.utils.OdeTransformer import OdeTransformer

# setup the template environment
env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templatesNEST')))
# setup the cmake template
template_cmakelists = env.get_template('CMakeLists.jinja2')
# setup the module class template
template_module_class = env.get_template('ModuleClass.jinja2')
# setup the NEST module template
template_module_header = env.get_template('ModuleHeader.jinja2')
# setup the SLI_Init file
template_sli_init = env.get_template('SLI_Init.jinja2')
# setup the neuron header template
template_neuron_h_file = env.get_template('NeuronHeader.jinja2')
# setup the neuron implementation template
template_neuron_cpp_file = env.get_template('NeuronClass.jinja2')

_printer = ExpressionsPrettyPrinter()

def generate_nest_module_code(neurons):
    # type: (list(ASTNeuron)) -> None
    """
    Generates code that is necessary to integrate neuron models into the NEST infrastructure.
    :param neurons: a list of neurons
    :type neurons: list(ASTNeuron)
    """
    namespace = {'neurons': neurons, 'moduleName': FrontendConfiguration.getModuleName()}
    if not os.path.exists(FrontendConfiguration.getTargetPath()):
        os.makedirs(FrontendConfiguration.getTargetPath())

    with open(str(os.path.join(FrontendConfiguration.getTargetPath(),
                               FrontendConfiguration.getModuleName())) + '.h', 'w+') as f:
        f.write(str(template_module_header.render(namespace)))

    with open(str(os.path.join(FrontendConfiguration.getTargetPath(),
                               FrontendConfiguration.getModuleName())) + '.cpp', 'w+') as f:
        f.write(str(template_module_class.render(namespace)))

    with open(str(os.path.join(FrontendConfiguration.getTargetPath(),
                               'CMakeLists')) + '.txt', 'w+') as f:
        f.write(str(template_cmakelists.render(namespace)))

    if not os.path.isdir(os.path.realpath(os.path.join(FrontendConfiguration.getTargetPath(), 'sli'))):
        os.makedirs(os.path.realpath(os.path.join(FrontendConfiguration.getTargetPath(), 'sli')))

    with open(str(os.path.join(FrontendConfiguration.getTargetPath(), 'sli',
                               FrontendConfiguration.getModuleName() + "-init")) + '.sli', 'w+') as f:
        f.write(str(template_sli_init.render(namespace)))

    code, message = Messages.getModuleGenerated(FrontendConfiguration.getTargetPath())
    Logger.logMessage(None, code, message, None, LOGGING_LEVEL.INFO)


def analyse_and_generate_neurons(neurons):
    # type: (list(ASTNeuron)) -> None
    """
    Analysis a list of neurons, solves them and generates the corresponding code.
    :param neurons: a list of neurons.
    """
    for neuron in neurons:
        print("Generates code for the neuron {}.".format(neuron.getName()))
        analyse_and_generate_neuron(neuron)


def analyse_and_generate_neuron(neuron):
    # type: (ASTNeuron) -> None
    """
    Analysis a single neuron, solves it and generates the corresponding code.
    :param neuron: a single neuron.
    """
    code, message = Messages.getStartProcessingNeuron(neuron.getName())
    Logger.logMessage(neuron, code, message, neuron.getSourcePosition(), LOGGING_LEVEL.INFO)
    # make noramlization
    # apply spikes to buffers
    # get rid of convolve, store them and apply then at the end
    equations_block = neuron.get_equations_block()
    shape_to_buffers = {}
    if neuron.get_equations_block() is not None:
        # extract function names and corresponding incoming buffers
        convolve_calls = OdeTransformer.get_sumFunctionCalls(equations_block)
        for convolve in convolve_calls:
            shape_to_buffers[str(convolve.getArgs()[0])] = str(convolve.getArgs()[1])

        OdeTransformer.refactor_convolve_call(neuron.get_equations_block())
        make_functions_self_contained(equations_block.getOdeFunctions())
        replace_functions_through_defining_expressions(equations_block.getOdeEquations(), equations_block.getOdeFunctions())

        # transform everything into gsl processable (e.g. no functional shapes) or exact form.
        transform_shapes_and_odes(neuron, shape_to_buffers)
        # update the symbol table
        ASTSymbolTableVisitor.updateSymbolTable(neuron)

    generate_nest_code(neuron)

    # at that point all shapes are transformed into the ODE form and spikes can be applied
    code, message = Messages.getCodeGenerated(neuron.getName(), FrontendConfiguration.getTargetPath())
    Logger.logMessage(neuron, code, message, neuron.getSourcePosition(), LOGGING_LEVEL.INFO)


def generate_nest_code(neuron):
    # type: (ASTNeuron) -> None
    """
    For a handed over neuron, this method generates the corresponding header and implementation file.
    :param neuron: a single neuron object.
    """
    if not os.path.isdir(FrontendConfiguration.getTargetPath()):
        os.makedirs(FrontendConfiguration.getTargetPath())
    generate_model_h_file(neuron)
    generate_neuron_cpp_file(neuron)


def generate_model_h_file(neuron):
    # type: (ASTNeuron) -> None
    """
    For a handed over neuron, this method generates the corresponding header file.
    :param neuron: a single neuron object.
    """
    print("!!!", neuron)
    neuron_h_file = template_neuron_h_file.render(setup_generation_helpers(neuron))
    with open(str(os.path.join(FrontendConfiguration.getTargetPath(), neuron.getName())) + '.h', 'w+') as f:
        f.write(str(neuron_h_file))


def generate_neuron_cpp_file(neuron):
    # type: (ASTNeuron) -> None
    """
    For a handed over neuron, this method generates the corresponding implementation file.
    :param neuron: a single neuron object.
    """
    neuron_cpp_file = template_neuron_cpp_file.render(setup_generation_helpers(neuron))
    with open(str(os.path.join(FrontendConfiguration.getTargetPath(), neuron.getName())) + '.cpp', 'w+') as f:
        f.write(str(neuron_cpp_file))


def setup_generation_helpers(neuron):
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

    namespace['neuronName'] = neuron.getName()
    namespace['neuron'] = neuron
    namespace['moduleName'] = FrontendConfiguration.getModuleName()
    namespace['printer'] = NestPrinter(legacy_pretty_printer)
    namespace['assignments'] = NestAssignmentsHelper()
    namespace['names'] = NestNamesConverter()
    namespace['declarations'] = NestDeclarationsHelper()
    namespace['utils'] = ASTUtils()
    namespace['idemPrinter'] = LegacyExpressionPrinter()
    namespace['outputEvent'] = namespace['printer'].printOutputEvent(neuron.getBody())
    namespace['isSpikeInput'] = ASTUtils.isSpikeInput(neuron.getBody())
    namespace['isCurrentInput'] = ASTUtils.isCurrentInput(neuron.getBody())
    namespace['odeTransformer'] = OdeTransformer()
    namespace['printerGSL'] = gsl_printer

    define_solver_type(neuron, namespace)
    return namespace


def define_solver_type(neuron, namespace):
    # type: (ASTNeuron, dict) -> None
    """
    For a handed over neuron this method enriches the namespace by methods which are used to solve
    odes.
    :param namespace: a single namespace dict.
    :param neuron: a single neuron
    """
    namespace['useGSL'] = False
    if neuron.get_equations_block() is not None and len(neuron.get_equations_block().getDeclarations()) > 0:
        if (not is_functional_shape_present(neuron.get_equations_block().getOdeShapes())) or \
                len(neuron.get_equations_block().getOdeEquations()) > 1:
            namespace['names'] = GSLNamesConverter()
            namespace['useGSL'] = True
            converter = NESTReferenceConverter(True)
            legacy_pretty_printer = LegacyExpressionPrinter(converter)
            namespace['printer'] = NestPrinter(legacy_pretty_printer)
    return


def is_functional_shape_present(shapes):
    # type: (list(ASTOdeShape)) -> bool
    """
    For a handed over list of shapes this method checks if a single shape exits with differential order of 0.
    :param shapes: a list of shapes
    :type shapes: list(ASTOdeShape)
    :return: True if at leas one shape with diff. order of 0 exits, otherwise False.
    :rtype: bool
    """
    for shape in shapes:
        if shape.getVariable().getDifferentialOrder() == 0:
            return True
    return False


def transform_shapes_and_odes(neuron, shape_to_buffers):
    # type: (ASTNeuron, map(str, str)) -> ASTNeuron
    """
    Solves all odes and equations in the handed over neuron.
    :param neuron: a single neuron instance.
    :param shape_to_buffers: Map of shape names to buffers to which they were connected.
    :return: A transformed version of the neuron that can be passed to the GSL.
    """
    # it should be ensured that most one equations block is present
    result = neuron

    if isinstance(neuron.getEquationsBlocks(), ASTEquationsBlock):
        equations_block = neuron.get_equations_block()

        if len(equations_block.getOdeShapes()) == 0:
            code, message = Messages.getNeuronSolvedBySolver(neuron.getName())
            Logger.logMessage(neuron, code, message, neuron.getSourcePosition(), LOGGING_LEVEL.INFO)
            result = neuron
        if len(equations_block.getOdeShapes()) == 1 and \
                str(equations_block.getOdeShapes()[0].getExpression()).strip().startswith("delta"): # assume the model is well formed
            shape = equations_block.getOdeShapes()[0]

            integrate_delta_solution(equations_block, neuron, shape, shape_to_buffers)
            return result

        elif len(equations_block.getOdeEquations()) == 1:
            code, message = Messages.getNeuronAnalyzed(neuron.getName())
            Logger.logMessage(neuron, code, message, neuron.getSourcePosition(), LOGGING_LEVEL.INFO)
            solver_result = solve_ode_with_shapes(equations_block)

            if solver_result["solver"] is "analytical":
                result = integrate_exact_solution(neuron, solver_result)
                result.remove_equations_block()
            elif solver_result["solver"] is "numeric":
                at_least_one_functional_shape = False
                for shape in equations_block.getOdeShapes():
                    if shape.getVariable().getDifferentialOrder() == 0:
                        at_least_one_functional_shape = True
                if at_least_one_functional_shape:
                    functional_shapes_to_odes(result, solver_result)
            else:
                result = neuron
        else:
            code, message = Messages.getNeuronSolvedBySolver(neuron.getName())
            Logger.logMessage(neuron, code, message, neuron.getSourcePosition(), LOGGING_LEVEL.INFO)
            at_least_one_functional_shape = False
            for shape in equations_block.getOdeShapes():
                if shape.getVariable().getDifferentialOrder() == 0:
                    at_least_one_functional_shape = True
            if at_least_one_functional_shape:
                ode_shapes = solve_functional_shapes(equations_block)
                functional_shapes_to_odes(result, ode_shapes)

        apply_spikes_from_buffers(result, shape_to_buffers)
    return result


def apply_spikes_from_buffers(neuron, shape_to_buffers):
    spike_updates = []
    initial_values = neuron.get_initial_values_blocks()
    for declaration in initial_values.getDeclarations():

        variable = declaration.getVariables()[0]
        for shape in shape_to_buffers:
            matcher_computed_shape_odes = re.compile(shape + r"(__\d+)?")

            if re.match(matcher_computed_shape_odes, str(variable)):
                assignment_string = str(variable) + " += " + shape_to_buffers[shape] + " * " + \
                                    _printer.printExpression(declaration.getExpression())
                spike_updates.append(ModelParser.parseAssignment(assignment_string))
                # the IV is applied. can be reseted
                declaration.set_expression(ModelParser.parseExpression("0"))
    for assignment in spike_updates:
        add_assignment_to_update_block(assignment, neuron)


def solve_ode_with_shapes(equations_block):
    # type: (ASTEquationsBlock) -> dict[str, list]
    odes_shapes_json = transform_ode_and_shapes_to_json(equations_block)

    return analysis(odes_shapes_json)


def transform_ode_and_shapes_to_json(equations_block):
    # type: (ASTEquationsBlock) -> dict[str, list]
    """
    Converts AST node to a JSON representation
    :param equations_block:equations_block
    :return: json mapping: {odes: [...], shape: [...]}
    """
    result = {"odes": [], "shapes": []}

    for equation in equations_block.getOdeEquations():
        result["odes"].append({"symbol": equation.getLhs().getName(),
                               "definition": _printer.printExpression(equation.getRhs())})

    ode_shape_names = set()
    for shape in equations_block.getOdeShapes():
        if shape.getVariable().getDifferentialOrder() == 0:
            result["shapes"].append({"type": "function",
                                     "symbol": shape.getVariable().getCompleteName(),
                                     "definition": _printer.printExpression(shape.getExpression())})

        else:
            extracted_shape_name = shape.getVariable().getName()
            if '__' in shape.getVariable().getName():
                extracted_shape_name = shape.getVariable().getName()[0:shape.getVariable().getName().find("__")]
            if extracted_shape_name not in ode_shape_names:  # add shape name only once
                ode_shape_names.add(extracted_shape_name)

    # try to resolve all available initial values
    shape_name_to_initial_values = {}
    shape_name_to_shape_definition = {}

    for shape_name in ode_shape_names:
        shape_name_symbol = equations_block.getScope().resolveToAllSymbols(shape_name, SymbolKind.VARIABLE)
        shape_name_to_initial_values[shape_name] = [_printer.printExpression(shape_name_symbol.getDeclaringExpression())]
        shape_name_to_shape_definition[shape_name] = _printer.printExpression(shape_name_symbol.getOdeDefinition())
        order = 1
        while True:
            shape_name_symbol = equations_block.getScope().resolveToAllSymbols(shape_name + "__" + 'd' * order, SymbolKind.VARIABLE)
            if shape_name_symbol is not None:
                shape_name_to_initial_values[shape_name].append(_printer.printExpression(shape_name_symbol.getDeclaringExpression()))
                shape_name_to_shape_definition[shape_name] = _printer.printExpression(shape_name_symbol.getOdeDefinition())
            else:
                break
            order = order + 1

    for shape_name in ode_shape_names:
            result["shapes"].append({"type": "ode",
                                     "symbol": shape_name,
                                     "definition": shape_name_to_shape_definition[shape_name],
                                     "initial_values": shape_name_to_initial_values[shape_name]})

    result["parameters"] = []  # ode-framework requires this.
    return result


def solve_functional_shapes(equations_block):
    # type: (ASTEquationsBlock) -> dict[str, list]
    shapes_json = transform_functional_shapes_to_json(equations_block)

    return analysis(shapes_json)


def transform_functional_shapes_to_json(equations_block):
    # type: (ASTEquationsBlock) -> dict[str, list]
    """
    Converts AST node to a JSON representation
    :param equations_block:equations_block
    :return: json mapping: {odes: [...], shape: [...]}
    """
    result = {"odes": [], "shapes": []}

    for shape in equations_block.getOdeShapes():
        if shape.getVariable().getDifferentialOrder() == 0:
            result["shapes"].append({"type": "function",
                                     "symbol": shape.getVariable().getCompleteName(),
                                     "definition": _printer.printExpression(shape.getExpression())})

    result["parameters"] = []  # ode-framework requires this.
    return result


_variable_matching_template = r'(\b)({})(\b)'


def make_functions_self_contained(functions):
    # type: (list(ASTOdeFunction)) -> list(ASTOdeFunction)
    """
    TODO: it should be a method inside of the ASTOdeFunction
    Make function definition self contained, e.g. without any references to functions from `functions`.
    :param functions: A sorted list with entries ASTOdeFunction.
    :return: A list with ASTOdeFunctions. Defining expressions don't depend on each other.
    """
    for source in functions:
        for target in functions:
            matcher = re.compile(_variable_matching_template.format(source.getVariableName()))
            target_definition = str(target.getExpression())
            target_definition = re.sub(matcher, "(" + str(source.getExpression()) + ")", target_definition)
            target.setExpression(ModelParser.parseExpression(target_definition))
    return functions


def replace_functions_through_defining_expressions(definitions, functions):
    # type: (list(ASTOdeEquation), list(ASTOdeFunction)) -> list(ASTOdeFunction)
    """
    Refactors symbols form `functions` in `definitions` with corresponding defining expressions from `functions`.
    :param definitions: A sorted list with entries {"symbol": "name", "definition": "expression"} that should be made
    free from.
    :param functions: A sorted list with entries {"symbol": "name", "definition": "expression"} with functions which
    must be replaced in `definitions`.
    :return: A list with definitions. Expressions in `definitions` don't depend on functions from `functions`.
    """
    for fun in functions:
        for target in definitions:
            matcher = re.compile(_variable_matching_template.format(fun.getVariableName()))
            target_definition = str(target.getRhs())
            target_definition = re.sub(matcher, "(" + str(fun.getExpression()) + ")", target_definition)
            target.set_rhs(ModelParser.parseExpression(target_definition))
    return definitions


def transform_functions_json(equations_block):
    # type: (ASTEquationsBlock) -> list[dict[str, str]]
    """
    Converts AST node to a JSON representation
    :param equations_block:equations_block
    :return: json mapping: {odes: [...], shape: [...]}
    """
    equations_block = OdeTransformer.refactor_convolve_call(equations_block)
    result = []

    for fun in equations_block.get_functions():
        result.append({"symbol": fun.getVariableName(),
                       "definition": _printer.printExpression(fun.getExpression())})

    return result
