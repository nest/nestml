# -*- coding: utf-8 -*-
#
# ast_utils.py
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

from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Union

import re
import sympy

import odetoolbox

from pynestml.codegeneration.printers.ast_printer import ASTPrinter
from pynestml.codegeneration.printers.cpp_variable_printer import CppVariablePrinter
from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.generated.PyNestMLLexer import PyNestMLLexer
from pynestml.meta_model.ast_assignment import ASTAssignment
from pynestml.meta_model.ast_stmts_body import ASTStmtsBody
from pynestml.meta_model.ast_block_with_variables import ASTBlockWithVariables
from pynestml.meta_model.ast_declaration import ASTDeclaration
from pynestml.meta_model.ast_elif_clause import ASTElifClause
from pynestml.meta_model.ast_equations_block import ASTEquationsBlock
from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_external_variable import ASTExternalVariable
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.meta_model.ast_if_clause import ASTIfClause
from pynestml.meta_model.ast_inline_expression import ASTInlineExpression
from pynestml.meta_model.ast_input_block import ASTInputBlock
from pynestml.meta_model.ast_input_port import ASTInputPort
from pynestml.meta_model.ast_kernel import ASTKernel
from pynestml.meta_model.ast_model import ASTModel
from pynestml.meta_model.ast_model_body import ASTModelBody
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_node_factory import ASTNodeFactory
from pynestml.meta_model.ast_ode_equation import ASTOdeEquation
from pynestml.meta_model.ast_on_receive_block import ASTOnReceiveBlock
from pynestml.meta_model.ast_return_stmt import ASTReturnStmt
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.meta_model.ast_small_stmt import ASTSmallStmt
from pynestml.meta_model.ast_stmt import ASTStmt
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.symbol_table.scope import Scope
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.symbols.predefined_variables import PredefinedVariables
from pynestml.symbols.symbol import SymbolKind
from pynestml.symbols.unit_type_symbol import UnitTypeSymbol
from pynestml.symbols.variable_symbol import BlockType
from pynestml.symbols.variable_symbol import VariableSymbol, VariableType
from pynestml.utils.ast_source_location import ASTSourceLocation
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.messages import Messages
from pynestml.utils.string_utils import removesuffix
from pynestml.visitors.ast_higher_order_visitor import ASTHigherOrderVisitor
from pynestml.visitors.ast_visitor import ASTVisitor


class ASTUtils:
    r"""
    A collection of helpful methods for AST manipulation.
    """

    @classmethod
    def get_all_neurons(cls, list_of_compilation_units):
        """
        For a list of compilation units, it returns a list containing all neurons defined in all compilation
        units.
        :param list_of_compilation_units: a list of compilation units.
        :type list_of_compilation_units: list(ASTNestMLCompilationUnit)
        :return: a list of neurons
        :rtype: list(ASTModel)
        """
        ret = list()
        for compilationUnit in list_of_compilation_units:
            ret.extend(compilationUnit.get_model_list())
        return ret

    @classmethod
    def get_all_models(cls, list_of_compilation_units):
        """
        For a list of compilation units, it returns a list containing all nodes defined in all compilation
        units.
        :param list_of_compilation_units: a list of compilation units.
        :type list_of_compilation_units: list(ASTNestMLCompilationUnit)
        :return: a list of nodes
        :rtype: list(ASTNode)
        """
        from pynestml.meta_model.ast_model import ASTModel
        ret = list()
        for compilationUnit in list_of_compilation_units:
            if isinstance(compilationUnit, ASTModel):
                ret.extend(compilationUnit.get_model_list())
        return ret

    @classmethod
    def is_small_stmt(cls, ast):
        """
        Indicates whether the handed over meta_model is a small statement. Used in the template.
        :param ast: a single meta_model object.
        :type ast: AST_
        :return: True if small stmt, otherwise False.
        :rtype: bool
        """
        from pynestml.meta_model.ast_small_stmt import ASTSmallStmt
        return isinstance(ast, ASTSmallStmt)

    @classmethod
    def is_compound_stmt(cls, ast):
        """
        Indicates whether the handed over meta_model is a compound statement. Used in the template.
        :param ast: a single meta_model object.
        :type ast: AST_
        :return: True if compound stmt, otherwise False.
        :rtype: bool
        """
        from pynestml.meta_model.ast_compound_stmt import ASTCompoundStmt
        return isinstance(ast, ASTCompoundStmt)

    @classmethod
    def filter_variables_list(cls, variables_list, variables_to_filter_by):
        """
        """
        variables_to_filter_by = [str(var) for var in variables_to_filter_by]
        ret = []
        for var in variables_list:
            if var in variables_to_filter_by:
                ret.append(var)
                # Add higher order variables of var if not already in the filter list
                ret.extend(cls.get_higher_order_variables(var, variables_list, variables_to_filter_by))
        return ret

    @classmethod
    def get_higher_order_variables(cls, var, variables_list, variables_to_filter_by) -> List[str]:
        """
        Returns a list of higher order state variables of ``var`` from the ``variables_list`` that are not already present in ``variables_to_filter_by``.
        """
        ret = []
        for v in variables_list:
            order = v.count('__d')
            if order > 0:
                if v.split("__d")[0] == var and v not in variables_to_filter_by:
                    ret.append(v)
        return ret

    @classmethod
    def has_spike_input(cls, body: ASTModelBody) -> bool:
        """
        Checks if the handed over neuron contains a spike input port.
        :param body: a single body element.
        :return: True if spike input port is contained, otherwise False.
        """
        inputs = (inputL for block in body.get_input_blocks() for inputL in block.get_input_ports())
        for port in inputs:
            if port.is_spike():
                return True
        return False

    @classmethod
    def has_continuous_input(cls, body: ASTModelBody) -> bool:
        """
        Checks if the handed over neuron contains a continuous time input port.
        :param body: a single body element.
        :return: True if continuous time input port is contained, otherwise False.
        """
        inputs = (inputL for block in body.get_input_blocks() for inputL in block.get_input_ports())
        for inputL in inputs:
            if inputL.is_continuous():
                return True
        return False

    @classmethod
    def compute_type_name(cls, data_type) -> str:
        """
        Computes the representation of the data type.
        :param data_type: a single data type.
        :type data_type: ast_data_type
        :return: the corresponding representation.
        """
        if data_type.is_boolean:
            return 'boolean'

        if data_type.is_integer:
            return 'integer'

        if data_type.is_real:
            return 'real'

        if data_type.is_string:
            return 'string'

        if data_type.is_void:
            return 'void'

        if data_type.is_unit_type():
            return str(data_type)

        Logger.log_message(message='Type could not be derived!', log_level=LoggingLevel.ERROR)

        return ''

    @classmethod
    def deconstruct_assignment(cls, lhs=None, is_plus=False, is_minus=False, is_times=False, is_divide=False,
                               _rhs=None):
        """
        From lhs and rhs it constructs a new rhs which corresponds to direct assignment.
        E.g.: a += b*c -> a = a + b*c
        :param lhs: a lhs rhs
        :type lhs: ast_expression or ast_simple_expression
        :param is_plus: is plus assignment
        :type is_plus: bool
        :param is_minus: is minus assignment
        :type is_minus: bool
        :param is_times: is times assignment
        :type is_times: bool
        :param is_divide: is divide assignment
        :type is_divide: bool
        :param _rhs: a rhs rhs
        :type _rhs: ASTExpression or ASTSimpleExpression
        :return: a new direct assignment rhs.
        :rtype: ASTExpression
        """
        from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor
        from pynestml.meta_model.ast_node_factory import ASTNodeFactory
        assert ((is_plus + is_minus + is_times + is_divide) == 1), \
            '(PyNestML.CodeGeneration.Utils) Type of assignment not correctly specified!'
        if is_plus:
            op = ASTNodeFactory.create_ast_arithmetic_operator(is_plus_op=True,
                                                               source_position=_rhs.get_source_position())
        elif is_minus:
            op = ASTNodeFactory.create_ast_arithmetic_operator(is_minus_op=True,
                                                               source_position=_rhs.get_source_position())
        elif is_times:
            op = ASTNodeFactory.create_ast_arithmetic_operator(is_times_op=True,
                                                               source_position=_rhs.get_source_position())
        else:
            op = ASTNodeFactory.create_ast_arithmetic_operator(is_div_op=True,
                                                               source_position=_rhs.get_source_position())
        var_expr = ASTNodeFactory.create_ast_simple_expression(variable=lhs,
                                                               source_position=lhs.get_source_position())
        var_expr.update_scope(lhs.get_scope())
        op.update_scope(lhs.get_scope())
        rhs_in_brackets = ASTNodeFactory.create_ast_expression(is_encapsulated=True, expression=_rhs,
                                                               source_position=_rhs.get_source_position())
        rhs_in_brackets.update_scope(_rhs.get_scope())
        expr = ASTNodeFactory.create_ast_compound_expression(lhs=var_expr, binary_operator=op, rhs=rhs_in_brackets,
                                                             source_position=_rhs.get_source_position())
        expr.update_scope(lhs.get_scope())
        # update the symbols
        expr.accept(ASTSymbolTableVisitor())
        return expr

    @classmethod
    def get_inline_expression_symbols(cls, ast: ASTNode) -> List[VariableSymbol]:
        """
        For the handed over AST node, this method collects all inline expression variable symbols in it.
        :param ast: a single AST node
        :return: a list of all inline expression variable symbols
        """
        from pynestml.visitors.ast_higher_order_visitor import ASTHigherOrderVisitor
        from pynestml.meta_model.ast_variable import ASTVariable
        res = list()

        def loc_get_vars(node):
            if isinstance(node, ASTVariable):
                res.append(node)

        ast.accept(ASTHigherOrderVisitor(visit_funcs=loc_get_vars))

        ret = list()
        for var in res:
            if '\'' not in var.get_complete_name():
                symbol = ast.get_scope().resolve_to_symbol(var.get_complete_name(), SymbolKind.VARIABLE)
                if symbol is not None and symbol.is_inline_expression:
                    ret.append(symbol)
        return ret

    @classmethod
    def is_castable_to(cls, type_a, type_b):
        """
        Indicates whether typeA can be casted to type b. E.g., in Nest, a unit is always casted down to real, thus
        a unit where unit is expected is allowed.
        :param type_a: a single TypeSymbol
        :type type_a: type_symbol
        :param type_b: a single TypeSymbol
        :type type_b: TypeSymbol
        :return: True if castable, otherwise False
        :rtype: bool
        """
        # we can always cast from unit to real
        if type_a.is_unit and type_b.is_real:
            return True
        elif type_a.is_boolean and type_b.is_real:
            return True
        elif type_a.is_real and type_b.is_boolean:
            return True
        elif type_a.is_integer and type_b.is_real:
            return True
        elif type_a.is_real and type_b.is_integer:
            return True
        else:
            return False

    @classmethod
    def get_all(cls, ast, node_type):
        """
        Finds all meta_model which are part of the tree as spanned by the handed over meta_model.
        The type has to be specified.
        :param ast: a single meta_model node
        :type ast: AST_
        :param node_type: the type
        :type node_type: AST_
        :return: a list of all meta_model of the specified type
        :rtype: list(AST_)
        """
        from pynestml.visitors.ast_higher_order_visitor import ASTHigherOrderVisitor
        ret = list()

        def loc_get_all_of_type(node):
            if isinstance(node, node_type):
                ret.append(node)

        ast.accept(ASTHigherOrderVisitor(visit_funcs=loc_get_all_of_type))
        return ret

    @classmethod
    def get_vectorized_variable(cls, ast, scope):
        """
        Returns all variable symbols which are contained in the scope and have a size parameter.
        :param ast: a single meta_model
        :type ast: AST_
        :param scope: a scope object
        :type scope: Scope
        :return: the first element with the size parameter
        :rtype: variable_symbol
        """
        from pynestml.meta_model.ast_variable import ASTVariable
        from pynestml.symbols.symbol import SymbolKind
        variables = (var for var in cls.get_all(ast, ASTVariable) if
                     scope.resolve_to_symbol(var.get_complete_name(), SymbolKind.VARIABLE))
        for var in variables:
            symbol = scope.resolve_to_symbol(var.get_complete_name(), SymbolKind.VARIABLE)
            if symbol is not None and symbol.has_vector_parameter():
                return symbol
        return None

    @classmethod
    def get_numeric_vector_size(cls, variable: ASTVariable) -> int:
        """
        Returns the numerical size of the vector by resolving any variable used as a size parameter in declaration
        :param variable: vector variable
        :return: the size of the vector as a numerical value
        """
        vector_parameter = variable.get_vector_parameter()
        if vector_parameter.is_variable():
            symbol = vector_parameter.get_scope().resolve_to_symbol(vector_parameter.get_variable().get_complete_name(), SymbolKind.VARIABLE)
            return symbol.get_declaring_expression().get_numeric_literal()

        assert vector_parameter.is_numeric_literal()
        return int(vector_parameter.get_numeric_literal())

    @classmethod
    def get_numeric_vector_input_port_size(cls, port: ASTInputPort) -> int:
        """
        Returns the numerical size of the vector by resolving any variable used as a size parameter in declaration
        :param port: input port
        :return: the size of the vector as a numerical value
        """
        size_parameter = port.get_size_parameter()
        if size_parameter.is_variable():
            symbol = port.get_scope().resolve_to_symbol(size_parameter.get_variable().get_name(),
                                                        SymbolKind.VARIABLE)
            return symbol.get_declaring_expression().get_numeric_literal()

        assert size_parameter.is_numeric_literal()
        return int(size_parameter.get_numeric_literal())

    @classmethod
    def get_function_call(cls, ast, function_name):
        """
        Collects for a given name all function calls in a given meta_model node.
        :param ast: a single node
        :type ast: ast_node
        :param function_name: the name of the function
        :type function_name: str
        :return: a list of all function calls contained in _ast
        :rtype: list(ASTFunctionCall)
        """
        from pynestml.visitors.ast_higher_order_visitor import ASTHigherOrderVisitor
        ret = list()

        def loc_get_function(node):
            if isinstance(node, ASTFunctionCall) and node.get_name() == function_name:
                ret.append(node)

        ast.accept(ASTHigherOrderVisitor(loc_get_function, list()))
        return ret

    @classmethod
    def get_tuple_from_single_dict_entry(cls, dict_entry):
        """
        For a given dict of length 1, this method returns a tuple consisting of (key,value)
        :param dict_entry: a dict of length 1
        :type dict_entry:  dict
        :return: a single tuple
        :rtype: tuple
        """
        if len(dict_entry.keys()) == 1:
            # key() is not an actual list, thus indexing is not possible.
            for keyIter in dict_entry.keys():
                key = keyIter
                value = dict_entry[key]
                return key, value
        else:
            return None, None

    @classmethod
    def needs_arguments(cls, ast_function_call):
        """
        Indicates whether a given function call has any arguments
        :param ast_function_call: a function call
        :type ast_function_call: ASTFunctionCall
        :return: True if arguments given, otherwise false
        :rtype: bool
        """
        return len(ast_function_call.get_args()) > 0

    @classmethod
    def create_internal_block(cls, model: ASTModel):
        r"""
        Create an internals block in the handed over model if it does not yet exist.
        :param model: a single model
        :return: the modified model (the model is also changed in-place)
        """
        from pynestml.meta_model.ast_node_factory import ASTNodeFactory
        if not model.get_internals_blocks():
            block = ASTNodeFactory.create_ast_block_with_variables(False, False, True, list(),
                                                                   ASTSourceLocation.get_added_source_position())
            block.update_scope(model.get_scope())
            model.get_body().get_body_elements().append(block)

        from pynestml.visitors.ast_parent_visitor import ASTParentVisitor
        model.accept(ASTParentVisitor())

        return model

    @classmethod
    def create_state_block(cls, model: ASTModel):
        r"""
        Create a state block in the handed over model if it does not yet exist.
        :param model: a single model
        :return: the modified model (the model is also changed in-place)
        """
        # local import since otherwise circular dependency
        from pynestml.meta_model.ast_node_factory import ASTNodeFactory
        if not model.get_state_blocks():
            block = ASTNodeFactory.create_ast_block_with_variables(True, False, False, list(),
                                                                   ASTSourceLocation.get_added_source_position())
            block.update_scope(model.get_scope())
            model.get_body().get_body_elements().append(block)

        from pynestml.visitors.ast_parent_visitor import ASTParentVisitor
        model.accept(ASTParentVisitor())

        return model

    @classmethod
    def create_parameters_block(cls, model: ASTModel):
        r"""
        Create a parameters block in the handed over model if it does not yet exist.
        :param model: a single model
        :return: the modified model (the model is also changed in-place)
        """
        # local import since otherwise circular dependency
        from pynestml.meta_model.ast_node_factory import ASTNodeFactory
        if not model.get_parameters_blocks():
            block = ASTNodeFactory.create_ast_block_with_variables(False, True, False, list(),
                                                                   ASTSourceLocation.get_added_source_position())
            block.update_scope(model.get_scope())
            model.get_body().get_body_elements().append(block)

        from pynestml.visitors.ast_parent_visitor import ASTParentVisitor
        model.accept(ASTParentVisitor())

        return model

    @classmethod
    def create_equations_block(cls, model: ASTModel) -> ASTModel:
        r"""
        Create an equations block in the handed over model if it does not yet exist.
        :param model: a single model
        :return: the modified model (the model is also changed in-place)
        """
        # local import since otherwise circular dependency
        from pynestml.meta_model.ast_node_factory import ASTNodeFactory
        if not model.get_equations_blocks():
            block = ASTNodeFactory.create_ast_equations_block(list(),
                                                              ASTSourceLocation.get_added_source_position())
            block.update_scope(model.get_scope())
            model.get_body().get_body_elements().append(block)

        from pynestml.visitors.ast_parent_visitor import ASTParentVisitor
        model.accept(ASTParentVisitor())

        return model

    @classmethod
    def contains_convolve_call(cls, variable: VariableSymbol) -> bool:
        """
        Indicates whether the declaring rhs of this variable symbol has a convolve() in it.
        :return: True if contained, otherwise False.
        """
        if not variable.get_declaring_expression():
            return False

        for func in variable.get_declaring_expression().get_function_calls():
            if func.get_name() == PredefinedFunctions.CONVOLVE:
                return True

        return False

    @classmethod
    def get_declaration_by_name(cls, blocks: Union[ASTStmtsBody, List[ASTStmtsBody]], var_name: str) -> Optional[ASTDeclaration]:
        """
        Get a declaration by variable name.
        :param blocks: the block or blocks to look for the variable in
        :param var_name: name of the variable to look for (including single quotes indicating differential order)
        """
        if isinstance(blocks, ASTNode):
            blocks = [blocks]
        for block in blocks:
            for decl in block.get_declarations():
                for var in decl.get_variables():
                    if var.get_complete_name() == var_name:
                        return decl
        return None

    @classmethod
    def all_variables_defined_in_block(cls, blocks: Union[ASTStmtsBody, List[ASTStmtsBody]]) -> List[ASTVariable]:
        """return a list of all variable declarations in a block or blocks"""
        if isinstance(blocks, ASTNode):
            blocks = [blocks]
        vars = []
        for block in blocks:
            for decl in block.get_declarations():
                for var in decl.get_variables():
                    vars.append(var)
        return vars

    @classmethod
    def inline_aliases_convolution(cls, inline_expr: ASTInlineExpression) -> bool:
        """
        Returns True if and only if the inline expression is of the form ``var type = convolve(...)``.
        """
        expr = inline_expr.get_expression()
        if isinstance(expr, ASTExpression):
            expr = expr.get_lhs()
        if isinstance(expr, ASTSimpleExpression) \
           and expr.is_function_call() \
           and expr.get_function_call().get_name() == PredefinedFunctions.CONVOLVE:
            return True
        return False

    @classmethod
    def add_suffix_to_variable_name(cls, var_name: str, astnode: ASTNode, suffix: str, scope=None):
        """add suffix to variable by given name recursively throughout astnode"""

        def replace_var(_expr=None):
            if isinstance(_expr, ASTSimpleExpression) and _expr.is_variable():
                var = _expr.get_variable()
            elif isinstance(_expr, ASTVariable):
                var = _expr
            else:
                return

            if not suffix in var.get_name() \
               and not var.get_name() == "t" \
               and var.get_name() == var_name:
                var.set_name(var.get_name() + suffix)

        astnode.accept(ASTHigherOrderVisitor(lambda x: replace_var(x)))

    @classmethod
    def remove_state_var_from_integrate_odes_calls(cls, model: ASTModel, state_var_name: str):
        r"""Remove a state variable from the arguments (where it exists) of each integrate_odes() call in the model."""

        class RemoveStateVarFromIntegrateODEsCallsVisitor(ASTVisitor):
            def visit_function_call(self, node: ASTFunctionCall):
                if node.get_name() == PredefinedFunctions.INTEGRATE_ODES:
                    node.args = [arg for arg in node.args if not arg.get_variable().get_complete_name()]

        remove_state_var_from_integrate_odes_calls_visitor = RemoveStateVarFromIntegrateODEsCallsVisitor()
        model.accept(remove_state_var_from_integrate_odes_calls_visitor)

    @classmethod
    def resolve_variables_to_expressions(cls, astnode, analytic_state_variables_moved):
        """receives a list of variable names (as strings) and returns a list of ASTExpressions containing each ASTVariable"""
        expressions = []

        for var_name in analytic_state_variables_moved:
            node = ASTUtils.get_variable_by_name(astnode, var_name)
            assert node is not None
            expressions.append(ASTNodeFactory.create_ast_expression(False, None, False, ASTNodeFactory.create_ast_simple_expression(variable=node)))

        return expressions

    @classmethod
    def add_suffix_to_variable_names(cls, astnode: Union[ASTNode, List], suffix: str, altscope: Optional[Scope] = None):
        r"""Add suffix to variable names recursively throughout ``astnode``. Symbols will be resolved in the variable's default scope, unless ``altscope`` is set, in which case it will be used to try to resolve variables (this can be used in case of moved variables for neuron/synapse co-generation)."""

        if not isinstance(astnode, ASTNode):
            for node in astnode:
                ASTUtils.add_suffix_to_variable_names(node, suffix, altscope=altscope)
            return

        if altscope:
            scope = altscope
        else:
            scope = astnode.get_scope()

        def replace_var(_expr=None):
            if isinstance(_expr, ASTSimpleExpression) and _expr.is_variable():
                var = _expr.get_variable()
            elif isinstance(_expr, ASTVariable):
                var = _expr
            else:
                return

            if not var.get_name() in PredefinedVariables.get_variables().keys() \
               and not var.get_name().endswith(suffix):
                symbol = scope.resolve_to_symbol(var.get_name(), SymbolKind.VARIABLE)
                if symbol:    # make sure it is not a unit (like "ms")
                    var.set_name(var.get_name() + suffix)

        astnode.accept(ASTHigherOrderVisitor(lambda x: replace_var(x)))

    @classmethod
    def set_new_scope(cls, astnode: Union[ASTNode, List], new_scope: Scope):
        r"""set new scope on variables recursively throughout astnode"""

        if not isinstance(astnode, ASTNode):
            for node in astnode:
                ASTUtils.set_new_scope(node, new_scope)
            return

        def replace_var(_expr=None):
            if isinstance(_expr, ASTSimpleExpression) and _expr.is_variable():
                var = _expr.get_variable()
            elif isinstance(_expr, ASTVariable):
                var = _expr
            else:
                return

            if not var.get_name() in PredefinedVariables.get_variables().keys():
                symbol = new_scope.resolve_to_symbol(var.get_name(), SymbolKind.VARIABLE)
                if symbol:    # make sure it is not a unit (like "ms")
                    var.update_scope(new_scope)

        astnode.accept(ASTHigherOrderVisitor(lambda x: replace_var(x)))

    @classmethod
    def add_suffix_to_variable_names2(cls, variable_names: List[str], astnode: Union[ASTNode, List], suffix: str):
        r"""add suffix to variable names recursively throughout astnode"""

        if not isinstance(astnode, ASTNode):
            for node in astnode:
                ASTUtils.add_suffix_to_variable_names2(variable_names, node, suffix)
            return

        def replace_var(_expr=None):
            if isinstance(_expr, ASTSimpleExpression) and _expr.is_variable():
                var = _expr.get_variable()
            elif isinstance(_expr, ASTVariable):
                var = _expr
            else:
                return

            if var.get_name() in variable_names \
               and not var.get_name().endswith(suffix):
                var.set_name(var.get_name() + suffix)

        astnode.accept(ASTHigherOrderVisitor(lambda x: replace_var(x)))

    @classmethod
    def get_inline_expression_by_name(cls, node, name: str) -> Optional[ASTInlineExpression]:
        for equations_block in node.get_equations_blocks():
            for inline_expr in equations_block.get_inline_expressions():
                if name == inline_expr.variable_name:
                    return inline_expr

        return None

    @classmethod
    def get_inline_expression_by_constructed_rhs_name(cls, node, name: str) -> Optional[ASTInlineExpression]:
        for equations_block in node.get_equations_blocks():
            for inline_expr in equations_block.get_inline_expressions():
                if not ASTUtils.inline_aliases_convolution(inline_expr):
                    continue

                constructed_name = ASTUtils.construct_kernel_X_spike_buf_name(str(inline_expr.get_expression().get_function_call().get_args()[0]), inline_expr.get_expression().get_function_call().get_args()[1], order=0, suffix="__for_" + node.get_name())

                if name == constructed_name:
                    return inline_expr

        return None

    @classmethod
    def get_kernel_by_name(cls, node, name: str) -> Optional[ASTKernel]:
        for equations_block in node.get_equations_blocks():
            for kernel in equations_block.get_kernels():
                if name in kernel.get_variable_names():
                    return kernel

        return None

    @classmethod
    def print_alternate_var_name(cls, var_name, continuous_post_ports):
        for pair in continuous_post_ports:
            if pair[0] == var_name:
                return pair[1]

        assert False

    @classmethod
    def get_post_ports_of_neuron_synapse_pair(cls, neuron, synapse, codegen_opts_pairs):
        for pair in codegen_opts_pairs:
            if pair["neuron"] == removesuffix(neuron.get_name().split("__with_")[0], FrontendConfiguration.suffix) \
               and pair["synapse"] == removesuffix(synapse.get_name().split("__with_")[0], FrontendConfiguration.suffix) \
               and "post_ports" in pair.keys():
                return pair["post_ports"]

        return []

    @classmethod
    def get_var_name_tuples_of_neuron_synapse_pair(cls, post_port_names, post_port, reverse=False):
        for pair in post_port_names:
            if reverse and pair[1] == post_port:
                return pair[0]

            if not reverse and pair[0] == post_port:
                return pair[1]

        raise Exception("Port name not found!")

    @classmethod
    def replace_with_external_variable(cls, var_name, node: ASTNode, suffix: str, new_scope, alternate_name=None):
        r"""
        Replace all occurrences of variables (``ASTVariable``s) (e.g. ``post_trace'``) in the node with ``ASTExternalVariable``s, indicating that they are moved to the postsynaptic neuron.
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

            ast_ext_var.update_alt_scope(new_scope)
            from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor
            ast_ext_var.accept(ASTSymbolTableVisitor())

            if isinstance(_expr, ASTSimpleExpression) and _expr.is_variable():
                _expr.set_variable(ast_ext_var)
                ast_ext_var.parent_ = _expr
                return

            if isinstance(_expr, ASTVariable):
                ast_ext_var.parent_ = _expr.get_parent()
                if isinstance(_expr.get_parent(), ASTAssignment):
                    _expr.get_parent().lhs = ast_ext_var
                elif isinstance(_expr.get_parent(), ASTSimpleExpression) and _expr.get_parent().is_variable():
                    _expr.get_parent().set_variable(ast_ext_var)
                elif isinstance(_expr.get_parent(), ASTDeclaration):
                    # variable could occur on the left-hand side; ignore. Only replace if it occurs on the right-hand side.
                    pass
                else:
                    Logger.log_message(None, -1, "Error: unhandled use of variable "
                                       + var_name + " in expression " + str(_expr), None, LoggingLevel.INFO)
                    raise Exception()
                return

            p = var.get_parent()
            Logger.log_message(None, -1, "Error: unhandled use of variable "
                               + var_name + " in expression " + str(p), None, LoggingLevel.INFO)
            raise Exception()

        node.accept(ASTHigherOrderVisitor(lambda x: replace_var(x)))
        from pynestml.visitors.ast_parent_visitor import ASTParentVisitor
        node.accept(ASTParentVisitor())

    @classmethod
    def add_suffix_to_decl_lhs(cls, decl, suffix: str):
        """add suffix to the left-hand side of a declaration"""
        if isinstance(decl, ASTInlineExpression):
            decl.set_variable_name(decl.get_variable_name() + suffix)
        elif isinstance(decl, ASTOdeEquation):
            decl.get_lhs().set_name(decl.get_lhs().get_name() + suffix)
        elif isinstance(decl, ASTStmt):
            assert decl.small_stmt.is_assignment()
            decl.small_stmt.get_assignment().lhs.set_name(decl.small_stmt.get_assignment().lhs.get_name() + suffix)
        else:
            for var in decl.get_variables():
                var.set_name(var.get_name() + suffix)

    @classmethod
    def get_all_variables(cls, node: ASTNode) -> List[str]:
        """Make a list of all variable symbol names that are in ``node``"""
        if node is None:
            return []

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

        visitor = ASTVariablesFinderVisitor()
        node.accept(visitor)
        all_variables = [v.name for v in visitor._variables]
        return all_variables

    @classmethod
    def get_all_variables_used_in_convolutions(cls, nodes: Union[ASTEquationsBlock, List[ASTEquationsBlock]], parent_node: ASTNode) -> List[str]:
        """Make a list of all variable symbol names that are in one of the equation blocks in ``nodes`` and used in a convolution"""
        if not nodes:
            return []

        if isinstance(nodes, ASTNode):
            nodes = [nodes]

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
                    input_port = ASTUtils.get_input_port_by_name(
                        self.parent_node.get_input_blocks(), symbol_buffer.name)
                    if input_port:
                        found_parent_assignment = False
                        node_ = node
                        while not found_parent_assignment:
                            node_ = node_.get_parent()
                            # XXX TODO also needs to accept normal ASTExpression, ASTAssignment?
                            if isinstance(node_, ASTInlineExpression):
                                found_parent_assignment = True
                        var_name = node_.get_variable_name()
                        self._variables.append(var_name)

        variables = []
        for node in nodes:
            visitor = ASTAllVariablesUsedInConvolutionVisitor(node, parent_node)
            node.accept(visitor)
            variables.extend(visitor._variables)

        return variables

    @classmethod
    def move_decls(cls, var_name, from_block, to_block, var_name_suffix: str, block_type: BlockType, mode="move") -> List[ASTDeclaration]:
        r"""Move or copy declarations from ``from_block`` to ``to_block``."""
        from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor
        assert mode in ["move", "copy"]

        if not from_block \
           or not to_block:
            return []

        decls = ASTUtils.get_declarations_from_block(var_name, from_block)
        if var_name_suffix and var_name.endswith(var_name_suffix):
            decls.extend(ASTUtils.get_declarations_from_block(removesuffix(var_name, var_name_suffix), from_block))

        if decls:
            Logger.log_message(None, -1, ("Moving" if mode == "move" else "Copying") + " definition of " + var_name + " from synapse to neuron",
                               None, LoggingLevel.INFO)
            for decl in decls:
                if mode == "move":
                    from_block.declarations.remove(decl)
                if mode == "copy":
                    decl = decl.clone()
                assert len(decl.get_variables()) <= 1
                if not decl.get_variables()[0].name.endswith(var_name_suffix) and var_name_suffix:
                    ASTUtils.add_suffix_to_decl_lhs(decl, suffix=var_name_suffix)
                to_block.get_declarations().append(decl)
                decl.update_scope(to_block.get_scope())

                ast_symbol_table_visitor = ASTSymbolTableVisitor()
                ast_symbol_table_visitor.block_type_stack.push(block_type)
                decl.accept(ast_symbol_table_visitor)
                ast_symbol_table_visitor.block_type_stack.pop()

        from pynestml.visitors.ast_parent_visitor import ASTParentVisitor
        to_block.accept(ASTParentVisitor())

        return decls

    @classmethod
    def equations_from_block_to_block(cls, state_var, from_block, to_block, var_name_suffix, mode) -> List[ASTDeclaration]:
        assert mode in ["move", "copy"]

        if not from_block:
            return []

        decls = ASTUtils.get_declarations_from_block(state_var, from_block)

        for decl in decls:
            if mode == "move":
                from_block.declarations.remove(decl)
            ASTUtils.add_suffix_to_decl_lhs(decl, suffix=var_name_suffix)
            to_block.get_declarations().append(decl)
            decl.update_scope(to_block.get_scope())

        return decls

    @classmethod
    def collects_vars_used_in_equation(cls, state_var, from_block):
        if not from_block:
            return

        decls = ASTUtils.get_declarations_from_block(state_var, from_block)
        vars_used = []
        if decls:
            for decl in decls:
                if (type(decl) in [ASTDeclaration, ASTReturnStmt] and decl.has_expression()) \
                   or type(decl) is ASTInlineExpression:
                    vars_used.extend(
                        ASTUtils.collect_variable_names_in_expression(decl.get_expression()))
                elif type(decl) is ASTOdeEquation:
                    vars_used.extend(ASTUtils.collect_variable_names_in_expression(decl.get_rhs()))
                elif type(decl) is ASTKernel:
                    for expr in decl.get_expressions():
                        vars_used.extend(ASTUtils.collect_variable_names_in_expression(expr))
                else:
                    raise Exception("Tried to move unknown type " + str(type(decl)))

        return vars_used

    @classmethod
    def add_kernel_to_variable(cls, kernel: ASTKernel):
        r"""
        Adds the kernel as the defining equation.
        If the definition of the kernel is e.g. `g'' = ...` then variable symbols `g` and `g'` will have their kernel definition and variable type set.
        :param kernel: a single kernel object.
        """
        if len(kernel.get_variables()) == 1 \
                and kernel.get_variables()[0].get_differential_order() == 0:
            # we only update those which define an ODE; skip "direct function of time" specifications
            return

        for var, expr in zip(kernel.get_variables(), kernel.get_expressions()):
            for diff_order in range(var.get_differential_order()):
                var_name = var.get_name() + "'" * diff_order
                existing_symbol = kernel.get_scope().resolve_to_symbol(var_name, SymbolKind.VARIABLE)

                if existing_symbol is None:
                    code, message = Messages.get_no_variable_found(var.get_name_of_lhs())
                    Logger.log_message(code=code, message=message, error_position=kernel.get_source_position(), log_level=LoggingLevel.ERROR)
                    return

                existing_symbol.set_ode_or_kernel(expr)
                existing_symbol.set_variable_type(VariableType.KERNEL)
                kernel.get_scope().update_variable_symbol(existing_symbol)

    @classmethod
    def assign_ode_to_variables(cls, ode_block: ASTEquationsBlock):
        r"""
        Adds for each variable symbol the corresponding ode declaration if present.

        :param ode_block: a single block of ode declarations.
        """
        from pynestml.meta_model.ast_ode_equation import ASTOdeEquation
        from pynestml.meta_model.ast_kernel import ASTKernel
        for decl in ode_block.get_declarations():
            if isinstance(decl, ASTOdeEquation):
                ASTUtils.add_ode_to_variable(decl)
            elif isinstance(decl, ASTKernel):
                ASTUtils.add_kernel_to_variable(decl)

    @classmethod
    def add_ode_to_variable(cls, ode_equation: ASTOdeEquation):
        r"""
        Resolves to the corresponding symbol and updates the corresponding ode-declaration.

        :param ode_equation: a single ode-equation
        """
        for diff_order in range(ode_equation.get_lhs().get_differential_order()):
            var_name = ode_equation.get_lhs().get_name() + "'" * diff_order
            existing_symbol = ode_equation.get_scope().resolve_to_symbol(var_name, SymbolKind.VARIABLE)

            if existing_symbol is None:
                code, message = Messages.get_no_variable_found(ode_equation.get_lhs().get_name_of_lhs())
                Logger.log_message(code=code, message=message, error_position=ode_equation.get_source_position(),
                                   log_level=LoggingLevel.ERROR)
                return

            existing_symbol.set_ode_or_kernel(ode_equation)

            ode_equation.get_scope().update_variable_symbol(existing_symbol)

    @classmethod
    def get_statements_from_block(cls, var_name, block):
        """XXX: only simple statements such as assignments are supported for now. if..then..else compound statements and so are not yet supported."""
        block = block.get_stmts_body()
        all_stmts = block.get_stmts()
        stmts = []
        for node in all_stmts:
            if node.is_small_stmt() \
               and node.small_stmt.is_assignment() \
               and node.small_stmt.get_assignment().lhs.get_name() == var_name:
                stmts.append(node)
        return stmts

    @classmethod
    def is_function_delay_variable(cls, node: ASTFunctionCall) -> bool:
        """
        Checks if the given function call is actually a delayed variable. For a function call to be a delayed
        variable, the function name should be resolved to a state symbol, with one function argument which is an
        expression.
        :param node: The function call
        """
        # Check if the function name is a state variable
        symbol = cls.get_delay_variable_symbol(node)
        args = node.get_args()
        # Check if the length of arg list is 1
        if symbol and len(args) == 1 and isinstance(args[0], ASTExpression):
            return True
        return False

    @classmethod
    def get_delay_variable_symbol(cls, node: ASTFunctionCall):
        """
        Returns the variable symbol for the corresponding delayed variable
        :param node: The delayed variable parsed as a function call
        """
        symbol = node.get_scope().resolve_to_symbol(node.get_name(), SymbolKind.VARIABLE)
        if symbol and symbol.block_type == BlockType.STATE:
            return symbol
        return None

    @classmethod
    def extract_delay_parameter(cls, node: ASTFunctionCall) -> str:
        """
        Extracts the delay parameter from the delayed variable
        :param node: The delayed variable parsed as a function call
        """
        args = node.get_args()
        delay_parameter = args[0].get_rhs().get_variable()
        return delay_parameter.get_name()

    @classmethod
    def update_delay_parameter_in_state_vars(cls, neuron: ASTModel, state_vars_before_update: List[VariableSymbol]) -> None:
        """
        Updates the delay parameter in state variables after the symbol table update
        :param neuron: AST neuron
        :param state_vars_before_update: State variables before the symbol table update
        """
        for state_var in state_vars_before_update:
            if state_var.has_delay_parameter():
                symbol = neuron.get_scope().resolve_to_symbol(state_var.get_symbol_name(), SymbolKind.VARIABLE)
                if symbol is not None:
                    symbol.set_delay_parameter(state_var.get_delay_parameter())

    @classmethod
    def has_equation_with_delay_variable(cls, equations_with_delay_vars: ASTOdeEquation, sym: str) -> bool:
        """
        Returns true if the given variable has an equation defined with a delayed variable, false otherwise.
        :param equations_with_delay_vars: a list of equations containing delayed variables
        :param sym: symbol denoting the lhs of
        """
        for equation in equations_with_delay_vars:
            if equation.get_lhs().get_name() == sym:
                return True
        return False

    @classmethod
    def add_declarations_to_internals(cls, neuron: ASTModel, declarations: Mapping[str, str]) -> ASTModel:
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
    def add_declaration_to_internals(cls, neuron: ASTModel, variable_name: str, init_expression: str) -> ASTModel:
        """
        Adds the variable as stored in the declaration tuple to the neuron. The declared variable is of type real.
        :param neuron: a single neuron instance
        :param variable_name: the name of the variable to add
        :param init_expression: initialization expression
        :return: the neuron extended by the variable
        """
        assert len(neuron.get_internals_blocks()) <= 1, "Only one internals block supported for now"

        from pynestml.utils.model_parser import ModelParser
        from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor

        tmp = ModelParser.parse_expression(init_expression)
        vector_variable = ASTUtils.get_vectorized_variable(tmp, neuron.get_scope())

        declaration_string = variable_name + ' real' + (
            '[' + vector_variable.get_vector_parameter() + ']'
            if vector_variable is not None and vector_variable.has_vector_parameter() else '') + ' = ' + init_expression
        ast_declaration = ModelParser.parse_declaration(declaration_string)
        if vector_variable is not None:
            ast_declaration.set_size_parameter(vector_variable.get_vector_parameter())
        neuron.add_to_internals_block(ast_declaration)

        from pynestml.visitors.ast_parent_visitor import ASTParentVisitor
        neuron.accept(ASTParentVisitor())

        ast_declaration.update_scope(neuron.get_internals_blocks()[0].get_scope())
        symtable_visitor = ASTSymbolTableVisitor()
        symtable_visitor.block_type_stack.push(BlockType.INTERNALS)
        ast_declaration.accept(symtable_visitor)
        symtable_visitor.block_type_stack.pop()

        return neuron

    @classmethod
    def add_declarations_to_state_block(cls, neuron: ASTModel, variables: List, initial_values: List) -> ASTModel:
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
    def add_declaration_to_state_block(cls, neuron: ASTModel, variable: str, initial_value: str, type_str: str = "real") -> ASTModel:
        """
        Adds a single declaration to an arbitrary state block of the neuron. The declared variable is of type real.
        :param neuron: a neuron
        :param variable: state variable to add
        :param initial_value: corresponding initial value
        :return: a modified neuron
        """
        from pynestml.utils.model_parser import ModelParser
        from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor

        tmp = ModelParser.parse_expression(initial_value)
        vector_variable = ASTUtils.get_vectorized_variable(tmp, neuron.get_scope())
        declaration_string = variable + " " + type_str + (
            '[' + vector_variable.get_vector_parameter() + ']'
            if vector_variable is not None and vector_variable.has_vector_parameter() else '') + ' = ' + initial_value
        ast_declaration = ModelParser.parse_declaration(declaration_string)
        if vector_variable is not None:
            ast_declaration.set_size_parameter(vector_variable.get_vector_parameter())
        neuron.add_to_state_block(ast_declaration)

        from pynestml.visitors.ast_parent_visitor import ASTParentVisitor
        neuron.accept(ASTParentVisitor())

        symtable_visitor = ASTSymbolTableVisitor()
        symtable_visitor.block_type_stack.push(BlockType.STATE)
        ast_declaration.accept(symtable_visitor)
        symtable_visitor.block_type_stack.pop()

        return neuron

    @classmethod
    def declaration_in_state_block(cls, neuron: ASTModel, variable_name: str) -> bool:
        """
        Checks if the variable is declared in the state block
        :param neuron:
        :param variable_name:
        :return:
        """
        assert type(variable_name) is str

        if not neuron.get_state_blocks():
            return False

        for state_block in neuron.get_state_blocks():
            for decl in state_block.get_declarations():
                for var in decl.get_variables():
                    if var.get_complete_name() == variable_name:
                        return True

        return False

    @classmethod
    def add_assignment_to_update_block(cls, assignment: ASTAssignment, neuron: ASTModel) -> ASTModel:
        """
        Adds a single assignment to the end of the update block of the handed over neuron. At most one update block should be present.

        :param assignment: a single assignment
        :param neuron: a single neuron instance
        :return: the modified neuron
        """
        assert len(neuron.get_update_blocks()) <= 1, "At most one update block should be present"
        small_stmt = ASTNodeFactory.create_ast_small_stmt(assignment=assignment,
                                                          source_position=ASTSourceLocation.get_added_source_position())
        stmt = ASTNodeFactory.create_ast_stmt(small_stmt=small_stmt,
                                              source_position=ASTSourceLocation.get_added_source_position())
        if not neuron.get_update_blocks():
            neuron.create_empty_update_block()
        neuron.get_update_blocks()[0].get_stmts_body().get_stmts().append(stmt)
        small_stmt.update_scope(neuron.get_update_blocks()[0].get_stmts_body().get_scope())
        stmt.update_scope(neuron.get_update_blocks()[0].get_stmts_body().get_scope())
        return neuron

    @classmethod
    def add_declaration_to_update_block(cls, declaration: ASTDeclaration, neuron: ASTModel) -> ASTModel:
        """
        Adds a single declaration to the end of the update block of the handed over neuron.
        :param declaration: ASTDeclaration node to add
        :param neuron: a single neuron instance
        :return: a modified neuron
        """
        assert len(neuron.get_update_blocks()) <= 1, "At most one update block should be present"
        small_stmt = ASTNodeFactory.create_ast_small_stmt(declaration=declaration,
                                                          source_position=ASTSourceLocation.get_added_source_position())
        stmt = ASTNodeFactory.create_ast_stmt(small_stmt=small_stmt,
                                              source_position=ASTSourceLocation.get_added_source_position())
        if not neuron.get_update_blocks():
            neuron.create_empty_update_block()
        neuron.get_update_blocks()[0].get_stmts_body().get_stmts().append(stmt)
        small_stmt.update_scope(neuron.get_update_blocks()[0].get_stmts_body().get_scope())
        stmt.update_scope(neuron.get_update_blocks()[0].get_stmts_body().get_scope())
        return neuron

    @classmethod
    def add_state_updates(cls, neuron: ASTModel, update_expressions: Mapping[str, str]) -> ASTModel:
        """
        Adds all update instructions as contained in the solver output to the update block of the neuron.
        :param neuron: a single neuron
        :param update_expressions: map of variables to corresponding updates during the update step.
        :return: a modified version of the neuron
        """
        from pynestml.utils.model_parser import ModelParser
        for variable, update_expression in update_expressions.items():
            declaration_statement = variable + '__tmp real = ' + update_expression
            cls.add_declaration_to_update_block(ModelParser.parse_declaration(declaration_statement), neuron)
        for variable, update_expression in update_expressions.items():
            cls.add_assignment_to_update_block(ModelParser.parse_assignment(variable + ' = ' + variable + '__tmp'),
                                               neuron)
        return neuron

    @classmethod
    def variable_in_solver(cls, var: str, solver_dicts: List[dict]) -> bool:
        """
        Check if a variable by this name is defined in the ode-toolbox solver results,
        """

        for solver_dict in solver_dicts:
            if solver_dict is None:
                continue

            for var_name in solver_dict["state_variables"]:
                var_name_base = var_name.split("__X__")[0]
                if var_name_base == var:
                    return True

        return False

    @classmethod
    def is_ode_variable(cls, var_base_name: str, neuron: ASTModel) -> bool:
        """
        Checks if the variable is present in an ODE
        """
        for equations_block in neuron.get_equations_blocks():
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
        assert isinstance(var_name, str)
        for var, expr in zip(kernel.get_variables(), kernel.get_expressions()):
            if var.get_complete_name() == var_name:
                return expr
        assert False, "variable name not found in kernel"

    @classmethod
    def all_convolution_variable_names(cls, model: ASTModel) -> List[str]:
        vars = ASTUtils.all_variables_defined_in_block(model.get_state_blocks())
        var_names = [var.get_complete_name() for var in vars if "__X__" in var.get_complete_name()]
        return var_names

    @classmethod
    def construct_kernel_X_spike_buf_name(cls, kernel_var_name: str, spike_input_port: ASTInputPort, order: int,
                                          diff_order_symbol="__d", suffix=""):
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

        if isinstance(spike_input_port, ASTSimpleExpression):
            spike_input_port = spike_input_port.get_variable()

        if not isinstance(spike_input_port, str):
            spike_input_port_name = spike_input_port.get_name()
        else:
            spike_input_port_name = spike_input_port

        if isinstance(spike_input_port, ASTVariable):
            if spike_input_port.has_vector_parameter():
                spike_input_port_name += "_" + str(cls.get_numeric_vector_size(spike_input_port))

        return kernel_var_name.replace("$", "__DOLLAR") + suffix + "__X__" + spike_input_port_name + diff_order_symbol * order + suffix

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
            and expr.get_function_call().get_scope().resolve_to_symbol(expr.get_function_call().get_name(), SymbolKind.FUNCTION).equals(PredefinedFunctions.name2function["delta"])
        rhs_is_multiplied_delta_kernel = type(expr) is ASTExpression \
            and type(expr.get_rhs()) is ASTSimpleExpression \
            and expr.get_rhs().is_function_call() \
            and expr.get_rhs().get_function_call().get_scope().resolve_to_symbol(expr.get_rhs().get_function_call().get_name(), SymbolKind.FUNCTION).equals(PredefinedFunctions.name2function["delta"])
        return rhs_is_delta_kernel or rhs_is_multiplied_delta_kernel

    @classmethod
    def get_input_port_by_name(cls, input_blocks: List[ASTInputBlock], port_name: str) -> ASTInputPort:
        """
        Get the input port given the port name
        :param input_block: block to be searched
        :param port_name: name of the input port
        :return: input port object
        """
        for input_block in input_blocks:
            for input_port in input_block.get_input_ports():
                if input_port.has_size_parameter():
                    size_parameter = input_port.get_size_parameter()
                    if isinstance(size_parameter, ASTSimpleExpression):
                        size_parameter = size_parameter.get_numeric_literal()
                    port_name, port_index = port_name.split("_")
                    assert int(port_index) >= 0
                    assert int(port_index) <= size_parameter
                if input_port.name == port_name:
                    return input_port
        return None

    @classmethod
    def get_parameter_by_name(cls, node: ASTModel, var_name: str) -> ASTDeclaration:
        """
        Get the declaration based on the name of the parameter
        :param node: the neuron or synapse containing the parameter
        :param var_name: variable name to be searched
        :return: declaration containing the variable
        """
        for param_block in node.get_parameters_blocks():
            for decl in param_block.get_declarations():
                for var in decl.get_variables():
                    if var.get_name() == var_name:
                        return decl
        return None

    @classmethod
    def get_parameter_variable_by_name(cls, node: ASTModel, var_name: str) -> ASTVariable:
        """
        Get a parameter node based on the name of the parameter
        :param node: the neuron or synapse containing the parameter
        :param var_name: variable name to be searched
        :return: the parameter node
        """
        for param_block in node.get_parameters_blocks():
            for decl in param_block.get_declarations():
                for var in decl.get_variables():
                    if var.get_name() == var_name:
                        return var
        return None

    @classmethod
    def get_internal_by_name(cls, node: ASTModel, var_name: str) -> ASTDeclaration:
        """
        Get the declaration based on the name of the internal parameter
        :param node: the neuron or synapse containing the parameter
        :param var_name: variable name to be searched
        :return: declaration containing the variable
        """
        for internals_block in node.get_internals_blocks():
            for decl in internals_block.get_declarations():
                for var in decl.get_variables():
                    if var.get_name() == var_name:
                        return decl
        return None

    @classmethod
    def get_internal_variable_by_name(cls, node: ASTVariable, var_name: str) -> ASTVariable:
        """
        Get the internal parameter node based on the name of the internal parameter
        :param node: the neuron or synapse containing the parameter
        :param var_name: variable name to be searched
        :return: declaration containing the variable
        """
        for internals_block in node.get_internals_blocks():
            for decl in internals_block.get_declarations():
                for var in decl.get_variables():
                    if var.get_name() == var_name:
                        return var
        return None

    @classmethod
    def get_variable_by_name(cls, node: ASTModel, var_name: str) -> Optional[ASTVariable]:
        """
        Get a variable or parameter node based on the name
        :param node: the neuron or synapse containing the parameter
        :param var_name: variable name to be searched
        :return: the node if found, otherwise None
        """
        var = ASTUtils.get_state_variable_by_name(node, var_name)

        if not var:
            var = ASTUtils.get_parameter_variable_by_name(node, var_name)

        if not var:
            var = ASTUtils.get_internal_variable_by_name(node, var_name)

        if not var:
            expr = ASTUtils.get_inline_expression_by_name(node, var_name)
            if expr:
                var = ASTNodeFactory.create_ast_variable(var_name, differential_order=0)
                assert len(node.get_equations_blocks()) == 1, "Only one equations block supported for now"
                var.scope = node.get_equations_blocks()[0].scope

        return var

    @classmethod
    def get_state_variable_by_name(cls, node: ASTModel, var_name: str) -> Optional[ASTVariable]:
        """
        Get a state variable node based on the name
        :param node: the neuron or synapse containing the parameter
        :param var_name: variable name to be searched
        :return: the node if found, otherwise None
        """
        for state_block in node.get_state_blocks():
            for decl in state_block.get_declarations():
                for var in decl.get_variables():
                    if var.get_name() == var_name:
                        return var
        return None

    @classmethod
    def get_state_variable_declaration_by_name(cls, node: ASTModel, var_name: str) -> Optional[ASTDeclaration]:
        """
        Get the declaration based on the name of the parameter
        :param node: the neuron or synapse containing the parameter
        :param var_name: variable name to be searched
        :return: declaration containing the variable if found, otherwise None
        """
        for state_block in node.get_state_blocks():
            for decl in state_block.get_declarations():
                for var in decl.get_variables():
                    if var.get_name() == var_name:
                        return decl
        return None

    @classmethod
    def replace_post_moved_variable_names(cls, astnode, post_connected_continuous_input_ports, post_variable_names):
        if not isinstance(astnode, ASTNode):
            for node in astnode:
                ASTUtils.replace_post_moved_variable_names(node, post_connected_continuous_input_ports, post_variable_names)
            return

        def replace_var(_expr=None):
            if isinstance(_expr, ASTSimpleExpression) and _expr.is_variable():
                var = _expr.get_variable()
            elif isinstance(_expr, ASTVariable):
                var = _expr
            else:
                return

            if var.get_name() in post_connected_continuous_input_ports:
                idx = post_connected_continuous_input_ports.index(var.get_name())
                var.set_name(post_variable_names[idx])

        astnode.accept(ASTHigherOrderVisitor(lambda x: replace_var(x)))

    @classmethod
    def replace_post_moved_variable_names(cls, astnode, post_connected_continuous_input_ports, post_variable_names):
        r"""In the synapse, continuous-valued input ports could be referred to based on their name. When they are moved to the neuron, they need to be referred to by the variable name as it exists on the neuron side. This function performs the variable name replacement recursively in ``astnode``. ``astnode`` can also be a list of nodes."""
        if not isinstance(astnode, ASTNode):
            for node in astnode:
                ASTUtils.replace_post_moved_variable_names(node, post_connected_continuous_input_ports, post_variable_names)
            return

        def replace_var(_expr=None):
            if isinstance(_expr, ASTSimpleExpression) and _expr.is_variable():
                var = _expr.get_variable()
            elif isinstance(_expr, ASTVariable):
                var = _expr
            else:
                return

            if var.get_name() in post_connected_continuous_input_ports:
                idx = post_connected_continuous_input_ports.index(var.get_name())
                var.set_name(post_variable_names[idx])

        astnode.accept(ASTHigherOrderVisitor(lambda x: replace_var(x)))

    @classmethod
    def collect_variable_names_in_expression(cls, expr: ASTNode) -> List[ASTVariable]:
        """
        Collect all occurrences of variables (`ASTVariable`) XXX ...
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

            symbol = None
            if var and var.get_scope():
                symbol = var.get_scope().resolve_to_symbol(var.get_complete_name(), SymbolKind.VARIABLE)

            if var and symbol:
                vars_used_.append(var)

        expr.accept(ASTHigherOrderVisitor(lambda x: collect_vars(x)))

        return vars_used_

    @classmethod
    def get_declarations_from_block(cls, var_name: str, block: ASTStmtsBody) -> List[ASTDeclaration]:
        """
        Get declarations from the given block containing the given variable on the left-hand side.

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
    def recursive_dependent_variables_search(cls, vars: List[str], model: ASTModel) -> List[str]:
        """
        Collect all the variable names used in the defining expressions of a list of variables.
        :param vars: list of variable names moved from synapse to neuron
        :param model: ASTModel to perform the recursive search
        :return: list of variable names from the recursive search
        """

        for var in vars:
            assert type(var) is str

        vars_used = vars.copy()
        i = 0
        while i < len(vars_used):
            new_vars = ASTUtils.get_dependent_variables(vars_used[i], model)
            new_vars = list(set(new_vars) - set(vars_used))
            vars_used.extend(new_vars)
            i += 1

        return list(set(vars_used))

    @classmethod
    def recursive_necessary_variables_search(cls, vars: List[str], model: ASTModel) -> List[str]:
        """
        Collect all the variable names used in the defining expressions of a list of variables.
        :param vars: list of variable names moved from synapse to neuron
        :param model: ASTModel to perform the recursive search
        :return: list of variable names from the recursive search
        """

        for var in vars:
            assert type(var) is str

        vars_used = vars.copy()
        i = 0
        while i < len(vars_used):
            new_vars = ASTUtils.get_necessary_variables(vars_used[i], model)
            new_vars = list(set(new_vars) - set(vars_used))
            vars_used.extend(new_vars)
            i += 1

        return list(set(vars_used))

    @classmethod
    def remove_initial_values_for_kernels(cls, model: ASTModel) -> None:
        """
        Remove initial values for original declarations (e.g. g_in, g_in', V_m); these might conflict with the initial value expressions returned from ODE-toolbox.
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

    @classmethod
    def update_initial_values_for_odes(cls, model: ASTModel, solver_dicts: List[dict]) -> None:
        """
        Update initial values for original ODE declarations (e.g. V_m', g_ahp'') that are present in the model before ODE-toolbox processing, with the formatted variable names and initial values returned by ODE-toolbox.
        """
        from pynestml.utils.model_parser import ModelParser
        from pynestml.visitors.ast_parent_visitor import ASTParentVisitor
        from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor

        assert len(model.get_equations_blocks()) == 1, "Only one equation block should be present"

        if not model.get_state_blocks():
            return

        for state_block in model.get_state_blocks():
            for iv_decl in state_block.get_declarations():
                for var in iv_decl.get_variables():
                    var_name = var.get_complete_name()
                    if cls.is_ode_variable(var.get_name(), model):
                        assert cls.variable_in_solver(cls.to_ode_toolbox_processed_name(var_name), solver_dicts)

                        # replace the defining expression by the ode-toolbox result
                        iv_expr = cls.get_initial_value_from_ode_toolbox_result(
                            cls.to_ode_toolbox_processed_name(var_name), solver_dicts)
                        assert iv_expr is not None
                        iv_expr = ModelParser.parse_expression(iv_expr)
                        iv_expr.update_scope(state_block.get_scope())
                        iv_decl.set_expression(iv_expr)

        model.accept(ASTParentVisitor())
        model.accept(ASTSymbolTableVisitor())

    @classmethod
    def integrate_odes_args_strs_from_function_call(cls, function_call: ASTFunctionCall):
        arg_names = []
        for arg in function_call.get_args():
            if isinstance(arg, ASTExpression):
                arg = arg.get_expression()
            assert isinstance(arg, ASTSimpleExpression)
            arg_names.append(arg.get_variable().get_name())

        arg_names.sort()

        return arg_names

    @classmethod
    def integrate_odes_args_str_from_function_call(cls, function_call: ASTFunctionCall):
        arg_names = ASTUtils.integrate_odes_args_strs_from_function_call(function_call)
        args_str = "_".join(arg_names)

        return args_str

    @classmethod
    def get_necessary_variables(cls, var: str, model: ASTExpression) -> List[ASTVariable]:
        r"""Return a list of all right-hand side variables in the model that a certain, given left-hand side variable ``var`` depends on."""
        class GetNecessaryVariablesVisitor(ASTVisitor):
            r"""N.B. use get_name() rather than get_complete_name() so we grab higher orders as well"""
            def __init__(self):
                super().__init__()
                self.vars = set()

            def visit_declaration(self, node: ASTDeclaration) -> None:
                for lhs_var in node.get_variables():
                    if var == lhs_var.get_name():
                        self.vars |= set(ASTUtils.get_all_variables_names_in_expression(node.get_expression()))

            def visit_inline_expression(self, node: ASTInlineExpression) -> None:
                if var == node.get_variable_name():
                    self.vars |= set(ASTUtils.get_all_variables_names_in_expression(node.get_expression()))

            def visit_ode_equation(self, node: ASTOdeEquation) -> None:
                if var == node.get_lhs().get_name():
                    self.vars |= set(ASTUtils.get_all_variables_names_in_expression(node.get_rhs()))

            def visit_kernel(self, node: ASTKernel) -> None:
                for expr in node.get_expressions():
                    if var in ASTUtils.get_all_variables_names_in_expression(expr):
                        self.vars |= set([str(s) for s in node.get_variable_names()])

            def visit_assignment(self, node: ASTAssignment) -> None:
                if var == node.lhs.get_name():
                    self.vars |= set(ASTUtils.get_all_variables_names_in_expression(node.get_expression()))

        visitor = GetNecessaryVariablesVisitor()
        model.accept(visitor)

        if var in visitor.vars:
            visitor.vars.remove(var)

        return visitor.vars

    @classmethod
    def get_all_variables_assigned_to(cls, node: ASTNode):
        class GetDependentVariablesVisitor(ASTVisitor):
            def __init__(self):
                super().__init__()
                self.vars = set()

            def visit_assignment(self, node: ASTAssignment) -> None:
                self.vars.add(node.lhs.get_name())

        visitor = GetDependentVariablesVisitor()
        node.accept(visitor)

        return visitor.vars

    @classmethod
    def get_dependent_variables(cls, var: str, model: ASTExpression) -> List[ASTVariable]:
        r"""Return a list of all left-hand side variables in the model that depend on ``var`` in their right-hand side."""
        class GetDependentVariablesVisitor(ASTVisitor):
            def __init__(self):
                super().__init__()
                self.vars = set()

            def visit_declaration(self, node: ASTDeclaration) -> None:
                if var in ASTUtils.get_all_variables_names_in_expression(node.get_expression()):
                    self.vars |= set([var.get_name() for var in node.get_variables()])

            def visit_inline_expression(self, node: ASTInlineExpression) -> None:
                if var in ASTUtils.get_all_variables_names_in_expression(node.get_expression()):
                    self.vars.add(node.get_variable_name())

            def visit_ode_equation(self, node: ASTOdeEquation) -> None:
                if var in ASTUtils.get_all_variables_names_in_expression(node.get_rhs()):
                    self.vars.add(node.get_lhs().get_name())

            def visit_kernel(self, node: ASTKernel) -> None:
                for expr in node.get_expressions():
                    # exclude the special case "t" because a function-of-time kernel might depend on t
                    if not var == "t" and var in ASTUtils.get_all_variables_names_in_expression(expr):
                        self.vars |= set([var.get_name() for var in node.get_variables()])

            def visit_assignment(self, node: ASTAssignment) -> None:
                rhs_vars = ASTUtils.get_all_variables_names_in_expression(node.rhs)

                if var in rhs_vars:
                    self.vars.add(str(node.lhs))

            def _visit_if_clause(self, node: ASTIfClause) -> None:
                cond_vars = ASTUtils.get_all_variables_names_in_expression(node.condition)
                if var in cond_vars:
                    # collect all variables assigned to in the if-block -- they all depend on ``var``
                    self.vars |= ASTUtils.get_all_variables_assigned_to(node.get_stmts_body())

            def visit_if_clause(self, node: ASTIfClause) -> None:
                self._visit_if_clause(node)

            def visit_elif_clause(self, node: ASTElifClause) -> None:
                self._visit_if_clause(node)

        visitor = GetDependentVariablesVisitor()
        model.accept(visitor)

        if var in visitor.vars:
            visitor.vars.remove(var)

        return visitor.vars

    @classmethod
    def get_all_variables_in_expression(cls, expr: ASTExpression) -> List[ASTVariable]:
        r"""
        """
        class GetAllVariablesVisitor(ASTVisitor):
            def __init__(self):
                super().__init__()
                self.vars = set()

            def visit_variable(self, node: ASTVariable):
                symbol = expr.get_scope().resolve_to_symbol(node.get_name(), SymbolKind.VARIABLE)
                if symbol:
                    self.vars.add(node)

            def visit_simple_expression(self, node: ASTSimpleExpression):
                if node.is_variable():
                    symbol = expr.get_scope().resolve_to_symbol(node.get_variable().get_name(), SymbolKind.VARIABLE)
                    if symbol:
                        self.vars.add(node.get_variable())

        visitor = GetAllVariablesVisitor()
        expr.accept(visitor)

        return visitor.vars

    @classmethod
    def get_all_variables_names_in_expression(cls, expr: ASTExpression) -> List[str]:
        r"""
        Get variable names of any order (foo, foo', foo'', etc. will result in "foo" being added to the list returned)
        """
        if not expr:
            return []

        return [var.get_name() for var in ASTUtils.get_all_variables_in_expression(expr)]

    @classmethod
    def create_integrate_odes_combinations(cls, model: ASTModel) -> None:
        r"""
        Visit all integrate_odes() calls in the model, compose these as a list of strings, and set them as a model private member (``model.integrate_odes_combinations``).
        """
        model.integrate_odes_combinations = []

        class IntegrateODEsFunctionCallVisitor(ASTVisitor):
            all_args = None

            def __init__(self):
                super().__init__()
                self.all_args = []

            def visit_small_stmt(self, node: ASTSmallStmt):
                self._visit(node)

            def visit_simple_expression(self, node: ASTSimpleExpression):
                self._visit(node)

            def _visit(self, node):
                if node.is_function_call() and node.get_function_call().get_name() == "integrate_odes":
                    args_str = ASTUtils.integrate_odes_args_str_from_function_call(node.get_function_call())
                    self.all_args.append(args_str)

        visitor = IntegrateODEsFunctionCallVisitor()
        model.accept(visitor)
        model.integrate_odes_combinations = visitor.all_args

        # always ensure code is generated for an integrate_odes() call without any arguments. This is needed, for example, for gap junctions support
        if not "" in model.integrate_odes_combinations:
            model.integrate_odes_combinations.append("")

        return model.integrate_odes_combinations

    @classmethod
    def get_all_integrate_odes_calls_unique(cls, model: ASTModel) -> None:
        r"""Get a list of all unique ``integrate_odes()`` function calls in the model (i.e. each having a different set of parameters)."""
        model.integrate_odes_combinations = []

        class IntegrateODEsFunctionCallVisitor(ASTVisitor):
            calls = None

            def __init__(self):
                super().__init__()
                self.calls = []

            def visit_small_stmt(self, node: ASTSmallStmt):
                self._visit(node)

            def visit_simple_expression(self, node: ASTSimpleExpression):
                self._visit(node)

            def _visit(self, node):
                if node.is_function_call() and node.get_function_call().get_name() == "integrate_odes" and not any([call.equals(node.get_function_call()) for call in self.calls]):
                    self.calls.append(node.get_function_call())

        visitor = IntegrateODEsFunctionCallVisitor()
        model.accept(visitor)

        return visitor.calls

    @classmethod
    def create_initial_values_for_kernels(cls, model: ASTModel, solver_dicts: List[Dict], kernels: List[ASTKernel]) -> None:
        r"""
        Add the variables used in kernels from the ode-toolbox result dictionary as ODEs in NESTML AST
        """
        for solver_dict in solver_dicts:
            if solver_dict is None:
                continue

            for var_name in solver_dict["initial_values"].keys():
                if cls.variable_in_kernels(var_name, kernels):
                    # original initial value expressions should have been removed to make place for ode-toolbox results
                    assert not cls.declaration_in_state_block(model, var_name)

        for solver_dict in solver_dicts:
            if solver_dict is None:
                continue

            for var_name, expr in solver_dict["initial_values"].items():
                # overwrite is allowed because initial values might be repeated between numeric and analytic solver
                if cls.variable_in_kernels(var_name, kernels):
                    spike_in_port_name = var_name.split("__X__")[1]
                    spike_in_port_name = spike_in_port_name.split("__d")[0]
                    spike_in_port = ASTUtils.get_input_port_by_name(model.get_input_blocks(), spike_in_port_name)
                    type_str = "real"
                    if spike_in_port:
                        differential_order: int = len(re.findall("__d", var_name))
                        if differential_order:
                            type_str = "(s**-" + str(differential_order) + ")"

                    expr = "0 " + type_str    # for kernels, "initial value" returned by ode-toolbox is actually the increment value; the actual initial value is 0 (property of the convolution)
                    if not cls.declaration_in_state_block(model, var_name):
                        cls.add_declaration_to_state_block(model, var_name, expr, type_str)

    @classmethod
    def transform_ode_and_kernels_to_json(cls, model: ASTModel, parameters_blocks: Sequence[ASTBlockWithVariables],
                                          kernel_buffers: Mapping[ASTKernel, ASTInputPort], printer: ASTPrinter) -> Dict:
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
        for equations_block in model.get_equations_blocks():
            for equation in equations_block.get_ode_equations():
                # n.b. includes single quotation marks to indicate differential order
                lhs = cls.to_ode_toolbox_name(equation.get_lhs().get_complete_name())
                rhs = printer.print(equation.get_rhs())
                entry = {"expression": lhs + " = " + rhs}
                symbol_name = equation.get_lhs().get_name()
                symbol = equations_block.get_scope().resolve_to_symbol(symbol_name, SymbolKind.VARIABLE)

                entry["initial_values"] = {}
                symbol_order = equation.get_lhs().get_differential_order()
                for order in range(symbol_order):
                    iv_symbol_name = symbol_name + "'" * order
                    initial_value_expr = model.get_initial_value(iv_symbol_name)
                    if initial_value_expr:
                        expr = printer.print(initial_value_expr)
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
                    entry["initial_values"][iv_sym_name_ode_toolbox] = printer.print(initial_value_expr)

                odetoolbox_indict["dynamics"].append(entry)

        odetoolbox_indict["parameters"] = {}
        for parameters_block in parameters_blocks:
            for decl in parameters_block.get_declarations():
                for var in decl.variables:
                    odetoolbox_indict["parameters"][var.get_complete_name()] = printer.print(decl.get_expression())

        return odetoolbox_indict

    @classmethod
    def remove_ode_definitions_from_equations_block(cls, model: ASTModel) -> None:
        """
        Removes all ODE definitions from all equations blocks in the model.
        """
        for equations_block in model.get_equations_blocks():
            decl_to_remove = set()
            for decl in equations_block.get_ode_equations():
                decl_to_remove.add(decl)

            for decl in decl_to_remove:
                equations_block.get_declarations().remove(decl)

    @classmethod
    def get_delta_factors_(cls, neuron: ASTModel, equations_block: ASTEquationsBlock) -> dict:
        r"""
        For every occurrence of a convolution of the form `x^(n) = a * convolve(kernel, inport) + ...` where `kernel` is a delta function, add the element `(x^(n), inport) --> a` to the set.
        """
        delta_factors = {}

        for ode_eq in equations_block.get_ode_equations():
            var = ode_eq.get_lhs()
            expr = ode_eq.get_rhs()
            conv_calls = ASTUtils.get_convolve_function_calls(expr)
            for conv_call in conv_calls:
                assert len(
                    conv_call.args) == 2, "convolve() function call should have precisely two arguments: kernel and spike input port"
                kernel = conv_call.args[0]
                if cls.is_delta_kernel(neuron.get_kernel_by_name(kernel.get_variable().get_name())):
                    inport = conv_call.args[1].get_variable()
                    expr_str = str(expr)
                    sympy_expr = sympy.parsing.sympy_parser.parse_expr(expr_str, global_dict=odetoolbox.Shape._sympy_globals)
                    sympy_expr = sympy.expand(sympy_expr)
                    sympy_conv_expr = sympy.parsing.sympy_parser.parse_expr(str(conv_call), global_dict=odetoolbox.Shape._sympy_globals)
                    factor_str = []
                    for term in sympy.Add.make_args(sympy_expr):
                        if term.find(sympy_conv_expr):
                            factor_str.append(str(term.replace(sympy_conv_expr, 1)))
                    factor_str = " + ".join(factor_str)
                    delta_factors[(var, inport)] = factor_str

        return delta_factors

    @classmethod
    def remove_kernel_definitions_from_equations_block(cls, model: ASTModel) -> ASTDeclaration:
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

        return decl_to_remove

    @classmethod
    def generate_kernel_buffers(cls, model: ASTModel, equations_block: Union[ASTEquationsBlock, List[ASTEquationsBlock]]) -> Mapping[ASTKernel, ASTInputPort]:
        """
        For every occurrence of a convolution of the form `convolve(var, spike_buf)`: add the element `(kernel, spike_buf)` to the set, with `kernel` being the kernel that contains variable `var`.
        """

        kernel_buffers = set()
        convolve_calls = ASTUtils.get_convolve_function_calls(equations_block)
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
            kernel_buffers.add(el)

        return kernel_buffers

    @classmethod
    def replace_convolution_aliasing_inlines(cls, neuron: ASTModel) -> None:
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

        for equation_block in neuron.get_equations_blocks():
            for decl in equation_block.get_declarations():
                if isinstance(decl, ASTInlineExpression):
                    expr = decl.get_expression()
                    if isinstance(expr, ASTExpression):
                        expr = expr.get_lhs()

                    if isinstance(expr, ASTSimpleExpression) \
                            and '__X__' in str(expr) \
                            and expr.get_variable():
                        replace_with_var_name = expr.get_variable().get_name()
                        neuron.accept(ASTHigherOrderVisitor(lambda x: replace_var(
                            x, decl.get_variable_name(), replace_with_var_name)))

    @classmethod
    def replace_variable_names_in_expressions(cls, model: ASTModel, solver_dicts: List[dict]) -> None:
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

        model.accept(ASTHigherOrderVisitor(func))

    @classmethod
    def replace_convolve_calls_with_buffers_(cls, model: ASTModel, equations_block: ASTEquationsBlock) -> None:
        r"""
        Replace all occurrences of `convolve(kernel[']^n, spike_input_port)` with the corresponding buffer variable, e.g. `g_E__X__spikes_exc[__d]^n` for a kernel named `g_E` and a spike input port named `spikes_exc`.
        """
        from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor

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
        equations_block.accept(ASTSymbolTableVisitor())

    @classmethod
    def update_blocktype_for_common_parameters(cls, node):
        r"""Change the BlockType for all homogeneous parameters to BlockType.COMMON_PARAMETER"""
        if node is None:
            return

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
                    Logger.log_message(None, -1, "Changing block type of variable " + str(node.get_complete_name()),
                                       None, LoggingLevel.INFO)

        visitor = ASTHomogeneousParametersBlockTypeChangeVisitor(all_homogeneous_parameters)
        node.accept(visitor)

    @classmethod
    def find_model_by_name(cls, model_name: str, models: Iterable[ASTModel]) -> Optional[ASTModel]:
        for model in models:
            if model.get_name() == model_name:
                return model

        return None

    @classmethod
    def get_convolve_function_calls(cls, nodes: Union[ASTNode, List[ASTNode]]):
        """
        Returns all sum function calls in the handed over meta_model node or one of its children.
        :param nodes: a single or list of AST nodes.
        """
        if isinstance(nodes, ASTNode):
            nodes = [nodes]

        function_calls = []
        for node in nodes:
            function_calls.extend(cls.get_function_calls(node, PredefinedFunctions.CONVOLVE))

        return function_calls

    @classmethod
    def contains_convolve_function_call(cls, ast: ASTNode) -> bool:
        """
        Indicates whether _ast or one of its child nodes contains a sum call.
        :param ast: a single meta_model
        :return: True if sum is contained, otherwise False.
        """
        return len(cls.get_function_calls(ast, PredefinedFunctions.CONVOLVE)) > 0

    @classmethod
    def get_function_calls(cls, ast_node: ASTNode, function_list: List[str]) -> List[ASTFunctionCall]:
        """
        For a handed over list of function names, this method retrieves all function calls in the meta_model.
        :param ast_node: a single meta_model node
        :param function_list: a list of function names
        :return: a list of all functions in the meta_model
        """
        res = list()
        if ast_node is None:
            return res
        from pynestml.visitors.ast_higher_order_visitor import ASTHigherOrderVisitor
        from pynestml.meta_model.ast_function_call import ASTFunctionCall
        fun = (lambda x: res.append(x) if isinstance(x, ASTFunctionCall) and x.get_name() in function_list else True)
        vis = ASTHigherOrderVisitor(visit_funcs=fun)
        ast_node.accept(vis)
        return res

    @classmethod
    def resolve_to_variable_symbol_in_blocks(cls, variable_name: str, blocks: List[ASTStmtsBody]):
        r"""
        Resolve a variable (by name) to its corresponding ``Symbol`` within the AST blocks in ``blocks``.
        """
        for block in blocks:
            sym = block.get_scope().resolve_to_symbol(variable_name, SymbolKind.VARIABLE)
            if sym:
                return sym
        return None

    @classmethod
    def get_unit_name(cls, variable: ASTVariable) -> str:
        assert variable.get_scope() is not None, "Undeclared variable: " + variable.get_complete_name()

        variable_name = CppVariablePrinter._print_cpp_name(variable.get_complete_name())
        symbol = variable.get_scope().resolve_to_symbol(variable_name, SymbolKind.VARIABLE)
        if isinstance(symbol.get_type_symbol(), UnitTypeSymbol):
            return symbol.get_type_symbol().unit.unit.to_string()

        return ''

    @classmethod
    def _find_port_in_dict(cls, rport_to_port_map: Dict[int, List[VariableSymbol]], port: VariableSymbol) -> int:
        """
        Finds the corresponding "inhibitory" port for a given "excitatory" port and vice versa in the handed over map.
        :param rport_to_port_map: map containing NESTML port names for the rport
        :param port: port to be searched
        :return: key value in the map if the port is found, else None
        """
        for key, value in rport_to_port_map.items():
            if len(value) == 1:
                if (port.is_excitatory() and value[0].is_inhibitory() and not value[0].is_excitatory()) \
                        or (port.is_inhibitory() and value[0].is_excitatory() and not value[0].is_inhibitory()):
                    if port.has_vector_parameter():
                        if cls.get_numeric_vector_size(port) == cls.get_numeric_vector_size(value[0]):
                            return key
                    else:
                        return key
        return None

    @classmethod
    def get_spike_input_ports_in_pairs(cls, neuron: ASTModel) -> Dict[int, List[VariableSymbol]]:
        """
        Returns a list of spike input ports in pairs in case of input port qualifiers.
        The result of this function is used to construct a vector that provides a mapping to the NESTML spike buffer index. The vector looks like below:
        .. code-block::
            [ {AMPA_SPIKES, GABA_SPIKES}, {NMDA_SPIKES, -1} ]

        where the vector index is the NEST rport number. The value is a tuple containing the NESTML index(es) to the spike buffer.
        In case if the rport is shared between two NESTML buffers, the vector element contains the tuple of the form (excitatory_port_index, inhibitory_port_index). Otherwise, the tuple is of the form (spike_port_index, -1).
        """
        rport_to_port_map = {}
        rport = 0
        for port in neuron.get_spike_input_ports():
            if port.is_excitatory() and port.is_inhibitory():
                rport_to_port_map[rport] = [port]
                rport += cls.get_numeric_vector_size(port) if port.has_vector_parameter() else 1
            else:
                key = cls._find_port_in_dict(rport_to_port_map, port)
                if key is not None:
                    # The corresponding spiking input pair is found.
                    # Add the port to the list and update rport
                    rport_to_port_map[key].append(port)
                    rport += cls.get_numeric_vector_size(port) if port.has_vector_parameter() else 1
                else:
                    # New input port. Retain the same rport number until the corresponding input port pair is found.
                    rport_to_port_map[rport] = [port]

        return rport_to_port_map

    @classmethod
    def assign_numeric_non_numeric_state_variables(cls, neuron, numeric_state_variable_names, numeric_update_expressions, update_expressions):
        r"""For each ASTVariable, set the ``node._is_numeric`` member to True or False based on whether this variable will be solved with the analytic or numeric solver.

        Ideally, this would not be a property of the ASTVariable as it is an implementation detail (that only emerges during code generation) and not an intrinsic part of the model itself. However, this approach is preferred over setting it as a property of the variable printers as it would have to make each printer aware of all models and variables therein."""
        class ASTVariableOriginSetterVisitor(ASTVisitor):
            def visit_variable(self, node):
                assert isinstance(node, ASTVariable)
                if node.get_complete_name() in self._numeric_state_variables:
                    node._is_numeric = True
                else:
                    node._is_numeric = False

                # Set the `_is_numeric` flag in its corresponding symbol
                symbol = node.get_scope().resolve_to_symbol(node.get_complete_name(), SymbolKind.VARIABLE)
                if symbol:
                    symbol._is_numeric = node._is_numeric

        visitor = ASTVariableOriginSetterVisitor()
        visitor._numeric_state_variables = numeric_state_variable_names
        neuron.accept(visitor)

        if "extra_on_emit_spike_stmts_from_synapse" in dir(neuron):
            for expr in neuron.extra_on_emit_spike_stmts_from_synapse:
                expr.accept(visitor)

        if update_expressions:
            for expr in update_expressions.values():
                expr.accept(visitor)

        if numeric_update_expressions:
            for expr in numeric_update_expressions.values():
                expr.accept(visitor)

        for update_expr_list in neuron.spike_updates.values():
            for update_expr in update_expr_list:
                update_expr.accept(visitor)

        for update_expr in neuron.post_spike_updates.values():
            update_expr.accept(visitor)

        for node in neuron.equations_with_delay_vars + neuron.equations_with_vector_vars:
            node.accept(visitor)

    @classmethod
    def depends_only_on_vars(cls, expr, vars):
        r"""Returns True if and only if all variables that occur in ``expr`` are in ``vars``"""

        class VariableFinderVisitor(ASTVisitor):
            def __init__(self):
                super(VariableFinderVisitor, self).__init__()
                self.vars = []

            def visit_variable(self, node: ASTNode):
                if not node.get_name() in self.vars:
                    self.vars.append(node.get_name())

        visitor = VariableFinderVisitor()
        expr.accept(visitor)

        for var in visitor.vars:
            if not var in vars:
                return False

        return True

    @classmethod
    def get_on_receive_blocks_by_input_port_name(cls, model: ASTModel, port_name: str) -> List[ASTOnReceiveBlock]:
        r"""Get the onReceive blocks in the model associated with a given input port."""
        blks = []
        for blk in model.get_on_receive_blocks():
            if blk.get_port_name() == port_name:
                blks.append(blk)

        return blks

    @classmethod
    def initial_value_or_zero(cls, astnode: ASTModel, var):
        if ASTUtils.get_state_variable_by_name(astnode, var):
            return astnode.get_initial_value(var)

        return "0"
