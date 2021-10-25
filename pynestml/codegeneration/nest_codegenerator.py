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
import glob
from typing import Any, Dict, List, Mapping, Optional, Sequence, Union

import datetime
import os
from jinja2 import Environment, FileSystemLoader, TemplateRuntimeError, Template
from odetoolbox import analysis

import pynestml
from pynestml.codegeneration.ast_transformers import ASTTransformers
from pynestml.codegeneration.codegenerator import CodeGenerator
from pynestml.codegeneration.expressions_pretty_printer import ExpressionsPrettyPrinter
from pynestml.codegeneration.gsl_names_converter import GSLNamesConverter
from pynestml.codegeneration.gsl_reference_converter import GSLReferenceConverter
from pynestml.codegeneration.unitless_expression_printer import UnitlessExpressionPrinter
from pynestml.codegeneration.nest_assignments_helper import NestAssignmentsHelper
from pynestml.codegeneration.nest_declarations_helper import NestDeclarationsHelper
from pynestml.codegeneration.nest_names_converter import NestNamesConverter
from pynestml.codegeneration.nest_printer import NestPrinter
from pynestml.codegeneration.nest_reference_converter import NESTReferenceConverter
from pynestml.exceptions.invalid_path_exception import InvalidPathException
from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.generated.PyNestMLLexer import PyNestMLLexer
from pynestml.meta_model.ast_neuron_or_synapse import ASTNeuronOrSynapse
from pynestml.meta_model.ast_declaration import ASTDeclaration
from pynestml.meta_model.ast_external_variable import ASTExternalVariable
from pynestml.meta_model.ast_return_stmt import ASTReturnStmt
from pynestml.meta_model.ast_assignment import ASTAssignment
from pynestml.meta_model.ast_equations_block import ASTEquationsBlock
from pynestml.meta_model.ast_input_port import ASTInputPort
from pynestml.meta_model.ast_inline_expression import ASTInlineExpression
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.meta_model.ast_synapse import ASTSynapse
from pynestml.meta_model.ast_kernel import ASTKernel
from pynestml.meta_model.ast_ode_equation import ASTOdeEquation
from pynestml.meta_model.ast_stmt import ASTStmt
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.symbols.symbol import SymbolKind

from pynestml.utils.logger import Logger
from pynestml.utils.logger import LoggingLevel
from pynestml.utils.messages import Messages
from pynestml.utils.model_parser import ModelParser
from pynestml.utils.ode_transformer import OdeTransformer
from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor
from pynestml.symbol_table.symbol_table import SymbolTable
from pynestml.symbols.variable_symbol import BlockType
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.visitors.ast_higher_order_visitor import ASTHigherOrderVisitor
from pynestml.visitors.ast_visitor import ASTVisitor
from pynestml.visitors.ast_random_number_generator_visitor import ASTRandomNumberGeneratorVisitor

def find_spiking_post_port(synapse, namespace):
    if 'paired_neuron' in dir(synapse):
        for post_port_name in namespace["post_ports"]:
            if synapse.get_input_blocks() \
                    and synapse.get_input_blocks().get_input_ports() \
                    and ASTTransformers.get_input_port_by_name(synapse.get_input_blocks(), post_port_name).is_spike():
                return post_port_name
    return None


class NESTCodeGenerator(CodeGenerator):
    """
    Code generator for a C++ NEST extension module.

    Options:
    - **neuron_parent_class**: The C++ class from which the generated NESTML neuron class inherits. Examples: ``"ArchivingNode"``, ``"StructuralPlasticityNode"``. Default: ``"ArchivingNode"``.
    - **neuron_parent_class_include**: The C++ header filename to include that contains **neuron_parent_class**. Default: ``"archiving_node.h"``.
    - **neuron_synapse_pairs**: List of pairs of (neuron, synapse) model names.
    - **preserve_expressions**: Set to True, or a list of strings corresponding to individual variable names, to disable internal rewriting of expressions, and return same output as input expression where possible. Only applies to variables specified as first-order differential equations. (This parameter is passed to ODE-toolbox.)
    - **simplify_expression**: For all expressions ``expr`` that are rewritten by ODE-toolbox: the contents of this parameter string are ``eval()``ed in Python to obtain the final output expression. Override for custom expression simplification steps. Example: ``sympy.simplify(expr)``. Default: ``"sympy.logcombine(sympy.powsimp(sympy.expand(expr)))"``. (This parameter is passed to ODE-toolbox.)
    - **templates**: Path containing jinja templates used to generate code for NEST simulator.
        - **path**: Path containing jinja templates used to generate code for NEST simulator.
        - **model_templates**: A list of the jinja templates or a relative path to a directory containing the neuron and synapse model templates.
            - **neuron**: A list of neuron model jinja templates.
            - **synapse**: A list of synapse model jinja templates.
        - **module_templates**: A list of the jinja templates or a relative path to a directory containing the templates related to generating the NEST module.
    """

    _default_options = {
        "neuron_parent_class": "ArchivingNode",
        "neuron_parent_class_include": "archiving_node.h",
        "neuron_synapse_pairs": [],
        "preserve_expressions": False,
        "simplify_expression": "sympy.logcombine(sympy.powsimp(sympy.expand(expr)))",
        "templates": {
            "path": 'point_neuron',
            "model_templates": {
                "neuron": ['NeuronClass.cpp.jinja2', 'NeuronHeader.h.jinja2'],
                "synapse": ['SynapseHeader.h.jinja2']
            },
            "module_templates": ['setup']
        }
    }

    _model_templates = dict()
    _module_templates = list()

    def __init__(self, options: Optional[Mapping[str, Any]] = None):
        super().__init__("NEST", options)
        self._printer = ExpressionsPrettyPrinter()
        self.analytic_solver = {}
        self.numeric_solver = {}
        self.non_equations_state_variables = {}   # those state variables not defined as an ODE in the equations block
        self.setup_template_env()

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

        # Setup neuron template environment
        neuron_model_templates = self.get_option("templates")['model_templates']['neuron']
        if not neuron_model_templates:
            raise Exception('A list of neuron model template files/directories is missing.')
        self._model_templates["neuron"] = list()
        self._model_templates["neuron"].extend(self.__setup_template_env(neuron_model_templates, templates_root_dir))

        # Setup synapse template environment
        synapse_model_templates = self.get_option("templates")['model_templates']['synapse']
        if synapse_model_templates:
            self._model_templates["synapse"] = list()
            self._model_templates["synapse"].extend(self.__setup_template_env(synapse_model_templates, templates_root_dir))

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

    def update_blocktype_for_common_parameters(self, node):

        """Change the BlockType for all homogeneous parameters to BlockType.COMMON_PARAMETER"""
        # get all homogeneous parameters
        all_homogeneous_parameters = []
        for parameter in node.get_parameter_symbols():
            is_homogeneous = PyNestMLLexer.DECORATOR_HOMOGENEOUS in parameter.get_decorators()
            if is_homogeneous:
                all_homogeneous_parameters.append(parameter.name)

        # change the block type
        class ASTHomogeneousParametersBlockTypeChangeVisitor(ASTVisitor):
            def __init__(self, all_homogeneous_parameters):
                super(ASTHomogeneousParametersBlockTypeChangeVisitor, self).__init__()
                self._all_homogeneous_parameters = all_homogeneous_parameters

            def visit_variable(self, node: ASTNode):
                if node.get_name() in self._all_homogeneous_parameters:
                    symbol = node.get_scope().resolve_to_symbol(node.get_complete_name(),
                                                                SymbolKind.VARIABLE)
                    if symbol is None:
                        code, message = Messages.get_variable_not_defined(node.get_variable().get_complete_name())
                        Logger.log_message(code=code, message=message, error_position=node.get_source_position(),
                                           log_level=LoggingLevel.ERROR, astnode=node)
                        return

                    assert symbol.block_type in [BlockType.PARAMETERS, BlockType.COMMON_PARAMETERS]
                    symbol.block_type = BlockType.COMMON_PARAMETERS
                    Logger.log_message(None, -1, "Changing block type of variable " + str(node.get_complete_name()), None, LoggingLevel.INFO)

        if node is None:
            return

        visitor = ASTHomogeneousParametersBlockTypeChangeVisitor(all_homogeneous_parameters)
        node.accept(visitor)


    def is_continuous_port(self, port_name: str, parent_node: ASTNeuronOrSynapse):
        for port in parent_node.get_input_blocks().get_input_ports():
            if port.is_continuous() and port_name == port.get_name():
                return True
        return False

    def is_special_port(self, special_type: str, port_name: str, neuron_name: str, synapse_name: str) -> bool:
        """
        Check if a port by the given name is specified as connecting to the postsynaptic neuron. Only makes sense
        for synapses.
        """
        assert special_type in ["post", "vt"]
        if not "neuron_synapse_pairs" in self._options.keys():
            return False

        for neuron_synapse_pair in self._options["neuron_synapse_pairs"]:
            if not (neuron_name in [neuron_synapse_pair["neuron"], neuron_synapse_pair["neuron"] + FrontendConfiguration.suffix]
                    and synapse_name in [neuron_synapse_pair["synapse"], neuron_synapse_pair["synapse"] + FrontendConfiguration.suffix]):
                continue

            if not special_type + "_ports" in neuron_synapse_pair.keys():
                return False

            post_ports = neuron_synapse_pair[special_type + "_ports"]
            if not isinstance(post_ports, list):
                # only one port name given, not a list
                return port_name == post_ports

            for post_port in post_ports:
                if type(post_port) is not str and len(post_port) == 2:  # (syn_port_name, neuron_port_name) tuple
                    post_port = post_port[0]
                if type(post_port) is not str and len(post_port) == 1:  # (syn_port_name)
                    return post_port[0] == port_name
                if port_name == post_port:
                    return True
        return False

    def is_post_port(self, port_name: str, neuron_name: str, synapse_name: str) -> bool:
        return self.is_special_port("post", port_name, neuron_name, synapse_name)

    def is_vt_port(self, port_name: str, neuron_name: str, synapse_name: str) -> bool:
        return self.is_special_port("vt", port_name, neuron_name, synapse_name)

    def get_spiking_post_port_names(self, synapse, neuron_name: str, synapse_name: str):
        post_port_names = []
        for port in synapse.get_input_blocks().get_input_ports():
            if self.is_post_port(port.name, neuron_name, synapse_name) and port.is_spike():
                post_port_names.append(port.get_name())
        return post_port_names

    def get_post_port_names(self, synapse, neuron_name: str, synapse_name: str):
        post_port_names = []
        for port in synapse.get_input_blocks().get_input_ports():
            if self.is_post_port(port.name, neuron_name, synapse_name):
                post_port_names.append(port.get_name())
        return post_port_names

    def get_vt_port_names(self, synapse, neuron_name: str, synapse_name: str):
        post_port_names = []
        for port in synapse.get_input_blocks().get_input_ports():
            if self.is_vt_port(port.name, neuron_name, synapse_name):
                post_port_names.append(port.get_name())
        return post_port_names

    def get_neuron_var_name_from_syn_port_name(self, port_name: str, neuron_name: str, synapse_name: str) -> Optional[str]:
        """
        Check if a port by the given name is specified as connecting to the postsynaptic neuron. Only makes sense for synapses.
        """
        if not "neuron_synapse_pairs" in self._options.keys():
            return False

        for neuron_synapse_pair in self._options["neuron_synapse_pairs"]:
            if not (neuron_name in [neuron_synapse_pair["neuron"], neuron_synapse_pair["neuron"] + FrontendConfiguration.suffix]
                    and synapse_name in [neuron_synapse_pair["synapse"], neuron_synapse_pair["synapse"] + FrontendConfiguration.suffix]):
                continue

            if not "post_ports" in neuron_synapse_pair.keys():
                return None

            post_ports = neuron_synapse_pair["post_ports"]

            for post_port in post_ports:
                if type(post_port) is not str and len(post_port) == 2:  # (syn_port_name, neuron_var_name) tuple
                    if port_name == post_port[0]:
                        return post_port[1]

            return None

        return None

    def get_all_variables(self, node: ASTNode) -> List[str]:
        """Make a list of all variable symbol names that are in ``node``"""
        class ASTVariablesFinderVisitor(ASTVisitor):
            _variables = []

            def __init__(self):
                super(ASTVariablesFinderVisitor, self).__init__()


            def visit_declaration(self, node):
                symbol = node.get_scope().resolve_to_symbol(node.get_variables()[0].get_complete_name(),
                                                            SymbolKind.VARIABLE)
                if symbol is None:
                    code, message = Messages.get_variable_not_defined(node.get_variable().get_complete_name())
                    Logger.log_message(code=code, message=message, error_position=node.get_source_position(),
                                       log_level=LoggingLevel.ERROR, astnode=node)
                    return

                self._variables.append(symbol)

        if node is None:
            return []

        visitor = ASTVariablesFinderVisitor()
        node.accept(visitor)
        all_variables = [v.name for v in visitor._variables]
        return all_variables


    def get_all_Variables_used_in_convolutions(self, node: ASTNode, parent_node: ASTNode) -> List[str]:
        """Make a list of all variable symbol names that are in ``node`` and used in a convolution"""
        class ASTAllVariablesUsedInConvolutionVisitor(ASTVisitor):
            _variables = []
            parent_node = None

            def __init__(self, node, parent_node):
                super(ASTAllVariablesUsedInConvolutionVisitor, self).__init__()
                self.node = node
                self.parent_node = parent_node

            def visit_function_call(self, node):
                func_name = node.get_name()
                if func_name == 'convolve':
                    symbol_buffer = node.get_scope().resolve_to_symbol(str(node.get_args()[1]),
                                                                       SymbolKind.VARIABLE)
                    input_port = ASTTransformers.get_input_port_by_name(self.parent_node.get_input_blocks(), symbol_buffer.name)
                    if input_port:
                        found_parent_assignment = False
                        node_ = node
                        while not found_parent_assignment:
                            node_ = self.parent_node.get_parent(node_)
                            if isinstance(node_, ASTInlineExpression):   # XXX TODO also needs to accept normal ASTExpression, ASTAssignment?
                                found_parent_assignment = True
                        var_name = node_.get_variable_name()
                        self._variables.append(var_name)

        if node is None:
            return []

        visitor = ASTAllVariablesUsedInConvolutionVisitor(node, parent_node)
        node.accept(visitor)
        return visitor._variables

    def get_all_variables_assigned_to(self, node):
        class ASTAssignedToVariablesFinderVisitor(ASTVisitor):
            _variables = []

            def __init__(self, synapse):
                super(ASTAssignedToVariablesFinderVisitor, self).__init__()
                self.synapse = synapse


            def visit_assignment(self, node):
                symbol = node.get_scope().resolve_to_symbol(node.get_variable().get_complete_name(), SymbolKind.VARIABLE)
                assert symbol is not None  # should have been checked in a CoCo before
                self._variables.append(symbol)

        if node is None:
            return []

        visitor = ASTAssignedToVariablesFinderVisitor(node)
        node.accept(visitor)

        return [v.name for v in visitor._variables]

    def get_convolve_with_not_post_vars(self, node, neuron_name, synapse_name, parent_node):
        class ASTVariablesUsedInConvolutionVisitor(ASTVisitor):
            _variables = []

            def __init__(self, node: ASTNode, parent_node: ASTNode, codegen_class):
                super(ASTVariablesUsedInConvolutionVisitor, self).__init__()
                self.node = node
                self.parent_node = parent_node
                self.codegen_class = codegen_class

            def visit_function_call(self, node):
                func_name = node.get_name()
                if func_name == 'convolve':
                    symbol_buffer = node.get_scope().resolve_to_symbol(str(node.get_args()[1]),
                                                                       SymbolKind.VARIABLE)
                    input_port = ASTTransformers.get_input_port_by_name(self.parent_node.get_input_blocks(), symbol_buffer.name)
                    if input_port and not self.codegen_class.is_post_port(input_port.name, neuron_name, synapse_name):
                        found_parent_assignment = False
                        node_ = node
                        while not found_parent_assignment:
                            node_ = self.parent_node.get_parent(node_)
                            if isinstance(node_, ASTInlineExpression):   # XXX TODO also needs to accept normal ASTExpression, ASTAssignment?
                                found_parent_assignment = True
                        var_name = node_.get_variable_name()
                        self._variables.append(var_name)

        if node is None:
            return []

        visitor = ASTVariablesUsedInConvolutionVisitor(node, parent_node, self)
        node.accept(visitor)
        return visitor._variables

    def analyse_transform_neuron_synapse_pairs(self, neurons, synapses):
        """
        Does not modify existing neurons or synapses, but returns lists with additional elements representing new pair neuron and synapse
        """
        from pynestml.utils.ast_utils import ASTUtils
        if not "neuron_synapse_pairs" in self._options:
            return neurons, synapses

        paired_synapses = []
        for neuron_synapse_pair in self._options["neuron_synapse_pairs"]:
            neuron_name = neuron_synapse_pair["neuron"]
            neuron_names = [neuron.get_name() for neuron in neurons]
            if not neuron_name + FrontendConfiguration.suffix in neuron_names:
                raise Exception("Neuron name used in pair ('" + neuron_name + "') not found")  # XXX: log error
                return neurons, synapses
            neuron = neurons[neuron_names.index(neuron_name + FrontendConfiguration.suffix)]
            new_neuron = neuron.clone()

            synapse_name = neuron_synapse_pair["synapse"]
            synapse_names = [synapse.get_name() for synapse in synapses]
            if not synapse_name + FrontendConfiguration.suffix in synapse_names:
                raise Exception("Synapse name used in pair ('" + synapse_name + "') not found")  # XXX: log error
                return neurons, synapses
            synapse = synapses[synapse_names.index(synapse_name + FrontendConfiguration.suffix)]
            paired_synapses.append(synapse)
            new_synapse = synapse.clone()


            #
            #   determine which variables and dynamics in synapse can be transferred to neuron
            #

            all_variables = self.get_all_variables(synapse.get_state_blocks())
            Logger.log_message(None, -1, "All variables defined in state block: " + ", ".join(all_variables), None, LoggingLevel.INFO)

            all_conv_vars = self.get_all_Variables_used_in_convolutions(synapse.get_equations_blocks(), synapse)
            Logger.log_message(None, -1, "All variables due to convolutions: " + str(all_conv_vars), None, LoggingLevel.INFO)

            # if any variable is assigned to in any block that is not connected to a postsynaptic port
            strictly_synaptic_variables = []
            for port in new_synapse.get_input_blocks().get_input_ports():
                if not self.is_post_port(port.name, neuron.name, synapse.name):
                    strictly_synaptic_variables += self.get_all_variables_assigned_to(synapse.get_on_receive_block(port.name))
            Logger.log_message(None, -1, "Assigned-to variables in onReceive blocks other than post: " + ", ".join(strictly_synaptic_variables), None, LoggingLevel.INFO)
            strictly_synaptic_variables += self.get_all_variables_assigned_to(synapse.get_update_blocks())

            convolve_with_not_post_vars = self.get_convolve_with_not_post_vars(synapse.get_equations_blocks(), neuron.name, synapse.name, synapse)
            Logger.log_message(None, -1, "Variables used in convolve with other than 'spike post' port: " + str(convolve_with_not_post_vars), None, LoggingLevel.INFO)

            syn_to_neuron_state_vars = (set(all_variables) | set(all_conv_vars)) - (set(strictly_synaptic_variables) | set(convolve_with_not_post_vars))
            Logger.log_message(None, -1, "--> State variables that will be moved from synapse to neuron: " + str(syn_to_neuron_state_vars), None, LoggingLevel.INFO)

            #   collect all the variable/parameter/kernel/function/etc. names used in defining expressions of `syn_to_neuron_state_vars`
            recursive_vars_used = ASTTransformers.recursive_dependent_variables_search(syn_to_neuron_state_vars, synapse)
            Logger.log_message(None, -1, "recursive dependent variables search yielded the following new variables: " + str(recursive_vars_used), None, LoggingLevel.INFO)


            #
            #   move state variable definitions from synapse to neuron
            #

            var_name_suffix = "__for_" + synapse.get_name()

            def get_variable_declarations_from_block(var_name, block):
                decls = []
                for decl in block.get_declarations():
                    for var in decl.get_variables():
                        if var.get_name() == var_name:
                            decls.append(decl)
                            break
                return decls

            def add_suffix_to_variable_names(decl, suffix: str):
                """add suffix to the left-hand side of a declaration"""
                if isinstance(decl, ASTInlineExpression):
                    decl.set_variable_name(decl.get_variable_name() + suffix)
                elif isinstance(decl, ASTOdeEquation):
                    decl.get_lhs().set_name(decl.get_lhs().get_name() + suffix)
                elif isinstance(decl, ASTStmt):
                    # XXX: assume stmt is small_stmt and assignment
                    decl.small_stmt.get_assignment().lhs.set_name(decl.small_stmt.get_assignment().lhs.get_name() + suffix)
                else:
                    for var in decl.get_variables():
                        var.set_name(var.get_name() + suffix)
                # XXX: TODO: change variable names inside rhs expressions
                # XXX: TODO: change parameter names inside rhs expressions

            vars_used = []

            def move_decl_syn_neuron(state_var, neuron_block, synapse_block, var_name_suffix):
                if not neuron_block \
                   or not synapse_block:
                    return

                decls = get_variable_declarations_from_block(state_var, synapse_block)
                if decls:
                    Logger.log_message(None, -1, "Moving state var definition of " + state_var + " from synapse to neuron", None, LoggingLevel.INFO)
                    for decl in decls:
                        if decl.has_expression():
                            vars_used.extend(ASTTransformers.collect_variable_names_in_expression(decl.get_expression()))
                        synapse_block.declarations.remove(decl)
                        add_suffix_to_variable_names(decl, suffix=var_name_suffix)
                        neuron_block.get_declarations().append(decl)
                        decl.update_scope(neuron_block.get_scope())
                        decl.accept(ASTSymbolTableVisitor())

            for state_var in syn_to_neuron_state_vars:
                neuron_block = neuron.get_state_blocks()
                synapse_block = synapse.get_state_blocks()
                move_decl_syn_neuron(state_var, neuron_block, synapse_block, var_name_suffix)


            #
            #   move defining equations for variables from synapse to neuron
            #

            def equations_from_syn_to_neuron(state_var, synapse_block, neuron_block, var_name_suffix, mode):
                if not neuron_block or not synapse_block:
                    return

                assert mode in ["move", "copy"]

                decls = ASTTransformers.get_eq_declarations_from_block(state_var, synapse_block)

                if decls:
                    # print("\tvar = " + str(state_var) + " from synapse block to neuron")
                    for decl in decls:
                        if (type(decl) in [ASTDeclaration, ASTReturnStmt] and decl.has_expression()) \
                           or type(decl) is ASTInlineExpression:
                            vars_used.extend(ASTTransformers.collect_variable_names_in_expression(decl.get_expression()))
                        elif type(decl) is ASTOdeEquation:
                            vars_used.extend(ASTTransformers.collect_variable_names_in_expression(decl.get_rhs()))
                        elif type(decl) is ASTKernel:
                            for expr in decl.get_expressions():
                                vars_used.extend(ASTTransformers.collect_variable_names_in_expression(expr))
                        else:
                            raise Exception("Tried to move unknown type " + str(type(decl)))

                        if mode == "move":
                            synapse_block.declarations.remove(decl)
                        add_suffix_to_variable_names(decl, suffix=var_name_suffix)
                        neuron_block.get_declarations().append(decl)
                        decl.update_scope(neuron_block.get_scope())
                        decl.accept(ASTSymbolTableVisitor())
                        decl._is_moved_from_syn_to_neuron = True


            for state_var in syn_to_neuron_state_vars:
                Logger.log_message(None, -1, "Moving state var defining equation(s) " + str(state_var), None, LoggingLevel.INFO)
                equations_from_syn_to_neuron(state_var, new_synapse.get_equations_block(), new_neuron.get_equations_block(), var_name_suffix, mode="move")

            new_neuron._transferred_variables = [neuron_state_var + var_name_suffix for neuron_state_var in syn_to_neuron_state_vars]


            #
            #     mark postsynaptically connected input ports in the synapse
            #     convolutions with them ultimately yield variable updates when post neuron calls emit_spike()
            #


            def mark_post_ports(neuron, synapse):
                post_ports = []

                def mark_post_port(_expr=None):
                    var = None
                    if isinstance(_expr, ASTSimpleExpression) and _expr.is_variable():
                        var = _expr.get_variable()
                    elif isinstance(_expr, ASTVariable):
                        var = _expr

                    if var \
                       and self.is_post_port(var.name, neuron.name, synapse.name):
                        post_ports.append(var)

                        var._is_post_port = True

                synapse.accept(ASTHigherOrderVisitor(lambda x: mark_post_port(x)))
                return post_ports

            mark_post_ports(new_neuron, new_synapse)


            #
            #     mark variables in the neuron pertaining to synapse postsynaptic ports
            #
            #     convolutions with them ultimately yield variable updates when post neuron calls emit_spike()
            #


            def mark_post_ports(neuron, synapse):
                post_ports = []

                def mark_post_port(_expr=None):
                    var = None
                    if isinstance(_expr, ASTSimpleExpression) and _expr.is_variable():
                        var = _expr.get_variable()
                    elif isinstance(_expr, ASTVariable):
                        var = _expr

                    if var \
                       and self.is_post_port(var.name, neuron.name, synapse.name):
                        Logger.log_message(None, -1, "\tneuron " + neuron.name + " uses post spike port " + str(var.name) + " for synapse " + synapse.name, None, LoggingLevel.INFO)
                        post_ports.append(var)

                        var._is_post_port = True

                neuron.accept(ASTHigherOrderVisitor(lambda x: mark_post_port(x)))
                return post_ports

            mark_post_ports(new_neuron, new_synapse)


            #
            #    move initial values for equations
            #


            def iv_from_syn_to_neuron(state_var, synapse_block, neuron_block, var_name_suffix, mode):
                if not neuron_block \
                   or not synapse_block:
                    return

                assert mode in ["move", "copy"]

                decls = ASTTransformers.get_eq_declarations_from_block(state_var, synapse_block)

                for decl in decls:
                    if mode == "move":
                        synapse_block.declarations.remove(decl)
                    add_suffix_to_variable_names(decl, suffix=var_name_suffix)
                    neuron_block.get_declarations().append(decl)
                    decl.update_scope(neuron_block.get_scope())
                    decl.accept(ASTSymbolTableVisitor())

            for state_var in syn_to_neuron_state_vars:
                Logger.log_message(None, -1, "Moving state variables for equation(s) " + str(state_var), None, LoggingLevel.INFO)
                iv_from_syn_to_neuron(state_var, new_synapse.get_state_blocks(), new_neuron.get_state_blocks(), var_name_suffix, mode="move")

            #
            #    move updates in update block from synapse to neuron
            #

            def get_statements_from_block(var_name, block):
                """XXX: only simple statements such as assignments are supported for now. if..then..else compound statements and so are not yet supported."""
                block = block.get_block()
                all_stmts = block.get_stmts()
                stmts = []
                for node in all_stmts:
                    if node.is_small_stmt() \
                       and node.small_stmt.is_assignment() \
                       and node.small_stmt.get_assignment().lhs.get_name() == var_name:
                        stmts.append(node)
                return stmts

            def move_updates_syn_neuron(state_var, synapse_block, neuron_block, var_name_suffix):
                if not neuron_block \
                   or not synapse_block:
                    return

                stmts = get_statements_from_block(state_var, synapse_block)
                if stmts:
                    Logger.log_message(None, -1, "Moving state var updates for " + state_var + " from synapse to neuron", None, LoggingLevel.INFO)
                    for stmt in stmts:
                        vars_used.extend(ASTTransformers.collect_variable_names_in_expression(stmt))
                        synapse_block.get_block().stmts.remove(stmt)
                        add_suffix_to_variable_names(stmt, suffix=var_name_suffix)
                        neuron_block.get_block().stmts.append(stmt)
                        stmt.update_scope(neuron_block.get_scope())
                        stmt.accept(ASTSymbolTableVisitor())

            new_neuron.moved_spike_updates = []

            for state_var in syn_to_neuron_state_vars:
                Logger.log_message(None, -1, "Moving onPost updates for " + str(state_var), None, LoggingLevel.INFO)
                spiking_post_port_names = self.get_spiking_post_port_names(synapse, neuron.name, synapse.name)

                assert len(spiking_post_port_names) <= 1, "Can only handle one spiking \"post\" port"
                if len(spiking_post_port_names) == 0:
                    continue
                post_port_name = spiking_post_port_names[0]
                post_receive_block = new_synapse.get_on_receive_block(post_port_name)
                if post_receive_block:
                    stmts = get_statements_from_block(state_var, post_receive_block)
                    if stmts:
                        Logger.log_message(None, -1, "Moving state var updates for " + state_var + " from synapse to neuron", None, LoggingLevel.INFO)
                        for stmt in stmts:
                            vars_used.extend(ASTTransformers.collect_variable_names_in_expression(stmt))
                            post_receive_block.block.stmts.remove(stmt)
                            add_suffix_to_variable_names(stmt, suffix=var_name_suffix)
#                            neuron_block.get_block().stmts.append(stmt)
                            stmt.update_scope(new_neuron.get_update_blocks().get_scope())
                            stmt.accept(ASTSymbolTableVisitor())
                            new_neuron.moved_spike_updates.append(stmt)


            #
            #    move variable definitions from synapse to neuron
            #

            vars_used = list(set(vars_used))    # pick unique elements
            vars_used = [s for s in vars_used if not var_name_suffix in s.get_name()]
            Logger.log_message(None, -1, "Dependent variables: " + ", ".join([str(v) for v in vars_used]), None, LoggingLevel.INFO)

            Logger.log_message(None, -1, "Moving declarations from synapse equations block to neuron equations block...", None, LoggingLevel.INFO)
            all_state_vars = [s.get_variables() for s in new_neuron.get_state_blocks().get_declarations()]
            all_state_vars = sum(all_state_vars, [])
            all_state_vars = [var.name for var in all_state_vars]

            # add names of kernels
            kernel_buffers = ASTTransformers.generate_kernel_buffers_(synapse, synapse.get_equations_blocks())
            all_state_vars += [var.name for k in kernel_buffers for var in k[0].variables]

            for state_var in vars_used:
                if (new_synapse.get_equations_block() is not None) and (str(state_var) in all_state_vars):
                    Logger.log_message(None, -1, "\t• Moving variable " + str(state_var), None, LoggingLevel.INFO)
                    equations_from_syn_to_neuron(state_var, new_synapse.get_equations_block(), new_neuron.get_equations_block(), var_name_suffix, mode="move")

            #
            #    replace occurrences of the variables in expressions in the original synapse with calls to the corresponding neuron getters
            #

            def replace_variable_name_in_expressions(var_name, synapse, suffix, new_scope, alternate_name=None):
                """
                Replace all occurrences of variables (`ASTVariable`s) (e.g. `post_trace'`) in the synapse with `ASTExternalVariable`s, indicating that they are moved to the postsynaptic partner.
                """

                def replace_var(_expr=None):
                    if isinstance(_expr, ASTSimpleExpression) and _expr.is_variable():
                        var = _expr.get_variable()
                    elif isinstance(_expr, ASTVariable):
                        var = _expr
                    else:
                        return

                    if var.get_name() != var_name:
                        return

                    ast_ext_var = ASTExternalVariable(var.get_name() + suffix,
                                                      differential_order=var.get_differential_order(),
                                                      source_position=var.get_source_position())
                    if alternate_name:
                        ast_ext_var.set_alternate_name(alternate_name)
                    ast_ext_var.update_scope2(new_scope)  # variable reference is in synapse model, referent is variable in neuron model
                    ast_ext_var.accept(ASTSymbolTableVisitor())

                    if isinstance(_expr, ASTSimpleExpression) and _expr.is_variable():
                        Logger.log_message(None, -1, "ASTSimpleExpression replacement made (var = " + str(ast_ext_var.get_name()) + ") in expression: " + str(synapse.get_parent(_expr)), None, LoggingLevel.INFO)
                        _expr.set_variable(ast_ext_var)
                    elif isinstance(_expr, ASTVariable):
                        if isinstance(synapse.get_parent(_expr), ASTAssignment):
                            synapse.get_parent(_expr).lhs = ast_ext_var
                            Logger.log_message(None, -1, "ASTVariable replacement made in expression: " + str(synapse.get_parent(_expr)), None, LoggingLevel.INFO)
                        elif isinstance(synapse.get_parent(_expr), ASTSimpleExpression) and synapse.get_parent(_expr).is_variable():
                            synapse.get_parent(_expr).set_variable(ast_ext_var)
                        else:
                            Logger.log_message(None, -1, "Error: unhandled use of variable " + var_name + " in expression " + str(_expr), None, LoggingLevel.INFO)
                            raise
                    else:
                        p = synapse.get_parent(var)
                        Logger.log_message(None, -1, "Error: unhandled use of variable " + var_name + " in expression " + str(p), None, LoggingLevel.INFO)
                        raise

                synapse.accept(ASTHigherOrderVisitor(lambda x: replace_var(x)))

            Logger.log_message(None, -1, "In synapse: replacing variables with suffixed external variable references", None, LoggingLevel.INFO)
            for state_var in syn_to_neuron_state_vars:
                Logger.log_message(None, -1, "\t• Replacing variable " + str(state_var), None, LoggingLevel.INFO)
                replace_variable_name_in_expressions(state_var, new_synapse, var_name_suffix, new_neuron.get_equations_blocks().get_scope())


            # ---------------

            Logger.log_message(None, -1, "In synapse: replacing ``continuous`` type input ports that are connected to postsynaptic neuron with suffixed external variable references", None, LoggingLevel.INFO)
            post_connected_continuous_input_ports = []
            post_variable_names = []
            for port in synapse.get_input_blocks().get_input_ports():
                if self.is_post_port(port.get_name(), neuron.name, synapse.name) and self.is_continuous_port(port.get_name(), synapse):
                    post_connected_continuous_input_ports.append(port.get_name())
                    post_variable_names.append(self.get_neuron_var_name_from_syn_port_name(port.get_name(), neuron.name, synapse.name))

            for state_var, alternate_name in zip(post_connected_continuous_input_ports, post_variable_names):
                Logger.log_message(None, -1, "\t• Replacing variable " + str(state_var), None, LoggingLevel.INFO)
                replace_variable_name_in_expressions(state_var, new_synapse, "", new_synapse.get_equations_blocks().get_scope(), alternate_name)

            # --------------    add dummy variable to state variable (and initial value) declarations so that type of the ASTExternalVariable can be resolved
            """
            def iv_from_syn_to_neuron(state_var, synapse_block, neuron_block, var_name_suffix, mode):
                if not neuron_block \
                 or not synapse_block:
                    return

                assert mode in ["move", "copy"]

                decls = get_eq_declarations_from_block(state_var, synapse_block)

                for decl in decls:
                    if mode == "move":
                        synapse_block.declarations.remove(decl)
                    add_suffix_to_variable_names(decl, suffix=var_name_suffix)
                    neuron_block.get_declarations().append(decl)
                    decl.update_scope(neuron_block.get_scope())
                    decl.accept(ASTSymbolTableVisitor())

            for state_var in post_connected_continuous_input_ports:
                print("Adding state variables definition for " + str(state_var))
                iv_from_syn_to_neuron(state_var, new_synapse.get_state_blocks(), new_neuron.get_state_blocks(), var_name_suffix, mode="copy")
            """

            # --------------

            Logger.log_message(None, -1, "Add suffix to moved variable names in neuron...", None, LoggingLevel.INFO)
            for state_var in vars_used:
                Logger.log_message(None, -1, "\t• Variable " + str(state_var), None, LoggingLevel.INFO)
                ASTUtils.add_suffix_to_variable_name(str(state_var), new_neuron, var_name_suffix)

            #
            #    move parameters
            #

            def param_from_syn_to_neuron(state_var, synapse_block, neuron_block, var_name_suffix, mode):
                if not neuron_block \
                   or not synapse_block:
                    return

                assert mode in ["move", "copy"]

                decls = ASTTransformers.get_eq_declarations_from_block(state_var, synapse_block)

                for decl in decls:
                    if mode == "move":
                        synapse_block.declarations.remove(decl)
                    add_suffix_to_variable_names(decl, suffix=var_name_suffix)
                    neuron_block.get_declarations().append(decl)
                    decl.update_scope(neuron_block.get_scope())
                    decl.accept(ASTSymbolTableVisitor())

            Logger.log_message(None, -1, "Copying parameters from synapse to neuron...", None, LoggingLevel.INFO)
            all_param_vars = [s.get_variables() for s in new_synapse.get_parameter_blocks().get_declarations()]
            all_param_vars = sum(all_param_vars, [])
            all_param_vars = [var.name for var in all_param_vars]
            for param_var in set(list(vars_used) + list(recursive_vars_used)):
                if str(param_var) in all_param_vars:
                    Logger.log_message(None, -1, "\tCopying parameter with name " + str(param_var) + " from synapse to neuron", None, LoggingLevel.INFO)
                    param_from_syn_to_neuron(param_var, new_synapse.get_parameter_blocks(), new_neuron.get_parameter_blocks(), var_name_suffix, mode="copy")

            new_neuron.recursive_vars_used = recursive_vars_used


            #
            #     rename neuron
            #

            name_separator_str = "__with_"

            new_neuron_name = neuron.get_name() + name_separator_str + synapse.get_name()
            # self.analytic_solver[new_neuron_name] = self.analytic_solver[neuron.get_name()]
            # self.numeric_solver[new_neuron_name] = self.numeric_solver[neuron.get_name()]
            new_neuron.set_name(new_neuron_name)
            new_neuron.paired_synapse = new_synapse

            #
            #    rename synapse
            #

            new_synapse_name = synapse.get_name() + name_separator_str + neuron.get_name()
            # self.analytic_solver[new_synapse_name] = self.analytic_solver[synapse.get_name()]
            # self.numeric_solver[new_synapse_name] = self.numeric_solver[synapse.get_name()]
            new_synapse.set_name(new_synapse_name)
            new_synapse.paired_neuron = new_neuron
            new_neuron.paired_synapse = new_synapse

            #
            #    add modified versions of neuron and synapse to list
            #

            new_neuron.accept(ASTSymbolTableVisitor())
            new_synapse.accept(ASTSymbolTableVisitor())

            self.update_blocktype_for_common_parameters(new_synapse)

            # neurons = [new_neuron]
            # synapses = [new_synapse]  # XXX: only generate this neuron-synapse pair, and nothing else!
            neurons.append(new_neuron)
            synapses.append(new_synapse)

            Logger.log_message(None, -1, "Successfully constructed neuron-synapse pair " + new_neuron.name + ", " + new_synapse.name, None, LoggingLevel.INFO)

        #import pdb;pdb.set_trace()

        # remove those original synapses models that have been paired with a neuron
        synapses_ = []
        for synapse in synapses:
            if synapse not in paired_synapses:
                synapses_.append(synapse)
        synapses = synapses_

        return neurons, synapses

    def generate_code(self, neurons: List[ASTNeuron], synapses: List[ASTSynapse]) -> None:
        if self._options and "neuron_synapse_pairs" in self._options:
            neurons, synapses = self.analyse_transform_neuron_synapse_pairs(neurons, synapses)
        self.analyse_transform_neurons(neurons)
        self.analyse_transform_synapses(synapses)
        self.generate_neurons(neurons)
        self.generate_synapses(synapses)
        self.generate_module_code(neurons, synapses)

    def generate_module_code(self, neurons: Sequence[ASTNeuron], synapses: Sequence[ASTSynapse]):
        """
        Generates code that is necessary to integrate neuron models into the NEST infrastructure.
        :param neurons: a list of neurons
        :type neurons: list(ASTNeuron)
        """
        namespace = self._get_module_namespace(neurons, synapses)
        if not os.path.exists(FrontendConfiguration.get_target_path()):
            os.makedirs(FrontendConfiguration.get_target_path())

        for _module_templ in self._module_templates:
            file_name_parts = os.path.basename(_module_templ.filename).split('.')
            file_extension = file_name_parts[-2]
            if file_extension in ['cpp', 'h']:
                filename = FrontendConfiguration.get_module_name()
            else:
                filename = file_name_parts[0]

            file_path = str(os.path.join(FrontendConfiguration.get_target_path(), filename))
            with open(file_path + '.' + file_extension, 'w+') as f:
                f.write(str(_module_templ.render(namespace)))

        code, message = Messages.get_module_generated(FrontendConfiguration.get_target_path())
        Logger.log_message(None, code, message, None, LoggingLevel.INFO)

    def _get_module_namespace(self, neurons: List[ASTNeuron], synapses: List[ASTSynapse]) -> Dict:
        """
        Creates a namespace for generating NEST extension module code
        :param neurons: List of neurons
        :return: a context dictionary for rendering templates
        """
        namespace = {'neurons': neurons,
                     'synapses': synapses,
                     'moduleName': FrontendConfiguration.get_module_name(),
                     'now': datetime.datetime.utcnow()}
        return namespace

    def analyse_transform_neurons(self, neurons: List[ASTNeuron]) -> None:
        """
        Analyse and transform a list of neurons.
        :param neurons: a list of neurons.
        """
        for neuron in neurons:
            code, message = Messages.get_analysing_transforming_neuron(neuron.get_name())
            Logger.log_message(None, code, message, None, LoggingLevel.INFO)
            spike_updates, post_spike_updates = self.analyse_neuron(neuron)
            neuron.spike_updates = spike_updates
            neuron.post_spike_updates = post_spike_updates

    def analyse_transform_synapses(self, synapses):
        # type: (list(ASTsynapse)) -> None
        """
        Analyse and transform a list of synapses.
        :param synapses: a list of synapses.
        """
        for synapse in synapses:
            if Logger.logging_level == LoggingLevel.INFO:
                print("Analysing/transforming synapse {}.".format(synapse.get_name()))
            spike_updates, post_spike_updates = self.analyse_synapse(synapse)
            synapse.spike_updates = spike_updates

    def analyse_neuron(self, neuron: ASTNeuron) -> List[ASTAssignment]:
        """
        Analyse and transform a single neuron.
        :param neuron: a single neuron.
        :return: spike_updates: list of spike updates, see documentation for get_spike_update_expressions() for more information.
        """
        code, message = Messages.get_start_processing_model(neuron.get_name())
        Logger.log_message(neuron, code, message, neuron.get_source_position(), LoggingLevel.INFO)

        equations_block = neuron.get_equations_block()

        if equations_block is None:
            from pynestml.utils.ast_utils import ASTUtils
            # add all declared state variables as none of them are used in equations block
            self.non_equations_state_variables[neuron.get_name()] = []
            self.non_equations_state_variables[neuron.get_name()].extend(ASTUtils.all_variables_defined_in_block(neuron.get_state_blocks()))

            return [], []

        delta_factors = ASTTransformers.get_delta_factors_(neuron, equations_block)
        kernel_buffers = ASTTransformers.generate_kernel_buffers_(neuron, equations_block)
        ASTTransformers.replace_convolve_calls_with_buffers_(neuron, equations_block)
        ASTTransformers.make_inline_expressions_self_contained(equations_block.get_inline_expressions())
        ASTTransformers.replace_inline_expressions_through_defining_expressions(
            equations_block.get_ode_equations(), equations_block.get_inline_expressions())

        analytic_solver, numeric_solver = self.ode_toolbox_analysis(neuron, kernel_buffers)
        self.analytic_solver[neuron.get_name()] = analytic_solver
        self.numeric_solver[neuron.get_name()] = numeric_solver

        self.non_equations_state_variables[neuron.get_name()] = []
        for decl in neuron.get_state_blocks().get_declarations():
            for var in decl.get_variables():
                # check if this variable is not in equations
                if not neuron.get_equations_blocks():
                    self.non_equations_state_variables[neuron.get_name()].append(var)
                    continue

                used_in_eq = False
                for ode_eq in neuron.get_equations_blocks().get_ode_equations():
                    if ode_eq.get_lhs().get_name() == var.get_name():
                        used_in_eq = True
                        break
                for kern in neuron.get_equations_blocks().get_kernels():
                    for kern_var in kern.get_variables():
                        if kern_var.get_name() == var.get_name():
                            used_in_eq = True
                            break

                if not used_in_eq:
                    self.non_equations_state_variables[neuron.get_name()].append(var)

        ASTTransformers.remove_initial_values_for_kernels(neuron)
        kernels = ASTTransformers.remove_kernel_definitions_from_equations_block(neuron)
        ASTTransformers.update_initial_values_for_odes(neuron, [analytic_solver, numeric_solver])
        ASTTransformers.remove_ode_definitions_from_equations_block(neuron)
        ASTTransformers.create_initial_values_for_kernels(neuron, [analytic_solver, numeric_solver], kernels)
        ASTTransformers.replace_variable_names_in_expressions(neuron, [analytic_solver, numeric_solver])
        ASTTransformers.replace_convolution_aliasing_inlines(neuron)
        ASTTransformers.add_timestep_symbol(neuron)

        if self.analytic_solver[neuron.get_name()] is not None:
            neuron = ASTTransformers.add_declarations_to_internals(neuron, self.analytic_solver[neuron.get_name()]["propagators"])

        self.update_symbol_table(neuron, kernel_buffers)
        spike_updates, post_spike_updates = self.get_spike_update_expressions(
            neuron, kernel_buffers, [analytic_solver, numeric_solver], delta_factors)

        return spike_updates, post_spike_updates

    def analyse_synapse(self, synapse: ASTSynapse) -> None:
        """
        Analyse and transform a single synapse.
        :param synapse: a single synapse.
        """
        code, message = Messages.get_start_processing_model(synapse.get_name())
        Logger.log_message(synapse, code, message, synapse.get_source_position(), LoggingLevel.INFO)

        equations_block = synapse.get_equations_block()
        spike_updates, post_spike_updates = [], []
        if equations_block is not None:
            delta_factors = ASTTransformers.get_delta_factors_(synapse, equations_block)
            kernel_buffers = ASTTransformers.generate_kernel_buffers_(synapse, equations_block)
            # print("kernel_buffers = " + str([(str(a), str(b)) for a, b in kernel_buffers]))
            ASTTransformers.replace_convolve_calls_with_buffers_(synapse, equations_block)

            # print("NEST codegenerator step 0...")
            # self.mark_kernel_variable_symbols(synapse, kernel_buffers)

            # print("NEST codegenerator step 3...")
            # self.update_symbol_table(synapse, kernel_buffers)

            # print("NEST codegenerator: replacing functions through defining expressions...")
            ASTTransformers.make_inline_expressions_self_contained(equations_block.get_inline_expressions())
            ASTTransformers.replace_inline_expressions_through_defining_expressions(equations_block.get_ode_equations(), equations_block.get_inline_expressions())

            analytic_solver, numeric_solver = self.ode_toolbox_analysis(synapse, kernel_buffers)
            self.analytic_solver[synapse.get_name()] = analytic_solver
            self.numeric_solver[synapse.get_name()] = numeric_solver

            ASTTransformers.remove_initial_values_for_kernels(synapse)
            kernels = ASTTransformers.remove_kernel_definitions_from_equations_block(synapse)
            ASTTransformers.update_initial_values_for_odes(synapse, [analytic_solver, numeric_solver])
            ASTTransformers.remove_ode_definitions_from_equations_block(synapse)
            ASTTransformers.create_initial_values_for_kernels(synapse, [analytic_solver, numeric_solver], kernels)
            ASTTransformers.replace_variable_names_in_expressions(synapse, [analytic_solver, numeric_solver])
            ASTTransformers.add_timestep_symbol(synapse)
            self.update_symbol_table(synapse, kernel_buffers)

            # print("NEST codegenerator: Adding ode-toolbox processed kernels to AST...")
            # self.add_kernel_odes(synapse, [analytic_solver, numeric_solver], kernel_buffers)
            # self.replace_convolve_calls_with_buffers_(synapse, equations_block, kernel_buffers)

            if not self.analytic_solver[synapse.get_name()] is None:
                # print("NEST codegenerator: Adding propagators...")
                synapse = ASTTransformers.add_declarations_to_internals(synapse, self.analytic_solver[synapse.get_name()]["propagators"])

            self.update_symbol_table(synapse, kernel_buffers)
            # self.remove_kernel_definitions_from_equations_block(synapse, self.analytic_solver["state_variables"])

            # if not self.numeric_solver is None:
            #     functional_kernels_to_odes(synapse, self.numeric_solver)

            # update kernel buffers in case direct functions of time have been replaced by higher-order differential

            # print("NEST codegenerator step 5...")
            self.update_symbol_table(synapse, kernel_buffers)

            # print("NEST codegenerator step 6...")
            spike_updates, post_spike_updates = self.get_spike_update_expressions(synapse, kernel_buffers, [analytic_solver, numeric_solver], delta_factors)
        else:
            ASTTransformers.add_timestep_symbol(synapse)

        self.update_blocktype_for_common_parameters(synapse)

        return spike_updates, post_spike_updates

    def generate_neuron_code(self, neuron: ASTNeuron) -> None:
        """
        For a handed over neuron, this method generates the corresponding header and implementation file.
        :param neuron: a single neuron object.
        """
        if not os.path.isdir(FrontendConfiguration.get_target_path()):
            os.makedirs(FrontendConfiguration.get_target_path())
        for _model_templ in self._model_templates["neuron"]:
            file_extension = _model_templ.filename.split('.')[-2]
            _file = _model_templ.render(self._get_neuron_model_namespace(neuron))
            with open(str(os.path.join(FrontendConfiguration.get_target_path(),
                                       neuron.get_name())) + '.' + file_extension, 'w+') as f:
                f.write(str(_file))

    def generate_synapse_code(self, synapse: ASTSynapse) -> None:
        """
        For a handed over synapse, this method generates the corresponding header and implementation file.
        :param synapse: a single synapse object.
        """
        if not os.path.isdir(FrontendConfiguration.get_target_path()):
            os.makedirs(FrontendConfiguration.get_target_path())
        for _model_templ in self._model_templates["synapse"]:
            file_extension = _model_templ.filename.split('.')[-2]
            _file = _model_templ.render(self._get_synapse_model_namespace(synapse))
            with open(str(os.path.join(FrontendConfiguration.get_target_path(),
                                       synapse.get_name())) + '.' + file_extension, 'w+') as f:
                f.write(str(_file))

    def _get_synapse_model_namespace(self, synapse: ASTSynapse) -> Dict:
        """
        Returns a standard namespace with often required functionality.
        :param synapse: a single synapse instance
        :return: a map from name to functionality.
        :rtype: dict
        """
        from pynestml.utils.ast_utils import ASTUtils
        gsl_converter = GSLReferenceConverter()
        gsl_printer = UnitlessExpressionPrinter(gsl_converter)
        # helper classes and objects
        converter = NESTReferenceConverter(False)
        unitless_pretty_printer = UnitlessExpressionPrinter(converter)

        namespace = dict()

        if 'paired_neuron' in dir(synapse):
            # synapse is being co-generated with neuron
            namespace['paired_neuron'] = synapse.paired_neuron.get_name()
            base_neuron_name = namespace['paired_neuron'][:namespace['paired_neuron'].index("__with_") - len(FrontendConfiguration.suffix)]
            base_synapse_name = synapse.name[:synapse.name.index("__with_") - len(FrontendConfiguration.suffix)]
            namespace["post_ports"] = self.get_post_port_names(synapse, base_neuron_name, base_synapse_name)
            namespace["spiking_post_ports"] = self.get_spiking_post_port_names(synapse, base_neuron_name, base_synapse_name)
            namespace["vt_ports"] = self.get_vt_port_names(synapse, base_neuron_name, base_synapse_name)
            all_input_port_names = [p.name for p in synapse.get_input_blocks().get_input_ports()]
            namespace["pre_ports"] = list(set(all_input_port_names) - set(namespace["post_ports"]) - set(namespace["vt_ports"]))
        else:
            # separate (not neuron+synapse co-generated)
            all_input_port_names = [p.name for p in synapse.get_input_blocks().get_input_ports()]
            namespace["pre_ports"] = all_input_port_names

        assert len(namespace["pre_ports"]) <= 1, "Synapses only support one spiking input port"

        namespace['synapseName'] = synapse.get_name()
        namespace['synapse'] = synapse
        namespace['astnode'] = synapse
        namespace['moduleName'] = FrontendConfiguration.get_module_name()
        namespace['printer'] = NestPrinter(unitless_pretty_printer)
        namespace['assignments'] = NestAssignmentsHelper()
        namespace['names'] = NestNamesConverter()
        namespace['declarations'] = NestDeclarationsHelper()
        namespace['utils'] = ASTUtils
        namespace['idemPrinter'] = UnitlessExpressionPrinter()
        namespace['odeTransformer'] = OdeTransformer()
        namespace['printerGSL'] = gsl_printer
        namespace['now'] = datetime.datetime.utcnow()
        namespace['tracing'] = FrontendConfiguration.is_dev

        # event handlers priority
        # XXX: this should be refactored in case we have additional modulatory (3rd-factor) spiking input ports in the synapse
        namespace['pre_before_post_update'] = 0   # C++-compatible boolean...
        spiking_post_port = find_spiking_post_port(synapse, namespace)
        if spiking_post_port:
            post_spike_port_priority = None
            if "priority" in synapse.get_on_receive_block(spiking_post_port).get_const_parameters().keys():
                post_spike_port_priority = int(synapse.get_on_receive_block(spiking_post_port).get_const_parameters()["priority"])

            if post_spike_port_priority \
                    and len(namespace["pre_ports"]) and len(namespace["post_ports"]) \
                    and "priority" in synapse.get_on_receive_block(namespace["pre_ports"][0]).get_const_parameters().keys() \
                    and int(synapse.get_on_receive_block(namespace["pre_ports"][0]).get_const_parameters()["priority"]) < post_spike_port_priority:
                namespace['pre_before_post_update'] = 1   # C++-compatible boolean...

        namespace['PredefinedUnits'] = pynestml.symbols.predefined_units.PredefinedUnits
        namespace['UnitTypeSymbol'] = pynestml.symbols.unit_type_symbol.UnitTypeSymbol
        namespace['SymbolKind'] = pynestml.symbols.symbol.SymbolKind

        namespace['initial_values'] = {}
        namespace['uses_analytic_solver'] = synapse.get_name() in self.analytic_solver.keys() \
            and self.analytic_solver[synapse.get_name()] is not None
        if namespace['uses_analytic_solver']:
            namespace['analytic_state_variables'] = self.analytic_solver[synapse.get_name()]["state_variables"]
            namespace['analytic_variable_symbols'] = {sym: synapse.get_equations_block().get_scope().resolve_to_symbol(
                sym, SymbolKind.VARIABLE) for sym in namespace['analytic_state_variables']}
            namespace['update_expressions'] = {}
            for sym, expr in self.analytic_solver[synapse.get_name()]["initial_values"].items():
                namespace['initial_values'][sym] = expr
            for sym in namespace['analytic_state_variables']:
                expr_str = self.analytic_solver[synapse.get_name()]["update_expressions"][sym]
                expr_ast = ModelParser.parse_expression(expr_str)
                # pretend that update expressions are in "equations" block, which should always be present, as differential equations must have been defined to get here
                expr_ast.update_scope(synapse.get_equations_blocks().get_scope())
                expr_ast.accept(ASTSymbolTableVisitor())
                namespace['update_expressions'][sym] = expr_ast

            namespace['propagators'] = self.analytic_solver[synapse.get_name()]["propagators"]

        namespace['uses_numeric_solver'] = synapse.get_name() in self.numeric_solver.keys() \
            and self.numeric_solver[synapse.get_name()] is not None
        if namespace['uses_numeric_solver']:
            namespace['numeric_state_variables'] = self.numeric_solver[synapse.get_name()]["state_variables"]
            namespace['numeric_variable_symbols'] = {sym: synapse.get_equations_block().get_scope().resolve_to_symbol(
                sym, SymbolKind.VARIABLE) for sym in namespace['numeric_state_variables']}
            assert not any([sym is None for sym in namespace['numeric_variable_symbols'].values()])
            namespace['numeric_update_expressions'] = {}
            for sym, expr in self.numeric_solver[synapse.get_name()]["initial_values"].items():
                namespace['initial_values'][sym] = expr
            for sym in namespace['numeric_state_variables']:
                expr_str = self.numeric_solver[synapse.get_name()]["update_expressions"][sym]
                expr_ast = ModelParser.parse_expression(expr_str)
                # pretend that update expressions are in "equations" block, which should always be present, as differential equations must have been defined to get here
                expr_ast.update_scope(synapse.get_equations_blocks().get_scope())
                expr_ast.accept(ASTSymbolTableVisitor())
                namespace['numeric_update_expressions'][sym] = expr_ast

            namespace['useGSL'] = namespace['uses_numeric_solver']
            namespace['names'] = GSLNamesConverter()
            converter = NESTReferenceConverter(True)
            unitless_pretty_printer = UnitlessExpressionPrinter(converter)
            namespace['printer'] = NestPrinter(unitless_pretty_printer)

        namespace["spike_updates"] = synapse.spike_updates

        rng_visitor = ASTRandomNumberGeneratorVisitor()
        synapse.accept(rng_visitor)
        namespace['norm_rng'] = rng_visitor._norm_rng_is_used

        namespace["PyNestMLLexer"] = {}
        from pynestml.generated.PyNestMLLexer import PyNestMLLexer
        for kw in dir(PyNestMLLexer):
            if kw.isupper():
                namespace["PyNestMLLexer"][kw] = eval("PyNestMLLexer." + kw)

        return namespace

    def _get_neuron_model_namespace(self, neuron: ASTNeuron) -> Dict:
        """
        Returns a standard namespace with often required functionality.
        :param neuron: a single neuron instance
        :type neuron: ASTNeuron
        :return: a map from name to functionality.
        :rtype: dict
        """
        from pynestml.utils.ast_utils import ASTUtils
        gsl_converter = GSLReferenceConverter()
        gsl_printer = UnitlessExpressionPrinter(gsl_converter)
        # helper classes and objects
        converter = NESTReferenceConverter(False)
        unitless_pretty_printer = UnitlessExpressionPrinter(converter)

        namespace = dict()

        if 'paired_synapse' in dir(neuron):
            namespace['paired_synapse'] = neuron.paired_synapse.get_name()
            namespace["post_spike_updates"] = neuron.post_spike_updates
            if "moved_spike_updates" in dir(neuron):
                namespace["spike_update_stmts"] = neuron.moved_spike_updates
            else:
                namespace["spike_update_stmts"] = []
            namespace['transferred_variables'] = neuron._transferred_variables
            namespace['transferred_variables_syms'] = {var_name: neuron.scope.resolve_to_symbol(var_name, SymbolKind.VARIABLE) for var_name in namespace['transferred_variables']}
            # {var_name: ASTUtils.get_declaration_by_name(neuron.get_initial_values_blocks(), var_name) for var_name in namespace['transferred_variables']}
        namespace['neuronName'] = neuron.get_name()
        namespace['neuron'] = neuron
        namespace['astnode'] = neuron
        namespace['moduleName'] = FrontendConfiguration.get_module_name()
        namespace['printer'] = NestPrinter(unitless_pretty_printer)
        namespace['assignments'] = NestAssignmentsHelper()
        namespace['names'] = NestNamesConverter()
        namespace['declarations'] = NestDeclarationsHelper()
        namespace['utils'] = ASTUtils
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
            namespace['analytic_state_variables_moved'] = []
            if 'paired_synapse' in dir(neuron):
                namespace['analytic_state_variables'] = []
                for sv in self.analytic_solver[neuron.get_name()]["state_variables"]:
                    moved = False
                    for mv in neuron.recursive_vars_used:
                        name_snip = mv + "__"
                        if name_snip == sv[:len(name_snip)]:
                            # this variable was moved from synapse to neuron
                            if not sv in namespace['analytic_state_variables_moved']:
                                namespace['analytic_state_variables_moved'].append(sv)
                                moved = True
                    if not moved:
                        namespace['analytic_state_variables'].append(sv)
                        print("analytic_state_variables: " + str(namespace['analytic_state_variables']))
                namespace['analytic_variable_symbols_moved'] = {sym: neuron.get_equations_block().get_scope().resolve_to_symbol(
                    sym, SymbolKind.VARIABLE) for sym in namespace['analytic_state_variables_moved']}
            else:
                namespace['analytic_state_variables'] = self.analytic_solver[neuron.get_name()]["state_variables"]
            namespace['analytic_variable_symbols'] = {sym: neuron.get_equations_block().get_scope().resolve_to_symbol(
                sym, SymbolKind.VARIABLE) for sym in namespace['analytic_state_variables']}

            namespace['update_expressions'] = {}
            for sym, expr in self.analytic_solver[neuron.get_name()]["initial_values"].items():
                namespace['initial_values'][sym] = expr
            for sym in namespace['analytic_state_variables'] + namespace['analytic_state_variables_moved']:
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

            namespace['numeric_state_variables_moved'] = []
            if 'paired_synapse' in dir(neuron):
                namespace['numeric_state_variables'] = []
                for sv in self.numeric_solver[neuron.get_name()]["state_variables"]:
                    moved = False
                    for mv in neuron.recursive_vars_used:
                        name_snip = mv + "__"
                        if name_snip == sv[:len(name_snip)]:
                            # this variable was moved from synapse to neuron
                            if not sv in namespace['numeric_state_variables_moved']:
                                namespace['numeric_state_variables_moved'].append(sv)
                                moved = True
                    if not moved:
                        namespace['numeric_state_variables'].append(sv)
                namespace['numeric_variable_symbols_moved'] = {sym: neuron.get_equations_block().get_scope().resolve_to_symbol(
                    sym, SymbolKind.VARIABLE) for sym in namespace['numeric_state_variables_moved']}
            else:
                namespace['numeric_state_variables'] = self.numeric_solver[neuron.get_name()]["state_variables"]

            namespace['numeric_variable_symbols'] = {sym: neuron.get_equations_block().get_scope().resolve_to_symbol(
                sym, SymbolKind.VARIABLE) for sym in namespace['numeric_state_variables']}
            assert not any([sym is None for sym in namespace['numeric_variable_symbols'].values()])
            for sym, expr in self.numeric_solver[neuron.get_name()]["initial_values"].items():
                namespace['initial_values'][sym] = expr
            namespace['numeric_update_expressions'] = {}
            for sym in namespace['numeric_state_variables'] + namespace['numeric_state_variables_moved']:
                expr_str = self.numeric_solver[neuron.get_name()]["update_expressions"][sym]
                expr_ast = ModelParser.parse_expression(expr_str)
                # pretend that update expressions are in "equations" block, which should always be present, as differential equations must have been defined to get here
                expr_ast.update_scope(neuron.get_equations_blocks().get_scope())
                expr_ast.accept(ASTSymbolTableVisitor())
                namespace['numeric_update_expressions'][sym] = expr_ast

            if namespace['uses_numeric_solver']:
                if 'analytic_state_variables_moved' in namespace.keys():
                    namespace['purely_numeric_state_variables_moved'] = list(set(namespace['numeric_state_variables_moved']) - set(namespace['analytic_state_variables_moved']))
                else:
                    namespace['purely_numeric_state_variables_moved'] = namespace['numeric_state_variables_moved']

            namespace['useGSL'] = namespace['uses_numeric_solver']
            namespace['names'] = GSLNamesConverter()
            converter = NESTReferenceConverter(True)
            unitless_pretty_printer = UnitlessExpressionPrinter(converter)
            namespace['printer'] = NestPrinter(unitless_pretty_printer)
        namespace["spike_updates"] = neuron.spike_updates

        namespace["recordable_state_variables"] = [sym for sym in neuron.get_state_symbols()
                                                   if namespace['declarations'].get_domain_from_type(sym.get_type_symbol()) == "double"
                                                   and sym.is_recordable and not ASTTransformers.is_delta_kernel(neuron.get_kernel_by_name(sym.name))]
        namespace["recordable_inline_expressions"] = [sym for sym in neuron.get_inline_expression_symbols()
                                                      if namespace['declarations'].get_domain_from_type(sym.get_type_symbol()) == "double"
                                                      and sym.is_recordable]

        namespace["parameter_syms_with_iv"] = [sym for sym in neuron.get_parameter_symbols()
                                               if sym.has_declaring_expression()
                                               and (not neuron.get_kernel_by_name(sym.name))]

        rng_visitor = ASTRandomNumberGeneratorVisitor()
        neuron.accept(rng_visitor)
        namespace['norm_rng'] = rng_visitor._norm_rng_is_used

        return namespace

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
        odetoolbox_indict = ASTTransformers.transform_ode_and_kernels_to_json(neuron, parameters_block, kernel_buffers)
        odetoolbox_indict["options"] = {}
        odetoolbox_indict["options"]["output_timestep_symbol"] = "__h"
        solver_result = analysis(odetoolbox_indict,
                                 disable_stiffness_check=True,
                                 preserve_expressions=self.get_option('preserve_expressions'),
                                 simplify_expression=self.get_option('simplify_expression'),
                                 log_level=FrontendConfiguration.logging_level)
        analytic_solver = None
        analytic_solvers = [x for x in solver_result if x["solver"] == "analytical"]
        assert len(analytic_solvers) <= 1, "More than one analytic solver not presently supported"
        if len(analytic_solvers) > 0:
            analytic_solver = analytic_solvers[0]

        # if numeric solver is required, generate a stepping function that includes each state variable
        numeric_solver = None
        numeric_solvers = [x for x in solver_result if x["solver"].startswith("numeric")]
        if numeric_solvers:
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

    def update_symbol_table(self, neuron, kernel_buffers):
        """
        Update symbol table and scope.
        """
        SymbolTable.delete_neuron_scope(neuron.get_name())
        symbol_table_visitor = ASTSymbolTableVisitor()
        symbol_table_visitor.after_ast_rewrite_ = True
        neuron.accept(symbol_table_visitor)
        SymbolTable.add_neuron_scope(neuron.get_name(), neuron.get_scope())

    def get_spike_update_expressions(self, neuron: ASTNeuron, kernel_buffers, solver_dicts, delta_factors) -> List[ASTAssignment]:
        """
        Generate the equations that update the dynamical variables when incoming spikes arrive. To be invoked after ode-toolbox.

        For example, a resulting `assignment_str` could be "I_kernel_in += (in_spikes/nS) * 1". The values are taken from the initial values for each corresponding dynamical variable, either from ode-toolbox or directly from user specification in the model.

        Note that for kernels, `initial_values` actually contains the increment upon spike arrival, rather than the initial value of the corresponding ODE dimension.
        """
        spike_updates = []
        post_spike_updates = {}

        for kernel, spike_input_port in kernel_buffers:
            if ASTTransformers.is_delta_kernel(kernel):
                continue

            if "_is_post_port" in dir(spike_input_port.get_variable()) \
               and spike_input_port.get_variable()._is_post_port:
                # it's a port in the neuron ??? that receives post spikes ???
                orig_port_name = str(spike_input_port)[:str(spike_input_port).index("__for_")]
                buffer_type = neuron.paired_synapse.get_scope().resolve_to_symbol(orig_port_name, SymbolKind.VARIABLE).get_type_symbol()
            else:
                buffer_type = neuron.get_scope().resolve_to_symbol(str(spike_input_port), SymbolKind.VARIABLE).get_type_symbol()

            assert not buffer_type is None

            for kernel_var in kernel.get_variables():
                for var_order in range(ASTTransformers.get_kernel_var_order_from_ode_toolbox_result(kernel_var.get_name(), solver_dicts)):
                    kernel_spike_buf_name = ASTTransformers.construct_kernel_X_spike_buf_name(
                        kernel_var.get_name(), spike_input_port, var_order)
                    expr = ASTTransformers.get_initial_value_from_ode_toolbox_result(kernel_spike_buf_name, solver_dicts)
                    assert expr is not None, "Initial value not found for kernel " + kernel_var
                    expr = str(expr)
                    if expr in ["0", "0.", "0.0"]:
                        continue    # skip adding the statement if we're only adding zero

                    assignment_str = kernel_spike_buf_name + " += "
                    if "_is_post_port" in dir(spike_input_port.get_variable()) \
                       and spike_input_port.get_variable()._is_post_port:
                        assignment_str += "1."
                    else:
                        assignment_str += "(" + str(spike_input_port) + ")"
                    if not expr in ["1.", "1.0", "1"]:
                        assignment_str += " * (" + \
                            self._printer.print_expression(ModelParser.parse_expression(expr)) + ")"

                    if not buffer_type.print_nestml_type() in ["1.", "1.0", "1", "real", "integer"]:
                        assignment_str += " / (" + buffer_type.print_nestml_type() + ")"

                    ast_assignment = ModelParser.parse_assignment(assignment_str)
                    ast_assignment.update_scope(neuron.get_scope())
                    ast_assignment.accept(ASTSymbolTableVisitor())

                    if neuron.get_scope().resolve_to_symbol(str(spike_input_port), SymbolKind.VARIABLE) is None:
                        # this case covers variables that were moved from synapse to the neuron
                        post_spike_updates[kernel_var.get_name()] = ast_assignment
                    elif "_is_post_port" in dir(spike_input_port.get_variable()) and spike_input_port.get_variable()._is_post_port:
                        print("adding post assignment string: " + str(ast_assignment))
                        spike_updates.append(ast_assignment)
                    else:
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

        return spike_updates, post_spike_updates

