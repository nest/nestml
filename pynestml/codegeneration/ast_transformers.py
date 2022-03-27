# -*- coding: utf-8 -*-
#
# ast_transformers.py
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

import re

from typing import List, Mapping, Union, Sequence

import sympy

from pynestml.codegeneration.printers.printer import Printer
from pynestml.meta_model.ast_block import ASTBlock
from pynestml.meta_model.ast_block_with_variables import ASTBlockWithVariables
from pynestml.meta_model.ast_equations_block import ASTEquationsBlock
from pynestml.meta_model.ast_input_block import ASTInputBlock
from pynestml.meta_model.ast_input_port import ASTInputPort
from pynestml.meta_model.ast_node import ASTNode
from pynestml.symbols.variable_symbol import BlockType
from pynestml.meta_model.ast_assignment import ASTAssignment
from pynestml.meta_model.ast_declaration import ASTDeclaration
from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.meta_model.ast_node_factory import ASTNodeFactory
from pynestml.meta_model.ast_kernel import ASTKernel
from pynestml.meta_model.ast_inline_expression import ASTInlineExpression
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.meta_model.ast_ode_equation import ASTOdeEquation
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.meta_model.ast_return_stmt import ASTReturnStmt
from pynestml.utils.ast_source_location import ASTSourceLocation
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.symbols.symbol import SymbolKind
from pynestml.utils.ast_utils import ASTUtils
from pynestml.utils.model_parser import ModelParser
from pynestml.utils.ode_transformer import OdeTransformer
from pynestml.visitors.ast_higher_order_visitor import ASTHigherOrderVisitor
from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor


class ASTTransformers:
    _variable_matching_template = r'(\b)({})(\b)'

    @classmethod
    def add_declarations_to_internals(cls, neuron: ASTNeuron, declarations: Mapping[str, str]) -> ASTNeuron:
        """
        Adds the variables as stored in the declaration tuples to the neuron.
        :param neuron: a single neuron instance
        :param declarations: a map of variable names to declarations
        :return: a modified neuron
        """
        for variable in declarations:
            cls.add_declaration_to_internals(neuron, variable, declarations[variable])
        return neuron

    @classmethod
    def add_declaration_to_internals(cls, neuron: ASTNeuron, variable_name: str, init_expression: str) -> ASTNeuron:
        """
        Adds the variable as stored in the declaration tuple to the neuron. The declared variable is of type real.
        :param neuron: a single neuron instance
        :param variable_name: the name of the variable to add
        :param init_expression: initialization expression
        :return: the neuron extended by the variable
        """
        tmp = ModelParser.parse_expression(init_expression)
        vector_variable = ASTUtils.get_vectorized_variable(tmp, neuron.get_scope())

        declaration_string = variable_name + ' real' + (
            '[' + vector_variable.get_vector_parameter() + ']'
            if vector_variable is not None and vector_variable.has_vector_parameter() else '') + ' = ' + init_expression
        ast_declaration = ModelParser.parse_declaration(declaration_string)
        if vector_variable is not None:
            ast_declaration.set_size_parameter(vector_variable.get_vector_parameter())
        neuron.add_to_internal_block(ast_declaration)
        ast_declaration.update_scope(neuron.get_internals_blocks().get_scope())
        symtable_visitor = ASTSymbolTableVisitor()
        symtable_visitor.block_type_stack.push(BlockType.INTERNALS)
        ast_declaration.accept(symtable_visitor)
        symtable_visitor.block_type_stack.pop()
        return neuron

    @classmethod
    def add_declarations_to_state_block(cls, neuron: ASTNeuron, variables: List, initial_values: List) -> ASTNeuron:
        """
        Adds a single declaration to the state block of the neuron.
        :param neuron: a neuron
        :param variables: list of variables
        :param initial_values: list of initial values
        :return: a modified neuron
        """
        for variable, initial_value in zip(variables, initial_values):
            cls.add_declaration_to_state_block(neuron, variable, initial_value)
        return neuron

    @classmethod
    def add_declaration_to_state_block(cls, neuron: ASTNeuron, variable: str, initial_value: str) -> ASTNeuron:
        """
        Adds a single declaration to the state block of the neuron. The declared variable is of type real.
        :param neuron: a neuron
        :param variable: state variable to add
        :param initial_value: corresponding initial value
        :return: a modified neuron
        """
        tmp = ModelParser.parse_expression(initial_value)
        vector_variable = ASTUtils.get_vectorized_variable(tmp, neuron.get_scope())
        declaration_string = variable + ' real' + (
            '[' + vector_variable.get_vector_parameter() + ']'
            if vector_variable is not None and vector_variable.has_vector_parameter() else '') + ' = ' + initial_value
        ast_declaration = ModelParser.parse_declaration(declaration_string)
        if vector_variable is not None:
            ast_declaration.set_size_parameter(vector_variable.get_vector_parameter())
        neuron.add_to_state_block(ast_declaration)
        ast_declaration.update_scope(neuron.get_state_blocks().get_scope())

        symtable_visitor = ASTSymbolTableVisitor()
        symtable_visitor.block_type_stack.push(BlockType.STATE)
        ast_declaration.accept(symtable_visitor)
        symtable_visitor.block_type_stack.pop()

        return neuron

    @classmethod
    def declaration_in_state_block(cls, neuron: ASTNeuron, variable_name: str) -> bool:
        """
        Checks if the variable is declared in the state block
        :param neuron:
        :param variable_name:
        :return:
        """
        assert type(variable_name) is str

        if neuron.get_state_blocks() is None:
            return False

        for decl in neuron.get_state_blocks().get_declarations():
            for var in decl.get_variables():
                if var.get_complete_name() == variable_name:
                    return True

        return False

    @classmethod
    def add_assignment_to_update_block(cls, assignment: ASTAssignment, neuron: ASTNeuron) -> ASTNeuron:
        """
        Adds a single assignment to the end of the update block of the handed over neuron.
        :param assignment: a single assignment
        :param neuron: a single neuron instance
        :return: the modified neuron
        """
        small_stmt = ASTNodeFactory.create_ast_small_stmt(assignment=assignment,
                                                          source_position=ASTSourceLocation.get_added_source_position())
        stmt = ASTNodeFactory.create_ast_stmt(small_stmt=small_stmt,
                                              source_position=ASTSourceLocation.get_added_source_position())
        if not neuron.get_update_blocks():
            neuron.create_empty_update_block()
        neuron.get_update_blocks().get_block().get_stmts().append(stmt)
        small_stmt.update_scope(neuron.get_update_blocks().get_block().get_scope())
        stmt.update_scope(neuron.get_update_blocks().get_block().get_scope())
        return neuron

    @classmethod
    def add_declaration_to_update_block(cls, declaration: ASTDeclaration, neuron: ASTNeuron) -> ASTNeuron:
        """
        Adds a single declaration to the end of the update block of the handed over neuron.
        :param declaration: ASTDeclaration node to add
        :param neuron: a single neuron instance
        :return: a modified neuron
        """
        small_stmt = ASTNodeFactory.create_ast_small_stmt(declaration=declaration,
                                                          source_position=ASTSourceLocation.get_added_source_position())
        stmt = ASTNodeFactory.create_ast_stmt(small_stmt=small_stmt,
                                              source_position=ASTSourceLocation.get_added_source_position())
        if not neuron.get_update_blocks():
            neuron.create_empty_update_block()
        neuron.get_update_blocks().get_block().get_stmts().append(stmt)
        small_stmt.update_scope(neuron.get_update_blocks().get_block().get_scope())
        stmt.update_scope(neuron.get_update_blocks().get_block().get_scope())
        return neuron

    @classmethod
    def add_state_updates(cls, neuron: ASTNeuron, update_expressions: Mapping[str, str]) -> ASTNeuron:
        """
        Adds all update instructions as contained in the solver output to the update block of the neuron.
        :param neuron: a single neuron
        :param update_expressions: map of variables to corresponding updates during the update step.
        :return: a modified version of the neuron
        """
        for variable, update_expression in update_expressions.items():
            declaration_statement = variable + '__tmp real = ' + update_expression
            cls.add_declaration_to_update_block(ModelParser.parse_declaration(declaration_statement), neuron)
        for variable, update_expression in update_expressions.items():
            cls.add_assignment_to_update_block(ModelParser.parse_assignment(variable + ' = ' + variable + '__tmp'),
                                               neuron)
        return neuron

    @classmethod
    def variable_in_solver(cls, kernel_var: str, solver_dicts: List[dict]) -> bool:
        """
        Check if a variable by this name is defined in the ode-toolbox solver results,
        """

        for solver_dict in solver_dicts:
            if solver_dict is None:
                continue

            for var_name in solver_dict["state_variables"]:
                var_name_base = var_name.split("__X__")[0]
                if var_name_base == kernel_var:
                    return True

        return False

    @classmethod
    def is_ode_variable(cls, var_base_name: str, neuron: ASTNeuron) -> bool:
        """
        Checks if the variable is present in an ODE
        """
        equations_block = neuron.get_equations_blocks()
        for ode_eq in equations_block.get_ode_equations():
            var = ode_eq.get_lhs()
            if var.get_name() == var_base_name:
                return True
        return False

    @classmethod
    def variable_in_kernels(cls, var_name: str, kernels: List[ASTKernel]) -> bool:
        """
        Check if a variable by this name (in ode-toolbox style) is defined in the ode-toolbox solver results
        """

        var_name_base = var_name.split("__X__")[0]
        var_name_base = var_name_base.split("__d")[0]
        var_name_base = var_name_base.replace("__DOLLAR", "$")

        for kernel in kernels:
            for kernel_var in kernel.get_variables():
                if var_name_base == kernel_var.get_name():
                    return True

        return False

    @classmethod
    def get_initial_value_from_ode_toolbox_result(cls, var_name: str, solver_dicts: List[dict]) -> str:
        """
        Get the initial value of the variable with the given name from the ode-toolbox results JSON.

        N.B. the variable name is given in ode-toolbox notation.
        """

        for solver_dict in solver_dicts:
            if solver_dict is None:
                continue

            if var_name in solver_dict["state_variables"]:
                return solver_dict["initial_values"][var_name]

        assert False, "Initial value not found for ODE with name \"" + var_name + "\""

    @classmethod
    def get_kernel_var_order_from_ode_toolbox_result(cls, kernel_var: str, solver_dicts: List[dict]) -> int:
        """
        Get the differential order of the variable with the given name from the ode-toolbox results JSON.

        N.B. the variable name is given in NESTML notation, e.g. "g_in$"; convert to ode-toolbox export format notation (e.g. "g_in__DOLLAR").
        """

        kernel_var = kernel_var.replace("$", "__DOLLAR")

        order = -1
        for solver_dict in solver_dicts:
            if solver_dict is None:
                continue

            for var_name in solver_dict["state_variables"]:
                var_name_base = var_name.split("__X__")[0]
                var_name_base = var_name_base.split("__d")[0]
                if var_name_base == kernel_var:
                    order = max(order, var_name.count("__d") + 1)

        assert order >= 0, "Variable of name \"" + kernel_var + "\" not found in ode-toolbox result"
        return order

    @classmethod
    def to_ode_toolbox_processed_name(cls, name: str) -> str:
        """
        Convert name in the same way as ode-toolbox does from input to output, i.e. returned names are compatible with ode-toolbox output
        """
        return name.replace("$", "__DOLLAR").replace("'", "__d")

    @classmethod
    def to_ode_toolbox_name(cls, name: str) -> str:
        """
        Convert to a name suitable for ode-toolbox input
        """
        return name.replace("$", "__DOLLAR")

    @classmethod
    def get_expr_from_kernel_var(cls, kernel: ASTKernel, var_name: str) -> Union[ASTExpression, ASTSimpleExpression]:
        """
        Get the expression using the kernel variable
        """
        assert type(var_name) == str
        for var, expr in zip(kernel.get_variables(), kernel.get_expressions()):
            if var.get_complete_name() == var_name:
                return expr
        assert False, "variable name not found in kernel"

    @classmethod
    def construct_kernel_X_spike_buf_name(cls, kernel_var_name: str, spike_input_port: ASTInputPort, order: int,
                                          diff_order_symbol="__d"):
        """
        Construct a kernel-buffer name as <KERNEL_NAME__X__INPUT_PORT_NAME>

        For example, if the kernel is
        .. code-block::
            kernel I_kernel = exp(-t / tau_x)

        and the input port is
        .. code-block::
            pre_spikes nS <- spike

        then the constructed variable will be 'I_kernel__X__pre_pikes'
        """
        assert type(kernel_var_name) is str
        assert type(order) is int
        assert type(diff_order_symbol) is str
        return kernel_var_name.replace("$", "__DOLLAR") + "__X__" + str(spike_input_port) + diff_order_symbol * order

    @classmethod
    def replace_rhs_variable(cls, expr: ASTExpression, variable_name_to_replace: str, kernel_var: ASTVariable,
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
                new_variable_name = cls.construct_kernel_X_spike_buf_name(
                    kernel_var.get_name(), spike_buf, var_order - 1, diff_order_symbol="'")
                new_variable = ASTVariable(new_variable_name, var_order)
                new_variable.set_source_position(node.get_variable().get_source_position())
                node.set_variable(new_variable)

        expr.accept(ASTHigherOrderVisitor(visit_funcs=replace_kernel_var))

    @classmethod
    def replace_rhs_variables(cls, expr: ASTExpression, kernel_buffers: Mapping[ASTKernel, ASTInputPort]):
        """
        Replace variable names in definitions of kernel dynamics.

        Say that the kernel is

        .. code-block::

            G = -G / tau

        Its variable symbol might be replaced by "G__X__spikesEx":

        .. code-block::

            G__X__spikesEx = -G / tau

        This function updates the right-hand side of `expr` so that it would also read (in this example):

        .. code-block::

            G__X__spikesEx = -G__X__spikesEx / tau

        These equations will later on be fed to ode-toolbox, so we use the symbol "'" to indicate differential order.

        Note that for kernels/systems of ODE of dimension > 1, all variable orders and all variables for this kernel will already be present in `kernel_buffers`.
        """
        for kernel, spike_buf in kernel_buffers:
            for kernel_var in kernel.get_variables():
                variable_name_to_replace = kernel_var.get_name()
                cls.replace_rhs_variable(expr, variable_name_to_replace=variable_name_to_replace,
                                         kernel_var=kernel_var, spike_buf=spike_buf)

    @classmethod
    def is_delta_kernel(cls, kernel: ASTKernel) -> bool:
        """
        Catches definition of kernel, or reference (function call or variable name) of a delta kernel function.
        """
        if type(kernel) is ASTKernel:
            if not len(kernel.get_variables()) == 1:
                # delta kernel not allowed if more than one variable is defined in this kernel
                return False
            expr = kernel.get_expressions()[0]
        else:
            expr = kernel

        rhs_is_delta_kernel = type(expr) is ASTSimpleExpression \
            and expr.is_function_call() \
            and expr.get_function_call().get_scope().resolve_to_symbol(
            expr.get_function_call().get_name(), SymbolKind.FUNCTION) == PredefinedFunctions.name2function["delta"]
        rhs_is_multiplied_delta_kernel = type(expr) is ASTExpression \
            and type(expr.get_rhs()) is ASTSimpleExpression \
            and expr.get_rhs().is_function_call() \
            and expr.get_rhs().get_function_call().get_scope().resolve_to_symbol(
            expr.get_rhs().get_function_call().get_name(), SymbolKind.FUNCTION) == PredefinedFunctions.name2function[
            "delta"]
        return rhs_is_delta_kernel or rhs_is_multiplied_delta_kernel

    @classmethod
    def get_input_port_by_name(cls, input_block: ASTInputBlock, port_name: str) -> ASTInputPort:
        """
        Get the input port given the port name
        :param input_block: block to be searched
        :param port_name: name of the input port
        :return: input port object
        """
        for input_port in input_block.get_input_ports():
            if input_port.name == port_name:
                return input_port
        return None

    @classmethod
    def get_parameter_by_name(cls, parameters_block: ASTBlockWithVariables, var_name: str) -> ASTDeclaration:
        """
        Get the declaration based on the name of the parameter
        :param parameters_block: the parameter block
        :param var_name: variable name to be searched
        :return: declaration containing the variable
        """
        for decl in parameters_block.get_declarations():
            for var in decl.get_variables():
                if var.get_name() == var_name:
                    return decl
        return None

    @classmethod
    def collect_variable_names_in_expression(cls, expr: ASTNode) -> List[ASTVariable]:
        """
        Collect all occurrences of variables (`ASTVariable`), kernels (`ASTKernel`) XXX ...
        :param expr: expression to collect the variables from
        :return: a list of variables
        """
        vars_used_ = []

        def collect_vars(_expr=None):
            var = None
            if isinstance(_expr, ASTSimpleExpression) and _expr.is_variable():
                var = _expr.get_variable()
            elif isinstance(_expr, ASTVariable):
                var = _expr

            if var:
                vars_used_.append(var)

        expr.accept(ASTHigherOrderVisitor(lambda x: collect_vars(x)))

        return vars_used_

    @classmethod
    def get_declarations_from_block(cls, var_name: str, block: ASTBlock) -> List[ASTDeclaration]:
        """
        Get declarations from the given block containing the given variable.
        :param var_name: variable name
        :param block: block to collect the variable declarations
        :return: a list of declarations
        """
        if block is None:
            return []

        if not type(var_name) is str:
            var_name = str(var_name)

        decls = []

        for decl in block.get_declarations():
            if isinstance(decl, ASTInlineExpression):
                var_names = [decl.get_variable_name()]
            elif isinstance(decl, ASTOdeEquation):
                var_names = [decl.get_lhs().get_name()]
            else:
                var_names = [var.get_name() for var in decl.get_variables()]

            for _var_name in var_names:
                if _var_name == var_name:
                    decls.append(decl)
                    break

        return decls

    @classmethod
    def recursive_dependent_variables_search(cls, vars: List[str], node: ASTNode) -> List[str]:
        """
        Collect all the variable names used in the defining expressions of a list of variables.
        :param vars: list of variable names moved from synapse to neuron
        :param node: ASTNode to perform the recursive search
        :return: list of variable names from the recursive search
        """
        for var in vars:
            assert type(var) is str
        vars_used = []
        vars_to_check = set([var for var in vars])
        vars_checked = set()
        while vars_to_check:
            var = None
            for _var in vars_to_check:
                if not _var in vars_checked:
                    var = _var
                    break
            if not var:
                # all variables checked
                break
            decls = cls.get_declarations_from_block(var, node.get_equations_blocks())

            if decls:
                assert len(decls) == 1
                decl = decls[0]
                if (type(decl) in [ASTDeclaration, ASTReturnStmt] and decl.has_expression()) \
                        or type(decl) is ASTInlineExpression:
                    vars_used.extend(cls.collect_variable_names_in_expression(decl.get_expression()))
                elif type(decl) is ASTOdeEquation:
                    vars_used.extend(cls.collect_variable_names_in_expression(decl.get_rhs()))
                elif type(decl) is ASTKernel:
                    for expr in decl.get_expressions():
                        vars_used.extend(cls.collect_variable_names_in_expression(expr))
                else:
                    raise Exception("Unknown type " + str(type(decl)))
                vars_used = [str(var) for var in vars_used]
                vars_to_check = vars_to_check.union(set(vars_used))
            vars_checked.add(var)

        return list(set(vars_checked))

    @classmethod
    def remove_initial_values_for_kernels(cls, neuron: ASTNeuron) -> None:
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

    @classmethod
    def update_initial_values_for_odes(cls, neuron: ASTNeuron, solver_dicts: List[dict]) -> None:
        """
        Update initial values for original ODE declarations (e.g. V_m', g_ahp'') that are present in the model
        before ODE-toolbox processing, with the formatted variable names and initial values returned by ODE-toolbox.
        """
        assert isinstance(neuron.get_equations_blocks(), ASTEquationsBlock), "only one equation block should be present"

        if neuron.get_state_blocks() is None:
            return

        for iv_decl in neuron.get_state_blocks().get_declarations():
            for var in iv_decl.get_variables():
                var_name = var.get_complete_name()
                if cls.is_ode_variable(var.get_name(), neuron):
                    assert cls.variable_in_solver(cls.to_ode_toolbox_processed_name(var_name), solver_dicts)

                    # replace the left-hand side variable name by the ode-toolbox format
                    var.set_name(cls.to_ode_toolbox_processed_name(var.get_complete_name()))
                    var.set_differential_order(0)

                    # replace the defining expression by the ode-toolbox result
                    iv_expr = cls.get_initial_value_from_ode_toolbox_result(
                        cls.to_ode_toolbox_processed_name(var_name), solver_dicts)
                    assert iv_expr is not None
                    iv_expr = ModelParser.parse_expression(iv_expr)
                    iv_expr.update_scope(neuron.get_state_blocks().get_scope())
                    iv_decl.set_expression(iv_expr)

    @classmethod
    def create_initial_values_for_kernels(cls, neuron: ASTNeuron, solver_dicts: List[dict], kernels: List[ASTKernel]) -> None:
        """
        Add the variables used in kernels from the ode-toolbox result dictionary as ODEs in NESTML AST
        """
        for solver_dict in solver_dicts:
            if solver_dict is None:
                continue
            for var_name in solver_dict["initial_values"].keys():
                if cls.variable_in_kernels(var_name, kernels):
                    # original initial value expressions should have been removed to make place for ode-toolbox results
                    assert not cls.declaration_in_state_block(neuron, var_name)

        for solver_dict in solver_dicts:
            if solver_dict is None:
                continue

            for var_name, expr in solver_dict["initial_values"].items():
                # overwrite is allowed because initial values might be repeated between numeric and analytic solver
                if cls.variable_in_kernels(var_name, kernels):
                    expr = "0"    # for kernels, "initial value" returned by ode-toolbox is actually the increment value; the actual initial value is assumed to be 0
                    if not cls.declaration_in_state_block(neuron, var_name):
                        cls.add_declaration_to_state_block(neuron, var_name, expr)

    @classmethod
    def transform_ode_and_kernels_to_json(cls, neuron: ASTNeuron, parameters_block: ASTBlockWithVariables,
                                          kernel_buffers: Mapping[ASTKernel, ASTInputPort], printer: Printer) -> dict:
        """
        Converts AST node to a JSON representation suitable for passing to ode-toolbox.

        Each kernel has to be generated for each spike buffer convolve in which it occurs, e.g. if the NESTML model code contains the statements

        .. code-block::

           convolve(G, exc_spikes)
           convolve(G, inh_spikes)

        then `kernel_buffers` will contain the pairs `(G, exc_spikes)` and `(G, inh_spikes)`, from which two ODEs will be generated, with dynamical state (variable) names `G__X__exc_spikes` and `G__X__inh_spikes`.

        :param parameters_block:
        :param kernel_buffers:
        :param neuron:
        :return: Dict
        """
        odetoolbox_indict = {}

        odetoolbox_indict["dynamics"] = []
        equations_block = neuron.get_equations_block()
        for equation in equations_block.get_ode_equations():
            # n.b. includes single quotation marks to indicate differential order
            lhs = cls.to_ode_toolbox_name(equation.get_lhs().get_complete_name())
            rhs = printer.print_expression(equation.get_rhs())
            entry = {"expression": lhs + " = " + rhs}
            symbol_name = equation.get_lhs().get_name()
            symbol = equations_block.get_scope().resolve_to_symbol(symbol_name, SymbolKind.VARIABLE)

            entry["initial_values"] = {}
            symbol_order = equation.get_lhs().get_differential_order()
            for order in range(symbol_order):
                iv_symbol_name = symbol_name + "'" * order
                initial_value_expr = neuron.get_initial_value(iv_symbol_name)
                if initial_value_expr:
                    expr = printer.print_expression(initial_value_expr)
                    entry["initial_values"][cls.to_ode_toolbox_name(iv_symbol_name)] = expr
            odetoolbox_indict["dynamics"].append(entry)

        # write a copy for each (kernel, spike buffer) combination
        for kernel, spike_input_port in kernel_buffers:

            if cls.is_delta_kernel(kernel):
                # delta function -- skip passing this to ode-toolbox
                continue

            for kernel_var in kernel.get_variables():
                expr = cls.get_expr_from_kernel_var(kernel, kernel_var.get_complete_name())
                kernel_order = kernel_var.get_differential_order()
                kernel_X_spike_buf_name_ticks = cls.construct_kernel_X_spike_buf_name(
                    kernel_var.get_name(), spike_input_port, kernel_order, diff_order_symbol="'")

                cls.replace_rhs_variables(expr, kernel_buffers)

                entry = {"expression": kernel_X_spike_buf_name_ticks + " = " + str(expr), "initial_values": {}}

                # initial values need to be declared for order 1 up to kernel order (e.g. none for kernel function
                # f(t) = ...; 1 for kernel ODE f'(t) = ...; 2 for f''(t) = ... and so on)
                for order in range(kernel_order):
                    iv_sym_name_ode_toolbox = cls.construct_kernel_X_spike_buf_name(
                        kernel_var.get_name(), spike_input_port, order, diff_order_symbol="'")
                    symbol_name_ = kernel_var.get_name() + "'" * order
                    symbol = equations_block.get_scope().resolve_to_symbol(symbol_name_, SymbolKind.VARIABLE)
                    assert symbol is not None, "Could not find initial value for variable " + symbol_name_
                    initial_value_expr = symbol.get_declaring_expression()
                    assert initial_value_expr is not None, "No initial value found for variable name " + symbol_name_
                    entry["initial_values"][iv_sym_name_ode_toolbox] = printer.print_expression(initial_value_expr)

                odetoolbox_indict["dynamics"].append(entry)

        odetoolbox_indict["parameters"] = {}
        if parameters_block is not None:
            for decl in parameters_block.get_declarations():
                for var in decl.variables:
                    odetoolbox_indict["parameters"][var.get_complete_name(
                    )] = printer.print_expression(decl.get_expression())

        return odetoolbox_indict

    @classmethod
    def remove_ode_definitions_from_equations_block(cls, neuron: ASTNeuron) -> None:
        """
        Removes all ODEs in this block.
        """
        equations_block = neuron.get_equations_block()

        decl_to_remove = set()
        for decl in equations_block.get_ode_equations():
            decl_to_remove.add(decl)

        for decl in decl_to_remove:
            equations_block.get_declarations().remove(decl)

    @classmethod
    def make_inline_expressions_self_contained(cls, inline_expressions: List[ASTInlineExpression]) -> List[ASTInlineExpression]:
        """
        Make inline_expressions self contained, i.e. without any references to other inline_expressions.

        TODO: it should be a method inside of the ASTInlineExpression
        TODO: this should be done by means of a visitor

        :param inline_expressions: A sorted list with entries ASTInlineExpression.
        :return: A list with ASTInlineExpressions. Defining expressions don't depend on each other.
        """
        for source in inline_expressions:
            source_position = source.get_source_position()
            for target in inline_expressions:
                matcher = re.compile(cls._variable_matching_template.format(source.get_variable_name()))
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

    @classmethod
    def replace_inline_expressions_through_defining_expressions(cls, definitions: Sequence[ASTOdeEquation],
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
                matcher = re.compile(cls._variable_matching_template.format(m.get_variable_name()))
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

    @classmethod
    def get_delta_factors_(cls, neuron: ASTNeuron, equations_block: ASTEquationsBlock) -> dict:
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
                if cls.is_delta_kernel(neuron.get_kernel_by_name(kernel.get_variable().get_name())):
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

    @classmethod
    def remove_kernel_definitions_from_equations_block(cls, neuron: ASTNeuron) -> ASTDeclaration:
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

    @classmethod
    def add_timestep_symbol(cls, neuron: ASTNeuron) -> None:
        """
        Add timestep variable to the internals block
        """
        assert neuron.get_initial_value(
            "__h") is None, "\"__h\" is a reserved name, please do not use variables by this name in your NESTML file"
        assert not "__h" in [sym.name for sym in neuron.get_internal_symbols(
        )], "\"__h\" is a reserved name, please do not use variables by this name in your NESTML file"
        neuron.add_to_internal_block(ModelParser.parse_declaration('__h ms = resolution()'), index=0)

    @classmethod
    def generate_kernel_buffers_(cls, neuron: ASTNeuron, equations_block: ASTEquationsBlock) -> Mapping[ASTKernel, ASTInputPort]:
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

    @classmethod
    def replace_convolution_aliasing_inlines(cls, neuron: ASTNeuron) -> None:
        """
        Replace all occurrences of kernel names (e.g. ``I_dend`` and ``I_dend'`` for a definition involving a second-order kernel ``inline kernel I_dend = convolve(kern_name, spike_buf)``) with the ODE-toolbox generated variable ``kern_name__X__spike_buf``.
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
            if isinstance(decl, ASTInlineExpression) \
               and isinstance(decl.get_expression(), ASTSimpleExpression) \
               and '__X__' in str(decl.get_expression()):
                replace_with_var_name = decl.get_expression().get_variable().get_name()
                neuron.accept(ASTHigherOrderVisitor(lambda x: replace_var(
                    x, decl.get_variable_name(), replace_with_var_name)))

    @classmethod
    def replace_variable_names_in_expressions(cls, neuron: ASTNeuron, solver_dicts: List[dict]) -> None:
        """
        Replace all occurrences of variables names in NESTML format (e.g. `g_ex$''`)` with the ode-toolbox formatted
        variable name (e.g. `g_ex__DOLLAR__d__d`).

        Variables aliasing convolutions should already have been covered by replace_convolution_aliasing_inlines().
        """
        def replace_var(_expr=None):
            if isinstance(_expr, ASTSimpleExpression) and _expr.is_variable():
                var = _expr.get_variable()
                if cls.variable_in_solver(cls.to_ode_toolbox_processed_name(var.get_complete_name()), solver_dicts):
                    ast_variable = ASTVariable(cls.to_ode_toolbox_processed_name(
                        var.get_complete_name()), differential_order=0)
                    ast_variable.set_source_position(var.get_source_position())
                    _expr.set_variable(ast_variable)

            elif isinstance(_expr, ASTVariable):
                var = _expr
                if cls.variable_in_solver(cls.to_ode_toolbox_processed_name(var.get_complete_name()), solver_dicts):
                    var.set_name(cls.to_ode_toolbox_processed_name(var.get_complete_name()))
                    var.set_differential_order(0)

        def func(x):
            return replace_var(x)

        neuron.accept(ASTHigherOrderVisitor(func))

    @classmethod
    def replace_convolve_calls_with_buffers_(cls, neuron: ASTNeuron, equations_block: ASTEquationsBlock) -> None:
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
                buffer_var = cls.construct_kernel_X_spike_buf_name(
                    var.get_name(), spike_input_port, var.get_differential_order() - 1)
                if cls.is_delta_kernel(kernel):
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
