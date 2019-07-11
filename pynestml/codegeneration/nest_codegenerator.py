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

from jinja2 import Environment, FileSystemLoader, TemplateRuntimeError
from odetoolbox import analysis

from pynestml.codegeneration.codegenerator import CodeGenerator
from pynestml.codegeneration.expressions_pretty_printer import ExpressionsPrettyPrinter
from pynestml.codegeneration.gsl_names_converter import GSLNamesConverter
from pynestml.codegeneration.gsl_reference_converter import GSLReferenceConverter
from pynestml.codegeneration.idempotent_reference_converter import IdempotentReferenceConverter
from pynestml.codegeneration.unitless_expression_printer import UnitlessExpressionPrinter
from pynestml.codegeneration.nest_assignments_helper import NestAssignmentsHelper
from pynestml.codegeneration.nest_declarations_helper import NestDeclarationsHelper
from pynestml.codegeneration.nest_names_converter import NestNamesConverter
from pynestml.codegeneration.nest_printer import NestPrinter
from pynestml.codegeneration.nest_reference_converter import NESTReferenceConverter
from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.meta_model.ast_equations_block import ASTEquationsBlock
from pynestml.solver.solution_transformers import integrate_exact_solution, functional_shapes_to_odes
from pynestml.solver.transformer_base import add_assignment_to_update_block
from pynestml.symbols.symbol import SymbolKind
from pynestml.utils.ast_utils import ASTUtils
from pynestml.utils.logger import Logger
from pynestml.utils.logger import LoggingLevel
from pynestml.utils.messages import Messages
from pynestml.utils.model_parser import ModelParser
from pynestml.utils.ode_transformer import OdeTransformer
from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor
from pynestml.visitors.ast_higher_order_visitor import ASTHigherOrderVisitor

class NESTCodeGenerator(CodeGenerator):

    _variable_matching_template = r'(\b)({})(\b)'

    def __init__(self):
        # setup the template environment
        def raise_helper(msg):
            raise TemplateRuntimeError(msg)
        env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'resources_nest')))
        env.globals['raise'] = raise_helper
        setup_env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'resources_nest', 'setup')))
        setup_env.globals['raise'] = raise_helper
        # setup the cmake template
        self._template_cmakelists = setup_env.get_template('CMakeLists.jinja2')
        # setup the module class template
        self._template_module_class = env.get_template('ModuleClass.jinja2')
        # setup the NEST module template
        self._template_module_header = env.get_template('ModuleHeader.jinja2')
        # setup the SLI_Init file
        self._template_sli_init = setup_env.get_template('SLI_Init.jinja2')
        # setup the neuron header template
        self._template_neuron_h_file = env.get_template('NeuronHeader.jinja2')
        # setup the neuron implementation template
        self._template_neuron_cpp_file = env.get_template('NeuronClass.jinja2')

        self._printer = ExpressionsPrettyPrinter()

    def generate_code(self, neurons):
        self.analyse_transform_neurons(neurons)
        self.generate_neurons(neurons)
        self.generate_module_code(neurons)

    def generate_module_code(self, neurons):
        # type: (list(ASTNeuron)) -> None
        """
        Generates code that is necessary to integrate neuron models into the NEST infrastructure.
        :param neurons: a list of neurons
        :type neurons: list(ASTNeuron)
        """
        namespace = {'neurons': neurons,
                     'moduleName': FrontendConfiguration.get_module_name(),
                     'now': datetime.datetime.utcnow()}
        if not os.path.exists(FrontendConfiguration.get_target_path()):
            os.makedirs(FrontendConfiguration.get_target_path())

        with open(str(os.path.join(FrontendConfiguration.get_target_path(),
                                   FrontendConfiguration.get_module_name())) + '.h', 'w+') as f:
            f.write(str(self._template_module_header.render(namespace)))

        with open(str(os.path.join(FrontendConfiguration.get_target_path(),
                                   FrontendConfiguration.get_module_name())) + '.cpp', 'w+') as f:
            f.write(str(self._template_module_class.render(namespace)))

        with open(str(os.path.join(FrontendConfiguration.get_target_path(),
                                   'CMakeLists')) + '.txt', 'w+') as f:
            f.write(str(self._template_cmakelists.render(namespace)))

        if not os.path.isdir(os.path.realpath(os.path.join(FrontendConfiguration.get_target_path(), 'sli'))):
            os.makedirs(os.path.realpath(os.path.join(FrontendConfiguration.get_target_path(), 'sli')))

        with open(str(os.path.join(FrontendConfiguration.get_target_path(), 'sli',
                                   FrontendConfiguration.get_module_name() + "-init")) + '.sli', 'w+') as f:
            f.write(str(self._template_sli_init.render(namespace)))

        code, message = Messages.get_module_generated(FrontendConfiguration.get_target_path())
        Logger.log_message(None, code, message, None, LoggingLevel.INFO)


    def analyse_transform_neurons(self, neurons):
        # type: (list(ASTNeuron)) -> None
        """
        Analyse and transform a list of neurons.
        :param neurons: a list of neurons.
        """
        for neuron in neurons:
            code, message = Messages.get_analysing_transforming_neuron(neuron.get_name())
            Logger.log_message(None, code, message, None, LoggingLevel.INFO)
            self.analyse_neuron(neuron)
            # now store the transformed model
            self.store_transformed_model(neuron)


    def analyse_neuron(self, neuron):
        # type: (ASTNeuron) -> None
        """
        Analyse and transform a single neuron.
        :param neuron: a single neuron.
        """
        code, message = Messages.get_start_processing_neuron(neuron.get_name())
        Logger.log_message(neuron, code, message, neuron.get_source_position(), LoggingLevel.INFO)
        # make normalization
        # apply spikes to buffers
        # get rid of convolve, store them and apply then at the end
        equations_block = neuron.get_equations_block()
        shape_to_buffers = {}
        if equations_block is not None:
            # extract function names and corresponding incoming buffers
            convolve_calls = OdeTransformer.get_sum_function_calls(equations_block)
            for convolve in convolve_calls:
                shape_to_buffers[str(convolve.get_args()[0])] = str(convolve.get_args()[1])
            OdeTransformer.refactor_convolve_call(equations_block)
            self.make_functions_self_contained(equations_block.get_ode_functions())
            self.replace_functions_through_defining_expressions(equations_block.get_ode_equations(),
                                                           equations_block.get_ode_functions())
            # transform everything into gsl processable (e.g. no functional shapes) or exact form.
            self.transform_shapes_and_odes(neuron, shape_to_buffers)
            self.apply_spikes_from_buffers(neuron, shape_to_buffers)
            # update the symbol table
            symbol_table_visitor = ASTSymbolTableVisitor()
            symbol_table_visitor.after_ast_rewrite_ = True		# suppress warnings due to AST rewrites
            neuron.accept(symbol_table_visitor)


    def generate_neuron_code(self, neuron):
        # type: (ASTNeuron) -> None
        """
        For a handed over neuron, this method generates the corresponding header and implementation file.
        :param neuron: a single neuron object.
        """
        if not os.path.isdir(FrontendConfiguration.get_target_path()):
            os.makedirs(FrontendConfiguration.get_target_path())
        self.generate_model_h_file(neuron)
        self.generate_neuron_cpp_file(neuron)


    def generate_model_h_file(self, neuron):
        # type: (ASTNeuron) -> None
        """
        For a handed over neuron, this method generates the corresponding header file.
        :param neuron: a single neuron object.
        """
        # print("!!!", neuron)
        neuron_h_file = self._template_neuron_h_file.render(self.setup_generation_helpers(neuron))
        with open(str(os.path.join(FrontendConfiguration.get_target_path(), neuron.get_name())) + '.h', 'w+') as f:
            f.write(str(neuron_h_file))


    def generate_neuron_cpp_file(self, neuron):
        # type: (ASTNeuron) -> None
        """
        For a handed over neuron, this method generates the corresponding implementation file.
        :param neuron: a single neuron object.
        """
        neuron_cpp_file = self._template_neuron_cpp_file.render(self.setup_generation_helpers(neuron))
        with open(str(os.path.join(FrontendConfiguration.get_target_path(), neuron.get_name())) + '.cpp', 'w+') as f:
            f.write(str(neuron_cpp_file))


    def setup_generation_helpers(self, neuron):
        """
        Returns a standard namespace with often required functionality.
        :param neuron: a single neuron instance
        :type neuron: ASTNeuron
        :return: a map from name to functionality.
        :rtype: dict
        """
        gsl_converter = GSLReferenceConverter()
        gsl_printer = UnitlessExpressionPrinter(gsl_converter)
        # helper classes and objects
        converter = NESTReferenceConverter(False)
        unitless_pretty_printer = UnitlessExpressionPrinter(converter)

        namespace = dict()

        namespace['neuronName'] = neuron.get_name()
        namespace['neuron'] = neuron
        namespace['moduleName'] = FrontendConfiguration.get_module_name()
        namespace['printer'] = NestPrinter(unitless_pretty_printer)
        namespace['assignments'] = NestAssignmentsHelper()
        namespace['names'] = NestNamesConverter()
        namespace['declarations'] = NestDeclarationsHelper()
        namespace['utils'] = ASTUtils()
        namespace['idemPrinter'] = UnitlessExpressionPrinter()
        namespace['outputEvent'] = namespace['printer'].print_output_event(neuron.get_body())
        namespace['is_spike_input'] = ASTUtils.is_spike_input(neuron.get_body())
        namespace['is_current_input'] = ASTUtils.is_current_input(neuron.get_body())
        namespace['odeTransformer'] = OdeTransformer()
        namespace['printerGSL'] = gsl_printer
        namespace['now'] = datetime.datetime.utcnow()
        namespace['tracing'] = FrontendConfiguration.is_dev

        if not self.analytic_solver_dict is None:
            assert self.analytic_solver_dict["solver"] == "analytic"
            namespace['state_variables'] = self.analytic_solver_dict["state_variables"]
            namespace['update_expressions'] = self.analytic_solver_dict["update_expressions"]

        self.define_solver_type(neuron, namespace)
        return namespace


    def define_solver_type(self, neuron, namespace):
        # type: (ASTNeuron, dict) -> None
        """
        For a handed over neuron this method enriches the namespace by methods which are used to solve
        odes.
        :param namespace: a single namespace dict.
        :param neuron: a single neuron
        """
        namespace['useGSL'] = False
        if neuron.get_equations_block() is not None and len(neuron.get_equations_block().get_declarations()) > 0:
            if (not self.is_functional_shape_present(neuron.get_equations_block().get_ode_shapes())) or \
                    len(neuron.get_equations_block().get_ode_equations()) > 1:
                namespace['names'] = GSLNamesConverter()
                namespace['useGSL'] = True
                converter = NESTReferenceConverter(True)
                unitless_pretty_printer = UnitlessExpressionPrinter(converter)
                namespace['printer'] = NestPrinter(unitless_pretty_printer)
        return


    def is_functional_shape_present(self, shapes):
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


    def transform_shapes_and_odes(self, neuron, shape_to_buffers):
        # type: (ASTNeuron, map(str, str)) -> ASTNeuron
        """
        Solves all odes and equations in the handed over neuron.

        Precondition: it should be ensured that most one equations block is present.

        :param neuron: a single neuron instance.
        :param shape_to_buffers: Map of shape names to buffers to which they were connected.
        :return: A transformed version of the neuron that can be passed to the GSL.
        """

        assert isinstance(neuron.get_equations_blocks(), ASTEquationsBlock), "Precondition violated: only one equation block should be present"

        equations_block = neuron.get_equations_block()

        if len(equations_block.get_ode_shapes()) == 0 and len(equations_block.get_ode_equations()) == 0:
            # no equations defined -> no changes to the neuron
            return neuron

        # map from variable symbol names to buffer names
        # XXX: TODO: replace
        #    shape G = delta(t)
        #    V_abs' = .... * convolve(G, spikes) + ...
        # with
        #    V_abs' = .... * __spikes 
        # where __spikes is the spike buffer

        # shape_to_buffers[k]

        code, message = Messages.get_neuron_analyzed(neuron.get_name())
        Logger.log_message(neuron, code, message, neuron.get_source_position(), LoggingLevel.INFO)

        odes_shapes_json = self.transform_ode_and_shapes_to_json(equations_block)
        solver_result = analysis(odes_shapes_json, enable_stiffness_check=False)

        # XXX: TODO: assert that __h is not yet defined
        neuron.add_to_internal_block(ModelParser.parse_declaration('__h ms = resolution()'))

        ## XXX: be here add parameters? solver_dict["parameters"]

        for solver_dict in solver_result:
            if solver_dict["solver"] == "analytical":
                neuron = integrate_exact_solution(neuron, solver_dict)
            elif solver_dict["solver"].startswith("numeric"):
                functional_shapes_to_odes(neuron, solver_dict)

        return neuron


    def apply_spikes_from_buffers(self, neuron, shape_to_buffers):
        """generate the equations that update the dynamical variables when incoming spikes arrive.

        For example, a resulting `assignment_string` could be "I_shape_in += (in_spikes/nS) * 1".

        The definition of the spike kernel shape is then set to 0.
        """
        spike_updates = []
        initial_values = neuron.get_initial_values_blocks()
        for declaration in initial_values.get_declarations():
            variable = declaration.get_variables()[0]
            for shape in shape_to_buffers:
                matcher_computed_shape_odes = re.compile(shape + r"(__\d+)?")
                if re.match(matcher_computed_shape_odes, str(variable)):
                    buffer_type = neuron.get_scope(). \
                        resolve_to_symbol(shape_to_buffers[shape], SymbolKind.VARIABLE).get_type_symbol()
                    assignment_string = variable.get_complete_name() + " += (" + shape_to_buffers[
                        shape] + '/' + buffer_type.print_nestml_type() + ") * " + \
                                        self._printer.print_expression(declaration.get_expression())
                    spike_updates.append(ModelParser.parse_assignment(assignment_string))
                    # the IV is applied. can be reset
                    declaration.set_expression(ModelParser.parse_expression("0"))
        for assignment in spike_updates:
            add_assignment_to_update_block(assignment, neuron)


    def transform_ode_and_shapes_to_json(self, equations_block):
        # type: (ASTEquationsBlock) -> dict[str, list]
        """
        Converts AST node to a JSON representation
        :param equations_block:equations_block
        :return: json mapping: {odes: [...], shape: [...]}
        """
        odetoolbox_indict = { "dynamics" : [] }

        gsl_converter = IdempotentReferenceConverter()
        gsl_printer = UnitlessExpressionPrinter(gsl_converter)

        for equation in equations_block.get_ode_equations():
            lhs = str(equation.lhs)
            rhs = gsl_printer.print_expression(equation.get_rhs())
            entry = {"expression": lhs + " = " + rhs}
            symbol_name = equation.get_lhs().get_name()
            symbol = equations_block.get_scope().resolve_to_symbol(symbol_name, SymbolKind.VARIABLE)
            initial_value_expr = symbol.get_declaring_expression()
            if not initial_value_expr is None:
                entry["initial_value"] = gsl_printer.print_expression(initial_value_expr)

            odetoolbox_indict["dynamics"].append(entry)


        import pdb;pdb.set_trace()
        """
        for shape in equations_block.get_ode_shapes():
            if shape.get_variable().get_differential_order() == 0:
                result["shapes"].append({"type": "function",
                                         "symbol": shape.get_variable().get_complete_name(),
                                         "definition": self._printer.print_expression(shape.get_expression())})
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
                self._printer.print_expression(shape_name_symbol.get_declaring_expression())]
            shape_name_to_shape_definition[shape_name] = self._printer.print_expression(shape_name_symbol.get_ode_definition())
            order = 1
            while True:
                shape_name_symbol = equations_block.get_scope().resolve_to_symbol(shape_name + "__" + 'd' * order, SymbolKind.VARIABLE)
                if shape_name_symbol is not None:
                    shape_name_to_initial_values[shape_name].append(
                        self._printer.print_expression(shape_name_symbol.get_declaring_expression()))
                    shape_name_to_shape_definition[shape_name] = self._printer.print_expression(
                        shape_name_symbol.get_ode_definition())
                else:
                    break
                order = order + 1

        for shape_name in ode_shape_names:
            result["shapes"].append({"type": "ode",
                                     "symbol": shape_name,
                                     "definition": shape_name_to_shape_definition[shape_name],
                                     "initial_values": shape_name_to_initial_values[shape_name]})
"""
        return odetoolbox_indict


    def make_functions_self_contained(self, functions):
        # type: (list(ASTOdeFunction)) -> list(ASTOdeFunction)
        """
        TODO: it should be a method inside of the ASTOdeFunction
        TODO by KP: this should be done by means of a visitor
        Make function definition self contained, e.g. without any references to functions from `functions`.
        :param functions: A sorted list with entries ASTOdeFunction.
        :return: A list with ASTOdeFunctions. Defining expressions don't depend on each other.
        """
        for source in functions:
            source_position = source.get_source_position()
            for target in functions:
                matcher = re.compile(self._variable_matching_template.format(source.get_variable_name()))
                target_definition = str(target.get_expression())
                target_definition = re.sub(matcher, "(" + str(source.get_expression()) + ")", target_definition)
                target.expression = ModelParser.parse_expression(target_definition)

                def log_set_source_position(node):
                    if node.get_source_position().is_added_source_position():
                        node.set_source_position(source_position)

                target.expression.accept(ASTHigherOrderVisitor(visit_funcs=log_set_source_position))

        return functions


    def replace_functions_through_defining_expressions(self, definitions, functions):
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
            source_position = fun.get_source_position()
            for target in definitions:
                matcher = re.compile(self._variable_matching_template.format(fun.get_variable_name()))
                target_definition = str(target.get_rhs())
                target_definition = re.sub(matcher, "(" + str(fun.get_expression()) + ")", target_definition)
                target.rhs = ModelParser.parse_expression(target_definition)

                def log_set_source_position(node):
                    if node.get_source_position().is_added_source_position():
                        node.set_source_position(source_position)

                target.accept(ASTHigherOrderVisitor(visit_funcs=log_set_source_position))
        return definitions


    def transform_functions_json(self, equations_block):
        # type: (ASTEquationsBlock) -> list[dict[str, str]]
        """
        Converts AST node to a JSON representation
        :param equations_block:equations_block
        :return: json mapping: {odes: [...], shape: [...]}
        """
        equations_block = OdeTransformer.refactor_convolve_call(equations_block)
        result = []

        for fun in equations_block.get_functions():
            result.append({"symbol": fun.get_variable_name(),
                           "definition": self._printer.print_expression(fun.get_expression())})

        return result


    def store_transformed_model(self, ast):
        if FrontendConfiguration.store_log:
            with open(str(os.path.join(FrontendConfiguration.get_target_path(), '..', 'report',
                                       ast.get_name())) + '.txt', 'w+') as f:
                f.write(str(ast))
