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
from typing import Optional

from jinja2 import Environment, FileSystemLoader, TemplateRuntimeError
from odetoolbox import analysis

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
from pynestml.meta_model.ast_declaration import ASTDeclaration
from pynestml.meta_model.ast_equations_block import ASTEquationsBlock
from pynestml.meta_model.ast_node_factory import ASTNodeFactory
from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.meta_model.ast_ode_shape import ASTOdeShape
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.solver.solution_transformers import integrate_exact_solution, functional_shapes_to_odes
from pynestml.solver.transformer_base import add_assignment_to_update_block, add_declarations_to_internals
from pynestml.solver.transformer_base import add_declaration_to_initial_values, declaration_in_initial_values
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.symbols.symbol import SymbolKind
from pynestml.symbols.variable_symbol import VariableType, VariableSymbol
from pynestml.utils.ast_utils import ASTUtils
from pynestml.utils.logger import Logger
from pynestml.utils.logger import LoggingLevel
from pynestml.utils.messages import Messages
from pynestml.utils.model_parser import ModelParser
from pynestml.utils.ode_transformer import OdeTransformer
from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor
from pynestml.symbol_table.symbol_table import SymbolTable
from pynestml.symbols.variable_symbol import BlockType
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.visitors.ast_higher_order_visitor import ASTHigherOrderVisitor
#from pynestml.visitors.ast_symbol_table_visitor import assign_ode_to_variables


def variable_in_neuron_initial_values(name: str, neuron: ASTNeuron):
    for decl in neuron.get_initial_blocks().get_declarations():
        assert len(decl.get_variables()) == 1, "Multiple declarations in the same statement not yet supported"
        if decl.get_variables()[0].get_complete_name() == name:
            return True
    return False


def variable_in_solver(shape_var: str, solver_dicts):
    """Check if a variable by this name is defined in the ode-toolbox solver results
    """

    for solver_dict in solver_dicts:
        if solver_dict is None:
            continue

        for var_name in solver_dict["state_variables"]:
            var_name_base = var_name.split("__X__")[0]
            #var_name_base = var_name_base.split("__d")[0]
            if var_name_base == shape_var:
                return True

    return False

def is_ode_variable(var_base_name, neuron):
    equations_block = neuron.get_equations_blocks()
    for ode_eq in equations_block.get_ode_equations():
        var = ode_eq.get_lhs()
        if var.get_name() == var_base_name:
            return True
    return False


def variable_in_shapes(var_name: str, shapes):
    """Check if a variable by this name (in ode-toolbox style) is defined in the ode-toolbox solver results
    """

    var_name_base = var_name.split("__X__")[0]
    var_name_base = var_name_base.split("__d")[0]
    var_name_base = var_name_base.replace("__DOLLAR", "$")

    for shape in shapes:
        for shape_var in shape.get_variables():
            if var_name_base == shape_var.get_name():
                return True

    return False


def get_initial_value_from_odetb_result(var_name: str, solver_dicts):
    """Get the initial value of the variable with the given name from the ode-toolbox results JSON.

    N.B. the variable name is given in ode-toolbox notation.
    """

    order = -1
    for solver_dict in solver_dicts:
        if solver_dict is None:
            continue

        if var_name in solver_dict["state_variables"]:
            return solver_dict["initial_values"][var_name]

    assert False, "Initial value not found for ODE with name \"" + var_name + "\""


def get_shape_var_order_from_ode_toolbox_result(shape_var: str, solver_dicts):
    """Get the differential order of the variable with the given name from the ode-toolbox results JSON.

    N.B. the variable name is given in NESTML notation, e.g. "g_in$"; convert to ode-toolbox export format notation (e.g. "g_in__DOLLAR").
    """

    shape_var = shape_var.replace("$", "__DOLLAR")

    order = -1
    for solver_dict in solver_dicts:
        if solver_dict is None:
            continue

        for var_name in solver_dict["state_variables"]:
            var_name_base = var_name.split("__X__")[0]
            var_name_base = var_name_base.split("__d")[0]
            if var_name_base == shape_var:
                order = max(order, var_name.count("__d") + 1)

    assert order >= 0, "Variable of name \"" + shape_var + "\" not found in ode-toolbox result"
    return order


def to_odetb_processed_name(name: str) -> str:
    """convert name in the same way as ode-toolbox does from input to output, i.e. returned names are compatible with ode-toolbox output"""
    return name.replace("$", "__DOLLAR").replace("'", "__d")

def to_odetb_name(name: str) -> str:
    """convert to a name suitable for ode-toolbox input"""
    return name.replace("$", "__DOLLAR")


def get_expr_from_shape_var(shape, var_name):
    assert type(var_name) == str
    for var, expr in zip(shape.get_variables(), shape.get_expressions()):
        if var.get_complete_name() == var_name:
            return expr
    assert False, "variable name not found in shape"


def construct_shape_X_spike_buf_name(shape_var_name: str, spike_input_port, order: int, diff_order_symbol="__d"):
    assert type(shape_var_name) is str
    assert type(order) is int
    assert type(diff_order_symbol) is str
    return shape_var_name.replace("$", "__DOLLAR") + "__X__" + str(spike_input_port) + diff_order_symbol * order


def replace_rhs_variable(expr, variable_name_to_replace, shape_var, spike_buf):
    def replace_shape_var(node):
        if type(node) is ASTSimpleExpression \
            and node.is_variable() \
            and node.get_variable().get_name() == variable_name_to_replace:
            #replace_with.update_scope(node.get_scope())
            #replace_with.accept(ASTSymbolTableVisitor())
            var_order = node.get_variable().get_differential_order()
            new_variable_name = construct_shape_X_spike_buf_name(shape_var.get_name(), spike_buf, var_order - 1, diff_order_symbol="'")
            new_variable = ASTVariable(new_variable_name, var_order)
            new_variable.set_source_position(node.get_variable().get_source_position())
            #print("Replacing variable " + str(node.get_variable().get_name()) + " with " + str(new_variable_name))
            #print("\t order before = " + str(node.get_variable().get_differential_order()))
            #print("\t scope before = " + str(node.get_scope()))
            #print("\t scope before = " + str(node.get_variable().get_scope()))
            #print("\t source_position before = " + str(shape_var.get_source_position()))
            node.set_variable(new_variable)
            #print("\t order after = " + str(node.get_variable().get_differential_order()))
            #print("\t scope after = " + str(node.get_scope()))
            #print("\t scope after = " + str(node.get_variable().get_scope()))
            #print("\t source_position before = " + str(node.get_variable().get_source_position()))

    expr.accept(ASTHigherOrderVisitor(visit_funcs=replace_shape_var))


def replace_rhs_variables(expr, shape_buffers):
    """
    Replace variable names in definitions of shape dynamics.

    Say that the shape is

    .. code-block::

        G = -G / tau

    Its variable symbol might be replaced by "G__X__spikesEx":

    .. code-block::

        G__X__spikesEx = -G / tau

    This function updates the right-hand side of `expr` so that it would also read (in this example):

    .. code-block::

        G__X__spikesEx = -G__X__spikesEx / tau

    These equations will later on be fed to ode-toolbox, so we use the symbol "'" to indicate differential order.

    Note that for shapes/systems of ODE of dimension > 1, all variable orders and all variables for this shape will already be present in `shape_buffers`.
    """
    for shape, spike_buf in shape_buffers:
        for shape_var in shape.get_variables():
            variable_name_to_replace = shape_var.get_name()
            replace_rhs_variable(expr, variable_name_to_replace=variable_name_to_replace, shape_var=shape_var, spike_buf=spike_buf)


def is_delta_shape(shape):
    """catches definition of shape, or reference (function call or variable name) of a delta shape function"""
    if type(shape) is ASTOdeShape:
        if not len(shape.get_variables()) == 1:
            # delta shape not allowed if more than one variable is defined in this shape
            return False
        expr = shape.get_expressions()[0]
    else:
        expr = shape

    rhs_is_delta_shape = type(expr) is ASTSimpleExpression \
        and expr.is_function_call() \
        and expr.get_function_call().get_scope().resolve_to_symbol(expr.get_function_call().get_name(), SymbolKind.FUNCTION) == PredefinedFunctions.name2function["delta"]
    rhs_is_multiplied_delta_shape = type(expr) is ASTExpression \
        and type(expr.get_rhs()) is ASTSimpleExpression \
        and expr.get_rhs().is_function_call() \
        and expr.get_rhs().get_function_call().get_scope().resolve_to_symbol(expr.get_rhs().get_function_call().get_name(), SymbolKind.FUNCTION) == PredefinedFunctions.name2function["delta"]
    #is_name_of_delta_shape = type(expr) is ASTSimpleExpression \
        #and expr.is_variable() \
        #and expr.get_variable().get_scope().resolve_to_symbol(expr.get_variable().get_name(), SymbolKind.VARIABLE).is_shape() \
        #and expr.
    return rhs_is_delta_shape or rhs_is_multiplied_delta_shape


def get_delta_shape_prefactor_expr(shape):
    assert type(shape) is ASTOdeShape
    assert len(shape.get_variables()) == 1
    expr = shape.get_expressions()[0]
    if type(expr) is ASTExpression \
     and expr.get_rhs().is_function_call() \
     and expr.get_rhs().get_function_call().get_scope().resolve_to_symbol(expr.get_rhs().get_function_call().get_name(), SymbolKind.FUNCTION) == PredefinedFunctions.name2function["delta"] \
     and expr.binary_operator.is_times_op:
        return str(expr.lhs)


class NESTCodeGenerator(CodeGenerator):

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
            spike_updates = self.analyse_neuron(neuron)
            neuron.spike_updates = spike_updates
            # now store the transformed model
            self.store_transformed_model(neuron)


    def get_delta_factors_(self, neuron, equations_block):
        """For every occurrence of a convolution of the form `x^(n) = a * convolve(shape, inport) + ...` where `shape` is a delta function, add the element `(x^(n), inport) --> a` to the set. 
        """

        #gsl_converter = ODEToolboxReferenceConverter()
        #gsl_printer = UnitlessExpressionPrinter(gsl_converter)

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
                    #expr_str = gsl_printer.print_expression(expr)
                    expr_str = str(expr)
                    sympy_expr = sympy.parsing.sympy_parser.parse_expr(expr_str)
                    sympy_expr = sympy.expand(sympy_expr)
                    sympy_conv_expr = sympy.parsing.sympy_parser.parse_expr(str(conv_call))
                    factor_str = []
                    for term in sympy.Add.make_args(sympy_expr):
                        if term.find(sympy_conv_expr):
                            factor_str.append(str(term.replace(sympy_conv_expr, 1)))
                    factor_str = " + ".join(factor_str)
                    #factor = ModelParser.parse_expression(factor_str)
                    #factor.update_scope(neuron.get_scope())
                    #factor.accept(ASTSymbolTableVisitor())
                    delta_factors[(var, inport)] = factor_str

            print("Delta factors = " + str(delta_factors))

        return delta_factors


    def generate_shape_buffers_(self, neuron, equations_block):
        """For every occurrence of a convolution of the form `convolve(var, spike_buf)`: add the element `(shape, spike_buf)` to the set, with `shape` being the shape that contains variable `var`.
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
        """replace all occurrences of variables names in NESTML format (e.g. `g_ex$''`)` with the ode-toolbox formatted variable name (e.g. `g_ex__DOLLAR__d__d`).
        """
        def replace_var(_expr=None):
            #if isinstance(_expr, ASTDeclaration):
                #node = _expr
                #for var in node.get_variables():
                    #if variable_in_solver(to_odetb_processed_name(var.get_complete_name()), solver_dicts):
                        #existing_symbol = node.get_scope().resolve_to_symbol(var.get_complete_name(), SymbolKind.VARIABLE)
                        #existing_symbol.set_variable_type(VariableType.SHAPE)
                        #print("6666 setting symbol to " + var.get_name())

            #el
            if isinstance(_expr, ASTSimpleExpression) and _expr.is_variable():
                var = _expr.get_variable()
                if variable_in_solver(to_odetb_processed_name(var.get_complete_name()), solver_dicts):
                    ast_variable = ASTVariable(to_odetb_processed_name(var.get_complete_name()), differential_order=0)
                    ast_variable.set_source_position(var.get_source_position())
                    #print("\t source_position = " + str(ast_variable.get_source_position()))
                    #print("\t Replacing variable " + var.get_complete_name() + " by " + ast_variable.get_complete_name())
                    _expr.set_variable(ast_variable)
                    
                    #existing_symbol = neuron.get_scope().resolve_to_symbol(ast_variable.get_name(), SymbolKind.VARIABLE)
                    #existing_symbol.set_variable_type(VariableType.SHAPE)
                    
                    #print("1234 setting symbol to " + ast_variable.get_name())


            elif isinstance(_expr, ASTVariable):
                var = _expr
                if variable_in_solver(to_odetb_processed_name(var.get_complete_name()), solver_dicts):
                    #print("\t Replacing variable " + var.get_complete_name() + " by " + to_odetb_processed_name(var.get_complete_name()))
                    var.set_name(to_odetb_processed_name(var.get_complete_name()))
                    var.set_differential_order(0)

                    #existing_symbol = neuron.get_scope().resolve_to_symbol(var.get_name(), SymbolKind.VARIABLE)
                    #existing_symbol.set_variable_type(VariableType.SHAPE)

                    #print("1234 setting symbol to " + var.get_name())


        func = lambda x: replace_var(x)

        neuron.accept(ASTHigherOrderVisitor(func))
        #assert neuron.get_scope().resolve_to_symbol("V_m", SymbolKind.VARIABLE).get_variable_type() is VariableType.SHAPE
        #assert neuron.get_initial_values_blocks().get_scope().resolve_to_symbol("V_m", SymbolKind.VARIABLE).get_variable_type() is VariableType.SHAPE

    def replace_convolve_calls_with_buffers_(self, neuron, equations_block, shape_buffers):
        """replace all occurrences of `convolve(shape[']^n, spike_input_port)` with the corresponding buffer variable, e.g. `g_E__X__spikes_exc[__d]^n` for a shape named `g_E` and a spike input port named `spikes_exc`.
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
                    #print("Delta function: replacing convolve call " + str(convolve) + " with var " + str(buffer_var))
                    #import pdb;pdb.set_trace()
                else:
                    ast_variable = ASTVariable(buffer_var)
                    ast_variable.set_source_position(_expr.get_source_position())
                    _expr.set_variable(ast_variable)
                    #print("Replacing convolve call " + str(convolve) + " with var " + str(buffer_var))

                #elif type(buffer_var) in [int, float]:
                    #_expr.set_numeric_literal(buffer_var)

        func = lambda x: replace_function_call_through_var(x) if isinstance(x, ASTSimpleExpression) else True

        equations_block.accept(ASTHigherOrderVisitor(func))

    '''def replace_convolve_calls_with_buffer_expr_(self, equations_block, shape, spike_input_port, buffer_var):

        def replace_function_call_through_var(_expr=None):
            if _expr.is_function_call() and _expr.get_function_call().get_name() == "convolve":
                convolve = _expr.get_function_call()
                el = (convolve.get_args()[0], convolve.get_args()[1])
                sym = convolve.get_args()[0].get_scope().resolve_to_symbol(convolve.get_args()[0].get_variable().name, SymbolKind.VARIABLE)
                if sym.block_type == BlockType.INPUT_BUFFER_SPIKE:
                    el = (el[1], el[0])
                if shape.get_variable().get_name() == el[0].get_variable().get_name() \
                 and spike_input_port.get_variable().get_name() == el[1].get_variable().get_name():
                    _expr.set_function_call(None)
                    if type(buffer_var) is str:
                        ast_variable = ASTVariable(buffer_var)
                        #ast_variable.update_scope(_expr.get_scope())
                        _expr.set_variable(ast_variable)
                        #equations_block.accept(ASTSymbolTableVisitor())
                        #print("ast_variable scope = " + str(ast_variable.get_scope()))
                        #print("_expr scope = " + str(_expr.get_scope()))
                        #assert not ast_variable.get_scope() is None
                        #assert not equations_block.get_scope().resolve_to_symbol(ast_variable.get_name(), SymbolKind.VARIABLE) is None
                        print("Replacing convolve call " + str(convolve) + " with var " + str(buffer_var))
                    elif type(buffer_var) in [int, float]:
                        _expr.set_numeric_literal(buffer_var)
                        print("Replacing convolve call " + str(convolve) + " with expr " + str(buffer_var))
                    else:
                        assert False
                        # assert type(buffer_var) in [int, float]
                        _expr.set_numeric_literal()
                        print("Replacing convolve call " + str(convolve) + " with expr " + str(buffer_var))

        func = lambda x: replace_function_call_through_var(x) if isinstance(x, ASTSimpleExpression) else True

        equations_block.accept(ASTHigherOrderVisitor(func))


    def replace_convolve_calls_with_buffers_(self, neuron, equations_block, shape_buffers):
        """
        Replace each `convolve(shape, spike_buf)` function call with the corresponding element in `shape_buffers` (e.g. `G__X__spikesEx`). For delta shapes, replace the convolve call with the name of the spike input port directly.
        """
        for shape, spike_input_port in shape_buffers:
            shape_var = shape.get_variable()
            if is_delta_shape(neuron.get_shape_by_name(shape_var.get_complete_name())):
                self.replace_convolve_calls_with_buffer_expr_(equations_block, shape, spike_input_port, spike_input_port.__str__())
            else:
                shape_order = shape_var.get_differential_order()
                buffer_var = construct_shape_X_spike_buf_name(shape_var, spike_input_port, shape_order - 1)
                self.replace_convolve_calls_with_buffer_expr_(equations_block, shape_var_expr, spike_input_port, buffer_var)
'''

    def add_timestep_symbol(self, neuron):
        assert neuron.get_initial_value("__h") is None, "\"__h\" is a reserved name, please do not use variables by this name in your NESTML file"
        assert not "__h" in [sym.name for sym in neuron.get_internal_symbols()], "\"__h\" is a reserved name, please do not use variables by this name in your NESTML file"
        neuron.add_to_internal_block(ModelParser.parse_declaration('__h ms = resolution()'), index=0)


    def analyse_neuron(self, neuron):
        # type: (ASTNeuron) -> None
        """
        Analyse and transform a single neuron.
        :param neuron: a single neuron.
        """
        code, message = Messages.get_start_processing_neuron(neuron.get_name())
        Logger.log_message(neuron, code, message, neuron.get_source_position(), LoggingLevel.INFO)
        equations_block = neuron.get_equations_block()

        if equations_block is not None:
            delta_factors = self.get_delta_factors_(neuron, equations_block)
            shape_buffers = self.generate_shape_buffers_(neuron, equations_block)
            #print("shape_buffers = " + str([(str(a), str(b)) for a, b in shape_buffers]))
            self.replace_convolve_calls_with_buffers_(neuron, equations_block, shape_buffers)
            
            #print("NEST codegenerator step 0...")
            #self.mark_shape_variable_symbols(neuron, shape_buffers)
            
            #print("NEST codegenerator step 3...")
            #self.update_symbol_table(neuron, shape_buffers)

            #print("NEST codegenerator: replacing functions through defining expressions...")
            self.make_functions_self_contained(equations_block.get_ode_functions())
            self.replace_functions_through_defining_expressions(equations_block.get_ode_equations(), equations_block.get_ode_functions())
            #self.replace_functions_through_defining_expressions2([analytic_solver, numeric_solver], equations_block.get_ode_functions())

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
            #self.update_symbol_table(neuron, shape_buffers)

            #print("NEST codegenerator: Adding ode-toolbox processed shapes to AST...")
            #self.add_shape_odes(neuron, [analytic_solver, numeric_solver], shape_buffers)
            #self.replace_convolve_calls_with_buffers_(neuron, equations_block, shape_buffers)

            if not self.analytic_solver[neuron.get_name()] is None:
                #print("NEST codegenerator: Adding propagators...")
                neuron = add_declarations_to_internals(neuron, self.analytic_solver[neuron.get_name()]["propagators"])

            #self.update_symbol_table(neuron, shape_buffers)
            #self.remove_shape_definitions_from_equations_block(neuron, self.analytic_solver["state_variables"])

            #if not self.numeric_solver is None:
            #    functional_shapes_to_odes(neuron, self.numeric_solver)

            # update shape buffers in case direct functions of time have been replaced by higher-order differential

            #print("NEST codegenerator step 5...")
            self.update_symbol_table(neuron, shape_buffers)

            #print("NEST codegenerator step 6...")
            spike_updates = self.get_spike_update_expressions(neuron, shape_buffers, [analytic_solver, numeric_solver], delta_factors)
            

        return spike_updates


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
        #print("generate_model_h_file: neuron " + str(neuron.get_name()))
        neuron_h_file = self._template_neuron_h_file.render(self.setup_generation_helpers(neuron))
        with open(str(os.path.join(FrontendConfiguration.get_target_path(), neuron.get_name())) + '.h', 'w+') as f:
            f.write(str(neuron_h_file))


    def generate_neuron_cpp_file(self, neuron):
        # type: (ASTNeuron) -> None
        """
        For a handed over neuron, this method generates the corresponding implementation file.
        :param neuron: a single neuron object.
        """
        #print("generate_model_cpp_file: neuron " + str(neuron.get_name()))
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

        namespace['initial_values'] = {}
        namespace['uses_analytic_solver'] = not self.analytic_solver[neuron.get_name()] is None
        if namespace['uses_analytic_solver']:
            namespace['analytic_state_variables'] = self.analytic_solver[neuron.get_name()]["state_variables"]
            namespace['analytic_variable_symbols'] = { sym : neuron.get_equations_block().get_scope().resolve_to_symbol(sym, SymbolKind.VARIABLE) for sym in namespace['analytic_state_variables'] }
            namespace['update_expressions'] = {}
            for sym, expr in self.analytic_solver[neuron.get_name()]["initial_values"].items():
                namespace['initial_values'][sym] = expr
            for sym in namespace['analytic_state_variables']:
                expr_str = self.analytic_solver[neuron.get_name()]["update_expressions"][sym]
                expr_ast = ModelParser.parse_expression(expr_str)
                expr_ast.update_scope(neuron.get_update_blocks().get_scope()) # pretend that update expressions are in "update" block
                expr_ast.accept(ASTSymbolTableVisitor())
                namespace['update_expressions'][sym] = expr_ast

#            namespace['update_expressions'] = { sym : ModelParser.parse_expression(expr) for sym, expr in self.analytic_solver["update_expressions"].items() }

            #namespace['update_expressions'] = self.analytic_solver["update_expressions"]
            namespace['propagators'] = self.analytic_solver[neuron.get_name()]["propagators"]

        namespace['uses_numeric_solver'] = not self.numeric_solver[neuron.get_name()] is None
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
                expr_ast.update_scope(neuron.get_update_blocks().get_scope()) # pretend that update expressions are in "update" block
                expr_ast.accept(ASTSymbolTableVisitor())
                namespace['numeric_update_expressions'][sym] = expr_ast

            namespace['useGSL'] = namespace['uses_numeric_solver']
            namespace['names'] = GSLNamesConverter()
            converter = NESTReferenceConverter(True)
            unitless_pretty_printer = UnitlessExpressionPrinter(converter)
            namespace['printer'] = NestPrinter(unitless_pretty_printer)        

        namespace["spike_updates"] = neuron.spike_updates

        return namespace


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


    def ode_toolbox_analysis(self, neuron, shape_buffers):
        # type: (ASTNeuron, map(str, str)) -> ASTNeuron
        """
        Solves all odes and equations in the handed over neuron.

        Precondition: it should be ensured that most one equations block is present.

        :param neuron: a single neuron instance.
        :return: A transformed version of the neuron that can be passed to the GSL.
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
        #print("Invoking ode-toolbox with JSON input:")
        #print(odetoolbox_indict)
        solver_result = analysis(odetoolbox_indict, enable_stiffness_check=False)
        #print("Got result from ode-toolbox:")
        #print(solver_result)
        analytic_solver = None
        analytic_solvers = [x for x in solver_result if x["solver"] == "analytical"]
        assert len(analytic_solvers) <= 1, "More than one analytic solver not presently supported"
        if len(analytic_solvers) > 0:
            analytic_solver = analytic_solvers[0]

        # if numeric solver is required, generate a stepping function that includes each state variable
        numeric_solver = None
        numeric_solvers = [x for x in solver_result if x["solver"].startswith("numeric")]
        if numeric_solvers:
            solver_result = analysis(odetoolbox_indict, enable_stiffness_check=False, disable_analytic_solver=True)
            #print("Got result from ode-toolbox:")
            #print(solver_result)
            numeric_solvers = [x for x in solver_result if x["solver"].startswith("numeric")]
            assert len(numeric_solvers) <= 1, "More than one numeric solver not presently supported"
            if len(numeric_solvers) > 0:
                numeric_solver = numeric_solvers[0]


        return analytic_solver, numeric_solver






        """# XXX: TODO: split this off to a separate function/method
        # update lists of associated variables for all defined shapes
        # this is called e.g. in case a shape specified as a direct function of time is converted in a system of ODEs
        
        solver_dicts = [self.analytic_solver[neuron.get_name()], self.numeric_solver[neuron.get_name()]]
        
        for solver_dict in solver_dicts:
            if solver_dict is None:
                continue

            for var_name in solver_dict["initial_values"].keys():
                
                # construct and add element to add to shape_buffers
                # no need to check for doubles: shape_buffers is of type set
                
                if not "__X__" in var_name:
                    continue
                
                shape_name_base = var_name.split("__X__")[0]
                spike_buf_name = var_name.split("__X__")[1].split("__d")[0]
                shape_name_diff_order = len(re.findall(r"__d", var_name))
                complete_variable_name = shape_name_base + "__d" * shape_name_diff_order
                complete_variable_name_ticks = shape_name_base + "'" * shape_name_diff_order
                #ast_variable = self._get_ast_variable(neuron, var_name)
                #assert not ast_variable is None, "Variable by name \"" + var_name + "\" should have been declared in initial values"
                ast_variable = ASTVariable(shape_name_base, differential_order=shape_name_diff_order)

                spike_buf_var = ASTVariable(spike_buf_name, 0)

                shape_var_expr = ASTNodeFactory.create_ast_simple_expression(variable=ast_variable, source_position=ast_variable.get_source_position())
                shape_buf_expr = ASTNodeFactory.create_ast_simple_expression(variable=spike_buf_var, source_position=ast_variable.get_source_position())
                el = (shape_var_expr, shape_buf_expr)

                shape_name_diff_order = shape_var_expr.get_variable().get_differential_order()
                assert var_name == construct_shape_X_spike_buf_name(shape_var_expr.get_variable(), shape_buf_expr, shape_name_diff_order)
                
                
                print("Adding to spike buf (1): " + shape_name_base + ", " + spike_buf_name)

                if not (complete_variable_name_ticks, spike_buf_name) in [(str(a[0]), str(a[1])) for a in shape_buffers]:
                    print("\tAdding to spike buf (2): " + shape_name_base + ", " + spike_buf_name)
                    shape_buffers.add(el)
                
                #shape = neuron.get_shape_by_name(var_name)
                #if not shape is None:
                    
                    #if not ast_variable in shape.variables:
                        #shape.variables.append(ast_variable)
                    
                ##shape_var = shape_var_expr.get_variable()
                ##var_order = shape_var.get_differential_order()
                ##shape = neuron.get_shape_by_name(shape_var.get_name())


        #shape_buffers = set()
        #convolve_calls = OdeTransformer.get_convolve_function_calls(equations_block)
        #for convolve in convolve_calls:
            #el = (convolve.get_args()[0], convolve.get_args()[1])
            #sym = convolve.get_args()[0].get_scope().resolve_to_symbol(convolve.get_args()[0].get_variable().name, SymbolKind.VARIABLE)
            #if sym is None:
                #raise Exception("No initial value(s) defined for shape with variable \"" + convolve.get_args()[0].get_variable().get_complete_name() + "\"")
            #if sym.block_type == BlockType.INPUT_BUFFER_SPIKE:
                #el = (el[1], el[0])
            #print("Adding variable used in convolve: " + el[0].__str__() + ", " + el[1].__str__())

            ## find the corresponding shape object
            #var = el[0].get_variable()
            #shape = neuron.get_shape_by_name(var.get_name())

            ## generate an entry for all variables defined in the shape
            #for var in shape.get_variables():
                #expr = ASTNodeFactory.create_ast_simple_expression(variable=var, source_position=var.get_source_position())
                #el = (expr, el[1])
                #shape_buffers.add(el)
                #print("Adding " + el[0].__str__() + ", " + el[1].__str__())

        #return shape_buffers
                """




    def update_symbol_table(self, neuron, shape_buffers):
        """mark corresponding variable symbols properly as belonging to a shape"""
        #print("SymbolTable scope keys before update: " + str(SymbolTable.name2neuron_scope.keys()))
        #print("Updating for neuron: " + str(neuron.get_name()))
        SymbolTable.delete_neuron_scope(neuron.get_name())
        #SymbolTable.clean_up_table()
        #SymbolTable.initialize_symbol_table(neuron.get_source_position())
        symbol_table_visitor = ASTSymbolTableVisitor()
        symbol_table_visitor.after_ast_rewrite_ = True
        neuron.accept(symbol_table_visitor)
        SymbolTable.add_neuron_scope(neuron.get_name(), neuron.get_scope())
        #print("SymbolTable scope keys after update: " + str(SymbolTable.name2neuron_scope.keys()))


    '''def get_shape_buffer_names(self, neuron, shape_buffers):
        shape_buffer_names = []
        for shape, spike_input_port in shape_buffers:
            for shape_var in shape.get_variables():
                var_order = shape_var.get_differential_order()
                shape_spike_buf_name = construct_shape_X_spike_buf_name(shape_var.get_name(), spike_input_port, var_order)
                shape_buffer_names.append(shape_spike_buf_name)

        return shape_buffer_names'''


    '''def get_shape_variable_names(self, shape):
        shape_variable_names = []

        for var in shape.get_variables():
            shape_variable_names.append(var.get_complete_name())

        return shape_variable_names'''


    '''def mark_shape_variable_symbols(self, neuron, shape_buffers):

        shape_buffer_names = self.get_shape_buffer_names(neuron, shape_buffers)

        def mark_variable_symbol_as_shape(_expr=None):
            if _expr.is_variable():
                if _expr.get_variable().get_name() in shape_buffer_names:
                    sym = _expr.get_scope().resolve_to_symbol(str(_expr), SymbolKind.VARIABLE)
                    if not sym is None:
                        sym.set_variable_type(VariableType.SHAPE)
                        print("Marking symbol " + str(sym.name) + " as SHAPE")

        func = lambda x: mark_variable_symbol_as_shape(x) if isinstance(x, ASTSimpleExpression) else True

        neuron.accept(ASTHigherOrderVisitor(func))'''


    def remove_initial_values_for_shapes(self, neuron):
        """remove initial values for original declarations (e.g. g_in, g_in', V_m); these might conflict with the initial value expressions returned from ode-toolbox
        """

        #print("Removing initial values for shapes...")
        assert isinstance(neuron.get_equations_blocks(), ASTEquationsBlock), "only one equation block should be present"

        equations_block = neuron.get_equations_block()

        symbols_to_remove = set()

        for shape in equations_block.get_ode_shapes():
            for shape_var in shape.get_variables():
                shape_var_order = shape_var.get_differential_order()
                for order in range(shape_var_order):
                    symbol_name = shape_var.get_name() + "'" * order
                    symbol = equations_block.get_scope().resolve_to_symbol(symbol_name, SymbolKind.VARIABLE)
                    #print("\tMarking shape symbol " + str(symbol_name) + " = " + str(symbol) + " for removal")
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
            #print("\tRemoving decl: " + str(decl))
            neuron.get_initial_blocks().get_declarations().remove(decl)


    def remove_initial_values_for_odes(self, neuron, solver_dicts, shape_buffers, shapes):
        """remove initial values for original declarations (e.g. g_in, V_m', g_ahp''), i.e. before ode-toolbox processing
        """
        #print("Replacing initial values for ODEs...")
        assert isinstance(neuron.get_equations_blocks(), ASTEquationsBlock), "only one equation block should be present"
        equations_block = neuron.get_equations_block()

        #
        #   mark all variables that occur in ODE equations as "to be removed" by default
        #
        """
        symbols_to_remove = set()
        for ode_eq in equations_block.get_ode_equations():
            var = ode_eq.get_lhs()
            for order in range(var.get_differential_order()):
                var_name = var.get_name() + "'" * order
                if variable_in_neuron_initial_values(var_name, neuron):
                    symbols_to_remove.add(var_name)
                    print("\tMarking symbol " + var.get_complete_name() + " for removal")
        """
            

        #
        #   for each variable that can be matched in the ode-toolbox results dictionary:
        #   - replace the defining expression by the ode-toolbox result
        #   - unmark for deletion
        #

        #print("replace test:")

        for iv_decl in neuron.get_initial_blocks().get_declarations():
            for var in iv_decl.get_variables():
                var_name = var.get_complete_name()
                #print("\tvar = " + var_name)
                
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
                    #print("\t  --> replace the defining expression by the ode-toolbox result: iv_expr = " + str(iv_expr))
                    iv_expr = ModelParser.parse_expression(iv_expr)
                    iv_expr.update_scope(neuron.get_initial_blocks().get_scope())
                    iv_decl.set_expression(iv_expr)



    def _get_ast_variable(self, neuron, var_name) -> Optional[ASTVariable]:
        # grab the ASTVariable corresponding to the initial value by this name
        for decl in neuron.get_initial_values_blocks().get_declarations():
            for var in decl.variables:
                if var.get_name() == var_name:
                    return var
        return None


    def create_initial_values_for_odetb_shapes(self, neuron, solver_dicts, shape_buffers, shapes):
        """add the variables used in ODEs from the ode-toolbox result dictionary as ODEs in NESTML AST"""

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

                #print("1089273 Var " + var_name + " is ", end="")
                #if not variable_in_shapes(var_name, shapes):
                    #print(" NOT ", end="")
                #print(" in shapes")
                if variable_in_shapes(var_name, shapes):
                    expr = "0"    # for shapes, "initial value" returned by ode-toolbox is actually the increment value; the actual initial value is assumed to be 0
                
                    if not declaration_in_initial_values(neuron, var_name):
                        add_declaration_to_initial_values(neuron, var_name, expr)
                    #print("\tAdding to initial values: " + str(var_name) + " = " + str(expr))



    def create_initial_values_for_odetb_odes(self, neuron, solver_dicts, shape_buffers, shapes):
        """add the variables used in ODEs from the ode-toolbox result dictionary as ODEs in NESTML AST"""

        ##
        ##   shapes containing delta functions were removed before passing to ode-toolbox; reinstate initial values here
        ##

        #for shape, spike_input_port in shape_buffers:
            #if is_delta_shape(shape):
                #assert len(shape.get_variables()) == 1
                #shape_var = shape.get_variables()[0]
                #assert shape_var.get_differential_order() == 0
                #new_var_name = construct_shape_X_spike_buf_name(shape_var.get_name(), spike_input_port, order=0)
                #iv_expr = get_delta_shape_prefactor_expr(shape)
                #assert not declaration_in_initial_values(neuron, new_var_name)
                #add_declaration_to_initial_values(neuron, new_var_name, iv_expr)
                #print("Adding to initial values: " + str(new_var_name) + " = " + str(expr))


        #
        #   add everything returned from ode-toolbox
        #

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

                #print("1089273 Var " + var_name + " is ", end="")
                #if not variable_in_shapes(var_name, shapes):
                    #print(" NOT ", end="")
                #print(" in shapes")
                if variable_in_shapes(var_name, shapes):
                    expr = "0"    # for shapes, "initial value" returned by ode-toolbox is actually the increment value; the actual initial value is assumed to be 0
                
                if not declaration_in_initial_values(neuron, var_name):
                    add_declaration_to_initial_values(neuron, var_name, expr)
                #print("\tAdding to initial values: " + str(var_name) + " = " + str(expr))



        ## XXX: TODO: split this off to a separate function/method
        ## update lists of associated variables for all defined shapes
        ## this is called e.g. in case a shape specified as a direct function of time is converted in a system of ODEs
        #for solver_dict in solver_dicts:
            #if solver_dict is None:
                #continue

            #for var_name in solver_dict["initial_values"].keys():
                #shape = neuron.get_shape_by_name(var_name)
                #if not shape is None:
                    ##shape_name_base = var_name.split("__X__")[0]
                    ##shape_name_diff_order = len(re.findall(r"__d", var_name))
                    ##complete_variable_name = shape_name_base + "__d" * shape_name_diff_order
                    
                    ##ast_variable = self._get_ast_variable(neuron, complete_variable_name)
                    #ast_variable = self._get_ast_variable(neuron, var_name)
                    #assert not ast_variable is None, "Variable by name \"" + var_name + "\" should have been declared in initial values"
                    
                    #if not ast_variable in shape.variables:
                        #shape.variables.append(ast_variable)
                    
                ##shape_var = shape_var_expr.get_variable()
                ##var_order = shape_var.get_differential_order()
                ##shape = neuron.get_shape_by_name(shape_var.get_name())
                
        
        """
        # shapes containing delta functions were removed before passing to ode-toolbox; reinstate initial values here
        spike_updates = []
        for shape, spike_input_port in shape_buffers:
            buffer_type = neuron.get_scope().resolve_to_symbol(str(spike_input_port), SymbolKind.VARIABLE).get_type_symbol()
            print("\t\tshape = " + str(shape))
            if is_delta_shape(shape):
                shape_spike_buf_name = shape.__str__() + "__X__" + spike_input_port.__str__()
                add_declaration_to_initial_values(neuron, shape_spike_buf_name, "0")"""

    """def get_shape_spike_buf_names(self, neuron, shape, spike_input_port):
        shape_order = 0
        while True:
            shape_spike_buf_name = shape.get_variable().get_name().replace("$", "__DOLLAR") + "__X__" + spike_input_port.__str__() + "__d" * shape_order
            shape_order += 1
            if neuron.get_initial_value(shape_spike_buf_name) is None:
                break

        print("\tShape " + str(shape.get_variable().get_name()) + ", order = " + str(shape_order))

        shape_spike_buf_names = []
        for order in range(shape_order):
            shape_spike_buf_name = shape.get_variable().get_name().replace("$", "__DOLLAR") + "__X__" + spike_input_port.__str__() + "__d" * order
            shape_spike_buf_names.append(shape_spike_buf_name)

            # check whether other variables exist that belong to the same shape, e.g. "g_in$" for the shape named "g_in"
            for decl in neuron.get_equations_block().get_declarations():
                if isinstance(decl, ASTOdeShape) \
                 and re.compile(shape.get_variable().get_name() + "\$+").search(decl.get_variable().get_name()):
                    assert decl.get_variable().get_differential_order() == 1
                    shape_spike_buf_names.append(decl.get_variable().get_name().replace("$", "__DOLLAR") + "__X__" + str(spike_input_port))

        return shape_spike_buf_names
"""

    def get_spike_update_expressions(self, neuron, shape_buffers, solver_dicts, delta_factors):
        """Generate the equations that update the dynamical variables when incoming spikes arrive. To be invoked after ode-toolbox.

        For example, a resulting `assignment_str` could be "I_shape_in += (in_spikes/nS) * 1". The values are taken from the initial values for each corresponding dynamical variable, either from ode-toolbox or directly from user specification in the model.

        Note that for shapes, `initial_values` actually contains the increment upon spike arrival, rather than the initial value of the corresponding ODE dimension.
        """

        spike_updates = []
        initial_values = neuron.get_initial_values_blocks()

        for shape, spike_input_port in shape_buffers:
            buffer_type = neuron.get_scope().resolve_to_symbol(str(spike_input_port), SymbolKind.VARIABLE).get_type_symbol()

            if is_delta_shape(shape):
                continue

            #    buffer_type = neuron.get_scope().resolve_to_symbol(str(spike_input_port), SymbolKind.VARIABLE).get_type_symbol()

            for shape_var in shape.get_variables():
                for var_order in range(get_shape_var_order_from_ode_toolbox_result(shape_var.get_name(), solver_dicts)):
                    shape_spike_buf_name = construct_shape_X_spike_buf_name(shape_var.get_name(), spike_input_port, var_order)
                    #expr = neuron.get_initial_value(shape_spike_buf_name)
                    expr = get_initial_value_from_odetb_result(shape_spike_buf_name, solver_dicts)
                    assert not expr is None, "Initial value not found for shape " + shape_var
                    #print("\t" + str(shape_spike_buf_name))
                    #print("\t" + str(spike_input_port))
                    expr = str(expr)
                    if expr in ["0", "0.", "0.0"]:
                        #print("\tzero")
                        continue    # skip adding the statement if we're only adding zero

                    assignment_str = shape_spike_buf_name + " += "
                    assignment_str += "(" + str(spike_input_port) + ")"
                    if not expr in ["1.", "1.0", "1"]:
                        assignment_str += " * (" + self._printer.print_expression(ModelParser.parse_expression(expr)) + ")"

                    if not buffer_type.print_nestml_type() in ["1.", "1.0", "1"]:
                        assignment_str += " / (" + buffer_type.print_nestml_type() + ")"

                    #print("\t\t\t--> assignment_str = " + str(assignment_str))
                    #spike_updates.append(assignment_str + "\n")
                    #print("\t\tupdating scope to that of neuron " + str(neuron.get_name()) + ", scope = " + str(neuron.get_scope()))
                    ast_assignment = ModelParser.parse_assignment(assignment_str)
                    ast_assignment.update_scope(neuron.get_scope())
                    ast_assignment.accept(ASTSymbolTableVisitor())

                    spike_updates.append(ast_assignment)

        print("spike_updates = " + str(spike_updates))

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

        print("spike_updates = " + ", ".join([str(s) for s in spike_updates]))

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

        #print("Removing shapes " + ", ".join([str(d) for d in decl_to_remove]))

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

        #print("Removing ODEs " + ", ".join([str(d) for d in decl_to_remove]))

        for decl in decl_to_remove:
            equations_block.get_declarations().remove(decl)


    def transform_ode_and_shapes_to_json(self, neuron, parameters_block, shape_buffers):
        # type: (ASTEquationsBlock) -> dict[str, list]
        """Converts AST node to a JSON representation suitable for passing to ode-toolbox

        Each shape has to be generated for each spike buffer convolve in which it occurs, e.g. if the NESTML model code contains the statements

            convolve(G, ex_spikes)
            convolve(G, in_spikes)

        then `shape_buffers` will contain the pairs `(G, ex_spikes)` and `(G, in_spikes)`, from which two ODEs will be generated, with dynamical state (variable) names `G__X__ex_spikes` and `G__X__in_spikes`.            

        :param equations_block:equations_block
        :return: dictionary
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
                if not initial_value_expr is None:
                    expr = gsl_printer.print_expression(initial_value_expr)
                    entry["initial_values"][to_odetb_name(iv_symbol_name)] = expr
            odetoolbox_indict["dynamics"].append(entry)

        # write a copy for each (shape, spike buffer) combination
        for shape, spike_input_port in shape_buffers:

            if is_delta_shape(shape):
                # delta function -- skip passing this to ode-toolbox
                continue

            #print("Making JSON entry for shape with variables " + ", ".join([var.get_complete_name() for var in shape.get_variables()]) + " and spike buffer " + spike_input_port.__str__())

            for shape_var in shape.get_variables():
                #print("\tvariable: " + shape_var.get_name())
                expr = get_expr_from_shape_var(shape, shape_var.get_complete_name())
                shape_order = shape_var.get_differential_order()
                #shape_X_spike_buf_name = construct_shape_X_spike_buf_name(shape_var, spike_buf, shape_order)
                shape_X_spike_buf_name_ticks = construct_shape_X_spike_buf_name(shape_var.get_name(), spike_input_port, shape_order, diff_order_symbol="'")

                replace_rhs_variables(expr, shape_buffers)

                #expr.update_scope(equations_block.get_scope())
                #expr.accept(ASTSymbolTableVisitor())
                #print("\t updating scope to " + str(equations_block.get_scope()))
                #print("\t shape expression after transform = " + str(expr))

                entry = {}
                entry["expression"] = shape_X_spike_buf_name_ticks + " = " + str(expr)

                # initial values need to be declared for order 1 up to shape order (e.g. none for shape function f(t) = ...; 1 for shape ODE f'(t) = ...; 2 for f''(t) = ... and so on)
                entry["initial_values"] = {}
                for order in range(shape_order):
                    iv_sym_name_odetb = construct_shape_X_spike_buf_name(shape_var.get_name(), spike_input_port, order, diff_order_symbol="'")
                    #symbol_name_ = shape_var_expr.get_variable().get_name() + "'" * order
                    #symbol_name = shape_X_spike_buf_name + "'" * order
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
        #print("odetoolbox_indict = " + str(json.dumps(odetoolbox_indict, indent=4)))
        return odetoolbox_indict


    def make_functions_self_contained(self, functions):
        # type: (list(ASTOdeFunction)) -> list(ASTOdeFunction)
        """
        Make function definition self contained, i.e. without any references to other functions.

        TODO: it should be a method inside of the ASTOdeFunction
        TODO by KP: this should be done by means of a visitor

        :param functions: A sorted list with entries ASTOdeFunction.
        :return: A list with ASTOdeFunctions. Defining expressions don't depend on each other.
        """
        for source in functions:
            source_position = source.get_source_position()
            #print("In make_functions_self_contained(): source = " + str(source))
            for target in functions:
                matcher = re.compile(self._variable_matching_template.format(source.get_variable_name()))
                target_definition = str(target.get_expression())
                target_definition = re.sub(matcher, "(" + str(source.get_expression()) + ")", target_definition)
                target.expression = ModelParser.parse_expression(target_definition)
                target.expression.update_scope(source.get_scope())
                target.expression.accept(ASTSymbolTableVisitor())

                #print("\ttarget = " + str(target))

                def log_set_source_position(node):
                    if node.get_source_position().is_added_source_position():
                        node.set_source_position(source_position)

                target.expression.accept(ASTHigherOrderVisitor(visit_funcs=log_set_source_position))

                #print("\t -> updating scope to " + str(source.get_scope()))

        return functions


    def replace_functions_through_defining_expressions(self, definitions, functions):
        # type: (list(ASTOdeEquation), list(ASTOdeFunction)) -> list(ASTOdeFunction)
        """
        Refactors symbols from `functions` in `definitions` with corresponding defining expressions from `functions`.
        
        Note that this only touches "ode functions", i.e. one-liner function definitions without an `end` keyword.

        :param definitions: A sorted list with entries {"symbol": "name", "definition": "expression"} that should be made
        free from.
        :param functions: A sorted list with entries {"symbol": "name", "definition": "expression"} with functions which
        must be replaced in `definitions`.
        :return: A list with definitions. Expressions in `definitions` don't depend on functions from `functions`.
        """
        for fun in functions:
            #print("In replace_functions_through_defining_expressions(): fun = " + str(fun))
            source_position = fun.get_source_position()
            for target in definitions:
                #print("\ttarget = " + str(target))
                matcher = re.compile(self._variable_matching_template.format(fun.get_variable_name()))
                target_definition = str(target.get_rhs())
                target_definition = re.sub(matcher, "(" + str(fun.get_expression()) + ")", target_definition)
                target.rhs = ModelParser.parse_expression(target_definition)
                target.update_scope(fun.get_scope())
                target.accept(ASTSymbolTableVisitor())

                def log_set_source_position(node):
                    if node.get_source_position().is_added_source_position():
                        node.set_source_position(source_position)

                target.accept(ASTHigherOrderVisitor(visit_funcs=log_set_source_position))

                #print("\t updating scope to " + str(fun.get_scope()))

        return definitions

    def replace_functions_through_defining_expressions2(self, solver_dicts, functions):
        # type: (list(ASTOdeEquation), list(ASTOdeFunction)) -> list(ASTOdeFunction)
        """
        Refactors symbols form `functions` in `definitions` with corresponding defining expressions from `functions`.

        :param definitions: A sorted list with entries {"symbol": "name", "definition": "expression"} that should be made
        free from.
        :param functions: A sorted list with entries {"symbol": "name", "definition": "expression"} with functions which
        must be replaced in `definitions`.
        :return: A list with definitions. Expressions in `definitions` don't depend on functions from `functions`.
        """

        def replace_func_by_def_in_expr(expr, functions):
            for fun in functions:
                #print("In replace_functions_through_defining_expressions(): fun = " + str(fun))
                matcher = re.compile(self._variable_matching_template.format(fun.get_variable_name()))
                expr = re.sub(matcher, "(" + str(fun.get_expression()) + ")", expr)
                target_definition = str(target.get_expression())
                target_definition = re.sub(matcher, "(" + str(source.get_expression()) + ")", target_definition)
                target.expression = ModelParser.parse_expression(target_definition)
                target.expression.update_scope(source.get_scope())
                target.expression.accept(ASTSymbolTableVisitor())

                #print("\ttarget = " + str(target))

                def log_set_source_position(node):
                    if node.get_source_position().is_added_source_position():
                        node.set_source_position(source_position)

                target.expression.accept(ASTHigherOrderVisitor(visit_funcs=log_set_source_position))


            return expr
        
        for solver_dict in solver_dicts:
            if solver_dict is None:
                continue
            
            for var, expr in solver_dict["update_expressions"].items():
                solver_dict["update_expressions"][var] = replace_func_by_def_in_expr(expr, functions)

            if "propagators" in solver_dict.keys():
                for var, expr in solver_dict["propagators"].items():
                    solver_dict["propagators"][var] = replace_func_by_def_in_expr(expr, functions)



    def store_transformed_model(self, ast):
        if FrontendConfiguration.store_log:
            with open(str(os.path.join(FrontendConfiguration.get_target_path(), '..', 'report',
                                       ast.get_name())) + '.txt', 'w+') as f:
                f.write(str(ast))
