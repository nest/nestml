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
from pynestml.generated.PyNestMLLexer import PyNestMLLexer
from pynestml.meta_model.ast_assignment import ASTAssignment
from pynestml.meta_model.ast_block import ASTBlock
from pynestml.meta_model.ast_block_with_variables import ASTBlockWithVariables
from pynestml.meta_model.ast_declaration import ASTDeclaration
from pynestml.meta_model.ast_equations_block import ASTEquationsBlock
from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_external_variable import ASTExternalVariable
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.meta_model.ast_inline_expression import ASTInlineExpression
from pynestml.meta_model.ast_input_block import ASTInputBlock
from pynestml.meta_model.ast_input_port import ASTInputPort
from pynestml.meta_model.ast_model import ASTModel
from pynestml.meta_model.ast_model import ASTModel
from pynestml.meta_model.ast_model_body import ASTModelBody
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_node_factory import ASTNodeFactory
from pynestml.meta_model.ast_ode_equation import ASTOdeEquation
from pynestml.meta_model.ast_return_stmt import ASTReturnStmt
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.meta_model.ast_stmt import ASTStmt
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.symbols.predefined_functions import PredefinedFunctions
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
    def get_numeric_vector_size(cls, variable: VariableSymbol) -> int:
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
    def create_internal_block(cls, neuron):
        """
        Creates a single internal block in the handed over neuron.
        :param neuron: a single neuron
        :type neuron: ast_neuron
        :return: the modified neuron
        :rtype: ast_neuron
        """
        from pynestml.meta_model.ast_node_factory import ASTNodeFactory
        if not neuron.get_internals_blocks():
            internal = ASTNodeFactory.create_ast_block_with_variables(False, False, True, list(),
                                                                      ASTSourceLocation.get_added_source_position())
            internal.update_scope(neuron.get_scope())
            neuron.get_body().get_body_elements().append(internal)
        return neuron

    @classmethod
    def create_state_block(cls, neuron):
        """
        Creates a single internals block in the handed over neuron.
        :param neuron: a single neuron
        :type neuron: ast_neuron
        :return: the modified neuron
        :rtype: ast_neuron
        """
        # local import since otherwise circular dependency
        from pynestml.meta_model.ast_node_factory import ASTNodeFactory
        if not neuron.get_internals_blocks():
            state = ASTNodeFactory.create_ast_block_with_variables(True, False, False, list(),
                                                                   ASTSourceLocation.get_added_source_position())
            neuron.get_body().get_body_elements().append(state)
        return neuron

    @classmethod
    def create_equations_block(cls, neuron: ASTModel) -> ASTModel:
        """
        Creates a single equations block in the handed over neuron.
        :param neuron: a single neuron
        :return: the modified neuron
        """
        # local import since otherwise circular dependency
        from pynestml.meta_model.ast_node_factory import ASTNodeFactory
        if not neuron.get_equations_blocks():
            block = ASTNodeFactory.create_ast_equations_block(list(),
                                                              ASTSourceLocation.get_added_source_position())
            neuron.get_body().get_body_elements().append(block)
        return neuron

    @classmethod
    def get_declaration_by_name(cls, blocks: Union[ASTBlock, List[ASTBlock]], var_name: str) -> Optional[ASTDeclaration]:
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
    def all_variables_defined_in_block(cls, blocks: Union[ASTBlock, List[ASTBlock]]) -> List[ASTVariable]:
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
    def add_suffix_to_variable_names(cls, astnode: Union[ASTNode, List], suffix: str):
        """add suffix to variable names recursively throughout astnode"""

        if not isinstance(astnode, ASTNode):
            for node in astnode:
                ASTUtils.add_suffix_to_variable_names(node, suffix)
            return

        def replace_var(_expr=None):
            if isinstance(_expr, ASTSimpleExpression) and _expr.is_variable():
                var = _expr.get_variable()
            elif isinstance(_expr, ASTVariable):
                var = _expr
            else:
                return

            if not suffix in var.get_name() \
               and not var.get_name() == "t":
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
    def replace_with_external_variable(cls, var_name, node: ASTNode, suffix, new_scope, alternate_name=None):
        """
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
                Logger.log_message(None, -1, "ASTSimpleExpression replacement made (var = " + str(
                    ast_ext_var.get_name()) + ") in expression: " + str(node.get_parent(_expr)), None, LoggingLevel.INFO)
                _expr.set_variable(ast_ext_var)
                return

            if isinstance(_expr, ASTVariable):
                if isinstance(node.get_parent(_expr), ASTAssignment):
                    node.get_parent(_expr).lhs = ast_ext_var
                    Logger.log_message(None, -1, "ASTVariable replacement made in expression: "
                                       + str(node.get_parent(_expr)), None, LoggingLevel.INFO)
                elif isinstance(node.get_parent(_expr), ASTSimpleExpression) and node.get_parent(_expr).is_variable():
                    node.get_parent(_expr).set_variable(ast_ext_var)
                elif isinstance(node.get_parent(_expr), ASTDeclaration):
                    # variable could occur on the left-hand side; ignore. Only replace if it occurs on the right-hand side.
                    pass
                else:
                    Logger.log_message(None, -1, "Error: unhandled use of variable "
                                       + var_name + " in expression " + str(_expr), None, LoggingLevel.INFO)
                    raise Exception()
                return

            p = node.get_parent(var)
            Logger.log_message(None, -1, "Error: unhandled use of variable "
                               + var_name + " in expression " + str(p), None, LoggingLevel.INFO)
            raise Exception()

        node.accept(ASTHigherOrderVisitor(lambda x: replace_var(x)))

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
    def move_decls(cls, var_name, from_block, to_block, var_name_suffix, block_type: BlockType, mode="move", scope=None) -> List[ASTDeclaration]:
        from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor
        assert mode in ["move", "copy"]

        if not from_block \
           or not to_block:
            return []

        decls = ASTUtils.get_declarations_from_block(var_name, from_block)
        if var_name.endswith(var_name_suffix):
            decls.extend(ASTUtils.get_declarations_from_block(removesuffix(var_name, var_name_suffix), from_block))

        if decls:
            Logger.log_message(None, -1, "Moving definition of " + var_name + " from synapse to neuron",
                               None, LoggingLevel.INFO)
            for decl in decls:
                if mode == "move":
                    from_block.declarations.remove(decl)
                if mode == "copy":
                    decl = decl.clone()
                assert len(decl.get_variables()) <= 1
                if not decl.get_variables()[0].name.endswith(var_name_suffix):
                    ASTUtils.add_suffix_to_decl_lhs(decl, suffix=var_name_suffix)
                to_block.get_declarations().append(decl)
                decl.update_scope(to_block.get_scope())

                ast_symbol_table_visitor = ASTSymbolTableVisitor()
                ast_symbol_table_visitor.block_type_stack.push(block_type)
                decl.accept(ast_symbol_table_visitor)
                ast_symbol_table_visitor.block_type_stack.pop()

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
                else:
                    raise Exception("Tried to move unknown type " + str(type(decl)))

        return vars_used

    @classmethod
    def assign_ode_to_variables(cls, ode_block: ASTEquationsBlock):
        r"""
        Adds for each variable symbol the corresponding ode declaration if present.

        :param ode_block: a single block of ode declarations.
        """
        from pynestml.meta_model.ast_ode_equation import ASTOdeEquation
        for decl in ode_block.get_declarations():
            if isinstance(decl, ASTOdeEquation):
                ASTUtils.add_ode_to_variable(decl)

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

            existing_symbol.set_ode(ode_equation)

            ode_equation.get_scope().update_variable_symbol(existing_symbol)

    @classmethod
    def get_statements_from_block(cls, var_name, block):
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

    _variable_matching_template = r'(\b)({})(\b)'

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
    def add_declaration_to_state_block(cls, neuron: ASTModel, variable: str, initial_value: str) -> ASTModel:
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
        declaration_string = variable + ' real' + (
            '[' + vector_variable.get_vector_parameter() + ']'
            if vector_variable is not None and vector_variable.has_vector_parameter() else '') + ' = ' + initial_value
        ast_declaration = ModelParser.parse_declaration(declaration_string)
        if vector_variable is not None:
            ast_declaration.set_size_parameter(vector_variable.get_vector_parameter())
        neuron.add_to_state_block(ast_declaration)

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
        neuron.get_update_blocks()[0].get_block().get_stmts().append(stmt)
        small_stmt.update_scope(neuron.get_update_blocks()[0].get_block().get_scope())
        stmt.update_scope(neuron.get_update_blocks()[0].get_block().get_scope())
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
        neuron.get_update_blocks()[0].get_block().get_stmts().append(stmt)
        small_stmt.update_scope(neuron.get_update_blocks()[0].get_block().get_scope())
        stmt.update_scope(neuron.get_update_blocks()[0].get_block().get_scope())
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
    def get_input_port_by_name(cls, input_blocks: List[ASTInputBlock], port_name: str) -> ASTInputPort:
        """
        Get the input port given the port name
        :param input_block: block to be searched
        :param port_name: name of the input port
        :return: input port object
        """
        for input_block in input_blocks:
            for input_port in input_block.get_input_ports():
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

            for equations_block in node.get_equations_blocks():
                decls = cls.get_declarations_from_block(var, equations_block)

                if decls:
                    assert len(decls) == 1
                    decl = decls[0]
                    if (type(decl) in [ASTDeclaration, ASTReturnStmt] and decl.has_expression()) \
                            or type(decl) is ASTInlineExpression:
                        vars_used.extend(cls.collect_variable_names_in_expression(decl.get_expression()))
                    elif type(decl) is ASTOdeEquation:
                        vars_used.extend(cls.collect_variable_names_in_expression(decl.get_rhs()))
                    else:
                        raise Exception("Unknown type " + str(type(decl)))
                    vars_used = [str(var) for var in vars_used]
                    vars_to_check = vars_to_check.union(set(vars_used))

            vars_checked.add(var)

        return list(set(vars_checked))

    @classmethod
    def update_initial_values_for_odes(cls, neuron: ASTModel, solver_dicts: List[dict]) -> None:
        """
        Update initial values for original ODE declarations (e.g. V_m', g_ahp'') that are present in the model
        before ODE-toolbox processing, with the formatted variable names and initial values returned by ODE-toolbox.
        """
        from pynestml.utils.model_parser import ModelParser
        assert len(neuron.get_equations_blocks()) == 1, "Only one equation block should be present"

        if not neuron.get_state_blocks():
            return

        for state_block in neuron.get_state_blocks():
            for iv_decl in state_block.get_declarations():
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
                        iv_expr.update_scope(state_block.get_scope())
                        iv_decl.set_expression(iv_expr)

    @classmethod
    def transform_odes_to_json(cls, neuron: ASTModel, parameters_blocks: Sequence[ASTBlockWithVariables],
                                          printer: ASTPrinter) -> Dict:
        """
        Converts AST node to a JSON representation suitable for passing to ode-toolbox.
        """
        odetoolbox_indict = {}

        odetoolbox_indict["dynamics"] = []
        for equations_block in neuron.get_equations_blocks():
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
                    initial_value_expr = neuron.get_initial_value(iv_symbol_name)
                    if initial_value_expr:
                        expr = printer.print(initial_value_expr)
                        entry["initial_values"][cls.to_ode_toolbox_name(iv_symbol_name)] = expr
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
    def make_inline_expressions_self_contained(cls, inline_expressions: List[ASTInlineExpression]) -> List[ASTInlineExpression]:
        """
        Make inline_expressions self contained, i.e. without any references to other inline_expressions.

        TODO: it should be a method inside of the ASTInlineExpression
        TODO: this should be done by means of a visitor

        :param inline_expressions: A sorted list with entries ASTInlineExpression.
        :return: A list with ASTInlineExpressions. Defining expressions don't depend on each other.
        """
        from pynestml.utils.model_parser import ModelParser
        from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor

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
        from pynestml.utils.model_parser import ModelParser
        from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor

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
    def add_timestep_symbol(cls, neuron: ASTModel) -> None:
        """
        Add timestep variable to the internals block
        """
        from pynestml.utils.model_parser import ModelParser
        assert neuron.get_initial_value(
            "__h") is None, "\"__h\" is a reserved name, please do not use variables by this name in your NESTML file"
        assert not "__h" in [sym.name for sym in neuron.get_internal_symbols(
        )], "\"__h\" is a reserved name, please do not use variables by this name in your NESTML file"
        neuron.add_to_internals_block(ModelParser.parse_declaration('__h ms = resolution()'), index=0)

    @classmethod
    def replace_variable_names_in_expressions(cls, neuron: ASTModel, solver_dicts: List[dict]) -> None:
        """
        Replace all occurrences of variables names in NESTML format (e.g. `g_ex$''`)` with the ode-toolbox formatted
        variable name (e.g. `g_ex__DOLLAR__d__d`).
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
    def resolve_to_variable_symbol_in_blocks(cls, variable_name: str, blocks: List[ASTBlock]):
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

        visitor = ASTVariableOriginSetterVisitor()
        visitor._numeric_state_variables = numeric_state_variable_names
        neuron.accept(visitor)

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
