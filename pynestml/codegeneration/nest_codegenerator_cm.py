# -*- coding: utf-8 -*-
#
# nest_codegenerator.py
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
import glob
import os
import re
from typing import Any, Dict, List, Mapping, Optional, Sequence

from jinja2 import Environment, FileSystemLoader, TemplateRuntimeError, Template
import jinja2.environment
from odetoolbox import analysis
import pynestml
from pynestml.codegeneration.ast_transformers import ASTTransformers
from pynestml.codegeneration.codegenerator import CodeGenerator
from pynestml.codegeneration.expressions_pretty_printer import ExpressionsPrettyPrinter
from pynestml.codegeneration.gsl_names_converter import GSLNamesConverter
from pynestml.codegeneration.gsl_reference_converter import GSLReferenceConverter
from pynestml.codegeneration.nest_assignments_helper import NestAssignmentsHelper
from pynestml.codegeneration.nest_declarations_helper import NestDeclarationsHelper
from pynestml.codegeneration.nest_names_converter import NestNamesConverter
from pynestml.codegeneration.nest_printer import NestPrinter
from pynestml.codegeneration.nest_reference_converter import NESTReferenceConverter
from pynestml.codegeneration.ode_toolbox_reference_converter import ODEToolboxReferenceConverter
from pynestml.codegeneration.pynestml_2_nest_type_converter import PyNestml2NestTypeConverter
from pynestml.codegeneration.unitless_expression_printer import UnitlessExpressionPrinter
from pynestml.exceptions.invalid_path_exception import InvalidPathException
from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.meta_model.ast_assignment import ASTAssignment
from pynestml.meta_model.ast_block_with_variables import ASTBlockWithVariables
from pynestml.meta_model.ast_equations_block import ASTEquationsBlock
from pynestml.meta_model.ast_inline_expression import ASTInlineExpression
from pynestml.meta_model.ast_input_port import ASTInputPort
from pynestml.meta_model.ast_kernel import ASTKernel
from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.meta_model.ast_ode_equation import ASTOdeEquation
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.meta_model.ast_synapse import ASTSynapse
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.symbol_table.symbol_table import SymbolTable
from pynestml.symbols.symbol import SymbolKind
from pynestml.symbols.variable_symbol import BlockType
from pynestml.utils.ast_channel_information_collector import ASTChannelInformationCollector
from pynestml.utils.ast_utils import ASTUtils
from pynestml.utils.chan_info_enricher import ChanInfoEnricher
from pynestml.utils.logger import Logger
from pynestml.utils.logger import LoggingLevel
from pynestml.utils.messages import Messages
from pynestml.utils.model_parser import ModelParser
from pynestml.utils.ode_transformer import OdeTransformer
from pynestml.utils.syns_info_enricher import SynsInfoEnricher
from pynestml.utils.syns_processing import SynsProcessing
from pynestml.visitors.ast_higher_order_visitor import ASTHigherOrderVisitor
from pynestml.visitors.ast_random_number_generator_visitor import ASTRandomNumberGeneratorVisitor
from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor
import sympy


class NESTCodeGeneratorCM(CodeGenerator):
    """
    Code generator for a C++ NEST extension module.

    Options:
    - **neuron_parent_class**: The C++ class from which the generated NESTML neuron class inherits. Examples: ``"ArchivingNode"``, ``"StructuralPlasticityNode"``. Default: ``"ArchivingNode"``.
    - **neuron_parent_class_include**: The C++ header filename to include that contains **neuron_parent_class**. Default: ``"archiving_node.h"``.
    - **preserve_expressions**: Set to True, or a list of strings corresponding to individual variable names, to disable internal rewriting of expressions, and return same output as input expression where possible. Only applies to variables specified as first-order differential equations. (This parameter is passed to ODE-toolbox.)
    - **simplify_expression**: For all expressions ``expr`` that are rewritten by ODE-toolbox: the contents of this parameter string are ``eval()``ed in Python to obtain the final output expression. Override for custom expression simplification steps. Example: ``sympy.simplify(expr)``. Default: ``"sympy.logcombine(sympy.powsimp(sympy.expand(expr)))"``. (This parameter is passed to ODE-toolbox.)
    - **templates**: Path containing jinja templates used to generate code for NEST simulator.
        - **path**: Path containing jinja templates used to generate code for NEST simulator.
        - **model_templates**: A list of the jinja templates or a relative path to a directory containing the templates related to the neuron model(s).
        - **module_templates**: A list of the jinja templates or a relative path to a directory containing the templates related to generating the NEST module.
    """

    _default_options = {
        "neuron_parent_class": "ArchivingNode",
        "neuron_parent_class_include": "archiving_node.h",
        "preserve_expressions": False,
        "simplify_expression": "sympy.logcombine(sympy.powsimp(sympy.expand(expr)))",
        "templates": {
            "path": 'cm_templates',
            "model_templates": [
                'CompartmentCurrentsClass.jinja2',
                'CompartmentCurrentsHeader.jinja2',
                'MainClass.jinja2',
                'MainHeader.jinja2',
                'TreeClass.jinja2',
                'TreeHeader.jinja2'
            ],
            "module_templates": ['setup']
        }
    }

    _variable_matching_template = r'(\b)({})(\b)'
    _model_templates = list()
    _module_templates = list()

    def __init__(self, options: Optional[Mapping[str, Any]] = None):
        super().__init__("NEST_COMPARTMENTAL", options)
        self._printer = ExpressionsPrettyPrinter()
        self.analytic_solver = {}
        self.numeric_solver = {}
        self.non_equations_state_variables = {}  # those state variables not defined as an ODE in the equations block
        self.setup_template_env()
        # maps kernel names to their analytic solutions separately
        # this is needed needed for the cm_syns case
        self.kernel_name_to_analytic_solver = {}

    def raise_helper(self, msg):
        raise TemplateRuntimeError(msg)

    def setup_template_env(self):
        """
        Setup the Jinja2 template environment
        """

        # Get templates path
        templates_root_dir = self.get_option("templates")['path']
        if not os.path.isabs(templates_root_dir):
            # Prefix the default templates location
            templates_root_dir = os.path.join(os.path.dirname(__file__), 'resources_nest', templates_root_dir)
            code, message = Messages.get_template_root_path_created(templates_root_dir)
            Logger.log_message(None, code, message, None, LoggingLevel.INFO)
        if not os.path.isdir(templates_root_dir):
            raise InvalidPathException('Templates path (' + templates_root_dir + ')  is not a directory')

        # Setup models template environment
        model_templates = self.get_option("templates")['model_templates']
        if not model_templates:
            raise Exception('A list of neuron model template files/directories is missing.')
        self._model_templates.extend(self.__setup_template_env(model_templates, templates_root_dir))

        # Setup modules template environment
        module_templates = self.get_option("templates")['module_templates']
        if not module_templates:
            raise Exception('A list of module template files/directories is missing.')
        self._module_templates.extend(self.__setup_template_env(module_templates, templates_root_dir))

    def __setup_template_env(self, template_files: List[str], templates_root_dir: str) -> List[Template]:
        """
        A helper function to setup the jinja2 template environment
        :param template_files: A list of template file names or a directory (relative to ``templates_root_dir``) containing the templates
        :param templates_root_dir: path of the root directory containing all the jinja2 templates
        :return: A list of jinja2 template objects
        """
        _template_files = self._get_abs_template_paths(template_files, templates_root_dir)
        _template_dirs = set([os.path.dirname(_file) for _file in _template_files])

        # Environment for neuron templates
        env = Environment(loader=FileSystemLoader(_template_dirs))
        env.globals['raise'] = self.raise_helper
        env.globals["is_delta_kernel"] = ASTTransformers.is_delta_kernel

        # Load all the templates
        _templates = list()
        for _templ_file in _template_files:
            _templates.append(env.get_template(os.path.basename(_templ_file)))

        return _templates

    def _get_abs_template_paths(self, template_files: List[str], templates_root_dir: str) -> List[str]:
        """
        Resolve the directory paths and get the absolute paths of the jinja templates.
        :param template_files: A list of template file names or a directory (relative to ``templates_root_dir``) containing the templates
        :param templates_root_dir: path of the root directory containing all the jinja2 templates
        :return: A list of absolute paths of the ``template_files``
        """
        _abs_template_paths = list()
        for _path in template_files:
            # Convert from relative to absolute path
            _path = os.path.join(templates_root_dir, _path)
            if os.path.isdir(_path):
                for file in glob.glob(os.path.join(_path, "*.jinja2")):
                    _abs_template_paths.append(os.path.join(_path, file))
            else:
                _abs_template_paths.append(_path)

        return _abs_template_paths

    def generate_code(self, neurons: List[ASTNeuron], synapses: List[ASTSynapse] = None) -> None:
        self.analyse_transform_neurons(neurons)
        self.generate_neurons(neurons)
        self.generate_module_code(neurons)

    def generate_module_code(self, neurons: List[ASTNeuron]) -> None:
        """
        Generates code that is necessary to integrate neuron models into the NEST infrastructure.
        :param neurons: a list of neurons
        :type neurons: list(ASTNeuron)
        """
        namespace = self._get_module_namespace(neurons)
        if not os.path.exists(FrontendConfiguration.get_target_path()):
            os.makedirs(FrontendConfiguration.get_target_path())

        for _module_temp in self._module_templates:
            file_name_parts = os.path.basename(_module_temp.filename).split('.')
            file_extension = file_name_parts[-2]
            if file_extension in ['cpp', 'h']:
                filename = FrontendConfiguration.get_module_name()
            else:
                filename = file_name_parts[0]

            file_path = str(os.path.join(FrontendConfiguration.get_target_path(), filename))
            with open(file_path + '.' + file_extension, 'w+') as f:
                f.write(str(_module_temp.render(namespace)))

        code, message = Messages.get_module_generated(FrontendConfiguration.get_target_path())
        Logger.log_message(None, code, message, None, LoggingLevel.INFO)

    def _get_module_namespace(self, neurons: List[ASTNeuron]) -> Dict:
        """
        Creates a namespace for generating NEST extension module code
        :param neurons: List of neurons
        :return: a context dictionary for rendering templates
        """
        namespace = {'neurons': neurons,
                     'moduleName': FrontendConfiguration.get_module_name(),
                     'now': datetime.datetime.utcnow()}

        # neuron specific file names in compartmental case
        neuron_name_to_filename = dict()
        for neuron in neurons:
            neuron_name_to_filename[neuron.get_name()] = {
                "compartmentcurrents": self.get_cm_syns_compartmentcurrents_file_prefix(neuron),
                "main": self.get_cm_syns_main_file_prefix(neuron),
                "tree": self.get_cm_syns_tree_file_prefix(neuron)
            }
        namespace['perNeuronFileNamesCm'] = neuron_name_to_filename

        # compartmental case files that are not neuron specific - currently empty
        namespace['sharedFileNamesCmSyns'] = {
        }

        return namespace

    def get_cm_syns_compartmentcurrents_file_prefix(self, neuron):
        return "cm_compartmentcurrents_" + neuron.get_name()

    def get_cm_syns_main_file_prefix(self, neuron):
        return "cm_main_" + neuron.get_name()

    def get_cm_syns_tree_file_prefix(self, neuron):
        return "cm_tree_" + neuron.get_name()

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
        r"""
        For every occurrence of a convolution of the form `x^(n) = a * convolve(kernel, inport) + ...` where `kernel` is a delta function, add the element `(x^(n), inport) --> a` to the set.
        """
        delta_factors = {}
        for ode_eq in equations_block.get_ode_equations():
            var = ode_eq.get_lhs()
            expr = ode_eq.get_rhs()
            conv_calls = OdeTransformer.get_convolve_function_calls(expr)
            for conv_call in conv_calls:
                assert len(
                    conv_call.args) == 2, "convolve() function call should have precisely two arguments: kernel and spike input port"
                kernel = conv_call.args[0]
                if ASTTransformers.is_delta_kernel(neuron.get_kernel_by_name(kernel.get_variable().get_name())):
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

    def generate_kernel_buffers_(self, neuron, equations_block):
        """
        For every occurrence of a convolution of the form `convolve(var, spike_buf)`: add the element `(kernel, spike_buf)` to the set, with `kernel` being the kernel that contains variable `var`.
        """

        kernel_buffers = set()
        convolve_calls = OdeTransformer.get_convolve_function_calls(equations_block)
        for convolve in convolve_calls:
            el = (convolve.get_args()[0], convolve.get_args()[1])
            sym = convolve.get_args()[0].get_scope().resolve_to_symbol(
                convolve.get_args()[0].get_variable().name, SymbolKind.VARIABLE)
            if sym is None:
                raise Exception("No initial value(s) defined for kernel with variable \""
                                + convolve.get_args()[0].get_variable().get_complete_name() + "\"")
            if sym.block_type == BlockType.INPUT:
                # swap the order
                el = (el[1], el[0])

            # find the corresponding kernel object
            var = el[0].get_variable()
            assert var is not None
            kernel = neuron.get_kernel_by_name(var.get_name())
            assert kernel is not None, "In convolution \"convolve(" + str(var.name) + ", " + str(
                el[1]) + ")\": no kernel by name \"" + var.get_name() + "\" found in neuron."

            el = (kernel, el[1])
            kernel_buffers.add(el)

        return kernel_buffers

    def replace_convolution_aliasing_inlines(self, neuron):
        """
        Replace all occurrences of kernel names
        (e.g. ``I_dend`` and ``I_dend'``
        for a definition involving a second-order kernel
        `inline kernel I_dend = convolve(kern_name, spike_buf)``)
        with the ODE-toolbox generated variable ``kern_name__X__spike_buf``.
        """

        def replace_var(_expr, replace_var_name: str, replace_with_var_name: str):
            if isinstance(_expr, ASTSimpleExpression) and _expr.is_variable():
                var = _expr.get_variable()
                if var.get_name() == replace_var_name:
                    ast_variable = ASTVariable(replace_with_var_name + '__d' * var.get_differential_order(),
                                               differential_order=0)
                    ast_variable.set_source_position(var.get_source_position())
                    _expr.set_variable(ast_variable)

            elif isinstance(_expr, ASTVariable):
                var = _expr
                if var.get_name() == replace_var_name:
                    var.set_name(replace_with_var_name + '__d' * var.get_differential_order())
                    var.set_differential_order(0)

        for decl in neuron.get_equations_block().get_declarations():
            from pynestml.utils.ast_utils import ASTUtils
            if isinstance(decl, ASTInlineExpression) \
                    and isinstance(decl.get_expression(), ASTSimpleExpression) \
                    and '__X__' in str(decl.get_expression()):
                replace_with_var_name = decl.get_expression().get_variable().get_name()
                neuron.accept(
                    ASTHigherOrderVisitor(lambda x: replace_var(x, decl.get_variable_name(), replace_with_var_name)))

    def create_ode_indict(self, neuron: ASTNeuron, parameters_block: ASTBlockWithVariables,
                          kernel_buffers: Mapping[ASTKernel, ASTInputPort]):
        odetoolbox_indict = self.transform_ode_and_kernels_to_json(neuron, parameters_block, kernel_buffers)
        odetoolbox_indict["options"] = {}
        odetoolbox_indict["options"]["output_timestep_symbol"] = "__h"
        return odetoolbox_indict

    def ode_solve_analytically(self, neuron: ASTNeuron, parameters_block: ASTBlockWithVariables,
                               kernel_buffers: Mapping[ASTKernel, ASTInputPort]):
        odetoolbox_indict = self.create_ode_indict(neuron, parameters_block, kernel_buffers)
        full_solver_result = analysis(odetoolbox_indict,
                                      disable_stiffness_check=True,
                                      preserve_expressions=self.get_option('preserve_expressions'),
                                      simplify_expression=self.get_option('simplify_expression'),
                                      log_level=FrontendConfiguration.logging_level)
        analytic_solver = None
        analytic_solvers = [x for x in full_solver_result if x["solver"] == "analytical"]
        assert len(analytic_solvers) <= 1, "More than one analytic solver not presently supported"
        if len(analytic_solvers) > 0:
            analytic_solver = analytic_solvers[0]

        return full_solver_result, analytic_solver

    def ode_toolbox_anaysis_cm_syns(self, neuron: ASTNeuron, kernel_buffers: Mapping[ASTKernel, ASTInputPort]):
        """
        Prepare data for ODE-toolbox input format, invoke ODE-toolbox analysis via its API, and return the output.
        """
        assert isinstance(neuron.get_equations_blocks(), ASTEquationsBlock), "only one equation block should be present"

        equations_block = neuron.get_equations_block()

        if len(equations_block.get_kernels()) == 0 and len(equations_block.get_ode_equations()) == 0:
            # no equations defined -> no changes to the neuron
            return None, None

        code, message = Messages.get_neuron_analyzed(neuron.get_name())
        Logger.log_message(neuron, code, message, neuron.get_source_position(), LoggingLevel.INFO)

        parameters_block = neuron.get_parameter_blocks()

        kernel_name_to_analytic_solver = dict()
        for kernel_buffer in kernel_buffers:
            _, analytic_result = self.ode_solve_analytically(neuron, parameters_block, set([tuple(kernel_buffer)]))
            kernel_name = kernel_buffer[0].get_variables()[0].get_name()
            kernel_name_to_analytic_solver[kernel_name] = analytic_result

        return kernel_name_to_analytic_solver

    def ode_toolbox_analysis(self, neuron: ASTNeuron, kernel_buffers: Mapping[ASTKernel, ASTInputPort]):
        """
        Prepare data for ODE-toolbox input format, invoke ODE-toolbox analysis via its API, and return the output.
        """
        assert isinstance(neuron.get_equations_blocks(), ASTEquationsBlock), "only one equation block should be present"

        equations_block = neuron.get_equations_block()

        if len(equations_block.get_kernels()) == 0 and len(equations_block.get_ode_equations()) == 0:
            # no equations defined -> no changes to the neuron
            return None, None

        code, message = Messages.get_neuron_analyzed(neuron.get_name())
        Logger.log_message(neuron, code, message, neuron.get_source_position(), LoggingLevel.INFO)

        parameters_block = neuron.get_parameter_blocks()

        solver_result, analytic_solver = self.ode_solve_analytically(neuron, parameters_block, kernel_buffers)

        # if numeric solver is required, generate a stepping function that includes each state variable
        numeric_solver = None
        numeric_solvers = [x for x in solver_result if x["solver"].startswith("numeric")]

        if numeric_solvers:
            odetoolbox_indict = self.create_ode_indict(neuron, parameters_block, kernel_buffers)
            solver_result = analysis(odetoolbox_indict,
                                     disable_stiffness_check=True,
                                     disable_analytic_solver=True,
                                     preserve_expressions=self.get_option('preserve_expressions'),
                                     simplify_expression=self.get_option('simplify_expression'),
                                     log_level=FrontendConfiguration.logging_level)
            numeric_solvers = [x for x in solver_result if x["solver"].startswith("numeric")]
            assert len(numeric_solvers) <= 1, "More than one numeric solver not presently supported"
            if len(numeric_solvers) > 0:
                numeric_solver = numeric_solvers[0]

        return analytic_solver, numeric_solver

    def find_non_equations_state_variables(self, neuron: ASTNeuron):
        non_equations_state_variables = []
        for decl in neuron.get_state_blocks().get_declarations():
            for var in decl.get_variables():
                # check if this variable is not in equations

                # if there is no equations, all variables are not in equations
                if not neuron.get_equations_blocks():
                    non_equations_state_variables.append(var)
                    continue

                    # check if equation name is also a state variable
                used_in_eq = False
                for ode_eq in neuron.get_equations_blocks().get_ode_equations():
                    if ode_eq.get_lhs().get_name() == var.get_name():
                        used_in_eq = True
                        break

                # check for any state variables being used by a kernel
                for kern in neuron.get_equations_blocks().get_kernels():
                    for kern_var in kern.get_variables():
                        if kern_var.get_name() == var.get_name():
                            used_in_eq = True
                            break

                # if no usage found at this point, we have a non-equation state variable
                if not used_in_eq:
                    non_equations_state_variables.append(var)
        return non_equations_state_variables

    def replace_variable_names_in_expressions(self, neuron, solver_dicts):
        """
        Replace all occurrences of variables names in NESTML format (e.g. `g_ex$''`)` with the ode-toolbox formatted
        variable name (e.g. `g_ex__DOLLAR__d__d`).

        Variables aliasing convolutions should already have been covered by replace_convolution_aliasing_inlines().
        """

        def replace_var(_expr=None):
            if isinstance(_expr, ASTSimpleExpression) and _expr.is_variable():
                var = _expr.get_variable()
                if ASTTransformers.variable_in_solver(ASTTransformers.to_ode_toolbox_processed_name(var.get_complete_name()), solver_dicts):
                    ast_variable = ASTVariable(ASTTransformers.to_ode_toolbox_processed_name(
                        var.get_complete_name()), differential_order=0)
                    ast_variable.set_source_position(var.get_source_position())
                    _expr.set_variable(ast_variable)

            elif isinstance(_expr, ASTVariable):
                var = _expr
                if ASTTransformers.variable_in_solver(ASTTransformers.to_ode_toolbox_processed_name(var.get_complete_name()), solver_dicts):
                    var.set_name(ASTTransformers.to_ode_toolbox_processed_name(var.get_complete_name()))
                    var.set_differential_order(0)

        def func(x):
            return replace_var(x)

        neuron.accept(ASTHigherOrderVisitor(func))

    def replace_convolve_calls_with_buffers_(self, neuron, equations_block, kernel_buffers):
        r"""
        Replace all occurrences of `convolve(kernel[']^n, spike_input_port)` with the corresponding buffer variable, e.g. `g_E__X__spikes_exc[__d]^n` for a kernel named `g_E` and a spike input port named `spikes_exc`.
        """

        def replace_function_call_through_var(_expr=None):
            if _expr.is_function_call() and _expr.get_function_call().get_name() == "convolve":
                convolve = _expr.get_function_call()
                el = (convolve.get_args()[0], convolve.get_args()[1])
                sym = convolve.get_args()[0].get_scope().resolve_to_symbol(
                    convolve.get_args()[0].get_variable().name, SymbolKind.VARIABLE)
                if sym.block_type == BlockType.INPUT:
                    # swap elements
                    el = (el[1], el[0])
                var = el[0].get_variable()
                spike_input_port = el[1].get_variable()
                kernel = neuron.get_kernel_by_name(var.get_name())

                _expr.set_function_call(None)
                buffer_var = ASTTransformers.construct_kernel_X_spike_buf_name(
                    var.get_name(), spike_input_port, var.get_differential_order() - 1)
                if ASTTransformers.is_delta_kernel(kernel):
                    # delta kernels are treated separately, and should be kept out of the dynamics (computing derivates etc.) --> set to zero
                    _expr.set_variable(None)
                    _expr.set_numeric_literal(0)
                else:
                    ast_variable = ASTVariable(buffer_var)
                    ast_variable.set_source_position(_expr.get_source_position())
                    _expr.set_variable(ast_variable)

        def func(x):
            return replace_function_call_through_var(x) if isinstance(x, ASTSimpleExpression) else True

        equations_block.accept(ASTHigherOrderVisitor(func))

    def add_timestep_symbol(self, neuron):
        assert neuron.get_initial_value(
            "__h") is None, "\"__h\" is a reserved name, please do not use variables by this name in your NESTML file"
        assert not "__h" in [sym.name for sym in neuron.get_internal_symbols(
        )], "\"__h\" is a reserved name, please do not use variables by this name in your NESTML file"
        neuron.add_to_internal_block(ModelParser.parse_declaration('__h ms = resolution()'), index=0)

    def analyse_neuron(self, neuron: ASTNeuron) -> List[ASTAssignment]:
        """
        Analyse and transform a single neuron.
        :param neuron: a single neuron.
        :return: spike_updates: list of spike updates, see documentation for get_spike_update_expressions() for more information.
        """
        # code, message = Messages.get_start_processing_neuron(neuron.get_name())
        # Logger.log_message(neuron, code, message, neuron.get_source_position(), LoggingLevel.INFO)
        code, message = Messages.get_start_processing_model(neuron.get_name())
        Logger.log_message(neuron, code, message, neuron.get_source_position(), LoggingLevel.INFO)

        equations_block = neuron.get_equations_block()

        if equations_block is None:
            # add all declared state variables as none of them are used in equations block
            self.non_equations_state_variables[neuron.get_name()] = []
            self.non_equations_state_variables[neuron.get_name()].extend(
                ASTUtils.all_variables_defined_in_block(neuron.get_state_blocks()))

            return []

        # goes through all convolve() inside ode's from equations block
        # if they have delta kernels, use sympy to expand the expression, then
        # find the convolve calls and replace them with constant value 1
        # then return every subexpression that had that convolve() replaced
        delta_factors = self.get_delta_factors_(neuron, equations_block)

        # goes through all convolve() inside equations block
        # extracts what kernel is paired with what spike buffer
        # returns pairs (kernel, spike_buffer)
        kernel_buffers = self.generate_kernel_buffers_(neuron, equations_block)

        # replace convolve(g_E, spikes_exc) with g_E__X__spikes_exc[__d]
        # done by searching for every ASTSimpleExpression inside equations_block
        # which is a convolve call and substituting that call with
        # newly created ASTVariable kernel__X__spike_buffer
        self.replace_convolve_calls_with_buffers_(neuron, equations_block, kernel_buffers)

        # substitute inline expressions with each other
        # such that no inline expression references another inline expression
        self.make_inline_expressions_self_contained(equations_block.get_inline_expressions())

        # dereference inline_expressions inside ode equations
        self.replace_inline_expressions_through_defining_expressions(
            equations_block.get_ode_equations(), equations_block.get_inline_expressions())

        # generate update expressions using ode toolbox
        # for each equation in the equation block attempt to solve analytically
        # then attempt to solve numerically
        # "update_expressions" key in those solvers contains a mapping
        # {expression1: update_expression1, expression2: update_expression2}
        analytic_solver, numeric_solver = self.ode_toolbox_analysis(neuron, kernel_buffers)

        # separate analytic solutions by kernel
        # this is is needed for the synaptic case
        self.kernel_name_to_analytic_solver[neuron.get_name()] = self.ode_toolbox_anaysis_cm_syns(neuron,
                                                                                                  kernel_buffers)
        self.analytic_solver[neuron.get_name()] = analytic_solver
        self.numeric_solver[neuron.get_name()] = numeric_solver

        # get all variables from state block that are not found in equations
        self.non_equations_state_variables[neuron.get_name()] = \
            self.find_non_equations_state_variables(neuron)

        # gather all variables used by kernels and delete their declarations
        # they will be inserted later again, but this time with values redefined
        # by odetoolbox, higher order variables don't get deleted here
        self.remove_initial_values_for_kernels(neuron)

        # delete all kernels as they are all converted into buffers
        # and corresponding update formulas calculated by odetoolbox
        # Remember them in a variable though
        kernels = self.remove_kernel_definitions_from_equations_block(neuron)

        # Every ODE variable (a variable of order > 0) is renamed according to ODE-toolbox conventions
        # their initial values are replaced by expressions suggested by ODE-toolbox.
        # Differential order can now be set to 0, becase they can directly represent the value of the derivative now.
        # initial value can be the same value as the originally stated one but it doesn't have to be
        self.update_initial_values_for_odes(neuron, [analytic_solver, numeric_solver], kernels)

        # remove differential equations from equations block
        # those are now resolved into zero order variables and their corresponding updates
        self.remove_ode_definitions_from_equations_block(neuron)

        # restore state variables that were referenced by kernels
        # and set their initial values by those suggested by ODE-toolbox
        self.create_initial_values_for_kernels(neuron, [analytic_solver, numeric_solver], kernels)

        # Inside all remaining expressions, translate all remaining variable names
        # according to the naming conventions of ODE-toolbox.
        self.replace_variable_names_in_expressions(neuron, [analytic_solver, numeric_solver])

        # find all inline kernels defined as ASTSimpleExpression
        # that have a single kernel convolution aliasing variable ('__X__')
        # translate all remaining variable names according to the naming conventions of ODE-toolbox
        self.replace_convolution_aliasing_inlines(neuron)

        # add variable __h to internals block
        self.add_timestep_symbol(neuron)

        # add propagator variables calculated by odetoolbox into internal blocks
        if self.analytic_solver[neuron.get_name()] is not None:
            neuron = ASTTransformers.add_declarations_to_internals(neuron, self.analytic_solver[neuron.get_name()]["propagators"])

        # generate how to calculate the next spike update
        self.update_symbol_table(neuron, kernel_buffers)
        # find any spike update expressions defined by the user
        spike_updates = self.get_spike_update_expressions(
            neuron, kernel_buffers, [analytic_solver, numeric_solver], delta_factors)

        return spike_updates
    
    def compute_name_of_generated_file(self, jinja_file_name, neuron):
        file_name_no_extension = os.path.basename(jinja_file_name).split(".")[0]
        
        file_name_calculators = {
            "CompartmentCurrents": self.get_cm_syns_compartmentcurrents_file_prefix,
            "Tree":  self.get_cm_syns_tree_file_prefix,
            "Main": self.get_cm_syns_main_file_prefix,
            }

        def compute_prefix (file_name):
            for indication, file_prefix_calculator in file_name_calculators.items():
                if file_name.lower().startswith(indication.lower()):
                    return file_prefix_calculator(neuron)
            return file_name_no_extension.lower() + "_" + neuron.get_name()
        
        file_extension = ''
        if file_name_no_extension.lower().endswith("class"):
            file_extension = "cpp"
        elif file_name_no_extension.lower().endswith("header"):
            file_extension = "h"
        else:
            file_extension = "unknown"
        
        return str(os.path.join(FrontendConfiguration.get_target_path(),
                                       compute_prefix(file_name_no_extension))) + '.' + file_extension
        

    def generate_neuron_code(self, neuron: ASTNeuron) -> None:
        """
        For a handed over neuron, this method generates the corresponding header and implementation file.
        :param neuron: a single neuron object.
        """
        if not os.path.isdir(FrontendConfiguration.get_target_path()):
            os.makedirs(FrontendConfiguration.get_target_path())
            
        for _model_temp in self._model_templates:
            _file = _model_temp.render(self._get_model_namespace(neuron))
            _generated_file = self.compute_name_of_generated_file(_model_temp.filename, neuron)
            print ("generated file: " + _generated_file)
            with open(_generated_file, 'w+') as f:
                f.write(str(_file))

    def getUniqueSuffix(self, neuron: ASTNeuron):
        ret = neuron.get_name().capitalize()
        underscore_pos = ret.find("_")
        while underscore_pos != -1:
            ret = ret[:underscore_pos] + ret[underscore_pos+1:].capitalize()
            underscore_pos = ret.find("_")
        return ret

    def _get_model_namespace(self, neuron: ASTNeuron) -> Dict:
        """
        Returns a standard namespace for generating neuron code for NEST
        :param neuron: a single neuron instance
        :return: a context dictionary for rendering templates
        :rtype: dict
        """
        gsl_converter = GSLReferenceConverter()
        gsl_printer = UnitlessExpressionPrinter(gsl_converter)
        # helper classes and objects
        converter = NESTReferenceConverter(False)
        unitless_pretty_printer = UnitlessExpressionPrinter(converter)

        namespace = dict()

        namespace['neuronName'] = neuron.get_name()
        namespace['type_converter'] = PyNestml2NestTypeConverter()
        namespace['neuron'] = neuron
        namespace['moduleName'] = FrontendConfiguration.get_module_name()
        namespace['printer'] = NestPrinter(unitless_pretty_printer)
        namespace['assignments'] = NestAssignmentsHelper()
        namespace['names'] = NestNamesConverter()
        namespace['declarations'] = NestDeclarationsHelper()
        namespace['utils'] = ASTUtils()
        namespace['idemPrinter'] = UnitlessExpressionPrinter()
        namespace['outputEvent'] = namespace['printer'].print_output_event(neuron.get_body())
        namespace['has_spike_input'] = ASTUtils.has_spike_input(neuron.get_body())
        namespace['has_continuous_input'] = ASTUtils.has_continuous_input(neuron.get_body())
        namespace['odeTransformer'] = OdeTransformer()
        namespace['printerGSL'] = gsl_printer
        namespace['now'] = datetime.datetime.utcnow()
        namespace['tracing'] = FrontendConfiguration.is_dev

        namespace['neuron_parent_class'] = self.get_option('neuron_parent_class')
        namespace['neuron_parent_class_include'] = self.get_option('neuron_parent_class_include')

        namespace['PredefinedUnits'] = pynestml.symbols.predefined_units.PredefinedUnits
        namespace['UnitTypeSymbol'] = pynestml.symbols.unit_type_symbol.UnitTypeSymbol
        namespace['SymbolKind'] = pynestml.symbols.symbol.SymbolKind

        namespace['initial_values'] = {}
        namespace['uses_analytic_solver'] = neuron.get_name() in self.analytic_solver.keys() \
            and self.analytic_solver[neuron.get_name()] is not None
        if namespace['uses_analytic_solver']:
            namespace['analytic_state_variables'] = self.analytic_solver[neuron.get_name()]["state_variables"]
            namespace['analytic_variable_symbols'] = {sym: neuron.get_equations_block().get_scope().resolve_to_symbol(
                sym, SymbolKind.VARIABLE) for sym in namespace['analytic_state_variables']}
            namespace['update_expressions'] = {}
            for sym, expr in self.analytic_solver[neuron.get_name()]["initial_values"].items():
                namespace['initial_values'][sym] = expr
            for sym in namespace['analytic_state_variables']:
                expr_str = self.analytic_solver[neuron.get_name()]["update_expressions"][sym]
                expr_ast = ModelParser.parse_expression(expr_str)
                # pretend that update expressions are in "equations" block, which should always be present, as differential equations must have been defined to get here
                expr_ast.update_scope(neuron.get_equations_blocks().get_scope())
                expr_ast.accept(ASTSymbolTableVisitor())
                namespace['update_expressions'][sym] = expr_ast

            namespace['propagators'] = self.analytic_solver[neuron.get_name()]["propagators"]

        # convert variables from ASTVariable instances to strings
        _names = self.non_equations_state_variables[neuron.get_name()]
        _names = [ASTTransformers.to_ode_toolbox_processed_name(var.get_complete_name()) for var in _names]
        namespace['non_equations_state_variables'] = _names

        namespace['uses_numeric_solver'] = neuron.get_name() in self.numeric_solver.keys() \
            and self.numeric_solver[neuron.get_name()] is not None
        if namespace['uses_numeric_solver']:
            namespace['numeric_state_variables'] = self.numeric_solver[neuron.get_name()]["state_variables"]
            namespace['numeric_variable_symbols'] = {sym: neuron.get_equations_block().get_scope().resolve_to_symbol(
                sym, SymbolKind.VARIABLE) for sym in namespace['numeric_state_variables']}
            assert not any([sym is None for sym in namespace['numeric_variable_symbols'].values()])
            namespace['numeric_update_expressions'] = {}
            for sym, expr in self.numeric_solver[neuron.get_name()]["initial_values"].items():
                namespace['initial_values'][sym] = expr
            for sym in namespace['numeric_state_variables']:
                expr_str = self.numeric_solver[neuron.get_name()]["update_expressions"][sym]
                expr_ast = ModelParser.parse_expression(expr_str)
                # pretend that update expressions are in "equations" block, which should always be present, as differential equations must have been defined to get here
                expr_ast.update_scope(neuron.get_equations_blocks().get_scope())
                expr_ast.accept(ASTSymbolTableVisitor())
                namespace['numeric_update_expressions'][sym] = expr_ast

            namespace['useGSL'] = namespace['uses_numeric_solver']
            namespace['names'] = GSLNamesConverter()
            converter = NESTReferenceConverter(True)
            unitless_pretty_printer = UnitlessExpressionPrinter(converter)
            namespace['printer'] = NestPrinter(unitless_pretty_printer)

        namespace["spike_updates"] = neuron.spike_updates

        namespace["recordable_state_variables"] = [sym for sym in neuron.get_state_symbols() if
                                                   namespace['declarations'].get_domain_from_type(
                                                       sym.get_type_symbol()) == "double" and sym.is_recordable and not ASTTransformers.is_delta_kernel(
                                                       neuron.get_kernel_by_name(sym.name))]
        namespace["recordable_inline_expressions"] = [sym for sym in neuron.get_inline_expression_symbols() if
                                                      namespace['declarations'].get_domain_from_type(
                                                          sym.get_type_symbol()) == "double" and sym.is_recordable]

        # parameter symbols with initial values
        namespace["parameter_syms_with_iv"] = [sym for sym in neuron.get_parameter_symbols() if
                                               sym.has_declaring_expression() and (
                                                   not neuron.get_kernel_by_name(sym.name))]

        rng_visitor = ASTRandomNumberGeneratorVisitor()
        neuron.accept(rng_visitor)
        namespace['norm_rng'] = rng_visitor._norm_rng_is_used

        namespace['cm_unique_suffix'] = self.getUniqueSuffix(neuron)
        namespace['chan_info'] = ASTChannelInformationCollector.get_chan_info(neuron)
        namespace['chan_info'] = ChanInfoEnricher.enrich_with_additional_info(neuron, namespace['chan_info'])

        namespace['syns_info'] = SynsProcessing.get_syns_info(neuron)
        syns_info_enricher = SynsInfoEnricher(neuron)
        namespace['syns_info'] = syns_info_enricher.enrich_with_additional_info(neuron, namespace['syns_info'],
                                                                                self.kernel_name_to_analytic_solver)

        # maybe log this on DEBUG?
        # print("syns_info: ")
        # syns_info_enricher.prettyPrint(namespace['syns_info'])
        # print("chan_info: ")
        # syns_info_enricher.prettyPrint(namespace['chan_info'])

        neuron_specific_filenames = {
            "compartmentcurrents": self.get_cm_syns_compartmentcurrents_file_prefix(neuron),
            "main": self.get_cm_syns_main_file_prefix(neuron),
            "tree": self.get_cm_syns_tree_file_prefix(neuron)
        }

        namespace['neuronSpecificFileNamesCmSyns'] = neuron_specific_filenames

        # there is no shared files any more
        namespace['sharedFileNamesCmSyns'] = {
        }

        return namespace

    def update_symbol_table(self, neuron, kernel_buffers):
        """
        Update symbol table and scope.
        """
        SymbolTable.delete_neuron_scope(neuron.get_name())
        symbol_table_visitor = ASTSymbolTableVisitor()
        symbol_table_visitor.after_ast_rewrite_ = True
        neuron.accept(symbol_table_visitor)
        SymbolTable.add_neuron_scope(neuron.get_name(), neuron.get_scope())

    def remove_initial_values_for_kernels(self, neuron):
        """
        Remove initial values for original declarations (e.g. g_in, g_in', V_m); these might conflict with the initial value expressions returned from ODE-toolbox.
        """
        assert isinstance(neuron.get_equations_blocks(), ASTEquationsBlock), "only one equation block should be present"

        equations_block = neuron.get_equations_block()
        symbols_to_remove = set()
        for kernel in equations_block.get_kernels():
            for kernel_var in kernel.get_variables():
                kernel_var_order = kernel_var.get_differential_order()
                for order in range(kernel_var_order):
                    symbol_name = kernel_var.get_name() + "'" * order
                    symbols_to_remove.add(symbol_name)

        decl_to_remove = set()
        for symbol_name in symbols_to_remove:
            for decl in neuron.get_state_blocks().get_declarations():
                if len(decl.get_variables()) == 1:
                    if decl.get_variables()[0].get_name() == symbol_name:
                        decl_to_remove.add(decl)
                else:
                    for var in decl.get_variables():
                        if var.get_name() == symbol_name:
                            decl.variables.remove(var)

        for decl in decl_to_remove:
            neuron.get_state_blocks().get_declarations().remove(decl)

    def update_initial_values_for_odes(self, neuron, solver_dicts, kernels) -> None:
        """
        Update initial values for original ODE declarations (e.g. g_in, V_m', g_ahp'') that are present in the model
        before ODE-toolbox processing, with the formatted variable names and initial values returned by ODE-toolbox.
        """
        assert isinstance(neuron.get_equations_blocks(), ASTEquationsBlock), "only one equation block should be present"

        if neuron.get_state_blocks() is None:
            return

        for iv_decl in neuron.get_state_blocks().get_declarations():
            for var in iv_decl.get_variables():
                var_name = var.get_complete_name()
                if ASTTransformers.is_ode_variable(var.get_name(), neuron):
                    assert ASTTransformers.variable_in_solver(ASTTransformers.to_ode_toolbox_processed_name(var_name), solver_dicts)

                    # replace the left-hand side variable name by the ode-toolbox format
                    var.set_name(ASTTransformers.to_ode_toolbox_processed_name(var.get_complete_name()))
                    var.set_differential_order(0)

                    # replace the defining expression by the ode-toolbox result
                    iv_expr = ASTTransformers.get_initial_value_from_ode_toolbox_result(
                        ASTTransformers.to_ode_toolbox_processed_name(var_name), solver_dicts)
                    assert iv_expr is not None
                    iv_expr = ModelParser.parse_expression(iv_expr)
                    iv_expr.update_scope(neuron.get_state_blocks().get_scope())
                    iv_decl.set_expression(iv_expr)

    def _get_ast_variable(self, neuron, var_name) -> Optional[ASTVariable]:
        """
        Grab the ASTVariable corresponding to the initial value by this name
        """
        for decl in neuron.get_state_blocks().get_declarations():
            for var in decl.variables:
                if var.get_name() == var_name:
                    return var
        return None

    def create_initial_values_for_kernels(self, neuron, solver_dicts, kernels):
        """
        Add the variables used in kernels from the ode-toolbox result dictionary as ODEs in NESTML AST
        """
        for solver_dict in solver_dicts:
            if solver_dict is None:
                continue
            for var_name in solver_dict["initial_values"].keys():
                if ASTTransformers.variable_in_kernels(var_name, kernels):
                    # original initial value expressions should have been removed to make place for ode-toolbox results
                    assert not ASTTransformers.declaration_in_state_block(neuron, var_name)

        for solver_dict in solver_dicts:
            if solver_dict is None:
                continue

            for var_name, expr in solver_dict["initial_values"].items():
                # here, overwrite is allowed because initial values might be repeated between numeric and analytic solver
                if ASTTransformers.variable_in_kernels(var_name, kernels):
                    expr = "0"  # for kernels, "initial value" returned by ode-toolbox is actually the increment value; the actual initial value is assumed to be 0
                    if not ASTTransformers.declaration_in_state_block(neuron, var_name):
                        ASTTransformers.add_declaration_to_state_block(neuron, var_name, expr)

    def create_initial_values_for_ode_toolbox_odes(self, neuron, solver_dicts, kernel_buffers, kernels):
        """
        Add the variables used in ODEs from the ode-toolbox result dictionary as ODEs in NESTML AST.
        """
        for solver_dict in solver_dicts:
            if solver_dict is None:
                continue
            for var_name in solver_dict["initial_values"].keys():
                # original initial value expressions should have been removed to make place for ode-toolbox results
                assert not ASTTransformers.declaration_in_state_block(neuron, var_name)

        for solver_dict in solver_dicts:
            if solver_dict is None:
                continue

            for var_name, expr in solver_dict["initial_values"].items():
                # here, overwrite is allowed because initial values might be repeated between numeric and analytic solver

                if ASTTransformers.variable_in_kernels(var_name, kernels):
                    expr = "0"  # for kernels, "initial value" returned by ode-toolbox is actually the increment value; the actual initial value is assumed to be 0

                if not ASTTransformers.declaration_in_state_block(neuron, var_name):
                    ASTTransformers.add_declaration_to_state_block(neuron, var_name, expr)

    def get_spike_update_expressions(self, neuron: ASTNeuron, kernel_buffers, solver_dicts, delta_factors) -> List[ASTAssignment]:
        """
        Generate the equations that update the dynamical variables when incoming spikes arrive. To be invoked after ode-toolbox.

        For example, a resulting `assignment_str` could be "I_kernel_in += (in_spikes/nS) * 1". The values are taken from the initial values for each corresponding dynamical variable, either from ode-toolbox or directly from user specification in the model.

        Note that for kernels, `initial_values` actually contains the increment upon spike arrival, rather than the initial value of the corresponding ODE dimension.
        """
        spike_updates = []

        for kernel, spike_input_port in kernel_buffers:
            if neuron.get_scope().resolve_to_symbol(str(spike_input_port), SymbolKind.VARIABLE) is None:
                continue

            buffer_type = neuron.get_scope().resolve_to_symbol(str(spike_input_port),
                                                               SymbolKind.VARIABLE).get_type_symbol()

            if ASTTransformers.is_delta_kernel(kernel):
                continue

            for kernel_var in kernel.get_variables():
                for var_order in range(
                        ASTTransformers.get_kernel_var_order_from_ode_toolbox_result(kernel_var.get_name(), solver_dicts)):
                    kernel_spike_buf_name = ASTTransformers.construct_kernel_X_spike_buf_name(
                        kernel_var.get_name(), spike_input_port, var_order)
                    expr = ASTTransformers.get_initial_value_from_ode_toolbox_result(kernel_spike_buf_name, solver_dicts)
                    assert expr is not None, "Initial value not found for kernel " + kernel_var
                    expr = str(expr)
                    if expr in ["0", "0.", "0.0"]:
                        continue  # skip adding the statement if we're only adding zero

                    assignment_str = kernel_spike_buf_name + " += "
                    assignment_str += "(" + str(spike_input_port) + ")"
                    if not expr in ["1.", "1.0", "1"]:
                        assignment_str += " * (" + \
                                          self._printer.print_expression(ModelParser.parse_expression(expr)) + ")"

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

    def remove_kernel_definitions_from_equations_block(self, neuron):
        """
        Removes all kernels in this block.
        """
        equations_block = neuron.get_equations_block()

        decl_to_remove = set()
        for decl in equations_block.get_declarations():
            if type(decl) is ASTKernel:
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

    def transform_ode_and_kernels_to_json(self, neuron: ASTNeuron, parameters_block, kernel_buffers):
        """
        Converts AST node to a JSON representation suitable for passing to ode-toolbox.

        Each kernel has to be generated for each spike buffer convolve in which it occurs, e.g. if the NESTML model code contains the statements

            convolve(G, ex_spikes)
            convolve(G, in_spikes)

        then `kernel_buffers` will contain the pairs `(G, ex_spikes)` and `(G, in_spikes)`, from which two ODEs will be generated, with dynamical state (variable) names `G__X__ex_spikes` and `G__X__in_spikes`.

        :param parameters_block: ASTBlockWithVariables
        :return: Dict
        """
        odetoolbox_indict = {}

        gsl_converter = ODEToolboxReferenceConverter()
        gsl_printer = UnitlessExpressionPrinter(gsl_converter)

        odetoolbox_indict["dynamics"] = []
        equations_block = neuron.get_equations_block()
        for equation in equations_block.get_ode_equations():
            # n.b. includes single quotation marks to indicate differential order
            lhs = ASTTransformers.to_ode_toolbox_name(equation.get_lhs().get_complete_name())
            rhs = gsl_printer.print_expression(equation.get_rhs())
            entry = {"expression": lhs + " = " + rhs}
            symbol_name = equation.get_lhs().get_name()
            symbol = equations_block.get_scope().resolve_to_symbol(symbol_name, SymbolKind.VARIABLE)

            entry["initial_values"] = {}
            symbol_order = equation.get_lhs().get_differential_order()
            for order in range(symbol_order):
                iv_symbol_name = symbol_name + "'" * order
                initial_value_expr = neuron.get_initial_value(iv_symbol_name)
                if initial_value_expr:
                    expr = gsl_printer.print_expression(initial_value_expr)
                    entry["initial_values"][ASTTransformers.to_ode_toolbox_name(iv_symbol_name)] = expr
            odetoolbox_indict["dynamics"].append(entry)

        # write a copy for each (kernel, spike buffer) combination
        for kernel, spike_input_port in kernel_buffers:

            if ASTTransformers.is_delta_kernel(kernel):
                # delta function -- skip passing this to ode-toolbox
                continue

            for kernel_var in kernel.get_variables():
                expr = ASTTransformers.get_expr_from_kernel_var(kernel, kernel_var.get_complete_name())
                kernel_order = kernel_var.get_differential_order()
                kernel_X_spike_buf_name_ticks = ASTTransformers.construct_kernel_X_spike_buf_name(
                    kernel_var.get_name(), spike_input_port, kernel_order, diff_order_symbol="'")

                ASTTransformers.replace_rhs_variables(expr, kernel_buffers)

                entry = {}
                entry["expression"] = kernel_X_spike_buf_name_ticks + " = " + str(expr)

                # initial values need to be declared for order 1 up to kernel order (e.g. none for kernel function f(t) = ...; 1 for kernel ODE f'(t) = ...; 2 for f''(t) = ... and so on)
                entry["initial_values"] = {}
                for order in range(kernel_order):
                    iv_sym_name_ode_toolbox = ASTTransformers.construct_kernel_X_spike_buf_name(
                        kernel_var.get_name(), spike_input_port, order, diff_order_symbol="'")
                    symbol_name_ = kernel_var.get_name() + "'" * order
                    symbol = equations_block.get_scope().resolve_to_symbol(symbol_name_, SymbolKind.VARIABLE)
                    assert symbol is not None, "Could not find initial value for variable " + symbol_name_
                    initial_value_expr = symbol.get_declaring_expression()
                    assert initial_value_expr is not None, "No initial value found for variable name " + symbol_name_
                    entry["initial_values"][iv_sym_name_ode_toolbox] = gsl_printer.print_expression(initial_value_expr)

                odetoolbox_indict["dynamics"].append(entry)

        odetoolbox_indict["parameters"] = {}
        if parameters_block is not None:
            for decl in parameters_block.get_declarations():
                for var in decl.variables:
                    odetoolbox_indict["parameters"][var.get_complete_name(
                    )] = gsl_printer.print_expression(decl.get_expression())

        return odetoolbox_indict

    def make_inline_expressions_self_contained(self, inline_expressions: List[ASTInlineExpression]) -> List[ASTInlineExpression]:
        """
        Make inline_expressions self contained, i.e. without any references to other inline_expressions.

        TODO: it should be a method inside of the ASTInlineExpression
        TODO: this should be done by means of a visitor

        :param inline_expressions: A sorted list with entries ASTInlineExpression.
        :return: A list with ASTInlineExpressions. Defining expressions don't depend on each other.
        """

        # compare all inline expresisons with each other
        # to figure out if one contains the other
        for source in inline_expressions:
            source_position = source.get_source_position()
            for target in inline_expressions:
                # find first(source) inside second(target)
                # replace source name with the actual expression behind it
                matcher = re.compile(self._variable_matching_template.format(source.get_variable_name()))
                target_definition = str(target.get_expression())
                target_definition = re.sub(matcher, "(" + str(source.get_expression()) + ")", target_definition)
                # parse as new combined expression
                target.expression = ModelParser.parse_expression(target_definition)
                # adjust scope for root node in the target
                target.expression.update_scope(source.get_scope())
                # recreate symbol table to detect all new symbols
                target.expression.accept(ASTSymbolTableVisitor())

                def log_set_source_position(node):
                    if node.get_source_position().is_added_source_position():
                        node.set_source_position(source_position)

                # now recursively recalculate scopes for subnodes
                target.expression.accept(ASTHigherOrderVisitor(visit_funcs=log_set_source_position))

        return inline_expressions

    def replace_inline_expressions_through_defining_expressions(self,
                                                                definitions: Sequence[ASTOdeEquation],
                                                                inline_expressions: Sequence[ASTInlineExpression]) -> Sequence[ASTOdeEquation]:
        """
        Replaces symbols from `inline_expressions` in `definitions` with corresponding defining expressions from `inline_expressions`.

        :param definitions: A list of ODE definitions (**updated in-place**).
        :param inline_expressions: A list of inline expression definitions.
        :return: A list of updated ODE definitions (same as the ``definitions`` parameter).
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

    def store_transformed_model(self, ast):
        if FrontendConfiguration.store_log:
            with open(str(os.path.join(FrontendConfiguration.get_target_path(), '..', 'report',
                                       ast.get_name())) + '.txt', 'w+') as f:
                f.write(str(ast))

