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

import copy
import json
import datetime
import os
import re
import sympy
from typing import Optional, Union, List, Dict, Mapping
from jinja2 import Environment, FileSystemLoader, TemplateRuntimeError
from odetoolbox import analysis

import pynestml

from pynestml.codegeneration.ast_transformers import add_assignment_to_update_block, add_declarations_to_internals, add_declaration_to_initial_values, declaration_in_initial_values, get_delta_shape_prefactor_expr, is_delta_shape, replace_rhs_variables, replace_rhs_variable, construct_shape_X_spike_buf_name, get_expr_from_shape_var, to_odetb_name, to_odetb_processed_name, get_shape_var_order_from_ode_toolbox_result, get_initial_value_from_odetb_result, variable_in_shapes, is_ode_variable, variable_in_solver, variable_in_neuron_initial_values
from pynestml.codegeneration.codegenerator import CodeGenerator
from pynestml.codegeneration.expressions_pretty_printer import ExpressionsPrettyPrinter
from pynestml.codegeneration.gsl_names_converter import GSLNamesConverter
from pynestml.codegeneration.gsl_reference_converter import GSLReferenceConverter
from pynestml.codegeneration.nestml_reference_converter import NestMLReferenceConverter
from pynestml.codegeneration.ode_toolbox_reference_converter import ODEToolboxReferenceConverter
from pynestml.codegeneration.unitless_expression_printer import UnitlessExpressionPrinter
from pynestml.codegeneration.nest_assignments_helper import NestAssignmentsHelper
from pynestml.codegeneration.nest_declarations_helper import NestDeclarationsHelper
from pynestml.codegeneration.nest_names_converter import NestNamesConverter
from pynestml.codegeneration.nest_printer import NestPrinter
from pynestml.codegeneration.nest_reference_converter import NESTReferenceConverter
from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.meta_model.ast_assignment import ASTAssignment
from pynestml.meta_model.ast_declaration import ASTDeclaration
from pynestml.meta_model.ast_equations_block import ASTEquationsBlock
from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_input_port import ASTInputPort
from pynestml.meta_model.ast_inline_expression import ASTInlineExpression
from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.meta_model.ast_node_factory import ASTNodeFactory
from pynestml.meta_model.ast_ode_shape import ASTOdeShape
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.symbol_table.symbol_table import SymbolTable
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.symbols.symbol import SymbolKind
from pynestml.symbols.variable_symbol import VariableType, VariableSymbol
from pynestml.symbols.variable_symbol import BlockType
from pynestml.utils.ast_utils import ASTUtils
from pynestml.utils.logger import Logger
from pynestml.utils.logger import LoggingLevel
from pynestml.utils.messages import Messages
from pynestml.utils.model_parser import ModelParser
from pynestml.utils.ode_transformer import OdeTransformer
from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor
from pynestml.visitors.ast_higher_order_visitor import ASTHigherOrderVisitor
from pynestml.visitors.ast_random_number_generator_visitor import ASTRandomNumberGeneratorVisitor


class NESTCodeGenerator(CodeGenerator):
    """
    Code generator for a C++ NEST extension module.
    """

    _variable_matching_template = r'(\b)({})(\b)'

    def __init__(self):
        self.analytic_solver = {}
        self.numeric_solver = {}
        # setup the template environment
        def raise_helper(msg):
            raise TemplateRuntimeError(msg)
        env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'resources_nest')))
        env.globals['raise'] = raise_helper
        env.globals["is_delta_shape"] = is_delta_shape
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

    def generate_module_code(self, neurons: List[ASTNeuron]) -> None:
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


    def analyse_transform_neurons(self, neurons: List[ASTNeuron]) -> None:
        """
        Analyse and transform a list of neurons.
        :param neurons: a list of neurons.
        """
        for neuron in neurons:
            code, message = Messages.get_analysing_transforming_neuron(neuron.get_name())
            Logger.log_message(None, code, message, None, LoggingLevel.INFO)
            spike_updates = self.analyse_neuron(neuron)
            neuron.spike_updates = spike_updates
            # now store the transformed model
            self.store_transformed_model(neuron)


    def get_delta_factors_(self, neuron, equations_block):
        """
        For every occurrence of a convolution of the form `x^(n) = a * convolve(shape, inport) + ...` where `shape` is a delta function, add the element `(x^(n), inport) --> a` to the set. 
        """
        delta_factors = {}
        for ode_eq in equations_block.get_ode_equations():
            var = ode_eq.get_lhs()
            expr = ode_eq.get_rhs()
            conv_calls = OdeTransformer.get_convolve_function_calls(expr)
            for conv_call in conv_calls:
                assert len(conv_call.args) == 2, "convolve() function call should have precisely two arguments: shape and spike buffer"
                shape = conv_call.args[0]
                if is_delta_shape(neuron.get_shape_by_name(shape.get_variable().get_name())):
                    inport = conv_call.args[1].get_variable()
                    expr_str = str(expr)
                    sympy_expr = sympy.parsing.sympy_parser.parse_expr(expr_str)
                    sympy_expr = sympy.expand(sympy_expr)
                    sympy_conv_expr = sympy.parsing.sympy_parser.parse_expr(str(conv_call))
                    factor_str = []
                    for term in sympy.Add.make_args(sympy_expr):
                        if term.find(sympy_conv_expr):
                            factor_str.append(str(term.replace(sympy_conv_expr, 1)))
                    factor_str = " + ".join(factor_str)
                    delta_factors[(var, inport)] = factor_str

        return delta_factors


    def generate_shape_buffers_(self, neuron, equations_block):
        """
        For every occurrence of a convolution of the form `convolve(var, spike_buf)`: add the element `(shape, spike_buf)` to the set, with `shape` being the shape that contains variable `var`.
        """

        shape_buffers = set()
        convolve_calls = OdeTransformer.get_convolve_function_calls(equations_block)
        for convolve in convolve_calls:
            el = (convolve.get_args()[0], convolve.get_args()[1])
            sym = convolve.get_args()[0].get_scope().resolve_to_symbol(convolve.get_args()[0].get_variable().name, SymbolKind.VARIABLE)
            if sym is None:
                raise Exception("No initial value(s) defined for shape with variable \"" + convolve.get_args()[0].get_variable().get_complete_name() + "\"")
            if sym.block_type == BlockType.INPUT_BUFFER_SPIKE:
                el = (el[1], el[0])

            # find the corresponding shape object
            var = el[0].get_variable()
            assert not var is None
            shape = neuron.get_shape_by_name(var.get_name())
            assert not shape is None, "In convolution \"convolve(" + str(var.name) + ", " + str(el[1]) + ")\": no shape by name \"" + var.get_name() + "\" found in neuron."

            el = (shape, el[1])
            shape_buffers.add(el)

        return shape_buffers


    def replace_variable_names_in_expressions(self, neuron, solver_dicts):
        """
        Replace all occurrences of variables names in NESTML format (e.g. `g_ex$''`)` with the ode-toolbox formatted variable name (e.g. `g_ex__DOLLAR__d__d`).
        """
        def replace_var(_expr=None):
            if isinstance(_expr, ASTSimpleExpression) and _expr.is_variable():
                var = _expr.get_variable()
                if variable_in_solver(to_odetb_processed_name(var.get_complete_name()), solver_dicts):
                    ast_variable = ASTVariable(to_odetb_processed_name(var.get_complete_name()), differential_order=0)
                    ast_variable.set_source_position(var.get_source_position())
                    _expr.set_variable(ast_variable)

            elif isinstance(_expr, ASTVariable):
                var = _expr
                if variable_in_solver(to_odetb_processed_name(var.get_complete_name()), solver_dicts):
                    var.set_name(to_odetb_processed_name(var.get_complete_name()))
                    var.set_differential_order(0)

        func = lambda x: replace_var(x)

        neuron.accept(ASTHigherOrderVisitor(func))


    def replace_convolve_calls_with_buffers_(self, neuron, equations_block, shape_buffers):
        """
        Replace all occurrences of `convolve(shape[']^n, spike_input_port)` with the corresponding buffer variable, e.g. `g_E__X__spikes_exc[__d]^n` for a shape named `g_E` and a spike input port named `spikes_exc`.
        """

        def replace_function_call_through_var(_expr=None):
            if _expr.is_function_call() and _expr.get_function_call().get_name() == "convolve":
                convolve = _expr.get_function_call()
                el = (convolve.get_args()[0], convolve.get_args()[1])
                sym = convolve.get_args()[0].get_scope().resolve_to_symbol(convolve.get_args()[0].get_variable().name, SymbolKind.VARIABLE)
                if sym.block_type == BlockType.INPUT_BUFFER_SPIKE:
                    el = (el[1], el[0])
                var = el[0].get_variable()
                spike_input_port = el[1].get_variable()
                shape = neuron.get_shape_by_name(var.get_name())

                _expr.set_function_call(None)
                buffer_var = construct_shape_X_spike_buf_name(var.get_name(), spike_input_port, var.get_differential_order() - 1)
                if is_delta_shape(shape):
                    # delta shapes are treated separately, and should be kept out of the dynamics (computing derivates etc.) --> set to zero
                    _expr.set_variable(None)
                    _expr.set_numeric_literal(0)
                else:
                    ast_variable = ASTVariable(buffer_var)
                    ast_variable.set_source_position(_expr.get_source_position())
                    _expr.set_variable(ast_variable)

        func = lambda x: replace_function_call_through_var(x) if isinstance(x, ASTSimpleExpression) else True

        equations_block.accept(ASTHigherOrderVisitor(func))


    def add_timestep_symbol(self, neuron):
        assert neuron.get_initial_value("__h") is None, "\"__h\" is a reserved name, please do not use variables by this name in your NESTML file"
        assert not "__h" in [sym.name for sym in neuron.get_internal_symbols()], "\"__h\" is a reserved name, please do not use variables by this name in your NESTML file"
        neuron.add_to_internal_block(ModelParser.parse_declaration('__h ms = resolution()'), index=0)


    def analyse_neuron(self, neuron: ASTNeuron) -> List[ASTAssignment]:
        """
        Analyse and transform a single neuron.
        :param neuron: a single neuron.
        :return: spike_updates: list of spike updates, see documentation for get_spike_update_expressions() for more information.
        """
        code, message = Messages.get_start_processing_neuron(neuron.get_name())
        Logger.log_message(neuron, code, message, neuron.get_source_position(), LoggingLevel.INFO)

        equations_block = neuron.get_equations_block()

        if equations_block is None:
            return []

        delta_factors = self.get_delta_factors_(neuron, equations_block)
        shape_buffers = self.generate_shape_buffers_(neuron, equations_block)
        self.replace_convolve_calls_with_buffers_(neuron, equations_block, shape_buffers)
        self.make_inline_expressions_self_contained(equations_block.get_inline_expressions())
        self.replace_inline_expressions_through_defining_expressions(equations_block.get_ode_equations(), equations_block.get_inline_expressions())

        analytic_solver, numeric_solver = self.ode_toolbox_analysis(neuron, shape_buffers)
        self.analytic_solver[neuron.get_name()] = analytic_solver
        self.numeric_solver[neuron.get_name()] = numeric_solver
        self.remove_initial_values_for_shapes(neuron)
        shapes = self.remove_shape_definitions_from_equations_block(neuron)
        self.remove_initial_values_for_odes(neuron, [analytic_solver, numeric_solver], shape_buffers, shapes)
        self.remove_ode_definitions_from_equations_block(neuron)
        self.create_initial_values_for_odetb_shapes(neuron, [analytic_solver, numeric_solver], shape_buffers, shapes)
        self.replace_variable_names_in_expressions(neuron, [analytic_solver, numeric_solver])
        self.add_timestep_symbol(neuron)

        if not self.analytic_solver[neuron.get_name()] is None:
            neuron = add_declarations_to_internals(neuron, self.analytic_solver[neuron.get_name()]["propagators"])

        self.update_symbol_table(neuron, shape_buffers)
        spike_updates = self.get_spike_update_expressions(neuron, shape_buffers, [analytic_solver, numeric_solver], delta_factors)

        return spike_updates


    def generate_neuron_code(self, neuron: ASTNeuron) -> None:
        """
        For a handed over neuron, this method generates the corresponding header and implementation file.
        :param neuron: a single neuron object.
        """
        if not os.path.isdir(FrontendConfiguration.get_target_path()):
            os.makedirs(FrontendConfiguration.get_target_path())
        self.generate_model_h_file(neuron)
        self.generate_neuron_cpp_file(neuron)


    def generate_model_h_file(self, neuron: ASTNeuron) -> None:
        """
        For a handed over neuron, this method generates the corresponding header file.
        :param neuron: a single neuron object.
        """
        neuron_h_file = self._template_neuron_h_file.render(self.setup_generation_helpers(neuron))
        with open(str(os.path.join(FrontendConfiguration.get_target_path(), neuron.get_name())) + '.h', 'w+') as f:
            f.write(str(neuron_h_file))


    def generate_neuron_cpp_file(self, neuron: ASTNeuron) -> None:
        """
        For a handed over neuron, this method generates the corresponding implementation file.
        :param neuron: a single neuron object.
        """
        neuron_cpp_file = self._template_neuron_cpp_file.render(self.setup_generation_helpers(neuron))
        with open(str(os.path.join(FrontendConfiguration.get_target_path(), neuron.get_name())) + '.cpp', 'w+') as f:
            f.write(str(neuron_cpp_file))


    def setup_generation_helpers(self, neuron: ASTNeuron) -> Dict:
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

        namespace['PredefinedUnits'] = pynestml.symbols.predefined_units.PredefinedUnits
        namespace['UnitTypeSymbol'] = pynestml.symbols.unit_type_symbol.UnitTypeSymbol

        namespace['initial_values'] = {}
        namespace['uses_analytic_solver'] = neuron.get_name() in self.analytic_solver.keys() \
                                            and not self.analytic_solver[neuron.get_name()] is None
        if namespace['uses_analytic_solver']:
            namespace['analytic_state_variables'] = self.analytic_solver[neuron.get_name()]["state_variables"]
            namespace['analytic_variable_symbols'] = { sym : neuron.get_equations_block().get_scope().resolve_to_symbol(sym, SymbolKind.VARIABLE) for sym in namespace['analytic_state_variables'] }
            namespace['update_expressions'] = {}
            for sym, expr in self.analytic_solver[neuron.get_name()]["initial_values"].items():
                namespace['initial_values'][sym] = expr
            for sym in namespace['analytic_state_variables']:
                expr_str = self.analytic_solver[neuron.get_name()]["update_expressions"][sym]
                expr_ast = ModelParser.parse_expression(expr_str)
                expr_ast.update_scope(neuron.get_equations_blocks().get_scope()) # pretend that update expressions are in "equations" block, which should always be present, as differential equations must have been defined to get here
                expr_ast.accept(ASTSymbolTableVisitor())
                namespace['update_expressions'][sym] = expr_ast

            namespace['propagators'] = self.analytic_solver[neuron.get_name()]["propagators"]

        namespace['uses_numeric_solver'] = neuron.get_name() in self.analytic_solver.keys() \
                                           and not self.numeric_solver[neuron.get_name()] is None
        if namespace['uses_numeric_solver']:
            namespace['numeric_state_variables'] = self.numeric_solver[neuron.get_name()]["state_variables"]
            namespace['numeric_variable_symbols'] = { sym : neuron.get_equations_block().get_scope().resolve_to_symbol(sym, SymbolKind.VARIABLE) for sym in namespace['numeric_state_variables'] }
            assert not any([sym is None for sym in namespace['numeric_variable_symbols'].values()])
            namespace['numeric_update_expressions'] = {}
            for sym, expr in self.numeric_solver[neuron.get_name()]["initial_values"].items():
                namespace['initial_values'][sym] = expr
            for sym in namespace['numeric_state_variables']:
                expr_str = self.numeric_solver[neuron.get_name()]["update_expressions"][sym]
                expr_ast = ModelParser.parse_expression(expr_str)
                expr_ast.update_scope(neuron.get_equations_blocks().get_scope()) # pretend that update expressions are in "equations" block, which should always be present, as differential equations must have been defined to get here
                expr_ast.accept(ASTSymbolTableVisitor())
                namespace['numeric_update_expressions'][sym] = expr_ast

            namespace['useGSL'] = namespace['uses_numeric_solver']
            namespace['names'] = GSLNamesConverter()
            converter = NESTReferenceConverter(True)
            unitless_pretty_printer = UnitlessExpressionPrinter(converter)
            namespace['printer'] = NestPrinter(unitless_pretty_printer)

        namespace["spike_updates"] = neuron.spike_updates

        rng_visitor = ASTRandomNumberGeneratorVisitor()
        neuron.accept(rng_visitor)
        namespace['norm_rng'] = rng_visitor._norm_rng_is_used

        return namespace


    def ode_toolbox_analysis(self, neuron: ASTNeuron, shape_buffers: Mapping[ASTOdeShape, ASTInputPort]):
        """
        Prepare data for ODE-toolbox input format, invoke ODE-toolbox analysis via its API, and return the output.
        """
        assert isinstance(neuron.get_equations_blocks(), ASTEquationsBlock), "only one equation block should be present"

        equations_block = neuron.get_equations_block()

        if len(equations_block.get_ode_shapes()) == 0 and len(equations_block.get_ode_equations()) == 0:
            # no equations defined -> no changes to the neuron
            return None, None

        code, message = Messages.get_neuron_analyzed(neuron.get_name())
        Logger.log_message(neuron, code, message, neuron.get_source_position(), LoggingLevel.INFO)

        parameters_block = neuron.get_parameter_blocks()
        odetoolbox_indict = self.transform_ode_and_shapes_to_json(neuron, parameters_block, shape_buffers)
        odetoolbox_indict["options"] = {}
        odetoolbox_indict["options"]["output_timestep_symbol"] = "__h"
        #solver_result = analysis(odetoolbox_indict, disable_stiffness_check=True, debug=FrontendConfiguration.logging_level=="DEBUG")
        solver_result = analysis(odetoolbox_indict, disable_stiffness_check=True, debug=True)
        analytic_solver = None
        analytic_solvers = [x for x in solver_result if x["solver"] == "analytical"]
        assert len(analytic_solvers) <= 1, "More than one analytic solver not presently supported"
        if len(analytic_solvers) > 0:
            analytic_solver = analytic_solvers[0]

        # if numeric solver is required, generate a stepping function that includes each state variable
        numeric_solver = None
        numeric_solvers = [x for x in solver_result if x["solver"].startswith("numeric")]
        if numeric_solvers:
            solver_result = analysis(odetoolbox_indict, disable_stiffness_check=True, disable_analytic_solver=True, debug=FrontendConfiguration.logging_level=="DEBUG")
            numeric_solvers = [x for x in solver_result if x["solver"].startswith("numeric")]
            assert len(numeric_solvers) <= 1, "More than one numeric solver not presently supported"
            if len(numeric_solvers) > 0:
                numeric_solver = numeric_solvers[0]

        return analytic_solver, numeric_solver


    def update_symbol_table(self, neuron, shape_buffers):
        """
        Update symbol table and scope.
        """
        SymbolTable.delete_neuron_scope(neuron.get_name())
        symbol_table_visitor = ASTSymbolTableVisitor()
        symbol_table_visitor.after_ast_rewrite_ = True
        neuron.accept(symbol_table_visitor)
        SymbolTable.add_neuron_scope(neuron.get_name(), neuron.get_scope())


    def remove_initial_values_for_shapes(self, neuron):
        """
        Remove initial values for original declarations (e.g. g_in, g_in', V_m); these might conflict with the initial value expressions returned from ODE-toolbox.
        """
        assert isinstance(neuron.get_equations_blocks(), ASTEquationsBlock), "only one equation block should be present"

        equations_block = neuron.get_equations_block()
        symbols_to_remove = set()
        for shape in equations_block.get_ode_shapes():
            for shape_var in shape.get_variables():
                shape_var_order = shape_var.get_differential_order()
                for order in range(shape_var_order):
                    symbol_name = shape_var.get_name() + "'" * order
                    symbol = equations_block.get_scope().resolve_to_symbol(symbol_name, SymbolKind.VARIABLE)
                    symbols_to_remove.add(symbol_name)

        decl_to_remove = set()
        for symbol_name in symbols_to_remove:
            for decl in neuron.get_initial_blocks().get_declarations():
                if len(decl.get_variables()) == 1:
                    if decl.get_variables()[0].get_name() == symbol_name:
                        decl_to_remove.add(decl)
                else:
                    for var in decl.get_variables():
                        if var.get_name() == symbol_name:
                            decl.variables.remove(var)

        for decl in decl_to_remove:
            neuron.get_initial_blocks().get_declarations().remove(decl)


    def remove_initial_values_for_odes(self, neuron, solver_dicts, shape_buffers, shapes):
        """
        Remove initial values for original declarations (e.g. g_in, V_m', g_ahp'') before ODE-toolbox processing
        """
        assert isinstance(neuron.get_equations_blocks(), ASTEquationsBlock), "only one equation block should be present"
        equations_block = neuron.get_equations_block()

        #
        #   for each variable that can be matched in the ode-toolbox results dictionary:
        #   - replace the defining expression by the ode-toolbox result
        #   - unmark for deletion
        #

        for iv_decl in neuron.get_initial_blocks().get_declarations():
            for var in iv_decl.get_variables():
                var_name = var.get_complete_name()
                if is_ode_variable(var.get_name(), neuron):
                    assert variable_in_solver(to_odetb_processed_name(var_name), solver_dicts)

                    #
                    #   replace the left-hand side variable name by the ode-toolbox format
                    #

                    var.set_name(to_odetb_processed_name(var.get_complete_name()))
                    var.set_differential_order(0)


                    #
                    #   replace the defining expression by the ode-toolbox result
                    #

                    iv_expr = get_initial_value_from_odetb_result(to_odetb_processed_name(var_name), solver_dicts)
                    assert not iv_expr is None
                    iv_expr = ModelParser.parse_expression(iv_expr)
                    iv_expr.update_scope(neuron.get_initial_blocks().get_scope())
                    iv_decl.set_expression(iv_expr)



    def _get_ast_variable(self, neuron, var_name) -> Optional[ASTVariable]:
        """
        Grab the ASTVariable corresponding to the initial value by this name
        """
        for decl in neuron.get_initial_values_blocks().get_declarations():
            for var in decl.variables:
                if var.get_name() == var_name:
                    return var
        return None


    def create_initial_values_for_odetb_shapes(self, neuron, solver_dicts, shape_buffers, shapes):
        """
        Add the variables used in ODEs from the ode-toolbox result dictionary as ODEs in NESTML AST
        """
        for solver_dict in solver_dicts:
            if solver_dict is None:
                continue
            for var_name in solver_dict["initial_values"].keys():
                if variable_in_shapes(var_name, shapes):
                    assert not declaration_in_initial_values(neuron, var_name)  # original initial value expressions should have been removed to make place for ode-toolbox results


        for solver_dict in solver_dicts:
            if solver_dict is None:
                continue

            for var_name, expr in solver_dict["initial_values"].items():
                # here, overwrite is allowed because initial values might be repeated between numeric and analytic solver
                if variable_in_shapes(var_name, shapes):
                    expr = "0"    # for shapes, "initial value" returned by ode-toolbox is actually the increment value; the actual initial value is assumed to be 0
                    if not declaration_in_initial_values(neuron, var_name):
                        add_declaration_to_initial_values(neuron, var_name, expr)


    def create_initial_values_for_odetb_odes(self, neuron, solver_dicts, shape_buffers, shapes):
        """
        Add the variables used in ODEs from the ode-toolbox result dictionary as ODEs in NESTML AST.
        """
        for solver_dict in solver_dicts:
            if solver_dict is None:
                continue
            for var_name in solver_dict["initial_values"].keys():
                assert not declaration_in_initial_values(neuron, var_name)  # original initial value expressions should have been removed to make place for ode-toolbox results

        for solver_dict in solver_dicts:
            if solver_dict is None:
                continue

            for var_name, expr in solver_dict["initial_values"].items():
                # here, overwrite is allowed because initial values might be repeated between numeric and analytic solver

                if variable_in_shapes(var_name, shapes):
                    expr = "0"    # for shapes, "initial value" returned by ode-toolbox is actually the increment value; the actual initial value is assumed to be 0

                if not declaration_in_initial_values(neuron, var_name):
                    add_declaration_to_initial_values(neuron, var_name, expr)


    def get_spike_update_expressions(self, neuron: ASTNeuron, shape_buffers, solver_dicts, delta_factors) -> List[ASTAssignment]:
        """
        Generate the equations that update the dynamical variables when incoming spikes arrive. To be invoked after ode-toolbox.

        For example, a resulting `assignment_str` could be "I_shape_in += (in_spikes/nS) * 1". The values are taken from the initial values for each corresponding dynamical variable, either from ode-toolbox or directly from user specification in the model.

        Note that for shapes, `initial_values` actually contains the increment upon spike arrival, rather than the initial value of the corresponding ODE dimension.
        """
        spike_updates = []
        initial_values = neuron.get_initial_values_blocks()

        for shape, spike_input_port in shape_buffers:
            if neuron.get_scope().resolve_to_symbol(str(spike_input_port), SymbolKind.VARIABLE) is None:
                continue

            buffer_type = neuron.get_scope().resolve_to_symbol(str(spike_input_port), SymbolKind.VARIABLE).get_type_symbol()

            if is_delta_shape(shape):
                continue

            for shape_var in shape.get_variables():
                for var_order in range(get_shape_var_order_from_ode_toolbox_result(shape_var.get_name(), solver_dicts)):
                    shape_spike_buf_name = construct_shape_X_spike_buf_name(shape_var.get_name(), spike_input_port, var_order)
                    expr = get_initial_value_from_odetb_result(shape_spike_buf_name, solver_dicts)
                    assert not expr is None, "Initial value not found for shape " + shape_var
                    expr = str(expr)
                    if expr in ["0", "0.", "0.0"]:
                        continue    # skip adding the statement if we're only adding zero

                    assignment_str = shape_spike_buf_name + " += "
                    assignment_str += "(" + str(spike_input_port) + ")"
                    if not expr in ["1.", "1.0", "1"]:
                        assignment_str += " * (" + self._printer.print_expression(ModelParser.parse_expression(expr)) + ")"

                    if not buffer_type.print_nestml_type() in ["1.", "1.0", "1"]:
                        assignment_str += " / (" + buffer_type.print_nestml_type() + ")"

                    ast_assignment = ModelParser.parse_assignment(assignment_str)
                    ast_assignment.update_scope(neuron.get_scope())
                    ast_assignment.accept(ASTSymbolTableVisitor())

                    spike_updates.append(ast_assignment)

        for k, factor in delta_factors.items():
            var = k[0]
            inport = k[1]
            assignment_str = var.get_name() + "'" * (var.get_differential_order() - 1) + " += "
            if not factor in ["1.", "1.0", "1"]:
                assignment_str += "(" + self._printer.print_expression(ModelParser.parse_expression(factor)) + ") * "
            assignment_str += str(inport)
            ast_assignment = ModelParser.parse_assignment(assignment_str)
            ast_assignment.update_scope(neuron.get_scope())
            ast_assignment.accept(ASTSymbolTableVisitor())

            spike_updates.append(ast_assignment)

        return spike_updates


    def remove_shape_definitions_from_equations_block(self, neuron):
        """
        Removes all shapes in this block.
        """
        equations_block = neuron.get_equations_block()

        decl_to_remove = set()
        for decl in equations_block.get_declarations():
            if type(decl) is ASTOdeShape:
                decl_to_remove.add(decl)

        for decl in decl_to_remove:
            equations_block.get_declarations().remove(decl)

        return decl_to_remove


    def remove_ode_definitions_from_equations_block(self, neuron):
        """
        Removes all ODEs in this block.
        """
        equations_block = neuron.get_equations_block()

        decl_to_remove = set()
        for decl in equations_block.get_ode_equations():
            decl_to_remove.add(decl)

        for decl in decl_to_remove:
            equations_block.get_declarations().remove(decl)


    def transform_ode_and_shapes_to_json(self, neuron: ASTNeuron, parameters_block, shape_buffers):
        """
        Converts AST node to a JSON representation suitable for passing to ode-toolbox.

        Each shape has to be generated for each spike buffer convolve in which it occurs, e.g. if the NESTML model code contains the statements

            convolve(G, ex_spikes)
            convolve(G, in_spikes)

        then `shape_buffers` will contain the pairs `(G, ex_spikes)` and `(G, in_spikes)`, from which two ODEs will be generated, with dynamical state (variable) names `G__X__ex_spikes` and `G__X__in_spikes`.            

        :param equations_block: ASTEquationsBlock
        :return: Dict
        """
        odetoolbox_indict = {}

        gsl_converter = ODEToolboxReferenceConverter()
        gsl_printer = UnitlessExpressionPrinter(gsl_converter)

        odetoolbox_indict["dynamics"] = []
        equations_block = neuron.get_equations_block()
        for equation in equations_block.get_ode_equations():
            lhs = to_odetb_name(equation.get_lhs().get_complete_name())   # n.b. includes single quotation marks to indicate differential order
            rhs = gsl_printer.print_expression(equation.get_rhs())
            entry = { "expression": lhs + " = " + rhs }
            symbol_name = equation.get_lhs().get_name()
            symbol = equations_block.get_scope().resolve_to_symbol(symbol_name, SymbolKind.VARIABLE)

            entry["initial_values"] = {}
            symbol_order = equation.get_lhs().get_differential_order()
            for order in range(symbol_order):
                iv_symbol_name = symbol_name + "'" * order
                initial_value_expr = neuron.get_initial_value(iv_symbol_name)
                if initial_value_expr:
                    expr = gsl_printer.print_expression(initial_value_expr)
                    entry["initial_values"][to_odetb_name(iv_symbol_name)] = expr
            odetoolbox_indict["dynamics"].append(entry)

        # write a copy for each (shape, spike buffer) combination
        for shape, spike_input_port in shape_buffers:

            if is_delta_shape(shape):
                # delta function -- skip passing this to ode-toolbox
                continue

            for shape_var in shape.get_variables():
                expr = get_expr_from_shape_var(shape, shape_var.get_complete_name())
                shape_order = shape_var.get_differential_order()
                shape_X_spike_buf_name_ticks = construct_shape_X_spike_buf_name(shape_var.get_name(), spike_input_port, shape_order, diff_order_symbol="'")

                replace_rhs_variables(expr, shape_buffers)

                entry = {}
                entry["expression"] = shape_X_spike_buf_name_ticks + " = " + str(expr)

                # initial values need to be declared for order 1 up to shape order (e.g. none for shape function f(t) = ...; 1 for shape ODE f'(t) = ...; 2 for f''(t) = ... and so on)
                entry["initial_values"] = {}
                for order in range(shape_order):
                    iv_sym_name_odetb = construct_shape_X_spike_buf_name(shape_var.get_name(), spike_input_port, order, diff_order_symbol="'")
                    symbol_name_ = shape_var.get_name() + "'" * order
                    symbol = equations_block.get_scope().resolve_to_symbol(symbol_name_, SymbolKind.VARIABLE)
                    assert not symbol is None, "Could not find initial value for variable " + symbol_name_
                    initial_value_expr = symbol.get_declaring_expression()
                    assert not initial_value_expr is None, "No initial value found for variable name " + symbol_name_
                    entry["initial_values"][iv_sym_name_odetb] = gsl_printer.print_expression(initial_value_expr)

                odetoolbox_indict["dynamics"].append(entry)

        odetoolbox_indict["parameters"] = {}
        for decl in parameters_block.get_declarations():
            for var in decl.variables:
                odetoolbox_indict["parameters"][var.get_complete_name()] = gsl_printer.print_expression(decl.get_expression())

        return odetoolbox_indict


    def make_inline_expressions_self_contained(self, inline_expressions: List[ASTInlineExpression]) -> List[ASTInlineExpression]:
        """
        Make inline_expressions self contained, i.e. without any references to other inline_expressions.

        TODO: it should be a method inside of the ASTInlineExpression
        TODO by KP: this should be done by means of a visitor

        :param inline_expressions: A sorted list with entries ASTInlineExpression.
        :return: A list with ASTInlineExpressions. Defining expressions don't depend on each other.
        """
        for source in inline_expressions:
            source_position = source.get_source_position()
            for target in inline_expressions:
                matcher = re.compile(self._variable_matching_template.format(source.get_variable_name()))
                target_definition = str(target.get_expression())
                target_definition = re.sub(matcher, "(" + str(source.get_expression()) + ")", target_definition)
                target.expression = ModelParser.parse_expression(target_definition)
                target.expression.update_scope(source.get_scope())
                target.expression.accept(ASTSymbolTableVisitor())

                def log_set_source_position(node):
                    if node.get_source_position().is_added_source_position():
                        node.set_source_position(source_position)

                target.expression.accept(ASTHigherOrderVisitor(visit_funcs=log_set_source_position))

        return inline_expressions


    def replace_inline_expressions_through_defining_expressions(self, definitions, inline_expressions):
        # type: (list(ASTOdeEquation), list(ASTInlineExpression)) -> list(ASTInlineExpression)
        """
        Refactors symbols from `inline_expressions` in `definitions` with corresponding defining expressions from `inline_expressions`.

        :param definitions: A sorted list with entries {"symbol": "name", "definition": "expression"} that should be made free from.
        :param inline_expressions: A sorted list with entries {"symbol": "name", "definition": "expression"} with inline_expressions which must be replaced in `definitions`.
        :return: A list with definitions. Expressions in `definitions` don't depend on inline_expressions from `inline_expressions`.
        """
        for m in inline_expressions:
            source_position = m.get_source_position()
            for target in definitions:
                matcher = re.compile(self._variable_matching_template.format(m.get_variable_name()))
                target_definition = str(target.get_rhs())
                target_definition = re.sub(matcher, "(" + str(m.get_expression()) + ")", target_definition)
                target.rhs = ModelParser.parse_expression(target_definition)
                target.update_scope(m.get_scope())
                target.accept(ASTSymbolTableVisitor())

                def log_set_source_position(node):
                    if node.get_source_position().is_added_source_position():
                        node.set_source_position(source_position)

                target.accept(ASTHigherOrderVisitor(visit_funcs=log_set_source_position))

        return definitions

    def replace_inline_expressions_through_defining_expressions2(self, solver_dicts, inline_expressions):
        # type: (list(ASTOdeEquation), list(ASTInlineExpression)) -> list(ASTInlineExpression)
        """
        Refactors symbols form `inline_expressions` in `definitions` with corresponding defining expressions from `inline_expressions`.

        :param definitions: A sorted list with entries {"symbol": "name", "definition": "expression"} that should be made
        free from.
        :param inline_expressions: A sorted list with entries {"symbol": "name", "definition": "expression"} with inline_expressions which
        must be replaced in `definitions`.
        :return: A list with definitions. Expressions in `definitions` don't depend on inline_expressions from `inline_expressions`.
        """

        def replace_func_by_def_in_expr(expr, inline_expressions):
            for m in inline_expressions:
                matcher = re.compile(self._variable_matching_template.format(m.get_variable_name()))
                expr = re.sub(matcher, "(" + str(m.get_expression()) + ")", expr)
                target_definition = str(target.get_expression())
                target_definition = re.sub(matcher, "(" + str(source.get_expression()) + ")", target_definition)
                target.expression = ModelParser.parse_expression(target_definition)
                target.expression.update_scope(source.get_scope())
                target.expression.accept(ASTSymbolTableVisitor())

                def log_set_source_position(node):
                    if node.get_source_position().is_added_source_position():
                        node.set_source_position(source_position)

                target.expression.accept(ASTHigherOrderVisitor(visit_funcs=log_set_source_position))

            return expr

        for solver_dict in solver_dicts:
            if solver_dict is None:
                continue

            for var, expr in solver_dict["update_expressions"].items():
                solver_dict["update_expressions"][var] = replace_func_by_def_in_expr(expr, inline_expressions)

            if "propagators" in solver_dict.keys():
                for var, expr in solver_dict["propagators"].items():
                    solver_dict["propagators"][var] = replace_func_by_def_in_expr(expr, inline_expressions)


    def store_transformed_model(self, ast):
        if FrontendConfiguration.store_log:
            with open(str(os.path.join(FrontendConfiguration.get_target_path(), '..', 'report',
                                       ast.get_name())) + '.txt', 'w+') as f:
                f.write(str(ast))
