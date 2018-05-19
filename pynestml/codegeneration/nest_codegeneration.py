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
from pynestml.meta_model.ASTEquationsBlock import ASTEquationsBlock
from pynestml.meta_model.ASTNeuron import ASTNeuron
from pynestml.meta_model.ASTOdeEquation import ASTOdeEquation
from pynestml.meta_model.ASTOdeFunction import ASTOdeFunction
from pynestml.meta_model.ASTOdeShape import ASTOdeShape
from pynestml.solver.TransformerBase import add_assignment_to_update_block
from pynestml.solver.solution_transformers import integrate_exact_solution, functional_shapes_to_odes, \
    integrate_delta_solution
from pynestml.symbols.Symbol import SymbolKind
from pynestml.utils.ASTUtils import ASTUtils
from pynestml.utils.Logger import Logger
from pynestml.utils.Logger import LoggingLevel
from pynestml.utils.Messages import Messages
from pynestml.utils.ModelParser import ModelParser
from pynestml.utils.OdeTransformer import OdeTransformer
from pynestml.visitors.ASTSymbolTableVisitor import ASTSymbolTableVisitor
from pynestml.visitors.ASTVisitor import ASTVisitor

# setup the template environment
env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'resources_NEST')))
setup_env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'resources_NEST', 'setup')))
# setup the cmake template
template_cmakelists = setup_env.get_template('CMakeLists.jinja2')
# setup the module class template
template_module_class = env.get_template('ModuleClass.jinja2')
# setup the NEST module template
template_module_header = env.get_template('ModuleHeader.jinja2')
# setup the SLI_Init file
template_sli_init = setup_env.get_template('SLI_Init.jinja2')
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
    namespace = {'neurons': neurons, 'moduleName': FrontendConfiguration.get_module_name()}
    if not os.path.exists(FrontendConfiguration.get_target_path()):
        os.makedirs(FrontendConfiguration.get_target_path())

    with open(str(os.path.join(FrontendConfiguration.get_target_path(),
                               FrontendConfiguration.get_module_name())) + '.h', 'w+') as f:
        f.write(str(template_module_header.render(namespace)))

    with open(str(os.path.join(FrontendConfiguration.get_target_path(),
                               FrontendConfiguration.get_module_name())) + '.cpp', 'w+') as f:
        f.write(str(template_module_class.render(namespace)))

    with open(str(os.path.join(FrontendConfiguration.get_target_path(),
                               'CMakeLists')) + '.txt', 'w+') as f:
        f.write(str(template_cmakelists.render(namespace)))

    if not os.path.isdir(os.path.realpath(os.path.join(FrontendConfiguration.get_target_path(), 'sli'))):
        os.makedirs(os.path.realpath(os.path.join(FrontendConfiguration.get_target_path(), 'sli')))

    with open(str(os.path.join(FrontendConfiguration.get_target_path(), 'sli',
                               FrontendConfiguration.get_module_name() + "-init")) + '.sli', 'w+') as f:
        f.write(str(template_sli_init.render(namespace)))

    code, message = Messages.get_module_generated(FrontendConfiguration.get_target_path())
    Logger.log_message(None, code, message, None, LoggingLevel.INFO)


def analyse_and_generate_neurons(neurons):
    # type: (list(ASTNeuron)) -> None
    """
    Analysis a list of neurons, solves them and generates the corresponding code.
    :param neurons: a list of neurons.
    """
    for neuron in neurons:
        print("Generates code for the neuron {}.".format(neuron.get_name()))
        analyse_and_generate_neuron(neuron)


def analyse_and_generate_neuron(neuron):
    # type: (ASTNeuron) -> None
    """
    Analysis a single neuron, solves it and generates the corresponding code.
    :param neuron: a single neuron.
    """
    code, message = Messages.get_start_processing_neuron(neuron.get_name())
    Logger.log_message(neuron, code, message, neuron.get_source_position(), LoggingLevel.INFO)
    # make normalization
    # apply spikes to buffers
    # get rid of convolve, store them and apply then at the end
    equations_block = neuron.get_equations_block()
    shape_to_buffers = {}
    if neuron.get_equations_block() is not None:
        # extract function names and corresponding incoming buffers
        convolve_calls = OdeTransformer.get_sum_function_calls(equations_block)
        for convolve in convolve_calls:
            shape_to_buffers[str(convolve.get_args()[0])] = str(convolve.get_args()[1])
        OdeTransformer.refactor_convolve_call(neuron.get_equations_block())
        make_functions_self_contained(equations_block.get_ode_functions())
        replace_functions_through_defining_expressions(equations_block.get_ode_equations(),
                                                       equations_block.get_ode_functions())
        # transform everything into gsl processable (e.g. no functional shapes) or exact form.
        transform_shapes_and_odes(neuron, shape_to_buffers)
        # update the symbol table
        neuron.accept(ASTSymbolTableVisitor())
    generate_nest_code(neuron)
    # at that point all shapes are transformed into the ODE form and spikes can be applied
    code, message = Messages.get_code_generated(neuron.get_name(), FrontendConfiguration.get_target_path())
    Logger.log_message(neuron, code, message, neuron.get_source_position(), LoggingLevel.INFO)


def generate_nest_code(neuron):
    # type: (ASTNeuron) -> None
    """
    For a handed over neuron, this method generates the corresponding header and implementation file.
    :param neuron: a single neuron object.
    """
    if not os.path.isdir(FrontendConfiguration.get_target_path()):
        os.makedirs(FrontendConfiguration.get_target_path())
    generate_model_h_file(neuron)
    generate_neuron_cpp_file(neuron)


def generate_model_h_file(neuron):
    # type: (ASTNeuron) -> None
    """
    For a handed over neuron, this method generates the corresponding header file.
    :param neuron: a single neuron object.
    """
    # print("!!!", neuron)
    neuron_h_file = template_neuron_h_file.render(setup_generation_helpers(neuron))
    with open(str(os.path.join(FrontendConfiguration.get_target_path(), neuron.get_name())) + '.h', 'w+') as f:
        f.write(str(neuron_h_file))


def generate_neuron_cpp_file(neuron):
    # type: (ASTNeuron) -> None
    """
    For a handed over neuron, this method generates the corresponding implementation file.
    :param neuron: a single neuron object.
    """
    neuron_cpp_file = template_neuron_cpp_file.render(setup_generation_helpers(neuron))
    with open(str(os.path.join(FrontendConfiguration.get_target_path(), neuron.get_name())) + '.cpp', 'w+') as f:
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

    namespace['neuronName'] = neuron.get_name()
    namespace['neuron'] = neuron
    namespace['moduleName'] = FrontendConfiguration.get_module_name()
    namespace['printer'] = NestPrinter(legacy_pretty_printer)
    namespace['assignments'] = NestAssignmentsHelper()
    namespace['names'] = NestNamesConverter()
    namespace['declarations'] = NestDeclarationsHelper()
    namespace['utils'] = ASTUtils()
    namespace['idemPrinter'] = LegacyExpressionPrinter()
    namespace['outputEvent'] = namespace['printer'].printOutputEvent(neuron.get_body())
    namespace['is_spike_input'] = ASTUtils.is_spike_input(neuron.get_body())
    namespace['is_current_input'] = ASTUtils.is_current_input(neuron.get_body())
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
    if neuron.get_equations_block() is not None and len(neuron.get_equations_block().get_declarations()) > 0:
        if (not is_functional_shape_present(neuron.get_equations_block().get_ode_shapes())) or \
                len(neuron.get_equations_block().get_ode_equations()) > 1:
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
        if shape.get_variable().get_differential_order() == 0:
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

    if isinstance(neuron.get_equations_blocks(), ASTEquationsBlock):
        equations_block = neuron.get_equations_block()

        if len(equations_block.get_ode_shapes()) == 0:
            code, message = Messages.get_neuron_solved_by_solver(neuron.get_name())
            Logger.log_message(neuron, code, message, neuron.get_source_position(), LoggingLevel.INFO)
            result = neuron
        if len(equations_block.get_ode_shapes()) == 1 and \
                str(equations_block.get_ode_shapes()[0].get_expression()).strip().startswith(
                    "delta"):  # assume the model is well formed
            shape = equations_block.get_ode_shapes()[0]

            integrate_delta_solution(equations_block, neuron, shape, shape_to_buffers)
            return result
        elif len(equations_block.get_ode_equations()) == 1:
            code, message = Messages.get_neuron_analyzed(neuron.get_name())
            Logger.log_message(neuron, code, message, neuron.get_source_position(), LoggingLevel.INFO)
            solver_result = solve_ode_with_shapes(equations_block)

            if solver_result["solver"] is "analytical":
                result = integrate_exact_solution(neuron, solver_result)
                result.remove_equations_block()
            elif solver_result["solver"] is "numeric":
                at_least_one_functional_shape = False
                for shape in equations_block.get_ode_shapes():
                    if shape.get_variable().get_differential_order() == 0:
                        at_least_one_functional_shape = True
                if at_least_one_functional_shape:
                    functional_shapes_to_odes(result, solver_result)
            else:
                result = neuron
        else:
            code, message = Messages.get_neuron_solved_by_solver(neuron.get_name())
            Logger.log_message(neuron, code, message, neuron.get_source_position(), LoggingLevel.INFO)
            at_least_one_functional_shape = False
            for shape in equations_block.get_ode_shapes():
                if shape.get_variable().get_differential_order() == 0:
                    at_least_one_functional_shape = True
                    break
            if at_least_one_functional_shape:
                ode_shapes = solve_functional_shapes(equations_block)
                functional_shapes_to_odes(result, ode_shapes)

        apply_spikes_from_buffers(result, shape_to_buffers)
    return result


def apply_spikes_from_buffers(neuron, shape_to_buffers):
    spike_updates = []
    initial_values = neuron.get_initial_values_blocks()
    for declaration in initial_values.get_declarations():
        variable = declaration.get_variables()[0]
        for shape in shape_to_buffers:
            matcher_computed_shape_odes = re.compile(shape + r"(__\d+)?")
            buffer_type = neuron.get_scope().\
                resolve_to_symbol(shape_to_buffers[shape], SymbolKind.VARIABLE).get_type_symbol()
            if re.match(matcher_computed_shape_odes, str(variable)):
                assignment_string = variable.get_complete_name() + " += (" + shape_to_buffers[
                    shape] + '/' + buffer_type.print_nestml_type() + ") * " +\
                                    _printer.print_expression(declaration.get_expression())
                spike_updates.append(ModelParser.parse_assignment(assignment_string))
                # the IV is applied. can be reset
                declaration.set_expression(ModelParser.parse_expression("0"))
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

    for equation in equations_block.get_ode_equations():
        result["odes"].append({"symbol": equation.get_lhs().get_name(),
                               "definition": _printer.print_expression(equation.get_rhs())})

    ode_shape_names = set()
    for shape in equations_block.get_ode_shapes():
        if shape.get_variable().get_differential_order() == 0:
            result["shapes"].append({"type": "function",
                                     "symbol": shape.get_variable().get_complete_name(),
                                     "definition": _printer.print_expression(shape.get_expression())})

        else:
            extracted_shape_name = shape.get_variable().get_name()
            if '__' in shape.get_variable().get_name():
                extracted_shape_name = shape.get_variable().get_name()[0:shape.get_variable().get_name().find("__")]
            if extracted_shape_name not in ode_shape_names:  # add shape name only once
                ode_shape_names.add(extracted_shape_name)

    # try to resolve all available initial values
    shape_name_to_initial_values = {}
    shape_name_to_shape_definition = {}

    for shape_name in ode_shape_names:
        shape_name_symbol = equations_block.get_scope().resolve_to_symbol(shape_name, SymbolKind.VARIABLE)
        shape_name_to_initial_values[shape_name] = [
            _printer.print_expression(shape_name_symbol.get_declaring_expression())]
        shape_name_to_shape_definition[shape_name] = _printer.print_expression(shape_name_symbol.get_ode_definition())
        order = 1
        while True:
            shape_name_symbol = equations_block.get_scope().resolve_to_symbol(shape_name + "__" + 'd' * order,
                                                                              SymbolKind.VARIABLE)
            if shape_name_symbol is not None:
                shape_name_to_initial_values[shape_name].append(
                    _printer.print_expression(shape_name_symbol.get_declaring_expression()))
                shape_name_to_shape_definition[shape_name] = _printer.print_expression(
                    shape_name_symbol.get_ode_definition())
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

    for shape in equations_block.get_ode_shapes():
        if shape.get_variable().get_differential_order() == 0:
            result["shapes"].append({"type": "function",
                                     "symbol": shape.get_variable().get_complete_name(),
                                     "definition": _printer.print_expression(shape.get_expression())})

    result["parameters"] = []  # ode-framework requires this.
    return result


# todo: not used
class ASTContainsVisitor(ASTVisitor):
    # todo
    def __init__(self, target):
        self.target = target
        self.result = False

    def visit_simple_expression(self, node):
        if node.get_name() == self.target:
            self.result = True


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
            matcher = re.compile(_variable_matching_template.format(source.get_variable_name()))
            target_definition = str(target.get_expression())
            target_definition = re.sub(matcher, "(" + str(source.get_expression()) + ")", target_definition)
            target.expression = ModelParser.parse_expression(target_definition)
    return functions


def replace_functions_through_defining_expressions(definitions, functions):
    # type: (list(ASTOdeEquation), list(ASTOdeFunction)) -> list(ASTOdeFunction)
    """
    Refractors symbols form `functions` in `definitions` with corresponding defining expressions from `functions`.
    :param definitions: A sorted list with entries {"symbol": "name", "definition": "expression"} that should be made
    free from.
    :param functions: A sorted list with entries {"symbol": "name", "definition": "expression"} with functions which
    must be replaced in `definitions`.
    :return: A list with definitions. Expressions in `definitions` don't depend on functions from `functions`.
    """
    for fun in functions:
        for target in definitions:
            matcher = re.compile(_variable_matching_template.format(fun.get_variable_name()))
            target_definition = str(target.get_rhs())
            target_definition = re.sub(matcher, "(" + str(fun.get_expression()) + ")", target_definition)
            target.rhs = ModelParser.parse_expression(target_definition)
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
                       "definition": _printer.print_expression(fun.get_expression())})

    return result
