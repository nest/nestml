# -*- coding: utf-8 -*-
#
# convolutions_transformer.py
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

from __future__ import annotations

from typing import Any, Dict, List, Sequence, Mapping, Optional, Tuple, Union

import re

import odetoolbox
import sympy

from pynestml.codegeneration.printers.ast_printer import ASTPrinter
from pynestml.codegeneration.printers.constant_printer import ConstantPrinter
from pynestml.codegeneration.printers.ode_toolbox_expression_printer import ODEToolboxExpressionPrinter
from pynestml.codegeneration.printers.ode_toolbox_function_call_printer import ODEToolboxFunctionCallPrinter
from pynestml.codegeneration.printers.ode_toolbox_variable_printer import ODEToolboxVariablePrinter
from pynestml.codegeneration.printers.unitless_sympy_simple_expression_printer import UnitlessSympySimpleExpressionPrinter
from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.meta_model.ast_assignment import ASTAssignment
from pynestml.meta_model.ast_block import ASTBlock
from pynestml.meta_model.ast_data_type import ASTDataType
from pynestml.meta_model.ast_declaration import ASTDeclaration
from pynestml.meta_model.ast_equations_block import ASTEquationsBlock
from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_inline_expression import ASTInlineExpression
from pynestml.meta_model.ast_input_port import ASTInputPort
from pynestml.meta_model.ast_kernel import ASTKernel
from pynestml.meta_model.ast_model import ASTModel
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_node_factory import ASTNodeFactory
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.meta_model.ast_small_stmt import ASTSmallStmt
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.symbols.real_type_symbol import RealTypeSymbol
from pynestml.symbols.symbol import SymbolKind
from pynestml.symbols.variable_symbol import BlockType
from pynestml.transformers.transformer import Transformer
from pynestml.utils.ast_source_location import ASTSourceLocation
from pynestml.utils.ast_utils import ASTUtils
from pynestml.utils.logger import Logger
from pynestml.utils.logger import LoggingLevel
from pynestml.utils.model_parser import ModelParser
from pynestml.utils.string_utils import removesuffix
from pynestml.visitors.ast_parent_visitor import ASTParentVisitor
from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor
from pynestml.visitors.ast_higher_order_visitor import ASTHigherOrderVisitor
from pynestml.visitors.ast_visitor import ASTVisitor


class ConvolutionsTransformer(Transformer):
    r"""For each convolution that occurs in the model, allocate one or more needed state variables and replace the convolution() calls by these variable names.

    A new event handler (onReceive block) will be generated that increments the new state variables when a spike arrives. The priority of the handler will be clearly defined to be the highest of all (or the lowest of all) event handlers, so that the rest of the code (update block and other event handlers) get a consistent "just before" or "just after" value.

    For instance,

    .. code-block:: nestml

       state:
           V_m mV = 0 mV

       equations:
           kernel K = exp(-t / tau_syn)
           V_m' = -V_m/tau_m + convolve(K, spikes) / C_m

        update:
            ...
            integrate_odes(V_m)
            ...

    would be transformed into

    .. code-block:: nestml

       state:
           V_m mV = 0 mV
           K__conv__spikes real = 0

       equations:
           V_m' = -V_m/tau_m + K__conv__spikes / C_m
           K__conv__spikes' = -K__conv__spikes / tau_syn

        onReceive(spikes, priority=?????????/):
            K__conv__spikes += spikes   # bump by spike weight

        update:
            K__conv__spikes__at_start_of_timestep real = K__conv__spikes    # backup old value of the convolution (add as first statement of update block)

            ...
            integrate_odes(V_m, K__conv__spikes)      # add integrating the convolutions to each integrate_odes() where, for any argument, there is reference to K__conv__spikes in an expression (checked recursively, and including inline expressions). XXX: in practice, it is added to every call that contains keyword arguments, such that it is always integrated.
            K__conv__spikes = K__conv__spikes__at_start_of_timestep    # restore old value of the convolution
            ...

            # add as a last statement:
            integrate_odes(K__conv__spikes)


    If there is a delta kernel, do not increment the dummy variable, but increment the variable on the lhs of the expression. The dummy variable always stays at zero.

    .. code-block:: nestml

       onReceive(spikes, priority=?????????/):
           V_m += spikes / C_m   # bump by spike weight

    """

    _default_options = {
        "convolution_separator": "__conv__",
        "diff_order_symbol": "__d",
        "simplify_expression": "sympy.logcombine(sympy.powsimp(sympy.expand(expr)))"
    }

    def __init__(self, options: Optional[Mapping[str, Any]] = None):
        super(Transformer, self).__init__(options)

        # ODE-toolbox printers
        self._constant_printer = ConstantPrinter()
        self._ode_toolbox_variable_printer = ODEToolboxVariablePrinter(None)
        self._ode_toolbox_function_call_printer = ODEToolboxFunctionCallPrinter(None)
        self._ode_toolbox_printer = ODEToolboxExpressionPrinter(simple_expression_printer=UnitlessSympySimpleExpressionPrinter(variable_printer=self._ode_toolbox_variable_printer,
                                                                                                                               constant_printer=self._constant_printer,
                                                                                                                               function_call_printer=self._ode_toolbox_function_call_printer))
        self._ode_toolbox_variable_printer._expression_printer = self._ode_toolbox_printer
        self._ode_toolbox_function_call_printer._expression_printer = self._ode_toolbox_printer

    def transform(self, models: Union[ASTNode, Sequence[ASTNode]]) -> Union[ASTNode, Sequence[ASTNode]]:
        r"""Transform a model or a list of models. Return an updated model or list of models."""
        for model in models:
            print("-------- MODEL BEFORE TRANSFORM ------------")
            print(model)
            kernel_buffers = self.generate_kernel_buffers(model)
            delta_factors = self.get_delta_factors_from_convolutions(model)

            print("Delta factors: ")
            for k, v in delta_factors.items():
                print("var = " + str(k[0]) + ", inport = " + str(k[1]) + ", expr = " + str(v))

            odetoolbox_indict = self.transform_kernels_to_json(model, kernel_buffers)
            print("odetoolbox indict: " + str(odetoolbox_indict))
            odetoolbox.Config.config["differential_order_symbol"] = "___D"
            solvers_json, shape_sys, shapes = odetoolbox._analysis(odetoolbox_indict,
                                                                   disable_stiffness_check=True,
                                                                   disable_analytic_solver=True,
                                                                   preserve_expressions=True,
                                                                   simplify_expression=self.get_option("simplify_expression"),
                                                                   log_level=FrontendConfiguration.logging_level)
            odetoolbox.Config.config["differential_order_symbol"] = "__d"
            print("odetoolbox outdict: " + str(solvers_json))

            self.replace_convolve_calls_with_buffers_(model)
            delta_factors.update(self.get_delta_factors_from_input_port_references(model))
            self.remove_initial_values_for_kernels(model)
            self.create_initial_values_for_kernels(model, solvers_json, kernel_buffers)
            self.create_spike_update_event_handlers(model, solvers_json, delta_factors)
            self.remove_kernel_definitions_from_equations_blocks(model)
            self.add_kernel_variables_to_integrate_odes_calls(model, solvers_json)
            self.add_restore_kernel_variables_to_start_of_timestep(model, solvers_json)
            self.add_temporary_kernel_variables_copy(model, solvers_json)
            self.add_integrate_odes_call_for_kernel_variables(model, solvers_json)
            self.add_convolution_equations(model, solvers_json)
            self.replace_port_variable_names_with_buffers_(model)

            print("-------- MODEL AFTER TRANSFORM ------------")
            print(model)
            print("-------------------------------------------")

        return models

    def add_restore_kernel_variables_to_start_of_timestep(self, model, solvers_json):
        r"""For each integrate_odes() call in the model, append statements restoring the kernel variables to the values at the start of the timestep"""

        var_names = []
        for solver_dict in solvers_json:
            if solver_dict is None:
                continue

            for var_name, expr in solver_dict["initial_values"].items():
                var_names.append(var_name)

        class IntegrateODEsFunctionCallVisitor(ASTVisitor):
            all_args = None

            def __init__(self):
                super().__init__()

            def visit_small_stmt(self, node: ASTSmallStmt):
                self._visit(node)

            def visit_simple_expression(self, node: ASTSimpleExpression):
                self._visit(node)

            def _visit(self, node):
                if node.is_function_call() and node.get_function_call().get_name() == PredefinedFunctions.INTEGRATE_ODES:
                    parent_stmt = node.get_parent()
                    parent_block = parent_stmt.get_parent()
                    assert isinstance(parent_block, ASTBlock)
                    idx = parent_block.stmts.index(parent_stmt)

                    for i, var_name in enumerate(var_names):
                        var = ASTNodeFactory.create_ast_variable(var_name + "__at_start_of_timestep")
                        var.update_scope(parent_block.get_scope())
                        expr = ASTNodeFactory.create_ast_simple_expression(variable=var)
                        ast_assignment = ASTNodeFactory.create_ast_assignment(lhs=ASTUtils.get_variable_by_name(model, var_name),
                                                                              is_direct_assignment=True,
                                                                              expression=expr, source_position=ASTSourceLocation.get_added_source_position())
                        ast_assignment.update_scope(parent_block.get_scope())
                        ast_small_stmt = ASTNodeFactory.create_ast_small_stmt(assignment=ast_assignment)
                        ast_small_stmt.update_scope(parent_block.get_scope())
                        ast_stmt = ASTNodeFactory.create_ast_stmt(small_stmt=ast_small_stmt)
                        ast_stmt.update_scope(parent_block.get_scope())

                        parent_block.stmts.insert(idx + i + 1, ast_stmt)

        model.accept(IntegrateODEsFunctionCallVisitor())

    def add_kernel_variables_to_integrate_odes_calls(self, model, solvers_json):
        for solver_dict in solvers_json:
            if solver_dict is None:
                continue

            for var_name, expr in solver_dict["initial_values"].items():
                var = ASTUtils.get_variable_by_name(model, var_name)
                ASTUtils.add_state_var_to_integrate_odes_calls(model, var)

        model.accept(ASTParentVisitor())

    def add_integrate_odes_call_for_kernel_variables(self, model, solvers_json):
        var_names = []
        for solver_dict in solvers_json:
            if solver_dict is None:
                continue

            for var_name, expr in solver_dict["initial_values"].items():
                var_names.append(var_name)

        if var_names:
            args = ASTUtils.resolve_variables_to_simple_expressions(model, var_names)
            ast_function_call = ASTNodeFactory.create_ast_function_call("integrate_odes", args)
            ASTUtils.add_function_call_to_update_block(ast_function_call, model)
            model.accept(ASTParentVisitor())

    def add_temporary_kernel_variables_copy(self, model, solvers_json):
        var_names = []
        for solver_dict in solvers_json:
            if solver_dict is None:
                continue

            for var_name, expr in solver_dict["initial_values"].items():
                var_names.append(var_name)

        scope = model.get_update_blocks()[0].scope

        for var_name in var_names:
            var = ASTNodeFactory.create_ast_variable(var_name + "__at_start_of_timestep")
            var.scope = scope
            expr = ASTNodeFactory.create_ast_simple_expression(variable=ASTUtils.get_variable_by_name(model, var_name))
            ast_declaration = ASTNodeFactory.create_ast_declaration(variables=[var],
                                                                    data_type=ASTDataType(is_real=True),
                                                                    expression=expr, source_position=ASTSourceLocation.get_added_source_position())
            ast_declaration.update_scope(scope)
            ast_small_stmt = ASTNodeFactory.create_ast_small_stmt(declaration=ast_declaration)
            ast_small_stmt.update_scope(scope)
            ast_stmt = ASTNodeFactory.create_ast_stmt(small_stmt=ast_small_stmt)
            ast_stmt.update_scope(scope)

            model.get_update_blocks()[0].get_block().stmts.insert(0, ast_stmt)

        model.accept(ASTParentVisitor())
        model.accept(ASTSymbolTableVisitor())

    def construct_kernel_spike_buf_name(self, kernel_var_name: str, spike_input_port: ASTInputPort, order: int, diff_order_symbol: Optional[str] = None):
        """
        Construct a kernel-buffer name as ``KERNEL_NAME__conv__INPUT_PORT_NAME``

        For example, if the kernel is
        .. code-block::
            kernel I_kernel = exp(-t / tau_x)

        and the input port is
        .. code-block::
            pre_spikes nS <- spike

        then the constructed variable will be ``I_kernel__conv__pre_pikes``
        """
        assert type(kernel_var_name) is str
        assert type(order) is int

        if isinstance(spike_input_port, ASTSimpleExpression):
            spike_input_port = spike_input_port.get_variable()

        if not isinstance(spike_input_port, str):
            spike_input_port_name = spike_input_port.get_name()
        else:
            spike_input_port_name = spike_input_port

        if isinstance(spike_input_port, ASTVariable):
            if spike_input_port.has_vector_parameter():
                spike_input_port_name += "_" + str(self.get_numeric_vector_size(spike_input_port))

        if not diff_order_symbol:
            diff_order_symbol = self.get_option("diff_order_symbol")

        return kernel_var_name.replace("$", "__DOLLAR") + self.get_option("convolution_separator") + spike_input_port_name + diff_order_symbol * order

    def replace_rhs_variable(self, expr: ASTExpression, variable_name_to_replace: str, kernel_var: ASTVariable,
                             spike_buf: ASTInputPort):
        """
        Replace variable names in definitions of kernel dynamics
        :param expr: expression in which to replace the variables
        :param variable_name_to_replace: variable name to replace in the expression
        :param kernel_var: kernel variable instance
        :param spike_buf: input port instance
        :return:
        """
        def replace_kernel_var(node):
            if type(node) is ASTSimpleExpression \
                    and node.is_variable() \
                    and node.get_variable().get_name() == variable_name_to_replace:
                var_order = node.get_variable().get_differential_order()
                new_variable_name = self.construct_kernel_spike_buf_name(
                    kernel_var.get_name(), spike_buf, var_order - 1, diff_order_symbol="'")
                new_variable = ASTVariable(new_variable_name, var_order)
                new_variable.set_source_position(node.get_variable().get_source_position())
                node.set_variable(new_variable)

        expr.accept(ASTHigherOrderVisitor(visit_funcs=replace_kernel_var))

    def replace_rhs_variables(self, expr: ASTExpression, kernel_buffers: Mapping[ASTKernel, ASTInputPort]):
        """
        Replace variable names in definitions of kernel dynamics.

        Say that the kernel is

        .. code-block::

            G = -G / tau

        Its variable symbol might be replaced by "G__conv__spikesEx":

        .. code-block::

            G__conv__spikesEx = -G / tau

        This function updates the right-hand side of `expr` so that it would also read (in this example):

        .. code-block::

            G__conv__spikesEx = -G__conv__spikesEx / tau

        These equations will later on be fed to ode-toolbox, so we use the symbol "'" to indicate differential order.

        Note that for kernels/systems of ODE of dimension > 1, all variable orders and all variables for this kernel will already be present in `kernel_buffers`.
        """
        for kernel, spike_buf in kernel_buffers:
            for kernel_var in kernel.get_variables():
                variable_name_to_replace = kernel_var.get_name()
                self.replace_rhs_variable(expr, variable_name_to_replace=variable_name_to_replace,
                                          kernel_var=kernel_var, spike_buf=spike_buf)

    @classmethod
    def remove_initial_values_for_kernels(cls, model: ASTModel) -> None:
        r"""
        Remove initial values for original declarations (e.g. g_in, g_in', V_m); these will be replaced with the initial value expressions returned from ODE-toolbox.
        """
        symbols_to_remove = set()
        for equations_block in model.get_equations_blocks():
            for kernel in equations_block.get_kernels():
                for kernel_var in kernel.get_variables():
                    kernel_var_order = kernel_var.get_differential_order()
                    for order in range(kernel_var_order):
                        symbol_name = kernel_var.get_name() + "'" * order
                        symbols_to_remove.add(symbol_name)

        decl_to_remove = set()
        for symbol_name in symbols_to_remove:
            for state_block in model.get_state_blocks():
                for decl in state_block.get_declarations():
                    if len(decl.get_variables()) == 1:
                        if decl.get_variables()[0].get_name() == symbol_name:
                            decl_to_remove.add(decl)
                    else:
                        for var in decl.get_variables():
                            if var.get_name() == symbol_name:
                                decl.variables.remove(var)

        for decl in decl_to_remove:
            for state_block in model.get_state_blocks():
                if decl in state_block.get_declarations():
                    state_block.get_declarations().remove(decl)

    def create_initial_values_for_kernels(self, model: ASTModel, solver_dicts: List[Dict], kernels: List[ASTKernel]) -> None:
        r"""
        Add the variables used in kernels from the ode-toolbox result dictionary as ODEs in NESTML AST
        """
        for solver_dict in solver_dicts:
            if solver_dict is None:
                continue

            for var_name, expr in solver_dict["initial_values"].items():
                spike_in_port_name = var_name.split(self.get_option("convolution_separator"))[1]
                spike_in_port_name = spike_in_port_name.split("__d")[0]
                spike_in_port_name = spike_in_port_name.split("___D")[0]
                spike_in_port = ASTUtils.get_input_port_by_name(model.get_input_blocks(), spike_in_port_name)
                type_str = "real"
                if spike_in_port:
                    differential_order: int = len(re.findall("__d", var_name))
                    if differential_order:
                        type_str = "(s**-" + str(differential_order) + ")"

                expr = "0 " + type_str    # for kernels, "initial value" returned by ode-toolbox is actually the increment value; the actual initial value is 0 (property of the convolution)
                if not ASTUtils.declaration_in_state_block(model, var_name):
                    ASTUtils.add_declaration_to_state_block(model, var_name, expr, type_str)

    def is_delta_kernel(self, kernel: ASTKernel) -> bool:
        """
        Catches definition of kernel, or reference (function call or variable name) of a delta kernel function.
        """
        if not isinstance(kernel, ASTKernel):
            return False

        if len(kernel.get_variables()) != 1:
            # delta kernel not allowed if more than one variable is defined in this kernel
            return False

        expr = kernel.get_expressions()[0]

        rhs_is_delta_kernel = type(expr) is ASTSimpleExpression \
            and expr.is_function_call() \
            and expr.get_function_call().get_scope().resolve_to_symbol(expr.get_function_call().get_name(), SymbolKind.FUNCTION).equals(PredefinedFunctions.name2function["delta"])

        rhs_is_multiplied_delta_kernel = type(expr) is ASTExpression \
            and type(expr.get_rhs()) is ASTSimpleExpression \
            and expr.get_rhs().is_function_call() \
            and expr.get_rhs().get_function_call().get_scope().resolve_to_symbol(expr.get_rhs().get_function_call().get_name(), SymbolKind.FUNCTION).equals(PredefinedFunctions.name2function["delta"])

        return rhs_is_delta_kernel or rhs_is_multiplied_delta_kernel

    def replace_convolve_calls_with_buffers_(self, model: ASTModel) -> None:
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
                kernel = model.get_kernel_by_name(var.get_name())

                _expr.set_function_call(None)
                if self.is_delta_kernel(kernel):
                    # special case for delta kernels: they will be incremented elsewhere
                    _expr.numeric_literal = 0.
                else:
                    buffer_var = self.construct_kernel_spike_buf_name(var.get_name(), spike_input_port, var.get_differential_order() - 1)
                    ast_variable = ASTVariable(buffer_var)
                    ast_variable.set_source_position(_expr.get_source_position())
                    _expr.set_variable(ast_variable)

        def func(x):
            return replace_function_call_through_var(x) if isinstance(x, ASTSimpleExpression) else True

        for equations_block in model.get_equations_blocks():
            equations_block.accept(ASTHigherOrderVisitor(func))

    def replace_port_variable_names_with_buffers_(self, model: ASTModel) -> None:
        r"""
        Replace all occurrences of ``spike_input_port`` with the numeric literal zero.
        """

        spike_inports = model.get_spike_input_ports()

        def replace_inport_through_numeric_literal(_expr=None):
            if _expr.variable:
                var = _expr.variable
                for inport in spike_inports:
                    if var.get_name() == inport.name:
                        _expr.variable = None
                        _expr.numeric_literal = 0.

        def func(x):
            return replace_inport_through_numeric_literal(x) if isinstance(x, ASTSimpleExpression) else True

        for equations_block in model.get_equations_blocks():
            equations_block.accept(ASTHigherOrderVisitor(func))

    def generate_kernel_buffers(self, model: ASTModel) -> Mapping[ASTKernel, ASTInputPort]:
        r"""
        For every occurrence of a convolution of the form `convolve(var, spike_buf)`: add the element `(kernel, spike_buf)` to the set, with `kernel` being the kernel that contains variable `var`.
        """
        kernel_buffers = set()
        for equations_block in model.get_equations_blocks():
            convolve_calls = ASTUtils.get_convolve_function_calls(equations_block)
            print("convolve_calls = " + " ".join([str(s) for s in convolve_calls]))
            for convolve in convolve_calls:
                el = (convolve.get_args()[0], convolve.get_args()[1])
                sym = convolve.get_args()[0].get_scope().resolve_to_symbol(convolve.get_args()[0].get_variable().name, SymbolKind.VARIABLE)
                if sym is None:
                    raise Exception("No initial value(s) defined for kernel with variable \""
                                    + convolve.get_args()[0].get_variable().get_complete_name() + "\"")
                if sym.block_type == BlockType.INPUT:
                    # swap the order
                    el = (el[1], el[0])

                # find the corresponding kernel object
                var = el[0].get_variable()
                assert var is not None
                kernel = model.get_kernel_by_name(var.get_name())
                assert kernel is not None, "In convolution \"convolve(" + str(var.name) + ", " + str(
                    el[1]) + ")\": no kernel by name \"" + var.get_name() + "\" found in model."

                el = (kernel, el[1])
                if not (str(el[0]), str(el[1])) in [(str(el[0]), str(el[1])) for el in kernel_buffers]:
                    kernel_buffers.add(el)

        return kernel_buffers

    def add_convolution_equations(self, model, solver_dicts):
        if not model.get_equations_blocks():
            ASTUtils.create_equations_block()

        assert len(model.get_equations_blocks()) <= 1

        equations_block = model.get_equations_blocks()[0]

        for solver_dict in solver_dicts:
            if solver_dict is None:
                continue

            for var_name, expr_str in solver_dict["update_expressions"].items():
                expr = ModelParser.parse_expression(expr_str)
                expr.update_scope(model.get_scope())
                expr.accept(ASTSymbolTableVisitor())

                if isinstance(expr.type, RealTypeSymbol):
                    expr = ModelParser.parse_expression("(" + expr_str + ") / ms")    # change per second XXX: why ms? this should be simulation platform target-dependent. See
                    expr.update_scope(model.get_scope())
                    expr.accept(ASTSymbolTableVisitor())

                var = ASTNodeFactory.create_ast_variable(var_name, differential_order=1, source_position=ASTSourceLocation.get_added_source_position())
                var.update_scope(equations_block.get_scope())
                ast_ode_equation = ASTNodeFactory.create_ast_ode_equation(lhs=var, rhs=expr, source_position=ASTSourceLocation.get_added_source_position())
                ast_ode_equation.update_scope(equations_block.get_scope())
                equations_block.declarations.append(ast_ode_equation)

        model.accept(ASTParentVisitor())
        model.accept(ASTSymbolTableVisitor())

    def remove_kernel_definitions_from_equations_blocks(self, model: ASTModel) -> ASTDeclaration:
        r"""
        Removes all kernels in equations blocks.
        """
        for equations_block in model.get_equations_blocks():
            decl_to_remove = set()
            for decl in equations_block.get_declarations():
                if type(decl) is ASTKernel:
                    decl_to_remove.add(decl)

            for decl in decl_to_remove:
                equations_block.get_declarations().remove(decl)

    def transform_kernels_to_json(self, model: ASTModel, kernel_buffers: List[Tuple[ASTKernel, ASTInputPort]]) -> Dict:
        """
        Converts AST node to a JSON representation suitable for passing to ode-toolbox.

        Each kernel has to be generated for each spike buffer convolve in which it occurs, e.g. if the NESTML model code contains the statements

         .. code-block::

           convolve(G, exc_spikes)
           convolve(G, inh_spikes)

        then `kernel_buffers` will contain the pairs `(G, exc_spikes)` and `(G, inh_spikes)`, from which two ODEs will be generated, with dynamical state (variable) names `G__X__exc_spikes` and `G__X__inh_spikes`.
        """
        odetoolbox_indict = {}
        odetoolbox_indict["dynamics"] = []

        for kernel, spike_input_port in kernel_buffers:
            for kernel_var in kernel.get_variables():
                expr = ASTUtils.get_expr_from_kernel_var(kernel, kernel_var.get_complete_name())
                kernel_order = kernel_var.get_differential_order()
                kernel_X_spike_buf_name_ticks = self.construct_kernel_spike_buf_name(kernel_var.get_name(), spike_input_port, kernel_order, diff_order_symbol="'")

                self.replace_rhs_variables(expr, kernel_buffers)

                if self.is_delta_kernel(kernel):
                    # ODE-toolbox does not know how to handle "delta(t)", so replace this by a constant rhs so it generates a dummy (do-nothing) update expression
                    expr = "1"

                entry = {"expression": kernel_X_spike_buf_name_ticks + " = " + str(expr), "initial_values": {}}

                # initial values need to be declared for order 1 up to kernel order (e.g. none for kernel function
                # f(t) = ...; 1 for kernel ODE f'(t) = ...; 2 for f''(t) = ... and so on)
                for order in range(kernel_order):
                    iv_sym_name_ode_toolbox = self.construct_kernel_spike_buf_name(kernel_var.get_name(), spike_input_port, order, diff_order_symbol="'")
                    symbol_name_ = kernel_var.get_name() + "'" * order
                    symbol = model.get_scope().resolve_to_symbol(symbol_name_, SymbolKind.VARIABLE)
                    assert symbol is not None, "Could not find initial value for variable " + symbol_name_
                    initial_value_expr = symbol.get_declaring_expression()
                    assert initial_value_expr is not None, "No initial value found for variable name " + symbol_name_
                    entry["initial_values"][iv_sym_name_ode_toolbox] = self._ode_toolbox_printer.print(initial_value_expr)

                odetoolbox_indict["dynamics"].append(entry)

            odetoolbox_indict["parameters"] = {}
            for parameters_block in model.get_parameters_blocks():
                for decl in parameters_block.get_declarations():
                    for var in decl.variables:
                        odetoolbox_indict["parameters"][var.get_complete_name()] = self._ode_toolbox_printer.print(decl.get_expression())

        return odetoolbox_indict

    def get_delta_factors_from_convolutions(self, model: ASTModel) -> dict:
        r"""
        For every occurrence of a convolution of the form `x^(n) = a * convolve(kernel, inport) + ...` where `kernel` is a delta function, add the element `(x^(n), inport) --> a` to the set.
        """
        delta_factors = {}

        for equations_block in model.get_equations_blocks():
            for ode_eq in equations_block.get_ode_equations():
                var = ode_eq.get_lhs()
                expr = ode_eq.get_rhs()
                conv_calls = ASTUtils.get_convolve_function_calls(expr)
                for conv_call in conv_calls:
                    assert len(conv_call.args) == 2, "convolve() function call should have precisely two arguments: kernel and spike input port"
                    kernel = conv_call.args[0]
                    if self.is_delta_kernel(model.get_kernel_by_name(kernel.get_variable().get_name())):
                        inport = conv_call.args[1].get_variable()
                        factor_str = self.get_factor_str_from_expr_and_inport(expr, str(conv_call))
                        assert factor_str
                        delta_factors[(var, inport)] = factor_str

        return delta_factors

    def get_factor_str_from_expr_and_inport(self, expr, sub_expr):
        from sympy.physics.units import Quantity, Unit, milli, micro, nano, pico, femto, kilo, mega, volt, ampere, ohm, farad, second, meter, hertz
        from pynestml.codegeneration.printers.nestml_printer_units_as_factors import NESTMLPrinterUnitsAsFactors
        from sympy import sympify

        units = {
            'V': volt,                      # Volt
            'mV': milli * volt,             # Millivolt (10^-3 V)
            'uV': micro * volt,             # Microvolt (10^-6 V)
            'nV': nano * volt,              # Nanovolt (10^-9 V)

            'A': ampere,                    # Ampere
            'mA': milli * ampere,           # Milliampere (10^-3 A)
            'uA': micro * ampere,           # Microampere (10^-6 A)
            'nA': nano * ampere,            # Nanoampere (10^-9 A)

            'Ohm': ohm,                     # Ohm
            'kOhm': kilo * ohm,             # Kiloohm (10^3 Ohm)
            'MOhm': mega * ohm,             # Megaohm (10^6 Ohm)

            'F': farad,                     # Farad
            'uF': micro * farad,            # Microfarad (10^-6 F)
            'nF': nano * farad,             # Nanofarad (10^-9 F)
            'pF': pico * farad,             # Picofarad (10^-12 F)
            'fF': femto * farad,            # Femtofarad (10^-15 F)

            's': second,                    # Second
            'ms': milli * second,           # Millisecond (10^-3 s)
            'us': micro * second,           # Microsecond (10^-6 s)
            'ns': nano * second,            # Nanosecond (10^-9 s)

            'Hz': hertz,                    # Hertz (1/s)
            'kHz': kilo * hertz,            # Kilohertz (10^3 Hz)
            'MHz': mega * hertz,            # Megahertz (10^6 Hz)

            'm': meter,                     # Meter
            'mm': milli * meter,            # Millimeter (10^-3 m)
            'um': micro * meter,            # Micrometer (10^-6 m)
            'nm': nano * meter,             # Nanometer (10^-9 m)
        }

        expr_str = NESTMLPrinterUnitsAsFactors().print(expr)

        print("In get_delta_factors_from_input_port_references(): parsing " + expr_str)
        sympy_expr = sympify(expr_str, locals=units)
        sympy_expr = sympy.expand(sympy_expr)
        sympy_conv_expr = sympy.parsing.sympy_parser.parse_expr(sub_expr)
        factor_str = []
        for term in sympy.Add.make_args(sympy_expr):
            if term.find(sympy_conv_expr):
                _expr = str(term.replace(sympy_conv_expr, 1))
                factor_str.append(_expr)

        factor_str = " + ".join(factor_str)

        return factor_str

    def get_delta_factors_from_input_port_references(self, model: ASTModel) -> dict:
        r"""
        For every occurrence of a convolution of the form ``x^(n) = a * inport + ...``, add the element `(x^(n), inport) --> a` to the set.
        """
        delta_factors = {}
        print("-----")
        print("get_delta_factors_from_input_port_references")

        spike_inports = model.get_spike_input_ports()
        for equations_block in model.get_equations_blocks():
            for ode_eq in equations_block.get_ode_equations():
                var = ode_eq.get_lhs()
                expr = ode_eq.get_rhs()

                for inport in spike_inports:
                    # inport = ASTUtils.get_input_port_by_name(model.get_input_blocks(), inport.name)

                    inport = ASTNodeFactory.create_ast_variable(inport.name)
                    inport.update_scope(equations_block.get_scope())

                    factor_str = self.get_factor_str_from_expr_and_inport(expr, inport.name)

                    if factor_str:
                        delta_factors[(var, inport)] = factor_str

        for k, v in delta_factors.items():
            print("var = " + str(k[0]) + ", inport = " + str(k[1]) + ", expr = " + str(v))
        print("-----")

        return delta_factors

    def create_spike_update_event_handlers(self, model: ASTModel, solver_dicts, delta_factors) -> Tuple[Dict[str, ASTAssignment], Dict[str, ASTAssignment]]:
        r"""
        Generate the equations that update the dynamical variables when incoming spikes arrive. To be invoked after
        ode-toolbox.

        For example, a resulting `assignment_str` could be "I_kernel_in += (inh_spikes/nS) * 1". The values are taken from the initial values for each corresponding dynamical variable, either from ode-toolbox or directly from user specification in the model.
        from the initial values for each corresponding dynamical variable, either from ode-toolbox or directly from
        user specification in the model.

        Note that for kernels, `initial_values` actually contains the increment upon spike arrival, rather than the
        initial value of the corresponding ODE dimension.
        """

        spike_in_port_to_stmts = {}
        for solver_dict in solver_dicts:
            for var, expr in solver_dict["initial_values"].items():
                expr = str(expr)
                if expr in ["0", "0.", "0.0"]:
                    continue    # skip adding the statement if we are only adding zero

                spike_in_port_name = var.split(self.get_option("convolution_separator"))[1]
                spike_in_port_name = spike_in_port_name.split("__d")[0]
                spike_in_port_name = spike_in_port_name.split("___D")[0]
                spike_in_port = ASTUtils.get_input_port_by_name(model.get_input_blocks(), spike_in_port_name)
                type_str = "real"

                assert spike_in_port
                differential_order: int = len(re.findall("__d", var))
                if differential_order:
                    type_str = "(s**-" + str(differential_order) + ")"

                assignment_str = var + " += "
                assignment_str += "1000. * (" + str(spike_in_port_name) + ")"  # XXX: not clear where the factor 1E3 comes from
                if not expr in ["1.", "1.0", "1"]:
                    assignment_str += " * (" + expr + ")"

                kernel = model.get_kernel_by_name(var.split(self.get_option("convolution_separator"))[0])
                if kernel and self.is_delta_kernel(kernel):
                    continue

                ast_assignment = ModelParser.parse_assignment(assignment_str)
                ast_assignment.update_scope(model.get_scope())
                ast_assignment.accept(ASTSymbolTableVisitor())

                ast_small_stmt = ASTNodeFactory.create_ast_small_stmt(assignment=ast_assignment)
                ast_stmt = ASTNodeFactory.create_ast_stmt(small_stmt=ast_small_stmt)

                if not spike_in_port_name in spike_in_port_to_stmts.keys():
                    spike_in_port_to_stmts[spike_in_port_name] = []

                spike_in_port_to_stmts[spike_in_port_name].append(ast_stmt)

        for k, factor in delta_factors.items():
            var = k[0]
            inport = k[1]
            assignment_str = var.get_name() + "'" * (var.get_differential_order() - 1) + " += "
            if not factor in ["1.", "1.0", "1"]:
                factor_expr = ModelParser.parse_expression(factor)
                factor_expr.update_scope(model.get_scope())
                factor_expr.accept(ASTSymbolTableVisitor())
                assignment_str += "(" + self._ode_toolbox_printer.print(factor_expr) + ") * "

            if "_is_post_port" in dir(inport) and inport._is_post_port:
                orig_port_name = inport[:inport.index("__for_")]
                buffer_type = model.paired_synapse.get_scope().resolve_to_symbol(orig_port_name, SymbolKind.VARIABLE).get_type_symbol()
            else:
                buffer_type = model.get_scope().resolve_to_symbol(inport.get_name(), SymbolKind.VARIABLE).get_type_symbol()

            assignment_str += str(inport)
            if not buffer_type.print_nestml_type() in ["1.", "1.0", "1"]:
                assignment_str += " / (" + buffer_type.print_nestml_type() + ")"
            ast_assignment = ModelParser.parse_assignment(assignment_str)
            ast_assignment.update_scope(model.get_scope())
            ast_assignment.accept(ASTSymbolTableVisitor())
            ast_small_stmt = ASTNodeFactory.create_ast_small_stmt(assignment=ast_assignment)
            ast_small_stmt.update_scope(model.get_scope())
            ast_small_stmt.accept(ASTSymbolTableVisitor())
            ast_stmt = ASTNodeFactory.create_ast_stmt(small_stmt=ast_small_stmt)
            ast_stmt.update_scope(model.get_scope())
            ast_stmt.accept(ASTSymbolTableVisitor())

            inport_name = inport.get_name()
            if inport.has_vector_parameter():
                inport_name += "_" + str(ASTUtils.get_numeric_vector_size(inport))

            if not spike_in_port_name in spike_in_port_to_stmts.keys():
                spike_in_port_to_stmts[spike_in_port_name] = []

            spike_in_port_to_stmts[spike_in_port_name].append(ast_stmt)

        # for every input port, add an onreceive block with its update statements
        for in_port, stmts in spike_in_port_to_stmts.items():
            stmts_block = ASTNodeFactory.create_ast_block(stmts, ASTSourceLocation.get_added_source_position())
            on_receive_block = ASTNodeFactory.create_ast_on_receive_block(stmts_block,
                                                                          in_port,
                                                                          const_parameters=None,  # XXX: TODO: add priority here!
                                                                          source_position=ASTSourceLocation.get_added_source_position())

            model.get_body().get_body_elements().append(on_receive_block)

        model.accept(ASTParentVisitor())
