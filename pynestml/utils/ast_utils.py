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

from typing import Iterable, List, Optional, Union

from pynestml.meta_model.ast_assignment import ASTAssignment
from pynestml.meta_model.ast_block import ASTBlock
from pynestml.meta_model.ast_block_with_variables import ASTBlockWithVariables
from pynestml.meta_model.ast_declaration import ASTDeclaration
from pynestml.meta_model.ast_equations_block import ASTEquationsBlock
from pynestml.meta_model.ast_external_variable import ASTExternalVariable
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.meta_model.ast_inline_expression import ASTInlineExpression
from pynestml.meta_model.ast_kernel import ASTKernel
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_neuron_or_synapse_body import ASTNeuronOrSynapseBody
from pynestml.meta_model.ast_ode_equation import ASTOdeEquation
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.meta_model.ast_stmt import ASTStmt
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.symbols.variable_symbol import VariableSymbol
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.symbols.symbol import Symbol, SymbolKind
from pynestml.symbols.variable_symbol import VariableSymbol, VariableType
from pynestml.symbols.variable_symbol import BlockType
from pynestml.utils.ast_source_location import ASTSourceLocation
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_higher_order_visitor import ASTHigherOrderVisitor
from pynestml.visitors.ast_visitor import ASTVisitor


class ASTUtils:
    """
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
        :rtype: list(ASTNeuron)
        """
        ret = list()
        for compilationUnit in list_of_compilation_units:
            ret.extend(compilationUnit.get_neuron_list())
        return ret

    @classmethod
    def get_all_synapses(cls, list_of_compilation_units):
        """
        For a list of compilation units, it returns a list containing all synapses defined in all compilation
        units.
        :param list_of_compilation_units: a list of compilation units.
        :type list_of_compilation_units: list(ASTNestMLCompilationUnit)
        :return: a list of synapses
        :rtype: list(ASTSynapse)
        """
        ret = list()
        for compilationUnit in list_of_compilation_units:
            ret.extend(compilationUnit.get_synapse_list())
        return ret

    @classmethod
    def get_all_nodes(cls, list_of_compilation_units):
        """
        For a list of compilation units, it returns a list containing all nodes defined in all compilation
        units.
        :param list_of_compilation_units: a list of compilation units.
        :type list_of_compilation_units: list(ASTNestMLCompilationUnit)
        :return: a list of nodes
        :rtype: list(ASTNode)
        """
        from pynestml.meta_model.ast_neuron import ASTNeuron
        from pynestml.meta_model.ast_synapse import ASTSynapse
        ret = list()
        for compilationUnit in list_of_compilation_units:
            if isinstance(compilationUnit, ASTNeuron):
                ret.extend(compilationUnit.get_neuron_list())
            elif isinstance(compilationUnit, ASTSynapse):
                ret.extend(compilationUnit.get_synapse_list())
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
    def is_integrate(cls, function_call):
        """
        Checks if the handed over function call is a ode integration function call.
        :param function_call: a single function call
        :type function_call: ASTFunctionCall
        :return: True if ode integration call, otherwise False.
        :rtype: bool
        """
        return function_call.get_name() == PredefinedFunctions.INTEGRATE_ODES

    @classmethod
    def has_spike_input(cls, body: ASTNeuronOrSynapseBody) -> bool:
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
    def has_continuous_input(cls, body: ASTNeuronOrSynapseBody) -> bool:
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
    def compute_type_name(cls, data_type):
        """
        Computes the representation of the data type.
        :param data_type: a single data type.
        :type data_type: ast_data_type
        :return: the corresponding representation.
        :rtype: str
        """
        if data_type.is_boolean:
            return 'boolean'
        elif data_type.is_integer:
            return 'integer'
        elif data_type.is_real:
            return 'real'
        elif data_type.is_string:
            return 'string'
        elif data_type.is_void:
            return 'void'
        elif data_type.is_unit_type():
            return str(data_type)
        else:
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
        vector_variable = ASTVariable(vector_parameter, scope=variable.get_corresponding_scope())
        symbol = vector_variable.get_scope().resolve_to_symbol(vector_variable.get_complete_name(), SymbolKind.VARIABLE)
        if symbol is not None:
            # vector size is a variable. Get the value from RHS
            return symbol.get_declaring_expression().get_numeric_literal()
        return int(vector_parameter)

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
        if neuron.get_internals_blocks() is None:
            internal = ASTNodeFactory.create_ast_block_with_variables(False, False, True, list(),
                                                                      ASTSourceLocation.get_added_source_position())
            internal.update_scope(neuron.get_scope())
            neuron.get_body().get_body_elements().append(internal)
        return neuron

    @classmethod
    def create_state_block(cls, neuron):
        """
        Creates a single internal block in the handed over neuron.
        :param neuron: a single neuron
        :type neuron: ast_neuron
        :return: the modified neuron
        :rtype: ast_neuron
        """
        # local import since otherwise circular dependency
        from pynestml.meta_model.ast_node_factory import ASTNodeFactory
        if neuron.get_internals_blocks() is None:
            state = ASTNodeFactory.create_ast_block_with_variables(True, False, False, list(),
                                                                   ASTSourceLocation.get_added_source_position())
            neuron.get_body().get_body_elements().append(state)
        return neuron

    @classmethod
    def contains_convolve_call(cls, variable: VariableSymbol) -> bool:
        """
        Indicates whether the declaring rhs of this variable symbol has a convolve() in it.
        :return: True if contained, otherwise False.
        """
        if not variable.get_declaring_expression():
            return False
        else:
            for func in variable.get_declaring_expression().get_function_calls():
                if func.get_name() == PredefinedFunctions.CONVOLVE:
                    return True
        return False

    @classmethod
    def add_to_state_block(cls, neuron, declaration):
        """
        Adds the handed over declaration the state block
        :param neuron: a single neuron instance
        :type neuron: ast_neuron
        :param declaration: a single declaration
        :type declaration: ast_declaration
        """
        if neuron.get_state_blocks() is None:
            ASTUtils.create_state_block(neuron)
        neuron.get_state_blocks().get_declarations().append(declaration)
        return

    @classmethod
    def get_declaration_by_name(cls, block: ASTBlock, var_name: str) -> Optional[ASTDeclaration]:
        """
        Get a declaration by variable name.
        :param block: the block to look for the variable in
        :param var_name: name of the variable to look for (including single quotes indicating differential order)
        """
        decls = block.get_declarations()
        for decl in decls:
            for var in decl.get_variables():
                if var.get_complete_name() == var_name:
                    return decl
        return None

    @classmethod
    def all_variables_defined_in_block(cls, block: Optional[ASTBlock]) -> List[ASTVariable]:
        """return a list of all variable declarations in a block"""
        if block is None:
            return []
        vars = []
        for decl in block.get_declarations():
            for var in decl.get_variables():
                vars.append(var)
        return vars

    @classmethod
    def inline_aliases_convolution(cls, inline_expr: ASTInlineExpression) -> bool:
        """
        Returns True if and only if the inline expression is of the form ``var type = convolve(...)``.
        """
        if isinstance(inline_expr.get_expression(), ASTSimpleExpression) \
           and inline_expr.get_expression().is_function_call() \
           and inline_expr.get_expression().get_function_call().get_name() == PredefinedFunctions.CONVOLVE:
            return True
        return False

    @classmethod
    def add_suffix_to_variable_name(cls, var_name: str, astnode: ASTNode, suffix: str, scope=None):
        """add suffix to variable by given name recursively throughout astnode"""
        from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor
        from pynestml.symbols.variable_symbol import BlockType
        from pynestml.symbols.variable_symbol import VariableSymbol, BlockType, VariableType

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

            # if scope is not None:
            #     symbol = VariableSymbol(name=var.get_name(), block_type=BlockType.PARAMETERS,
            #                     type_symbol=var.get_type_symbol(),
            #                     variable_type=VariableType.VARIABLE)
            #     scope.add_symbol(symbol)
            #     var.update_scope(scope)
            #     assert scope.resolve_to_symbol(var.get_name(), SymbolKind.VARIABLE) is not None
            #     assert scope.resolve_to_symbol(var.get_name(), SymbolKind.VARIABLE).block_type == BlockType.PARAMETERS
            #     #var.accept(ASTSymbolTableVisitor())

        astnode.accept(ASTHigherOrderVisitor(lambda x: replace_var(x)))

    @classmethod
    def add_suffix_to_variable_names(cls, astnode: Union[ASTNode, List], suffix: str):
        """add suffix to variable names recursively throughout astnode"""
        from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor
        from pynestml.symbols.variable_symbol import BlockType
        from pynestml.symbols.variable_symbol import VariableSymbol, BlockType, VariableType

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
        if not node.get_equations_block():
            return None
        for inline_expr in node.get_equations_block().get_inline_expressions():
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

    @classmethod
    def get_all_variables_used_in_convolutions(cls, node: ASTNode, parent_node: ASTNode) -> List[str]:
        """Make a list of all variable symbol names that are in ``node`` and used in a convolution"""
        from pynestml.codegeneration.ast_transformers import ASTTransformers

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
                    input_port = ASTTransformers.get_input_port_by_name(
                        self.parent_node.get_input_blocks(), symbol_buffer.name)
                    if input_port:
                        found_parent_assignment = False
                        node_ = node
                        while not found_parent_assignment:
                            node_ = self.parent_node.get_parent(node_)
                            # XXX TODO also needs to accept normal ASTExpression, ASTAssignment?
                            if isinstance(node_, ASTInlineExpression):
                                found_parent_assignment = True
                        var_name = node_.get_variable_name()
                        self._variables.append(var_name)

        if node is None:
            return []

        visitor = ASTAllVariablesUsedInConvolutionVisitor(node, parent_node)
        node.accept(visitor)
        return visitor._variables

    @classmethod
    def move_decls(cls, var_name, from_block, to_block, var_name_suffix, block_type: BlockType, mode="move", scope=None) -> List[ASTDeclaration]:
        from pynestml.codegeneration.ast_transformers import ASTTransformers
        from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor
        assert mode in ["move", "copy"]

        if not from_block \
           or not to_block:
            return []

        decls = ASTTransformers.get_declarations_from_block(var_name, from_block)
        if var_name.endswith(var_name_suffix):
            decls.extend(ASTTransformers.get_declarations_from_block(var_name.removesuffix(var_name_suffix), from_block))

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
        from pynestml.codegeneration.ast_transformers import ASTTransformers

        assert mode in ["move", "copy"]

        if not to_block or not from_block:
            return []

        decls = ASTTransformers.get_declarations_from_block(state_var, from_block)

        for decl in decls:
            if mode == "move":
                from_block.declarations.remove(decl)
            ASTUtils.add_suffix_to_decl_lhs(decl, suffix=var_name_suffix)
            to_block.get_declarations().append(decl)
            decl.update_scope(to_block.get_scope())

        return decls

    @classmethod
    def collects_vars_used_in_equation(cls, state_var, from_block):
        from pynestml.codegeneration.ast_transformers import ASTTransformers
        if not from_block:
            return

        decls = ASTTransformers.get_declarations_from_block(state_var, from_block)
        vars_used = []
        if decls:
            for decl in decls:
                if (type(decl) in [ASTDeclaration, ASTReturnStmt] and decl.has_expression()) \
                   or type(decl) is ASTInlineExpression:
                    vars_used.extend(
                        ASTTransformers.collect_variable_names_in_expression(decl.get_expression()))
                elif type(decl) is ASTOdeEquation:
                    vars_used.extend(ASTTransformers.collect_variable_names_in_expression(decl.get_rhs()))
                elif type(decl) is ASTKernel:
                    for expr in decl.get_expressions():
                        vars_used.extend(ASTTransformers.collect_variable_names_in_expression(expr))
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
        block = block.get_block()
        all_stmts = block.get_stmts()
        stmts = []
        for node in all_stmts:
            if node.is_small_stmt() \
               and node.small_stmt.is_assignment() \
               and node.small_stmt.get_assignment().lhs.get_name() == var_name:
                stmts.append(node)
        return stmts
